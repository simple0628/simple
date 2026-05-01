"""读取系统剪贴板内容"""


definition = {
    "type": "function",
    "function": {
        "name": "read_clipboard",
        "description": "读取用户系统剪贴板中的文本内容。当用户提到剪贴板、复制的内容、粘贴等，使用此工具读取。",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}


def label(args):
    return "正在读取剪贴板"


def execute(args, **kwargs):
    try:
        import pyperclip
        text = pyperclip.paste()
    except Exception as e:
        return f"读取剪贴板失败: {e}"

    if not text:
        return "剪贴板为空"

    lines = text.count('\n') + 1
    return f"剪贴板内容（{len(text)} 字符，{lines} 行）：\n\n{text}"
