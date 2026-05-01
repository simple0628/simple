import os

SKILLS_DIR = os.path.join(os.path.expanduser("~"), ".simple-code", "skills")

definition = {
    "type": "function",
    "function": {
        "name": "create_skill",
        "description": """创建一个自定义 Skill（快捷命令）。用户之后可以通过 /名称 来快速触发这个 Skill。

参数说明：
- name（必填）：Skill 的名称，用户之后通过 /名称 来调用，例如 "review"、"写小说"
- content（必填）：Skill 的提示词内容，调用时会作为用户消息发送给 AI

使用场景：用户想创建一个可复用的快捷命令时使用""",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Skill 名称"},
                "content": {"type": "string", "description": "Skill 的提示词内容"}
            },
            "required": ["name", "content"]
        }
    }
}


def label(args):
    return f"创建 Skill: {args.get('name', '')}"


def execute(args, **kwargs):
    name = args["name"]
    content = args["content"]

    os.makedirs(SKILLS_DIR, exist_ok=True)
    filepath = os.path.join(SKILLS_DIR, f"{name}.md")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return f"Skill '{name}' 已创建，输入 /{name} 即可使用"
