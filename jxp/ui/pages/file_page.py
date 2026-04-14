import reflex as rx

from jxp.ui.styles import PAGE_STACK_STYLE


def file_page() -> rx.Component:
    return rx.vstack(
        rx.heading("文件管理", size="8"),
        rx.text("页面建设中，后续可放文件浏览、上传下载、批处理等能力。", color="gray"),
        **PAGE_STACK_STYLE,
    )
