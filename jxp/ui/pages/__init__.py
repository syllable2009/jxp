import reflex as rx

from jxp.ui.pages.file_page import file_page
from jxp.ui.pages.image_page import image_page
from jxp.ui.pages.onboard_page import onboard_page
from jxp.ui.pages.user_page import user_page
from jxp.ui.state import State


def page_content() -> rx.Component:
    return rx.match(
        State.active_page,
        ("onboard_current", onboard_page()),
        ("user", user_page()),
        ("file", file_page()),
        ("image", image_page()),
        onboard_page(),
    )
