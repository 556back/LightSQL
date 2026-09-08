import json
import time
import uuid
from datetime import timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from pydantic import ValidationError
from sqlmodel import Session, col, select

from app.models import User
from app.modules.assistant import context as semantic_context
from app.modules.assistant import gateway
from app.modules.assistant.models import (
    AskInput,
    AssistantTurn,
    Conversation,
    ConversationPublic,
    PlanDecision,
    TurnPublic,
)
from app.modules.datasources.models import now
from app.modules.datasources.service import decrypt_password, encrypt_password
from app.modules.query import service as queries
from app.modules.query.compiler import fingerprint
from app.modules.query.exploration import catalog as exploration_catalog
from app.modules.query.models import QueryPlan, QuerySubmission, parse_plan


def unpack(turn: AssistantTurn) -> dict:
    return (
        json.loads(decrypt_password(turn.encrypted_payload))
        if turn.encrypted_payload
        else {}
    )


def pack(turn: AssistantTurn, payload: dict) -> None:
    turn.encrypted_payload = encrypt_password(json.dumps(payload, ensure_ascii=False))


def purge(session: Session) -> None:
    expired = select(Conversation.id).where(Conversation.expires_at <= now())
    for turn in session.exec(
        select(AssistantTurn).where(
            col(AssistantTurn.conversation_id).in_(expired),
            AssistantTurn.encrypted_payload != "",
        )
    ).all():
        turn.encrypted_payload = ""
        turn.message = "会话已过期"
        turn.status = "expired"
        session.add(turn)
    # Crash recovery never repeats paid model calls automatically.
    for turn in session.exec(
        select(AssistantTurn).where(
            AssistantTurn.status == "planning",
            AssistantTurn.created_at < now() - timedelta(minutes=4),
        )
    ).all():
        turn.status, turn.message = "failed", "规划中断，请重新提问"
        session.add(turn)
    old = list(
        session.exec(
            select(Conversation).where(
                Conversation.created_at < now() - timedelta(days=90)
            )
        ).all()
    )
    for conversation in old:
        for turn in session.exec(
            select(AssistantTurn).where(
                AssistantTurn.conversation_id == conversation.id
            )
        ).all():
            session.delete(turn)
        session.delete(conversation)


def owned(session: Session, conversation_id: uuid.UUID, user: User, lock=False):
    statement = select(Conversation).where(Conversation.id == conversation_id)
    conversation = session.exec(
        statement.with_for_update() if lock else statement
    ).first()
    if not conversation or conversation.actor_id != user.id:
        raise HTTPException(404, "会话不存在")
    if queries.utc(conversation.expires_at) <= now():
        purge(session)
        session.commit()
        raise HTTPException(410, "会话已过期，请新建会话")
    fresh_user = session.get(User, user.id, populate_existing=True)
    if not fresh_user or not fresh_user.is_active:
        raise HTTPException(403, "账号已不可用")
    current = queries.resolve(session, conversation.topic_id, fresh_user)
    if (
        current[1].id != conversation.release_id
        or current[6] != conversation.policy_fingerprint
    ):
        raise HTTPException(409, "语义版本或查询授权已变化，请新建会话")
    if current[3].database_type not in ("postgresql", "mysql", "oracle"):
        raise HTTPException(
            422, "当前智能问答仅验收 PostgreSQL、MySQL、Oracle；达梦和人大金仓暂缓"
        )
    return conversation, current


def public(session: Session, conversation: Conversation) -> ConversationPublic:
    turns = []
    for turn in session.exec(
        select(AssistantTurn)
        .where(AssistantTurn.conversation_id == conversation.id)
        .order_by(col(AssistantTurn.sequence))
    ).all():
        payload = unpack(turn)
        turns.append(
            TurnPublic(
                id=turn.id,
                sequence=turn.sequence,
                status=turn.status,
                question=payload.get("question", ""),
                message=turn.message,
                plan=payload.get("plan")
                if payload.get("plan", {}).get("kind") != "sql"
                else None,
                sql_plan=payload.get("plan")
                if payload.get("plan", {}).get("kind") == "sql"
                else None,
                chart=payload.get("chart", "auto"),
                analysis_requested=payload.get("analysis_requested", False),
                ambiguities=payload.get("ambiguities", []),
                model=turn.model,
                attempts=turn.attempts,
                elapsed_ms=turn.elapsed_ms,
                query_job_id=turn.query_job_id,
                feedback=payload.get("feedback"),
            )
        )
    return ConversationPublic(
        id=conversation.id,
        topic_id=conversation.topic_id,
        revision=conversation.revision,
        expires_at=conversation.expires_at,
        turns=turns,
        created_at=conversation.created_at,
    )


def create(session: Session, user: User, topic_id: uuid.UUID) -> ConversationPublic:
    queries.gate(session)
    purge(session)
    current = queries.resolve(session, topic_id, user)
    if current[3].database_type not in ("postgresql", "mysql", "oracle"):
        raise HTTPException(422, "当前智能问答仅支持 PostgreSQL、MySQL、Oracle")
    recent = session.exec(
        select(Conversation).where(
            Conversation.actor_id == user.id, Conversation.expires_at > now()
        )
    ).all()
    if len(recent) >= 100:
        raise HTTPException(429, "有效会话已达到 100 个，请删除不再需要的会话")
    conversation = Conversation(
        actor_id=user.id,
        topic_id=topic_id,
        release_id=current[1].id,
        policy_fingerprint=current[6],
        expires_at=now() + timedelta(hours=24),
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return public(session, conversation)


async def ask(
    session: Session, user: User, conversation_id: uuid.UUID, body: AskInput
) -> ConversationPublic:
    queries.gate(session)
    purge(session)
    conversation, current = owned(session, conversation_id, user, lock=True)
    turns = list(
        session.exec(
            select(AssistantTurn)
            .where(AssistantTurn.conversation_id == conversation.id)
            .order_by(col(AssistantTurn.sequence))
        ).all()
    )
    digest = fingerprint(body.model_dump(mode="json", exclude={"expected_revision"}))
    existing = next((t for t in turns if t.request_id == body.request_id), None)
    if existing:
        if existing.input_digest != digest:
            raise HTTPException(409, "同一请求标识不能替换问题")
        session.commit()
        return public(session, conversation)
    if conversation.revision != body.expected_revision:
        raise HTTPException(409, "会话已更新，请刷新后重试")
    planning = session.exec(
        select(AssistantTurn).where(AssistantTurn.status == "planning")
    ).all()
    if len(planning) >= 4 or any(t.status == "planning" for t in turns):
        raise HTTPException(429, "已有规划正在进行，请等待完成")
    from app.modules.integration.service import scheduling_actor
    from app.modules.integration.models import IntegrationIdentity

    owner_id = scheduling_actor(session, user.id)
    actor_ids = {owner_id, user.id}
    actor_ids.update(session.exec(select(IntegrationIdentity.actor_id).where(IntegrationIdentity.user_id == owner_id)).all())
    actor_conversations = {
        c.id
        for c in session.exec(
            select(Conversation).where(col(Conversation.actor_id).in_(actor_ids))
        ).all()
    }
    if any(t.conversation_id in actor_conversations for t in planning):
        raise HTTPException(429, "你已有规划正在进行，请等待完成")
    if len(turns) >= 50:
        raise HTTPException(422, "会话已达到 50 轮，请新建会话")
    previous = None
    if not body.reset_context:
        previous = next(
            (
                unpack(t).get("plan")
                for t in reversed(turns)
                if t.status in ("ready", "submitted")
            ),
            None,
        )
    question = body.question
    if (
        not body.reset_context
        and turns
        and turns[-1].status == "clarification"
        and not body.entity_choices
    ):
        question = (
            unpack(turns[-1]).get("effective_question", turns[-1].message)
            + "，补充："
            + question
        )
    if len(question) > 4000:
        raise HTTPException(422, "补充内容过长，请清除上下文后重新提问")
    conversation.revision += 1
    turn = AssistantTurn(
        conversation_id=conversation.id,
        request_id=body.request_id,
        input_digest=digest,
        sequence=conversation.revision,
    )
    payload = {"question": body.question, "effective_question": question}
    pack(turn, payload)
    session.add_all([conversation, turn])
    session.commit()
    session.refresh(turn)
    session.refresh(conversation)
    started = time.monotonic()
    try:
        prepared = semantic_context.prepare(
            current[2],
            current[5],
            question,
            QueryPlan.model_validate(previous)
            if previous and previous.get("kind") != "sql"
            else None,
            body.entity_choices,
            now().astimezone(ZoneInfo(current[2].timezone)).date(),
            allow_empty=body.mode != "metrics",
        )
        if body.mode != "metrics":
            prepared.catalog["tables"] = exploration_catalog(
                current[2], current[4], current[5]
            )
            prepared.catalog["relations"] = [
                r.model_dump(exclude={"description"})
                for r in current[2].relations
                if {r.from_model, r.to_model}
                <= {t["name"] for t in prepared.catalog["tables"]}
                and all(
                    set(names)
                    <= {
                        c["name"]
                        for t in prepared.catalog["tables"]
                        if t["name"] == model
                        for c in t["columns"]
                    }
                    for model, names in (
                        (r.from_model, r.from_columns),
                        (r.to_model, r.to_columns),
                    )
                )
            ]
            if previous and previous.get("kind") == "sql":
                prepared.prior = semantic_context.sql_history(previous, prepared)
        payload["safe_question"] = prepared.question
        if prepared.ambiguities:
            turn.status, turn.message = (
                "clarification",
                "同一词语对应多个实体，请选择后继续",
            )
            payload["ambiguities"] = [a.model_dump() for a in prepared.ambiguities]
        else:
            config = gateway.active(session)
            turn.gateway_id, turn.gateway_revision, turn.model = (
                config.id,
                config.revision,
                config.model,
            )
            turn.message = "正在调用模型生成查询计划"
            session.add(turn)
            session.commit()
            # Detach network input from the DB transaction; no locks held over I/O.
            session.refresh(config)
            session.expunge(config)
            session.commit()
            messages = [
                {
                    "role": "system",
                    "content": semantic_context.SYSTEM
                    if body.mode == "metrics"
                    else semantic_context.EXPLORATION_SYSTEM,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "question": prepared.question,
                            "mode": body.mode,
                            "catalog": prepared.catalog,
                            "previous_plan": prepared.prior,
                            "reference_bindings": [
                                {
                                    "ref": ref,
                                    "dimension_id": value[0],
                                    **next(
                                        (
                                            {"model_id": d.model_id, "column": d.column}
                                            for d in current[2].dimensions
                                            if d.id == value[0]
                                            and any(
                                                t["name"] == d.model_id
                                                and any(
                                                    c["name"] == d.column
                                                    for c in t["columns"]
                                                )
                                                for t in prepared.catalog.get(
                                                    "tables", []
                                                )
                                            )
                                        ),
                                        {},
                                    ),
                                }
                                for ref, value in prepared.refs.items()
                            ],
                        },
                        ensure_ascii=False,
                    ),
                },
            ]
            for attempt in range(2):
                session.expire_all()
                fresh_user = session.get(User, user.id)
                if not fresh_user:
                    raise HTTPException(403, "账号已不可用")
                owned(session, conversation_id, fresh_user)
                active_config = gateway.active(session)
                if (
                    active_config.id != config.id
                    or active_config.revision != config.revision
                ):
                    raise HTTPException(409, "模型配置已切换，请重新提问")
                turn.attempts = attempt + 1
                session.add(turn)
                session.commit()
                content, usage, _ = await gateway.complete(
                    config, messages, PlanDecision.model_json_schema()
                )
                turn.prompt_tokens += usage.get("prompt_tokens", 0)
                turn.completion_tokens += usage.get("completion_tokens", 0)
                turn.message = "正在校验查询结构、口径与数据权限"
                session.add(turn)
                session.commit()
                session.expire_all()
                fresh_user = session.get(User, user.id)
                if not fresh_user:
                    raise HTTPException(403, "账号已不可用")
                owned(session, conversation_id, fresh_user)
                try:
                    decision = PlanDecision.model_validate_json(content)
                    if decision.action == "plan":
                        if (decision.plan is None) == (decision.sql_plan is None):
                            raise ValueError("missing plan")
                        if decision.sql_plan is not None:
                            if body.mode == "metrics":
                                raise ValueError("SQL disabled in metric mode")
                            plan = semantic_context.materialize_sql(
                                decision.sql_plan, prepared
                            )
                        else:
                            assert decision.plan is not None
                            plan = semantic_context.materialize(decision.plan, prepared)
                        # Re-read auth and bindings after the external call.
                        session.expire_all()
                        fresh_user = session.get(User, user.id)
                        if not fresh_user:
                            raise HTTPException(403, "账号已不可用")
                        owned(session, conversation_id, fresh_user)
                        queries.compile_for(
                            session, conversation.topic_id, fresh_user, plan
                        )
                        payload["plan"] = plan.model_dump(mode="json")
                        payload["chart"] = decision.chart
                        payload["analysis_requested"] = decision.analysis_requested
                        turn.status, turn.message = (
                            "ready",
                            decision.message or "查询已通过本地只读和权限校验",
                        )
                    elif decision.plan is not None or decision.sql_plan is not None:
                        raise ValueError("unexpected plan")
                    else:
                        turn.status = (
                            "clarification"
                            if decision.action == "clarify"
                            else "unsupported"
                        )
                        turn.message = decision.message or "请补充问题的业务口径"
                    break
                except (ValidationError, ValueError, HTTPException) as exc:
                    if isinstance(exc, HTTPException) and exc.status_code in (
                        403,
                        404,
                        409,
                        410,
                    ):
                        raise
                    if attempt == 1:
                        raise HTTPException(
                            422, "模型计划未通过结构或语义校验，请补充口径后重试"
                        ) from None
                    # Never return SQL, original provider output, or error values.
                    messages.append(
                        {
                            "role": "user",
                            "content": "上一输出未通过本地校验。请仅依据当前目录与引用重建完整 JSON；无法表达时返回 clarify 或 unsupported。",
                        }
                    )
    except HTTPException as exc:
        turn.status, turn.message = "failed", str(exc.detail)[:500]
    turn.elapsed_ms = round((time.monotonic() - started) * 1000)
    pack(turn, payload)
    session.add(turn)
    session.commit()
    session.refresh(conversation)
    owned(session, conversation_id, user)
    return public(session, conversation)


def execute(
    session: Session, user: User, conversation_id: uuid.UUID, turn_id: uuid.UUID
):
    queries.gate(session)
    conversation, _ = owned(session, conversation_id, user, lock=True)
    turn = session.get(AssistantTurn, turn_id)
    if not turn or turn.conversation_id != conversation.id:
        raise HTTPException(404, "问答轮次不存在")
    if turn.status not in ("ready", "submitted"):
        raise HTTPException(409, "本轮尚无可执行计划")
    if turn.sequence != conversation.revision:
        raise HTTPException(409, "已有新的追问，请执行最新计划")
    plan = parse_plan(unpack(turn)["plan"])
    fresh_user = session.get(User, user.id, populate_existing=True)
    if not fresh_user or not fresh_user.is_active:
        raise HTTPException(403, "账号已不可用")
    job = queries.submit(
        session,
        fresh_user,
        QuerySubmission(topic_id=conversation.topic_id, request_id=turn.id, plan=plan),
    )
    turn.query_job_id, turn.status = job.id, "submitted"
    session.add(turn)
    session.commit()
    return queries.public(job, user)
