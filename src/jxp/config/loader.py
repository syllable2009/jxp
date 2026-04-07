import json
from pathlib import Path
from loguru import logger
import pydantic
from jxp.config.schema import Config


_current_config_path: Path | None = None
def get_config_path() -> Path:
    if _current_config_path is None:
        # Path.home()=自动获取你当前用户的home目录，在 Mac 上 = /Users/你的用户名
        return Path.home() / ".jxp" / "config.json"
    return _current_config_path


def load_config(config_path: Path | None = None) -> Config:
    path = config_path or get_config_path()
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            # 老配置转移到新配置上
            data = _migrate_config(data)
            # 把原始字典 data → 严格校验 → 转换成你的 Config 类对象
            return Config.model_validate(data)
        except (json.JSONDecodeError, ValueError, pydantic.ValidationError) as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            logger.warning("Using default configuration.")
    return Config()



def _migrate_config(data: dict) -> dict:
    """Migrate old config formats to current."""
    # Move tools.exec.restrictToWorkspace → tools.restrictToWorkspace
    tools = data.get("tools", {})
    exec_cfg = tools.get("exec", {})
    if "restrictToWorkspace" in exec_cfg and "restrictToWorkspace" not in tools:
        tools["restrictToWorkspace"] = exec_cfg.pop("restrictToWorkspace")
    return data