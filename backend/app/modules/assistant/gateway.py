import asyncio
import json
import time
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.modules.assistant.models import GatewayPublic, GatewayState, ModelGateway
from app.modules.datasources.service import decrypt_password

PRESETS = [
    {
        "provider": "zhipu",
        "label": "智谱",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
    },
    {
        "provider": "deepseek",
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com",
    },
    {
        "provider": "qwen",
        "label": "千问 · 百炼北京",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    {
        "provider": "qwen",
        "label": "千问 · 百炼新加坡",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    },
    {
        "provider": "qwen",
        "label": "千问 · 百炼美国",
        "base_url": "https://dashscope-us.aliyuncs.com/compatible-mode/v1",
    },
]


def validate_endpoint(provider: str, value: str) -> str:
    url = value.rstrip("/")
    parsed = urlsplit(url)
    allowed = {p["base_url"] for p in PRESETS if p["provider"] == provider}
    if provider == "custom":
        allowed = {v.rstrip("/") for v in settings.MODEL_GATEWAY_ALLOWED_BASE_URLS}
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or url not in allowed
    ):
        raise HTTPException(
            422,
            "服务地址不在允许名单中；自定义 HTTPS 地址需先配置 MODEL_GATEWAY_ALLOWED_BASE_URLS",
        )
    return url


def public(config: ModelGateway, active_id) -> GatewayPublic:
    return GatewayPublic(
        **config.model_dump(exclude={"encrypted_key"}),
        has_key=bool(config.encrypted_key),
        active=config.id == active_id,
    )


def active(session: Session) -> ModelGateway:
    state = session.get(GatewayState, 1)
    config = (
        session.get(ModelGateway, state.active_id)
        if state and state.active_id
        else None
    )
    if not config:
        raise HTTPException(503, "尚未配置并启用模型服务，请管理员在模型设置中添加")
    return config


def lock_state(session: Session) -> GatewayState:
    # QueryGate is also used for first-time state creation across API processes.
    from app.modules.query.service import gate

    gate(session)
    state = session.exec(
        select(GatewayState).where(GatewayState.id == 1).with_for_update()
    ).first()
    if state is None:
        state = GatewayState()
        session.add(state)
        session.flush()
    return state


async def complete(
    config: ModelGateway, messages: list[dict], schema: dict
) -> tuple[str, dict, int]:
    """One bounded request. No network retries, redirects, tools, or result data."""
    endpoint = validate_endpoint(config.provider, config.base_url)
    body: dict = {
        "model": config.model,
        "messages": messages,
        "stream": False,
        "max_tokens": config.max_tokens,
    }
    if config.json_mode:
        body["response_format"] = {"type": "json_object"}
    if config.thinking != "default":
        if config.provider == "qwen":
            body["enable_thinking"] = config.thinking == "enabled"
        else:
            body["thinking"] = {"type": config.thinking}
    body["messages"] = [
        *messages,
        {
            "role": "system",
            "content": "只输出符合此 JSON Schema 的 JSON 对象："
            + json.dumps(schema, ensure_ascii=False),
        },
    ]
    started = time.monotonic()

    async def request():
        async with httpx.AsyncClient(
            timeout=config.timeout_seconds, follow_redirects=False, trust_env=False
        ) as client:
            async with client.stream(
                "POST",
                endpoint + "/chat/completions",
                headers={
                    "Authorization": "Bearer " + decrypt_password(config.encrypted_key)
                },
                json=body,
            ) as response:
                if response.status_code != 200:
                    if response.status_code in (401, 403):
                        raise HTTPException(
                            502, "模型服务认证或访问失败，请检查密钥与模型权限"
                        )
                    if response.status_code == 429:
                        raise HTTPException(503, "模型服务限流或额度不足，请稍后重试")
                    raise HTTPException(
                        502, "模型服务拒绝请求，请检查地址、模型及输出模式配置"
                    )
                chunks = bytearray()
                async for chunk in response.aiter_bytes():
                    chunks.extend(chunk)
                    if len(chunks) > 256_000:
                        raise HTTPException(502, "模型响应超过大小限制")
                return json.loads(chunks)

    try:
        data = await asyncio.wait_for(request(), timeout=config.timeout_seconds)
        choice = data["choices"][0]
        content = choice["message"].get("content")
        if (
            choice.get("finish_reason") != "stop"
            or choice["message"].get("refusal")
            or not isinstance(content, str)
            or not content.strip()
        ):
            raise HTTPException(
                502, "模型未返回完整内容，请调整模型、思考模式或输出长度后重试"
            )
        usage = data.get("usage") or {}
        return (
            content,
            {
                k: max(0, min(int(usage.get(k, 0)), 10_000_000))
                for k in ("prompt_tokens", "completion_tokens")
            },
            round((time.monotonic() - started) * 1000),
        )
    except TimeoutError, httpx.TimeoutException:
        raise HTTPException(504, "模型生成超时，请稍后重试") from None
    except httpx.HTTPError, ValueError, KeyError, IndexError, TypeError:
        raise HTTPException(502, "模型连接失败或响应格式无效") from None
