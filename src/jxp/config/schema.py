from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings

# 继承 BaseModel = 让你的类变成「超级数据模型」自动获得 Pydantic 能力
# 1. 自动数据类型验证（最核心）
# 2. 支持 JSON ↔ 对象 自动转换
# 3. 支持别名（camelCase ↔ snake_case 自动互转）
# BaseModel 是通用选手，什么数据都能管。
class Base(BaseModel):
    """Base model that accepts both camelCase and snake_case keys."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class AgentDefaults(Base):
    """Default agent configuration."""

    workspace: str = "~/.jxp/workspace"
    model: str = "openai/gpt-5"
    provider: str = (
        "auto"  # Provider name (e.g. "anthropic", "openrouter") or "auto" for auto-detection
    )
    max_tokens: int = 8192
    context_window_tokens: int = 65_536
    context_block_limit: int | None = None
    temperature: float = 0.1
    max_tool_iterations: int = 200
    max_tool_result_chars: int = 16_000
    provider_retry_mode: Literal["standard", "persistent"] = "standard"
    reasoning_effort: str | None = None  # low / medium / high - enables LLM thinking mode
    timezone: str = "UTC"  # IANA timezone, e.g. "Asia/Shanghai", "America/New_York"


class AgentsConfig(Base):
    """Agent configuration."""
    defaults: AgentDefaults = Field(default_factory=AgentDefaults)

class ApiConfig(Base):
    """OpenAI-compatible API server configuration."""

    host: str = "127.0.0.1"  # Safer default: local-only bind.
    port: int = 8900
    timeout: float = 120.0  # Per-request timeout in seconds.

# BaseSettings = 专门读取【环境变量 + 配置文件】的配置模型
class Config(BaseSettings):
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    # channels: ChannelsConfig = Field(default_factory=ChannelsConfig)
    # providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    # gateway: GatewayConfig = Field(default_factory=GatewayConfig)
    # tools: ToolsConfig = Field(default_factory=ToolsConfig)