# jxp

uv venv
source .venv/bin/activate
uv add requests
uv sync

# 测试运行
uv run python src/jxp/cli/commands/commands.py goodbye Alice --formal


uv run python src/jxp/cli/commands/commands.py serve \
-p 8000 \
-H 0.0.0.0 \
-t 30.0 \
-v \
-w ./my-workspace \
-c ./config.toml

uv run python src/jxp/cli/commands/commands.py agent \
-m "hello"


uv run python src/jxp/cli/commands/commands.py onboard

uv run python -m jxp.cli.commands.commands find-link \
  -l "https://fastly.picsum.photos/id/1/400/400.jpg?hmac=lOytrN6lDOH_Yx7NwwGIaCtxp6pyuH2V4hD6Eac-VI0" \
  -r "(?i)\.(jpg|jpeg|png|webp)(\?.*)?$"

uv run python -m jxp.cli.commands.commands find-link \
  -l "https://www.21voa.com/special_english/wilbur-and-orville-wright-the-first-airplane-93397.html" \
  -r "(?i)mp3(\?.*)?$"


# 子命令
uv run python src/jxp/cli/commands/commands.py plugins list

uv run python src/jxp/cli/commands/commands.py down -l "https://files.21voa.com/audio/202503/wilbur-and-orville-wright-the-first-airplane.mp3" -d "/Users/jiaxiaopeng"


# reflex页面
reflex run