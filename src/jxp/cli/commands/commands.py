import typer
import asyncio
import mimetypes
import os
import re
import uuid
from pathlib import Path
from urllib.parse import urlparse, unquote, urljoin
from urllib.request import Request, urlopen
from crawlee.crawlers import BeautifulSoupCrawler
from playwright.async_api import async_playwright
from jxp.config import get_config_path, load_config, set_config_path

from jxp import __logo__

from rich.console import Console

from jxp.config.schema import Config

console = Console()
crawler = BeautifulSoupCrawler(max_requests_per_crawl=10)
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
    return f"{uuid.uuid4().hex}{ext}" if ext else f"{uuid.uuid4().hex}.bin"


def _download_file(url: str, save_dir: Path, timeout: int = 60) -> Path:
    request = Request(url, headers=_browser_like_headers(url), method="GET")
    with urlopen(request, timeout=timeout) as resp:
        content_disposition = resp.headers.get("Content-Disposition")
        content_type = resp.headers.get("Content-Type")
        filename = _infer_filename(url, content_disposition, content_type)
        save_path = save_dir / filename

        # 避免不同图片 URL 推导出相同文件名导致覆盖
        if save_path.exists():
            stem = save_path.stem or uuid.uuid4().hex
            suffix = save_path.suffix
            save_path = save_path.with_name(f"{stem}_{uuid.uuid4().hex[:8]}{suffix}")

        with open(save_path, "wb") as f:
            while True:
                chunk = resp.read(1024 * 128)
                if not chunk:
                    break
                f.write(chunk)
    return save_path


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
    # 根据配置地址和工作空间地址，来获取配置
    config = _load_runtime_config(config, workspace)
    # 从默认的templates下复制基础文件到新的工作个空间
    # sync_workspace_templates(config.workspace_path)
    #


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
    # 会将 ~ 符号自动转换为当前用户的家目录路径
    dest_path = Path(destination).expanduser()
    # 判断用户路径最后有没有带斜杠，带斜杠 = 明确表示这是文件夹
    trailing_sep = destination.endswith(("/", "\\"))
    # 用户明确指定文件名+后缀时，优先使用用户输入，不做推测，不是以斜杠结尾，路径最后一段有名字，有后缀
    user_explicit_file = (not trailing_sep) and bool(dest_path.name) and bool(dest_path.suffix)
    request = Request(url, headers=_browser_like_headers(url), method="GET")

    try:
        with urlopen(request, timeout=60) as resp:
            if user_explicit_file and not dest_path.is_dir():
                save_path = dest_path
            else:
                # 目录判定：已有目录，或参数明确以路径分隔符结尾
                is_directory = dest_path.is_dir() or trailing_sep
                # Content-Disposition 是 HTTP 响应头里的一个字段，用来告诉浏览器：这个返回的内容该怎么处理。
                # Content-Disposition: attachment; filename="example.pdf"
                content_disposition = resp.headers.get("Content-Disposition")
                content_type = resp.headers.get("Content-Type")
                filename = _infer_filename(url, content_disposition, content_type)
                save_path = dest_path / filename if is_directory else dest_path

                # 兜底，避免异常输入导致文件名为空
                if save_path.name in ("", "."):
                    save_path = dest_path / filename

            # 最终兜底，防止极端情况下无效文件名
            if save_path.name in ("", "."):
                save_path = dest_path / f"{uuid.uuid4().hex}.bin"

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
def find_link(
        url: str = typer.Option(..., "--url", "-l", help="Page URL to crawl images from"),
        pattern: str = typer.Option(
            r"""(?ix)\.(?:jpg|jpeg|png|gif|webp|bmp|svg|ico|avif)(?:\?.*)?$""",
            "--pattern",
            "-r",
            help="Regex used to filter extracted URLs",
        ),
):
    async def _collect_resource_urls(page_url: str, filter_pattern: re.Pattern[str]) -> list[str]:
        # 提取 HTML 中的资源地址（img/src、srcset、CSS url() 等）
        attr_pattern = re.compile(
            r"""(?ix)
            (?:src|href)\s*=\s*
            (?:
                "([^"]+)"
                |'([^']+)'
                |([^\s"'<>]+)
            )
            """
        )
        srcset_pattern = re.compile(
            r"""(?ix)
            srcset\s*=\s*
            (?:
                "([^"]+)"
                |'([^']+)'
                |([^\s"'<>]+)
            )
            """
        )
        css_url_pattern = re.compile(r"""(?ix)url\(\s*['"]?([^'")]+)['"]?\s*\)""")
        http_url_pattern = re.compile(r"""https?://[^\s"'<>]+""", re.IGNORECASE)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto(page_url, wait_until="networkidle", timeout=60000)
            html = await page.content()
            await context.close()
            await browser.close()

        raw_urls: list[str] = []
        for match in attr_pattern.finditer(html):
            raw_urls.append(next((g for g in match.groups() if g), ""))
        for match in srcset_pattern.finditer(html):
            srcset_value = next((g for g in match.groups() if g), "")
            for candidate in srcset_value.split(","):
                url_part = candidate.strip().split(" ")[0]
                if url_part:
                    raw_urls.append(url_part)
        for match in css_url_pattern.finditer(html):
            raw_urls.append(match.group(1))
        raw_urls.extend(http_url_pattern.findall(html))

        filtered_urls = [u for u in raw_urls if filter_pattern.search(u)]
        return filtered_urls if filtered_urls else raw_urls

    try:
        compiled_pattern = re.compile(pattern)
    except re.error as e:
        raise typer.BadParameter(f"正则表达式无效: {e}") from e

    try:
        target_list = asyncio.run(_collect_resource_urls(url, compiled_pattern))
    except Exception as e:
        raise typer.BadParameter(f"页面访问失败: {e}") from e

    result_urls: list[str] = []
    for src in target_list:
        if src.startswith("data:"):
            continue
        full_url = urljoin(url, src)
        if full_url not in result_urls:
            result_urls.append(full_url)

    if not result_urls:
        console.print("[yellow]未发现匹配的 URL[/yellow]")
        return []

    console.print(f"[cyan]匹配到 {len(result_urls)} 个 URL[/cyan]")
    for item in result_urls:
        console.print(item)

    return result_urls


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


def _load_runtime_config(config: str | None = None, workspace: str | None = None) -> Config:
    return Config()


if __name__ == "__main__":
    # 运行文件 → 触发 app() → Typer 开始工作 → 解析你的命令 → 执行函数
    # 启动整个命令行工具
    app()
    # config = load_config()
    # print(config)
    # save()
