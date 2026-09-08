import asyncio
import json
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlmodel import col, select
from starlette.concurrency import run_in_threadpool

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.modules.assistant import gateway, service
from app.modules.assistant.models import (
    AnalysisPublic,
    AnswerEvidence,
    AskInput,
    AssistantTurn,
    Conversation,
    ConversationCreate,
    ConversationPublic,
    FeedbackInput,
    FeedbackPublic,
    GatewayAudit,
    GatewayInput,
    GatewayPublic,
    GatewayRevision,
    GatewayState,
    GatewayTest,
    ModelGateway,
)
from app.modules.datasources.service import encrypt_password
from app.modules.query.models import QueryJobPublic

router = APIRouter(prefix="/assistant", tags=["assistant"])
admin = [Depends(get_current_active_superuser)]


@router.get("/gateways/presets", dependencies=admin)
def gateway_presets() -> list[dict[str, str]]:
    return gateway.PRESETS


@router.get("/gateways", dependencies=admin)
def list_gateways(session: SessionDep) -> list[GatewayPublic]:
    state = session.get(GatewayState, 1)
    return [
        gateway.public(c, state.active_id if state else None)
        for c in session.exec(select(ModelGateway)).all()
    ]


def audit(session, user, config, action):
    session.add(
        GatewayAudit(
            actor_id=user.id,
            gateway_id=config.id,
            action=action,
            revision=config.revision,
        )
    )


@router.post("/gateways", dependencies=admin, status_code=201)
def create_gateway(
    body: GatewayInput, session: SessionDep, current_user: CurrentUser
) -> GatewayPublic:
    state = gateway.lock_state(session)
    endpoint = gateway.validate_endpoint(body.provider, body.base_url)
    if (
        body.expected_revision != 0
        or not body.api_key
        or not body.api_key.get_secret_value().strip()
    ):
        raise HTTPException(422, "新配置需要密钥，初始版本必须为 0")
    if len(session.exec(select(ModelGateway)).all()) >= 30:
        raise HTTPException(422, "最多保存 30 个模型配置")
    config = ModelGateway(
        **body.model_dump(exclude={"api_key", "expected_revision", "base_url"}),
        base_url=endpoint,
        encrypted_key=encrypt_password(body.api_key.get_secret_value().strip()),
    )
    session.add(config)
    audit(session, current_user, config, "created")
    session.commit()
    session.refresh(config)
    return gateway.public(config, state.active_id)


@router.put("/gateways/{gateway_id}", dependencies=admin)
def update_gateway(
    gateway_id: uuid.UUID,
    body: GatewayInput,
    session: SessionDep,
    current_user: CurrentUser,
) -> GatewayPublic:
    state = gateway.lock_state(session)
    config = session.get(ModelGateway, gateway_id)
    if not config:
        raise HTTPException(404, "模型配置不存在")
    if config.revision != body.expected_revision:
        raise HTTPException(409, "模型配置已更新，请刷新后重试")
    endpoint = gateway.validate_endpoint(body.provider, body.base_url)
    secret = body.api_key.get_secret_value().strip() if body.api_key else ""
    if (endpoint != config.base_url or body.provider != config.provider) and not secret:
        raise HTTPException(422, "更换服务地址或厂商时必须重新填写密钥")
    for key, value in body.model_dump(
        exclude={"api_key", "expected_revision", "base_url"}
    ).items():
        setattr(config, key, value)
    config.base_url = endpoint
    if secret:
        config.encrypted_key = encrypt_password(secret)
    config.revision += 1
    session.add(config)
    audit(session, current_user, config, "updated")
    session.commit()
    session.refresh(config)
    return gateway.public(config, state.active_id)


@router.post("/gateways/{gateway_id}/activate", dependencies=admin)
def activate_gateway(
    gateway_id: uuid.UUID,
    body: GatewayRevision,
    session: SessionDep,
    current_user: CurrentUser,
) -> GatewayPublic:
    state = gateway.lock_state(session)
    config = session.get(ModelGateway, gateway_id)
    if not config or config.revision != body.expected_revision:
        raise HTTPException(409, "模型配置已更新，请刷新后重试")
    gateway.validate_endpoint(config.provider, config.base_url)
    state.active_id = config.id
    session.add(state)
    audit(session, current_user, config, "activated")
    session.commit()
    return gateway.public(config, config.id)


@router.post("/gateways/deactivate", dependencies=admin)
def deactivate_gateway(
    session: SessionDep, current_user: CurrentUser
) -> dict[str, bool]:
    state = gateway.lock_state(session)
    config = session.get(ModelGateway, state.active_id) if state.active_id else None
    if config:
        audit(session, current_user, config, "deactivated")
    state.active_id = None
    session.add(state)
    session.commit()
    return {"success": True}


@router.delete("/gateways/{gateway_id}", dependencies=admin)
def delete_gateway(
    gateway_id: uuid.UUID,
    body: GatewayRevision,
    session: SessionDep,
    current_user: CurrentUser,
) -> dict[str, bool]:
    state = gateway.lock_state(session)
    config = session.get(ModelGateway, gateway_id)
    if not config or config.revision != body.expected_revision:
        raise HTTPException(409, "模型配置已更新，请刷新后重试")
    if state.active_id == config.id:
        raise HTTPException(409, "请先停用或切换当前模型，再删除此配置")
    audit(session, current_user, config, "deleted")
    session.delete(config)
    session.commit()
    return {"success": True}


@router.post("/gateways/{gateway_id}/test", dependencies=admin)
async def test_gateway(
    gateway_id: uuid.UUID,
    body: GatewayRevision,
    session: SessionDep,
    current_user: CurrentUser,
) -> GatewayTest:
    config = session.get(ModelGateway, gateway_id)
    if not config or config.revision != body.expected_revision:
        raise HTTPException(409, "模型配置已更新，请刷新后重试")
    session.expunge(config)
    session.commit()
    started = time.monotonic()
    success, message = False, "测试返回内容不符合预期，请检查模型与 JSON 模式"
    try:
        content, _, _ = await gateway.complete(
            config,
            [
                {
                    "role": "user",
                    "content": '这是不含业务数据的连接测试。只输出 JSON：{"ok":true}',
                }
            ],
            {
                "type": "object",
                "properties": {"ok": {"type": "boolean"}},
                "required": ["ok"],
                "additionalProperties": False,
            },
        )
        success = json.loads(content) == {"ok": True}
        if success:
            message = "连接与 JSON 输出测试通过；问答质量需另行验证"
    except HTTPException as exc:
        message = str(exc.detail)
    except ValueError:
        pass
    audit(session, current_user, config, "test_passed" if success else "test_failed")
    session.commit()
    return GatewayTest(
        success=success,
        message=message,
        elapsed_ms=round((time.monotonic() - started) * 1000),
    )


@router.get("/status")
def model_status(
    session: SessionDep, _current_user: CurrentUser
) -> dict[str, str | bool]:
    try:
        config = gateway.active(session)
        return {"configured": True, "name": config.name, "model": config.model}
    except HTTPException:
        return {"configured": False, "name": "尚未配置模型", "model": ""}


@router.post("/conversations", status_code=201)
def create_conversation(
    body: ConversationCreate, session: SessionDep, current_user: CurrentUser
) -> ConversationPublic:
    return service.create(session, current_user, body.topic_id)


@router.get("/conversations")
def list_conversations(
    session: SessionDep, current_user: CurrentUser
) -> list[ConversationPublic]:
    service.purge(session)
    session.commit()
    conversations = session.exec(
        select(Conversation)
        .where(Conversation.actor_id == current_user.id)
        .order_by(col(Conversation.created_at).desc())
        .limit(100)
    ).all()
    result = []
    for conversation in conversations:
        try:
            service.owned(session, conversation.id, current_user)
            result.append(service.public(session, conversation))
        except HTTPException:
            continue
    return result


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> ConversationPublic:
    service.purge(session)
    session.commit()
    conversation, _ = service.owned(session, conversation_id, current_user)
    return service.public(session, conversation)


@router.get("/conversations/{conversation_id}/events")
async def conversation_events(
    conversation_id: uuid.UUID,
    request: Request,
    session: SessionDep,
    current_user: CurrentUser,
):
    from app.modules.assistant.workbench import snapshot
    from app.modules.query.compiler import fingerprint

    service.owned(session, conversation_id, current_user)
    actor_id, bind = current_user.id, session.get_bind()
    session.commit()

    async def events():
        previous = ""
        # Bounded streams force periodic JWT reauthentication. Reconnect restores
        # authoritative state, never resubmits questions or reruns queries.
        for tick in range(25):
            if await request.is_disconnected():
                return
            try:
                data = await run_in_threadpool(
                    snapshot, bind, actor_id, conversation_id
                )
            except HTTPException as exc:
                yield (
                    "event: access_error\ndata: "
                    + json.dumps({"detail": exc.detail}, ensure_ascii=False)
                    + "\n\n"
                )
                return
            digest = fingerprint(data)
            if digest != previous:
                yield (
                    f"id: {digest}\nevent: snapshot\ndata: "
                    + json.dumps(data, ensure_ascii=False)
                    + "\n\n"
                )
                previous = digest
            elif tick % 10 == 0:
                yield ": heartbeat\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


@router.get("/conversations/{conversation_id}/turns/{turn_id}/evidence")
def answer_evidence(
    conversation_id: uuid.UUID,
    turn_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> AnswerEvidence:
    from app.modules.assistant.workbench import evidence

    return evidence(session, current_user, conversation_id, turn_id)


@router.put("/conversations/{conversation_id}/turns/{turn_id}/feedback")
def save_feedback(
    conversation_id: uuid.UUID,
    turn_id: uuid.UUID,
    body: FeedbackInput,
    session: SessionDep,
    current_user: CurrentUser,
) -> FeedbackPublic:
    from app.modules.assistant.workbench import feedback

    return feedback(session, current_user, conversation_id, turn_id, body)


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> dict[str, bool]:
    from app.modules.query.service import gate

    gate(session)
    conversation = session.get(Conversation, conversation_id)
    if not conversation or conversation.actor_id != current_user.id:
        raise HTTPException(404, "会话不存在")
    turns = session.exec(
        select(AssistantTurn).where(AssistantTurn.conversation_id == conversation_id)
    ).all()
    if any(t.status == "planning" for t in turns):
        raise HTTPException(409, "请等待正在进行的规划结束后删除")
    for turn in turns:
        session.delete(turn)
    session.delete(conversation)
    session.commit()
    return {"success": True}


@router.post("/conversations/{conversation_id}/turns")
async def ask(
    conversation_id: uuid.UUID,
    body: AskInput,
    session: SessionDep,
    current_user: CurrentUser,
) -> ConversationPublic:
    return await service.ask(session, current_user, conversation_id, body)


@router.post("/conversations/{conversation_id}/turns/{turn_id}/analysis")
async def analyze(
    conversation_id: uuid.UUID,
    turn_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> AnalysisPublic:
    from app.modules.assistant.analysis import analyze as analyze_result

    return await analyze_result(session, current_user, conversation_id, turn_id)


@router.get("/topics/{topic_id}/tables")
def exploration_tables(
    topic_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> list[dict]:
    from app.modules.query.exploration import catalog
    from app.modules.query.service import resolve

    context = resolve(session, topic_id, current_user)
    return catalog(context[2], context[4], context[5])


@router.post(
    "/conversations/{conversation_id}/turns/{turn_id}/execute", status_code=202
)
def execute(
    conversation_id: uuid.UUID,
    turn_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> QueryJobPublic:
    return service.execute(session, current_user, conversation_id, turn_id)
