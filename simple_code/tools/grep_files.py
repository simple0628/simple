import os
import glob

definition = {
    "type": "function",
    "function": {
        "name": "grep_files",
        "description": """在文件内容中搜索关键词，返回匹配的文件名、行号和该行内容。

参数说明：
- keyword（必填）：要搜索的关键词，例如 "def login" 或 "TODO"
- pattern（选填）：文件匹配模式，默认 "**/*" 搜索所有文件，可指定如 "**/*.py" 只搜 Python 文件
- path（选填）：搜索的起始目录路径，默认为当前工作目录

返回格式：文件路径:行号: 该行内容""",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "要搜索的关键词"},
                "pattern": {"type": "string", "description": "文件匹配模式，默认 **/*"},
                "path": {"type": "string", "description": "搜索的起始目录路径，默认为当前工作目录"}
            },
            "required": ["keyword"]
        }
    }
}

def label(args):
    return f"正在搜索内容 \"{args.get('keyword', '')}\""

def execute(args, **kwargs):
    keyword = args["keyword"]
    pattern = args.get("pattern", "**/*")
    path = args.get("path", ".")
    full_pattern = os.path.join(path, pattern)
    files = glob.glob(full_pattern, recursive=True)

    results = []
    for file_path in files:
        if os.path.isdir(file_path):
            continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    if keyword in line:
                        results.append(f"{file_path}:{i}: {line.rstrip()}")
        except Exception:
            continue

    if not results:
        return f"未找到包含 \"{keyword}\" 的内容"
    return "\n".join(results)
