import glob
import os

definition = {
    "type": "function",
    "function": {
        "name": "glob_files",
        "description": """按文件名模式搜索文件，返回匹配的文件路径列表。

参数说明：
- pattern（必填）：文件匹配模式，例如 "**/*.py" 匹配所有 Python 文件，"*" 匹配当前目录所有文件
- path（选填）：搜索的起始目录路径，默认为当前工作目录

常用模式示例：
- "**/*.py" → 递归查找所有 .py 文件
- "*.txt" → 当前目录下的 .txt 文件
- "**/*" → 递归列出所有文件""",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "文件匹配模式，例如 **/*.py"},
                "path": {"type": "string", "description": "搜索的起始目录路径，默认为当前工作目录"}
            },
            "required": ["pattern"]
        }
    }
}

def label(args):
    return f"正在搜索文件 {args.get('pattern', '')}"

def execute(args, **kwargs):
    pattern = args["pattern"]
    path = args.get("path", ".")
    full_pattern = os.path.join(path, pattern)
    files = glob.glob(full_pattern, recursive=True)
    if not files:
        return "未找到匹配的文件"
    return "\n".join(files)
