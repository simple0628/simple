import subprocess
import re
import sys
import time

from simple_code.state import interrupt

# 危险命令关键词
DANGEROUS_PATTERNS = [
    r"\brm\b", r"\brmdir\b", r"\bdel\b", r"\brd\b",
    r"\bformat\b", r"\bdrop\b", r"\btruncate\b",
    r"--force", r"\s-rf\b", r"\s/s\b", r"\s/q\b",
    r"\bsudo\b", r"\bchmod\b", r"\bmkfs\b", r"\bdd\b",
    r"\bkill\s+-9\b", r"\bkillall\b",
]

TIMEOUT = 30  # 命令超时秒数

definition = {
    "type": "function",
    "function": {
        "name": "run_command",
        "description": f"""在终端执行一条命令并返回输出结果。

参数说明：
- command（必填）：要执行的完整命令，例如 "python test.py" 或 "dir E:\\project"

限制：
- 命令必须在 {TIMEOUT} 秒内完成，超时会被终止
- 不能运行需要用户交互输入的程序（如 input() 的程序）
- 如果要测试交互式程序，请编写独立的测试脚本来调用""",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "要执行的完整命令"}
            },
            "required": ["command"]
        }
    }
}

def label(args):
    return f"正在执行 {args.get('command', '')}"

def is_dangerous(command):
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False

def execute(args, **kwargs):
    app = kwargs.get("app")
    command = args["command"]

    if is_dangerous(command):
        if app:
            if not app.request_danger_confirm(command):
                return "用户取消了操作"
        else:
            user_input = input(f"  危险命令: {command}\n  按回车确认: ")
            if user_input.strip():
                return "用户取消了操作"

    try:
        kwargs_popen = {}
        if sys.platform == "win32":
            command = f"chcp 65001 >nul && {command}"
            kwargs_popen["creationflags"] = subprocess.CREATE_NO_WINDOW
        proc = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace",
            **kwargs_popen
        )

        start = time.time()
        while proc.poll() is None:
            # 每 0.5 秒检查一次中断和超时
            if interrupt.is_set():
                proc.kill()
                return "已中断：用户按下 ESC"
            if time.time() - start > TIMEOUT:
                proc.kill()
                return f"错误: 命令执行超时（{TIMEOUT}秒），可能是交互式程序，请避免运行需要用户输入的程序"
            time.sleep(0.5)

        stdout = proc.stdout.read() if proc.stdout else ""
        stderr = proc.stderr.read() if proc.stderr else ""
        output = stdout + stderr
        return output if output.strip() else "(无输出)"
    except Exception as e:
        return f"错误: {e}"
