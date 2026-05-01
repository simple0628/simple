import os

definition = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": """读取指定路径的文件内容。支持文本文件、PDF（.pdf）和 Word（.docx）。如果路径是文件夹则列出目录内容。

参数说明：
- path（必填）：要读取的文件或文件夹的完整路径

返回值：文件的完整文本内容，或文件夹内的文件列表""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件或文件夹的完整路径"}
            },
            "required": ["path"]
        }
    }
}

def label(args):
    return f"正在读取 {args.get('path', '')}"

def execute(args, **kwargs):
    path = args["path"]
    if os.path.isdir(path):
        items = os.listdir(path)
        return "\n".join(items) if items else "(空文件夹)"

    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        import pdfplumber
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts) if text_parts else "(PDF 内容为空)"

    if ext == ".docx":
        import docx
        doc = docx.Document(path)
        text_parts = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(text_parts) if text_parts else "(DOCX 内容为空)"

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
