definition = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": """编辑已有文件，将文件中的一段内容精确替换为新内容。

参数说明：
- path（必填）：要编辑的文件的完整路径，例如 "E:\\project\\main.py"
- old_string（必填）：要被替换的原始内容，必须与文件中的内容完全一致（包括缩进和空格）
- new_string（必填）：替换后的新内容

注意：old_string 必须在文件中唯一匹配，如果匹配到多处会报错""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "要编辑的文件的完整路径"},
                "old_string": {"type": "string", "description": "要被替换的原始内容，必须完全匹配"},
                "new_string": {"type": "string", "description": "替换后的新内容"}
            },
            "required": ["path", "old_string", "new_string"]
        }
    }
}

def label(args):
    return f"正在编辑 {args.get('path', '')}"

def execute(args, **kwargs):
    app = kwargs.get("app")
    path = args["path"]
    old_string = args["old_string"]
    new_string = args["new_string"]

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if old_string not in content:
        return "错误: 未找到要替换的内容"

    if content.count(old_string) > 1:
        return "错误: 找到多处匹配，请提供更精确的内容以确保唯一匹配"

    content = content.replace(old_string, new_string, 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    # 通过 TUI 显示 diff
    if app:
        app.write_diff(old_string, new_string)

    return f"文件已编辑: {path}"
