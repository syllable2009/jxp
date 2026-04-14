import subprocess
import shlex
from typing import Optional


def run_bash(
        command: str,
        timeout: int = 30,
        cwd: Optional[str] = None
) -> str:
    """
    安全执行 bash 命令，并返回执行结果（stdout + stderr）
    :param command: 要执行的 shell 命令
    :param timeout: 超时时间（秒）
    :param cwd: 工作目录
    :return: 命令执行结果字符串
    """
    try:
        # 安全解析命令（防止注入）
        args = shlex.split(command)

        # 执行命令，捕获 stdout / stderr
        result = subprocess.run(
            args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            shell=False  # 关闭 shell=True 更安全
        )

        # 拼接输出
        output = ""
        if result.stdout:
            output += f"[STDOUT]\n{result.stdout}\n"
        if result.stderr:
            output += f"[STDERR]\n{result.stderr}\n"

        output += f"[EXIT CODE] {result.returncode}"
        return output

    except subprocess.TimeoutExpired:
        return f"[ERROR] 命令执行超时（{timeout}秒）"
    except Exception as e:
        return f"[ERROR] 执行命令失败：{str(e)}"

if __name__ == '__main__':
    print(run_bash("pwd"))
    print(run_bash("ls -l"))
    # print(run_bash("ls -l", cwd=""))
    # print(run_bash("ls -l", timeout=1))