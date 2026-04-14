import reflex as rx

from jxp.ui.styles import PAGE_STACK_STYLE


def user_page() -> rx.Component:
    return rx.vstack(
        rx.heading("用户管理", size="8"),
        rx.text("页面建设中，后续可放用户列表、角色权限、状态管理等能力。", color="gray"),
        **PAGE_STACK_STYLE,
    )
