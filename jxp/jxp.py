import reflex as rx
import re
import shlex
import subprocess
from pathlib import Path

class State(rx.State):
    """The app state."""

    command_input: str = ""
    output: str = ""
    is_running: bool = False

    def set_command_input(self, value: str) -> None:
        self.command_input = value

    def _parse_user_command(self) -> list[str]:
        raw = self.command_input.strip()
        if not raw:
            return []
        # 兼容粘贴 shell 多行命令（反斜杠续行）。
        normalized = re.sub(r"\\\s*\n\s*", " ", raw)
        parts = shlex.split(normalized)
        # 有些复制场景会混入单个空格参数（如 ' '），这里清理掉。
        return [part for part in parts if part.strip()]

    @staticmethod
    def _ensure_uv_run_prefix(command: list[str]) -> list[str]:
        if len(command) >= 2 and command[0] == "uv" and command[1] == "run":
            return command
        return ["uv", "run", *command]

    @staticmethod
    def _normalize_python_module_call(command: list[str]) -> list[str]:
        # 当前项目命令实现位于脚本路径下，优先转换为脚本执行，避免 -m 导入失败。
        if len(command) >= 4 and command[0] in {"python", "python3"} and command[1] == "-m":
            if command[2] == "jxp.cli.commands.commands":
                return [command[0], "src/jxp/cli/commands/commands.py", *command[3:]]
        return command

    def run_command(self) -> None:
        self.is_running = True
        project_root = Path(__file__).resolve().parents[1]
        default_command = [
            "uv",
            "run",
            "python",
            "src/jxp/cli/commands/commands.py",
            "onboard",
        ]
        try:
            # 输入为空时执行默认命令；有输入时按完整命令执行。
            parsed_command = self._parse_user_command()
            full_command = (
                self._ensure_uv_run_prefix(
                    self._normalize_python_module_call(parsed_command)
                )
                if parsed_command
                else default_command
            )
            completed = subprocess.run(
                full_command,
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
            )
            stdout = completed.stdout.strip()
            stderr = completed.stderr.strip()
            result_lines = [
                f"命令: {shlex.join(full_command)}",
                f"退出码: {completed.returncode}",
            ]
            if stdout:
                result_lines.append(f"\n标准输出:\n{stdout}")
            if stderr:
                result_lines.append(f"\n错误输出:\n{stderr}")
            self.output = "\n".join(result_lines)
        except Exception as exc:
            self.output = f"执行失败: {exc}"
        finally:
            self.is_running = False


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("JXP Onboard 执行器", size="8"),
            rx.text("输入完整命令（可选）；支持多行 \\ 续行；留空执行默认 onboard。"),
            rx.input(
                placeholder="例如: python -m jxp.cli.commands.commands find-link -l https://... -r '(?i)\\.(jpg|jpeg|png|webp)(\\?.*)?$'（会自动用 uv run 执行）",
                value=State.command_input,
                on_change=State.set_command_input,
                width="100%",
            ),
            rx.button(
                rx.cond(State.is_running, "执行中...", "执行"),
                on_click=State.run_command,
                loading=State.is_running,
            ),
            rx.code_block(
                State.output,
                language="bash",
                width="100%",
                white_space="pre-wrap",
            ),
            spacing="4",
            width="100%",
            max_width="800px",
            min_height="85vh",
            justify="center",
        ),
        padding="2em",
    )


app = rx.App()
app.add_page(index)
