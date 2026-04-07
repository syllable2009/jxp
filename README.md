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


uv run python src/jxp/cli/commands/commands.py onboard

# 子命令
uv run python src/jxp/cli/commands/commands.py plugins list

uv run python src/jxp/cli/commands/commands.py down -l "https://files.21voa.com/audio/202503/wilbur-and-orville-wright-the-first-airplane.mp3" -d "/Users/jiaxiaopeng"