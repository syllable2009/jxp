import reflex as rx

from jxp.ui.navigation import MENU_TREE
from jxp.ui.state import State
from jxp.ui.styles import SIDEBAR_STYLE


def _tree_item(label: str, page_key: str, depth: int = 0, branch_prefix: str = "") -> rx.Component:
    return rx.button(
        f"{branch_prefix}{label}",
        variant="ghost",
        width="100%",
        justify_content="flex-start",
        on_click=State.set_active_page(page_key),
        background=rx.cond(State.active_page == page_key, "var(--accent-4)", "transparent"),
        padding_left=f"{depth * 16}px",
    )


def _render_node(node: dict, depth: int = 0, is_last: bool = True) -> rx.Component:
    has_children = bool(node.get("children"))
    icon = node.get("icon", "")
    label = node.get("label", "")
    group_key = node.get("key", "")
    branch_prefix = "└─ " if is_last else "├─ "
    folder_prefix = f"{branch_prefix}" if depth > 0 else ""

    if has_children:
        expanded = State.expanded_groups.get(group_key, False)
        children = node.get("children", [])
        return rx.vstack(
            rx.button(
                rx.hstack(
                    rx.text(rx.cond(expanded, "📂", icon or "📁")),
                    rx.text(f"{folder_prefix}{label}"),
                    spacing="2",
                    align="center",
                ),
                variant="ghost",
                width="100%",
                justify_content="flex-start",
                on_click=State.toggle_group(group_key),
                padding_left=f"{depth * 16}px",
            ),
            rx.cond(
                expanded,
                rx.vstack(
                    *[
                        _render_node(child, depth + 1, idx == len(children) - 1)
                        for idx, child in enumerate(children)
                    ],
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.fragment(),
            ),
            spacing="1",
            align="start",
            width="100%",
        )

    page_key = node.get("page_key", "")
    display = f"{icon} {label}".strip()
    return _tree_item(display, page_key, depth=depth, branch_prefix=folder_prefix)


def sidebar() -> rx.Component:
    return rx.box(
        rx.heading("目录树", size="5"),
        rx.vstack(
            *[
                _render_node(node, depth=0, is_last=idx == len(MENU_TREE) - 1)
                for idx, node in enumerate(MENU_TREE)
            ],
            spacing="2",
            align="start",
            width="100%",
        ),
        **SIDEBAR_STYLE,
    )
