"""Metadata backup and restoration into a NEW PostgreSQL database only.

Run on the app host with its environment and Docker access. Encryption keys are
read from the existing environment, never embedded in the archive or manifest.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def docker(container, *args, input_file=None, output_file=None):
    result = subprocess.run(
        ["docker", "exec", *(["-i"] if input_file else []), container, *args],
        stdin=input_file,
        stdout=output_file or subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            "PostgreSQL backup command failed; inspect the container locally"
        )
    return result.stdout.decode().strip() if result.stdout else ""


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["backup", "restore-test"])
    parser.add_argument("--container", required=True)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    archive = args.file.resolve()
    if args.demo:
        from module1_demo import configure

        configure()
    else:
        sys.path.insert(0, str(ROOT / "backend"))
        os.chdir(ROOT / "backend")
    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.engine import make_url
    from sqlmodel import Session, select
    from app.core.config import settings
    from app.core.db import engine
    from app.modules.datasources.models import now
    from app.modules.datasources.service import decrypt_password
    from app.modules.quality.models import BackupRecord

    source_url = make_url(str(settings.DATABASE_URL))
    database = source_url.database
    manifest_path = archive.with_suffix(archive.suffix + ".json")
    started = time.monotonic()
    if args.action == "backup":
        if archive.exists() or manifest_path.exists():
            raise RuntimeError(
                "Choose a new archive path; existing backups are never overwritten"
            )
        archive.parent.mkdir(parents=True, exist_ok=True)
        with engine.connect().execution_options(
            isolation_level="REPEATABLE READ"
        ) as connection:
            transaction = connection.begin()
            identity = str(
                connection.execute(
                    text("SELECT system_identifier FROM pg_control_system()")
                ).scalar_one()
            )
            container_identity = docker(
                args.container,
                "psql",
                "-U",
                "postgres",
                "-d",
                database,
                "-Atc",
                "SELECT system_identifier FROM pg_control_system()",
            )
            if identity != container_identity:
                raise RuntimeError(
                    "Container and app metadata database are different PostgreSQL clusters"
                )
            snapshot = connection.execute(
                text("SELECT pg_export_snapshot()")
            ).scalar_one()
            quote = connection.dialect.identifier_preparer.quote
            counts = {
                table: connection.execute(
                    text(f"SELECT COUNT(*) FROM public.{quote(table)}")
                ).scalar_one()
                for table in inspect(connection).get_table_names(schema="public")
            }
            with archive.open("xb") as output:
                docker(
                    args.container,
                    "pg_dump",
                    "-U",
                    "postgres",
                    "-d",
                    database,
                    "--format=custom",
                    "--no-owner",
                    "--no-acl",
                    "--schema=public",
                    "--snapshot=" + snapshot,
                    output_file=output,
                )
            transaction.rollback()
        checksum = digest(archive)
        # A record is only registered after the artifact and manifest exist.
        manifest = {
            "format": 1,
            "database": database,
            "sha256": checksum,
            "size_bytes": archive.stat().st_size,
            "created_at": now().isoformat(),
            "tables": counts,
            "scope": "public metadata schema; keys stored separately",
        }
        with manifest_path.open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2)
        with Session(engine) as session:
            session.add(
                BackupRecord(checksum=checksum, size_bytes=archive.stat().st_size)
            )
            session.commit()
        print(
            json.dumps(
                {
                    "backup": str(archive),
                    "sha256": checksum,
                    "tables": len(counts),
                    "elapsed_seconds": round(time.monotonic() - started, 2),
                }
            )
        )
        return

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest["sha256"] != digest(archive)
        or manifest["size_bytes"] != archive.stat().st_size
    ):
        raise RuntimeError("Backup integrity check failed; no database was created")
    target = "lightsql_restore_" + uuid.uuid4().hex
    docker(args.container, "createdb", "-U", "postgres", "--template=template0", target)
    # template0 supplies an empty public schema; the archive recreates it.
    # This generated database was just created above. No CASCADE or existing
    # database target is accepted by this command.
    docker(
        args.container,
        "psql",
        "-U",
        "postgres",
        "-d",
        target,
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        "DROP SCHEMA public",
    )
    with archive.open("rb") as stream:
        docker(
            args.container,
            "pg_restore",
            "-U",
            "postgres",
            "-d",
            target,
            "--exit-on-error",
            "--no-owner",
            "--no-acl",
            input_file=stream,
        )
    restored = create_engine(source_url.set(database=target))
    checked = 0
    try:
        with restored.connect() as connection:
            tables = inspect(connection).get_table_names(schema="public")
            if set(tables) != set(manifest["tables"]):
                raise RuntimeError("Restored tables differ from the backup snapshot")
            quote = connection.dialect.identifier_preparer.quote
            for table in tables:
                count = connection.execute(
                    text(f"SELECT COUNT(*) FROM public.{quote(table)}")
                ).scalar_one()
                if count != manifest["tables"][table]:
                    raise RuntimeError(
                        "Restored row counts differ from the backup snapshot"
                    )
                for column in inspect(connection).get_columns(table, schema="public"):
                    if column["name"] in {
                        "encrypted_payload",
                        "encrypted_key",
                        "encrypted_password",
                    }:
                        for value in connection.execute(
                            text(
                                f"SELECT {quote(column['name'])} FROM public.{quote(table)}"
                            )
                        ).scalars():
                            if value:
                                decrypt_password(value)
                                checked += 1
    finally:
        restored.dispose()
    with Session(engine) as session:
        records = session.exec(
            select(BackupRecord).where(BackupRecord.checksum == manifest["sha256"])
        ).all()
        for record in records:
            record.restored_at = now()
            session.add(record)
        session.commit()
    evidence = {
        "restored_database": target,
        "tables_verified": len(tables),
        "encrypted_values_verified": checked,
        "sha256": manifest["sha256"],
        "elapsed_seconds": round(time.monotonic() - started, 2),
        "verified_at": now().isoformat(),
    }
    archive.with_suffix(archive.suffix + ".restore.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf-8"
    )
    print(json.dumps(evidence))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Driver/tool errors can contain connection strings; don't print them.
        print(
            f"Backup/restore failed ({type(exc).__name__}); no existing database was overwritten.",
            file=sys.stderr,
        )
        raise SystemExit(1) from None
