
from jxp.config.schema import AgentDefaults
from jxp.config.router import CommandRouter

class AgentLoop:
    # 这是一个内部常量，用来:保存运行时状态,记录断点、进度、会话状态,方便中断后恢复
    _RUNTIME_CHECKPOINT_KEY = "runtime_checkpoint"

    def __init__(self, config: dict):
        defaults = AgentDefaults()


        self._register_default_tools()
        self.commands = CommandRouter()
        register_builtin_commands(self.commands)


    def _register_default_tools(self) -> None:
        pass