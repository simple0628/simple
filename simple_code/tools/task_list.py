definition = {
    "type": "function",
    "function": {
        "name": "task_list",
        "description": """管理任务清单，用于把复杂任务拆分成步骤并跟踪进度。

参数说明：
- action（必填）：操作类型
  - "create"：创建任务清单，需要提供 tasks 参数
  - "done"：标记某个任务完成，需要提供 index 参数（从1开始）
  - "list"：查看当前所有任务和状态

- tasks（create时必填）：任务列表，例如 ["了解项目结构", "创建文件", "测试验证"]
- index（done时必填）：要标记完成的任务编号，从1开始

使用场景：当任务涉及3个以上步骤时，先用 create 建立清单，每完成一步用 done 标记""",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "done", "list"],
                    "description": "操作类型"
                },
                "tasks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "任务列表（create时使用）"
                },
                "index": {
                    "type": "integer",
                    "description": "任务编号，从1开始（done时使用）"
                }
            },
            "required": ["action"]
        }
    }
}

# 内存中的任务列表，对话期间持久
_tasks = []


def label(args):
    action = args.get("action", "")
    if action == "create":
        count = len(args.get("tasks", []))
        return f"创建任务清单（{count}项）"
    elif action == "done":
        return f"完成任务 #{args.get('index', '?')}"
    else:
        return "查看任务清单"


def _format_tasks():
    """格式化任务清单"""
    if not _tasks:
        return "（暂无任务）"
    lines = []
    done_count = sum(1 for t in _tasks if t["done"])
    lines.append(f"进度: {done_count}/{len(_tasks)}")
    lines.append("")
    for i, t in enumerate(_tasks, 1):
        mark = "✅" if t["done"] else "⬜"
        lines.append(f"  {mark} {i}. {t['text']}")
    return "\n".join(lines)


def execute(args, **kwargs):
    action = args["action"]

    if action == "create":
        task_texts = args.get("tasks", [])
        if not task_texts:
            return "错误: 请提供 tasks 参数"
        _tasks.clear()
        for text in task_texts:
            _tasks.append({"text": text, "done": False})
        return _format_tasks()

    elif action == "done":
        index = args.get("index")
        if index is None:
            return "错误: 请提供 index 参数"
        if index < 1 or index > len(_tasks):
            return f"错误: 编号 {index} 不存在，当前共 {len(_tasks)} 个任务"
        _tasks[index - 1]["done"] = True
        return _format_tasks()

    elif action == "list":
        return _format_tasks()

    return f"错误: 未知操作 {action}"
