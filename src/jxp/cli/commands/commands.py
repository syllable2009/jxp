import typer
import asyncio
import mimetypes
import os
import uuid
from pathlib import Path
from urllib.parse import urlparse, unquote
from urllib.request import Request, urlopen
from jxp.config import get_config_path, load_config, set_config_path

from jxp import __logo__

from rich.console import Console

console = Console()
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


def _browser_like_headers(url: str) -> dict[str, str]:
    host = urlparse(url).netloc or "example.com"
    return {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "identity",
        "Connection": "keep-alive",
        "Referer": f"https://{host}/",
    }


def _filename_from_content_disposition(content_disposition: str | None) -> str | None:
    if not content_disposition:
        return None
    # 优先 RFC5987: filename*=UTF-8''encoded_name
    for part in content_disposition.split(";"):
        token = part.strip()
        if token.lower().startswith("filename*="):
            value = token.split("=", 1)[1].strip().strip('"')
            if "''" in value:
                _, encoded_name = value.split("''", 1)
                name = unquote(encoded_name).strip().strip('"')
            else:
                name = unquote(value)
            return os.path.basename(name) or None
    for part in content_disposition.split(";"):
        token = part.strip()
        if token.lower().startswith("filename="):
            name = token.split("=", 1)[1].strip().strip('"')
            name = unquote(name)
            return os.path.basename(name) or None
    return None


def _ext_from_content_type(content_type: str | None) -> str:
    if not content_type:
        return ""
    ctype = content_type.split(";")[0].strip().lower()
    ext = mimetypes.guess_extension(ctype) or ""
    # 常见补充类型
    if not ext:
        mapping = {
            "application/octet-stream": "",
            "application/x-rar-compressed": ".rar",
            "application/x-7z-compressed": ".7z",
            "application/x-msdownload": ".exe",
        }
        ext = mapping.get(ctype, "")
    return ext


def _infer_filename(url: str, content_disposition: str | None, content_type: str | None) -> str:
    by_header = _filename_from_content_disposition(content_disposition)
    if by_header:
        return by_header

    path_name = os.path.basename(unquote(urlparse(url).path))
    if path_name:
        if "." in path_name:
            return path_name
        ext = _ext_from_content_type(content_type)
        return f"{path_name}{ext}" if ext else path_name

    ext = _ext_from_content_type(content_type)
    return f"{uuid.uuid4().hex}{ext}" if ext else f"{uuid.uuid4().hex}.file"


@app.command()
def onboard(
        workspace: str | None = typer.Option(None, "--workspace", "-w", help="Workspace directory"),
        config: str | None = typer.Option(None, "--config", "-c", help="Path to config file"),
        wizard: bool = typer.Option(False, "--wizard", help="Use interactive wizard"),
):
    print(workspace, config, wizard)
    if config is not None:
        # 把用户随便写的路径，变成系统能看懂、不会出错、绝对标准的真实路径。
        config_path = Path(config).expanduser().resolve()
        set_config_path(config_path)
        console.print(f"[dim]Using config: {config_path}[/dim]")
    else:
        config_path = get_config_path()

    if config_path.exists():
        if wizard:
            pass
        else:
            pass
    else:
        pass
    console.print(f"[yellow]Config already exists at {config_path}[/yellow]")
    console.print("  [bold]y[/bold] = overwrite with defaults (existing values will be lost)")
    console.print("  [bold]N[/bold] = refresh config, keeping existing values and adding new fields")
    if typer.confirm("Overwrite existing config?"):
        print("Config overwritten!")
    else:
        print("Canceled.")


async def run_once():
    print(__logo__)

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
    if message:
        print(message)
    else:
        asyncio.run(run_once())

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
def down(
        url: str = typer.Option(..., "--url", "-l", help="File download URL"),
        destination: str = typer.Option(..., "--destination", "-d", help="Destination file path or directory"),
):
    dest_path = Path(destination).expanduser()
    request = Request(url, headers=_browser_like_headers(url), method="GET")

    try:
        with urlopen(request, timeout=60) as resp:
            content_disposition = resp.headers.get("Content-Disposition")
            content_type = resp.headers.get("Content-Type")
            filename = _infer_filename(url, content_disposition, content_type)

            save_path = dest_path / filename if dest_path.is_dir() or destination.endswith("/") else dest_path
            if save_path.name in (".", ""):
                save_path = dest_path / filename

            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 128)
                    if not chunk:
                        break
                    f.write(chunk)
    except Exception as e:
        raise typer.BadParameter(f"下载失败: {e}") from e

    console.print(f"[green]Downloaded:[/green] {save_path}")


@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")


@app.command()
def save():
    if typer.confirm("Overwrite existing config?"):
        print("Config overwritten!")
    else:
        print("Canceled.")


channels_app = typer.Typer(help="Manage channels")
app.add_typer(channels_app, name="channels")


@channels_app.command("status")
def channels_status(
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    print(config_path)
    pass


plugins_app = typer.Typer(help="Manage channel plugins")
app.add_typer(plugins_app, name="plugins")


@plugins_app.command("list")
def plugins_list():
    print(plugins_app)


if __name__ == "__main__":
    # 运行文件 → 触发 app() → Typer 开始工作 → 解析你的命令 → 执行函数
    # 启动整个命令行工具
    app()
    # config = load_config()
    # print(config)
    # save()
