import os
from rich.syntax import Syntax

definition = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": """创建新文件或覆盖已有文件。仅用于创建新文件，修改已有文件请用 edit_file。

参数说明：
- path（必填）：文件的完整路径，例如 "E:\\project\\main.py"
- content（必填）：要写入的完整文件内容

注意：会自动创建不存在的父目录""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件的完整路径"},
                "content": {"type": "string", "description": "要写入的完整文件内容"}
            },
            "required": ["path", "content"]
        }
    }
}

_LANG_MAP = {
    "py": "python", "js": "javascript", "ts": "typescript",
    "md": "markdown", "json": "json", "html": "html", "css": "css",
    "java": "java", "c": "c", "cpp": "cpp", "go": "go", "rs": "rust",
    "sh": "bash", "bat": "batch", "ps1": "powershell",
    "yaml": "yaml", "yml": "yaml", "toml": "toml", "xml": "xml",
}

def label(args):
    return f"正在写入 {args.get('path', '')}"

def execute(args, **kwargs):
    app = kwargs.get("app")
    path = args["path"]
    content = args["content"]
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    # 通过 TUI 显示代码预览
    if app:
        ext = os.path.splitext(path)[1].lstrip(".")
        lang = _LANG_MAP.get(ext, ext or "text")
        preview = content if len(content) <= 3000 else content[:3000] + "\n... (已截断)"
        app.write_code(Syntax(preview, lang, theme="monokai", line_numbers=True))

    lines = content.count('\n') + 1
    return f"文件已写入: {path}（{lines} 行）"
