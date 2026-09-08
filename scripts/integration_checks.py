"""Local development checks. No external model or production database calls."""
import sys
from pathlib import Path

from module1_demo import configure

configure()
action = sys.argv[1] if len(sys.argv) > 1 else "test"
if action == "test":
    import pytest
    raise SystemExit(pytest.main(["--confcutdir=tests/modules", "tests/modules/test_integration.py", "-q", *sys.argv[2:]]))
elif action == "migration":
    from alembic import command
    from alembic.config import Config
    command.revision(Config("alembic.ini"), message="add external integration and embed sessions", autogenerate=True)
elif action == "lint":
    import subprocess
    root = Path(__file__).resolve().parents[1]
    raise SystemExit(subprocess.call([sys.executable, "-m", "ruff", "check", "--fix", "app/modules/integration", "app/api/routes/integration.py", "tests/modules/test_integration.py", "app/modules/assistant/analysis.py"]))
elif action == "quality":
    import subprocess
    paths = ["app/modules/integration", "app/api/routes/integration.py", "tests/modules/test_integration.py", "app/modules/assistant/analysis.py", "app/main.py"]
    subprocess.run([sys.executable, "-m", "ruff", "format", *paths], check=True)
    subprocess.run([sys.executable, "-m", "ruff", "check", "--fix", *paths], check=True)
    subprocess.run([sys.executable, "-m", "ty", "check", "app"], check=True)
elif action == "migrate":
    from alembic import command
    from alembic.config import Config
    command.upgrade(Config("alembic.ini"), "head")
    command.check(Config("alembic.ini"))
elif action == "status":
    from sqlmodel import Session, select, col
    from app.core.db import engine
    from app.modules.query.models import QueryJob
    from app.modules.assistant.models import AssistantTurn
    from app.modules.integration.models import IntegrationTask
    with Session(engine) as session:
        counts = {
            "query_active": len(session.exec(select(QueryJob.id).where(col(QueryJob.status).in_(["queued", "running", "cancelling", "cleanup_pending"]))).all()),
            "planning_active": len(session.exec(select(AssistantTurn.id).where(AssistantTurn.status == "planning")).all()),
            "integration_active": len(session.exec(select(IntegrationTask.id).where(col(IntegrationTask.status).in_(["queued", "planning", "querying", "analyzing", "cancelling", "cleanup_pending"]))).all()),
        }
        print(counts)
        raise SystemExit(1 if any(counts.values()) else 0)
elif action == "openapi":
    import json
    from fastapi.openapi.utils import get_openapi
    from app.api.routes.integration import router
    target = Path(__file__).resolve().parents[1] / "docs/examples/lightsql-integration.openapi.json"
    target.write_text(json.dumps(get_openapi(title="LightSQL Integration API", version="1.0.0", routes=router.routes), ensure_ascii=False, indent=2), encoding="utf-8")
    print("Exported public integration schema")
