# 导入 Reflex 核心库
import reflex as rx

# 创建项目配置实例
config = rx.Config(
    app_name="jxp",  # 项目应用名称（必须与你的项目主模块名一致）
    plugins=[        # 启用的插件列表
        rx.plugins.SitemapPlugin(),  # 自动生成网站地图插件（SEO优化）
        rx.plugins.TailwindV4Plugin(),  # 启用 Tailwind CSS v4 样式框架
    ]
)