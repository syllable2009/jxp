# 这是 Python 里 ** 包的出口文件（统一大门）** 写法！
from jxp.config.loader import get_config_path, load_config


# all = [...] 定义：别人可以导入什么（白名单）
__all__ = [
    "get_config_path",
    "load_config",
]