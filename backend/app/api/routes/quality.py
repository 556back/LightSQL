import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.modules.quality import operations, service
from app.modules.quality.evaluation import score
from app.modules.quality.models import (
    DatasetInput,
    EvaluationDataset,
    EvaluationRun,
    FeedbackReviewPublic,
    ReviewInput,
    RunInput,
)
from app.modules.query.compiler import fingerprint
from app.modules.semantic.models import Topic

router = APIRouter(
    prefix="/quality",
    tags=["quality"],
    dependencies=[Depends(get_current_active_superuser)],
)


@router.get("/operations")
def operations_overview(session: SessionDep) -> dict:
    return operations.overview(session)


@router.get("/feedback")
def list_feedback(
    session: SessionDep, offset: int = Query(default=0, ge=0)
) -> list[FeedbackReviewPublic]:
    return service.feedback_list(session, offset)


@router.put("/feedback/{feedback_id}")
def review_feedback(
    feedback_id: uuid.UUID,
    body: ReviewInput,
    session: SessionDep,
    current_user: CurrentUser,
) -> FeedbackReviewPublic:
    return service.review(session, current_user, feedback_id, body)


@router.post("/datasets", status_code=201)
def create_dataset(
    body: DatasetInput, session: SessionDep, current_user: CurrentUser
) -> dict:
    if not session.get(Topic, body.topic_id):
        raise HTTPException(422, "题集主题不存在")
    payload = body.model_dump(mode="json")
    record = EvaluationDataset(
        name=body.name,
        topic_id=body.topic_id,
        digest=fingerprint(payload),
        encrypted_payload=service.encode(payload),
        created_by=current_user.id,
    )
    session.add(record)
    session.commit()
    return {"id": record.id, "digest": record.digest, "name": record.name}


@router.get("/datasets")
def list_datasets(
    session: SessionDep, offset: int = Query(default=0, ge=0)
) -> list[dict]:
    result = []
    for record in session.exec(
        select(EvaluationDataset)
        .order_by(col(EvaluationDataset.created_at).desc())
        .offset(offset)
        .limit(100)
    ).all():
        data = service.decode(record.encrypted_payload)
        result.append(
            {
                "id": record.id,
                "name": record.name,
                "digest": record.digest,
                "topic_id": record.topic_id,
                "provenance": data["provenance"],
                "semantic_version": data["semantic_version"],
                "source_snapshot": data["source_snapshot"],
                "dev": sum(c["split"] == "dev" for c in data["cases"]),
                "blind": sum(c["split"] == "blind" for c in data["cases"]),
            }
        )
    return result


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: uuid.UUID, session: SessionDep) -> dict:
    record = session.get(EvaluationDataset, dataset_id)
    if not record:
        raise HTTPException(404, "题集不存在")
    return {
        "id": record.id,
        "digest": record.digest,
        "definition": service.decode(record.encrypted_payload),
    }


@router.post("/runs", status_code=201)
def create_run(body: RunInput, session: SessionDep, current_user: CurrentUser) -> dict:
    dataset = session.get(EvaluationDataset, body.dataset_id)
    if not dataset or dataset.digest != body.dataset_digest:
        raise HTTPException(409, "题集不存在或摘要不匹配")
    definition = DatasetInput.model_validate(service.decode(dataset.encrypted_payload))
    encrypted_payload = service.encode(body.model_dump(mode="json"))
    summary = score(definition, body)
    record = EvaluationRun(
        dataset_id=dataset.id,
        model=body.model,
        context_variant=body.context_variant,
        evidence=body.evidence,
        split=body.split,
        encrypted_payload=encrypted_payload,
        summary=summary,
        created_by=current_user.id,
    )
    session.add(record)
    session.commit()
    return {"id": record.id, "summary": summary}


@router.get("/runs")
def list_runs(
    session: SessionDep,
    dataset_id: uuid.UUID | None = None,
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    query = (
        select(EvaluationRun)
        .order_by(col(EvaluationRun.created_at).desc())
        .offset(offset)
        .limit(100)
    )
    if dataset_id:
        query = query.where(EvaluationRun.dataset_id == dataset_id)
    return [
        record.model_dump(exclude={"encrypted_payload", "created_by"})
        for record in session.exec(query).all()
    ]


@router.get("/runs/{run_id}")
def get_run(run_id: uuid.UUID, session: SessionDep) -> dict:
    record = session.get(EvaluationRun, run_id)
    if not record:
        raise HTTPException(404, "评测运行不存在")
    return {
        "id": record.id,
        "summary": record.summary,
        "definition": service.decode(record.encrypted_payload),
    }
