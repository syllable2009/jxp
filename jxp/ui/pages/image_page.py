import reflex as rx

from jxp.ui.styles import PAGE_STACK_STYLE


def image_page() -> rx.Component:
    return rx.vstack(
        rx.heading("图片管理", size="8"),
        rx.text("页面建设中，后续可放图片筛选、压缩转换、批量标注等能力。", color="gray"),
        **PAGE_STACK_STYLE,
    )
