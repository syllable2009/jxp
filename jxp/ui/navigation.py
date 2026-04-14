"""Navigation tree configuration for sidebar and pages."""

MENU_TREE = [
    {
        "key": "onboard_manage",
        "label": "onboard管理",
        "icon": "📁",
        "children": [
            {
                "key": "onboard_current",
                "label": "当前页面功能",
                "icon": "⚙️",
                "page_key": "onboard_current",
            }
        ],
    },
    {
        "key": "user_manage",
        "label": "用户管理",
        "icon": "👤",
        "page_key": "user",
    },
    {
        "key": "file_manage",
        "label": "文件管理",
        "icon": "📄",
        "page_key": "file",
    },
    {
        "key": "image_manage",
        "label": "图片管理",
        "icon": "🖼️",
        "page_key": "image",
    },
]

DEFAULT_ACTIVE_PAGE = "onboard_current"
DEFAULT_EXPANDED_GROUPS = {"onboard_manage": True}
