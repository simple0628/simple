definition = {
    "type": "function",
    "function": {
        "name": "ask_user",
        "description": """向用户提问，等待用户回答后继续执行。

使用场景：
- 需求不明确，需要用户澄清
- 有多种方案，需要用户选择
- 操作有风险，需要用户确认

参数说明：
- question（必填）：要问用户的问题，尽量简洁明确

返回值：用户的回答文本""",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "要问用户的问题"}
            },
            "required": ["question"]
        }
    }
}


def label(args):
    q = args.get("question", "")
    if len(q) > 40:
        q = q[:40] + "..."
    return f"等待用户回答: {q}"


def execute(args, **kwargs):
    app = kwargs.get("app")
    question = args["question"]
    if app:
        return app.request_user_input(question)
    # 兜底：无 app 时用 input()
    answer = input(f"  {question}\n  > ")
    return answer if answer.strip() else "(用户未输入内容)"
