import time

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException

from app.core.config import settings
from app.modules.datasources.models import ConnectionTestResult, DataSourceInput, now


def cipher() -> Fernet:
    if not settings.DATASOURCE_ENCRYPTION_KEY:
        raise HTTPException(503, "数据源加密密钥尚未配置，请联系管理员")
    try:
        return Fernet(settings.DATASOURCE_ENCRYPTION_KEY.encode())
    except ValueError, TypeError:
        raise HTTPException(503, "数据源加密密钥配置无效，请联系管理员") from None


def encrypt_password(value: str) -> str:
    return cipher().encrypt(value.encode()).decode()


def decrypt_password(value: str) -> str:
    try:
        return cipher().decrypt(value.encode()).decode()
    except InvalidToken:
        raise HTTPException(503, "无法解密连接凭证，请检查加密密钥") from None


def check_host(host: str) -> None:
    allowed = {h.strip().lower() for h in settings.DATASOURCE_ALLOWED_HOSTS}
    if host.lower() not in allowed:
        raise HTTPException(422, "该数据库主机不在允许连接的名单中，请联系管理员配置")


def probe(source: DataSourceInput, password: str) -> ConnectionTestResult:
    """Only a fixed health query, on a short-lived connection. Never run user SQL."""
    check_host(source.host)
    started = time.monotonic()
    success = False
    message = "连接失败，请检查主机、端口、数据库、凭证及 TLS 设置"
    try:
        from app.modules.datasources.connection import readonly_cursor

        if source.database_type == "dameng" and source.tls_mode == "verify-full":
            message = (
                "当前达梦连接器尚未适配证书校验；仅在可信本地测试环境中关闭 TLS 后连接"
            )
        else:
            with readonly_cursor(source, password) as cursor:
                cursor.execute(
                    "SELECT 1 FROM DUAL"
                    if source.database_type in ("oracle", "dameng")
                    else "SELECT 1"
                )
                success = cursor.fetchone() == (1,)
    except ImportError, ModuleNotFoundError:
        message = "对应数据库驱动尚未安装，请联系管理员"
    except Exception:
        # Driver messages can contain credentials, hostnames or connection strings.
        # Do not persist, log or return their text.
        pass
    if success:
        message = "连接成功，已完成基础读取测试；数据库账号只读权限仍需单独核验"
    return ConnectionTestResult(
        success=success,
        message=message,
        latency_ms=round((time.monotonic() - started) * 1000),
        tested_at=now(),
    )
