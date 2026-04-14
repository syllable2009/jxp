import reflex as rx

from jxp.ui.state import State
from jxp.ui.styles import PAGE_STACK_STYLE


def onboard_page() -> rx.Component:
    return rx.vstack(
        rx.heading("JXP Onboard 执行器", size="8"),
        rx.text("输入完整命令（可选）；支持多行 \\ 续行；留空执行默认 onboard。"),
        rx.text_area(
            placeholder="例如: python -m jxp.cli.commands.commands find-link -l https://... -r '(?i)\\.(jpg|jpeg|png|webp)(\\?.*)?$'（会自动用 uv run 执行）",
            value=State.command_input,
            on_change=State.set_command_input,
            width="100%",
            min_height="140px",
            resize="vertical",
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
        **PAGE_STACK_STYLE,
    )
