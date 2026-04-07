import typer
from jxp.config import get_config_path, load_config


from jxp import __logo__
# typer.Typer () = 创建一个命令行工具
app = typer.Typer(
    # 定义命令的名字，对应终端的名字
    name="jxp",
    # 设置帮助命令，两个都能打开帮助
    context_settings={"help_option_names": ["-h", "--help"]},
    # 输入 nanobot --help 时显示的标题 / 介绍，会显示 LOGO + 说明文字
    help=f"{__logo__} jxp - Command Line Tools",
    # 如果你只输入 nanobot，不加任何子命令，自动显示帮助文档，而不是报错
    no_args_is_help=True,
)

@app.command()
def onboard(
    workspace: str | None = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
    config: str | None = typer.Option(None, "--config", "-c", help="Path to config file"),
    wizard: bool = typer.Option(False, "--wizard", help="Use interactive wizard"),
):
    print(workspace, config, wizard)
    pass

@app.command()
def agent(
    message: str = typer.Option(None, "--message", "-m", help="Message to send to the agent"),
    session_id: str = typer.Option("cli:direct", "--session", "-s", help="Session ID"),
    workspace: str | None = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
    config: str | None = typer.Option(None, "--config", "-c", help="Config file path"),
    markdown: bool = typer.Option(True, "--markdown/--no-markdown", help="Render assistant output as Markdown"),
    logs: bool = typer.Option(False, "--logs/--no-logs", help="Show nanobot runtime logs during chat"),
):
    print(message, session_id, workspace, config, markdown, logs)
    pass

@app.command()
def serve(
    port: int | None = typer.Option(None, "--port", "-p", help="API server port"),
    host: str | None = typer.Option(None, "--host", "-H", help="Bind address"),
    timeout: float | None = typer.Option(None, "--timeout", "-t", help="Per-request timeout (seconds)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show nanobot runtime logs"),
    workspace: str | None = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
    config: str | None = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    print(port, host, timeout, verbose, workspace, config)
    pass

@app.command()
def gateway(
    port: int | None = typer.Option(None, "--port", "-p", help="Gateway port"),
    workspace: str | None = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    config: str | None = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    print(port, workspace, verbose, config)
    pass

@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")




if __name__ == "__main__":
    # app()
    config = load_config()
    print(config)
