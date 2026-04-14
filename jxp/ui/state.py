import re
import shlex
import subprocess
from pathlib import Path

import reflex as rx

from jxp.ui.navigation import DEFAULT_ACTIVE_PAGE, DEFAULT_EXPANDED_GROUPS


class State(rx.State):
    """Global UI state."""

    active_page: str = DEFAULT_ACTIVE_PAGE
    expanded_groups: dict[str, bool] = DEFAULT_EXPANDED_GROUPS.copy()

    command_input: str = ""
    output: str = ""
    is_running: bool = False

    def set_active_page(self, page_key: str) -> None:
        self.active_page = page_key

    def toggle_group(self, group_key: str) -> None:
        updated = dict(self.expanded_groups)
        updated[group_key] = not updated.get(group_key, False)
        self.expanded_groups = updated

    def set_command_input(self, value: str) -> None:
        self.command_input = value

    def _parse_user_command(self) -> list[str]:
        raw = self.command_input.strip()
        if not raw:
            return []
        normalized = re.sub(r"\\\s*\n\s*", " ", raw)
        parts = shlex.split(normalized)
        return [part for part in parts if part.strip()]

    @staticmethod
    def _ensure_uv_run_prefix(command: list[str]) -> list[str]:
        if len(command) >= 2 and command[0] == "uv" and command[1] == "run":
            return command
        return ["uv", "run", *command]

    @staticmethod
    def _normalize_python_module_call(command: list[str]) -> list[str]:
        if len(command) >= 4 and command[0] in {"python", "python3"} and command[1] == "-m":
            if command[2] == "jxp.cli.commands.commands":
                return [command[0], "src/jxp/cli/commands/commands.py", *command[3:]]
        return command

    def run_command(self) -> None:
        self.is_running = True
        project_root = Path(__file__).resolve().parents[2]
        default_command = [
            "uv",
            "run",
            "python",
            "src/jxp/cli/commands/commands.py",
            "onboard",
        ]
        try:
            parsed_command = self._parse_user_command()
            full_command = (
                self._ensure_uv_run_prefix(self._normalize_python_module_call(parsed_command))
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
