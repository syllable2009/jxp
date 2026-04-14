import reflex as rx

from jxp.ui.components.sidebar import sidebar
from jxp.ui.pages import page_content
from jxp.ui.styles import CONTAINER_STYLE, CONTENT_WRAPPER_STYLE, LAYOUT_STYLE


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.hstack(
            sidebar(),
            rx.box(page_content(), **CONTENT_WRAPPER_STYLE),
            **LAYOUT_STYLE,
        ),
        **CONTAINER_STYLE,
    )


app = rx.App()
app.add_page(index)
