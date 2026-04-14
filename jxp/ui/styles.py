"""Centralized style definitions for app UI."""

SIDEBAR_WIDTH = "260px"
SIDEBAR_MIN_WIDTH = "220px"

CONTAINER_STYLE = {
    "max_width": "100%",
    "padding": "0",
}

LAYOUT_STYLE = {
    "width": "100%",
    "min_height": "90vh",
    "align": "start",
    "spacing": "0",
}

SIDEBAR_STYLE = {
    "width": SIDEBAR_WIDTH,
    "min_width": SIDEBAR_MIN_WIDTH,
    "height": "100%",
    "border_right": "1px solid var(--gray-6)",
    "padding": "1.25rem 1rem",
}

CONTENT_WRAPPER_STYLE = {
    "flex": "1",
    "padding": "2rem",
}

PAGE_STACK_STYLE = {
    "spacing": "4",
    "width": "100%",
    "max_width": "900px",
    "min_height": "85vh",
    "align": "start",
}
