"""流式对话处理：API 调用、工具调度、记忆保存"""

import json
from datetime import date

from simple_code.tools import definitions, executors, labels


def build_system_prompt(cwd, platform):
    """构建系统提示词"""
    return f"""你是 simple，一个终端助手。

## 基本信息
- 当前日期: {date.today().strftime('%Y年%m月%d日')}
- 当前工作目录: {cwd}
- 用户操作系统: {platform}

## 工作原则
- 启动后第一件事：收到用户第一条消息时，先用 read_file 读取当前工作目录下的 simple/simple.md 文件（如果存在），了解项目背景和历史记忆，再回复用户
- 记忆文件夹：当前工作目录下的 simple/ 文件夹存放各类记忆文件，simple.md 是通用记忆，simple-ppt.md 是 PPT 偏好记忆。创建 PPT 前应先读取 simple-ppt.md 了解用户偏好
- 当前工作目录优先：所有操作默认在当前工作目录下进行。读文件、搜索、执行命令都应该从当前目录开始，不要去访问其他无关路径
- 先理解再行动：修改代码前，先用搜索工具了解项目结构，再用读文件查看相关代码
- 最小改动：只改需要改的地方，用 edit_file 而不是 write_file 来修改现有文件
- 回复简洁：不要废话，直接给结果
- 复杂任务先列计划：当任务涉及多个步骤时，先输出一个编号计划清单，然后按顺序执行。每完成一步简要说明结果。例如：
  1. 了解项目结构
  2. 创建 models.py
  3. 创建 main.py
  4. 运行测试验证

## 工具使用优先级
1. 面对一个不熟悉的项目，先用 glob_files 了解文件结构
2. 需要找代码时，用 grep_files 搜索关键词，不要逐个读文件
3. 修改已有文件用 edit_file，创建新文件用 write_file
4. 写完代码后主动用 run_command 运行验证
5. 当用户需求不明确时，必须使用 ask_user 工具向用户提问，不要用普通文字回复来提问
6. 自定义 Skill 存放在 ~/.simple-code/skills/ 目录下，每个 .md 文件就是一个 skill。用户可以通过 create_skill 工具创建新 skill，也可以用 read_file 读取该目录查看已有的 skill
7. 创建 PPT 时，必须且只能使用 create_ppt 工具，禁止用 write_file 写脚本。流程：
   - 先通过对话了解清楚：主题、是否有资料、页数、风格偏好
   - 如果用户有资料，先用 read_file 读取，或用 read_clipboard 读剪贴板
   - 信息收集完毕后，调用 create_ppt 工具，传入每页的 title、bullets、notes
   - 结构完整：必须有封面、内容页、结尾页
   - 内容充实：每页至少 3-5 条要点
   - 演讲稿：每页 notes 写 3-5 句口语化演讲稿
   - 页数：一般不少于 6 页
"""


def chat_round(client, model_name, messages, app, tool_logs, token_counter, interrupt=None):
    """执行一轮对话（可能包含多次工具调用），支持流式显示，返回最终回复文本。"""

    used_search = [False]

    while True:
        if interrupt and interrupt.is_set():
            return ""
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=definitions,
            stream=True,
            stream_options={"include_usage": True}
        )

        reply = ""
        tool_calls_data = {}
        response_started = False

        for chunk in stream:
            if interrupt and interrupt.is_set():
                break

            if hasattr(chunk, 'usage') and chunk.usage:
                token_counter["total"] += chunk.usage.total_tokens
                token_counter["round"] += chunk.usage.total_tokens
                app.update_tokens(token_counter["round"], token_counter["total"])

            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            # 收集工具调用碎片
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_data:
                        tool_calls_data[idx] = {"id": "", "name": "", "arguments": "", "_shown": False}
                    if tc.id:
                        tool_calls_data[idx]["id"] = tc.id
                    if tc.function and tc.function.name:
                        tool_calls_data[idx]["name"] = tc.function.name
                        # 工具名已知，立即显示白色状态
                        if not tool_calls_data[idx]["_shown"]:
                            tool_calls_data[idx]["_shown"] = True
                            app.write_tool_preparing(tc.function.name)
                    if tc.function and tc.function.arguments:
                        tool_calls_data[idx]["arguments"] += tc.function.arguments

            # 流式显示文本
            if delta.content:
                reply += delta.content
                if not response_started:
                    app.begin_response()
                    response_started = True
                app.stream_chunk(reply)

        # 结束当前流的显示
        if response_started:
            app.end_response(reply)

        # 处理工具调用
        if tool_calls_data:
            msg_index_before_tools = len(messages)
            messages.append({"role": "assistant", "content": reply or None, "tool_calls": [
                {"id": tc["id"], "type": "function", "function": {"name": tc["name"], "arguments": tc["arguments"]}}
                for tc in tool_calls_data.values()
            ]})

            for tc in tool_calls_data.values():
                if interrupt and interrupt.is_set():
                    break

                name = tc["name"]
                try:
                    args = json.loads(tc["arguments"])
                except json.JSONDecodeError:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": "参数解析失败"
                    })
                    continue
                tip = labels[name](args) if name in labels else f"正在调用 {name}"
                app.write_tool(tip)

                try:
                    result = executors[name](args, app=app)
                    tool_logs.append(f"[{tip}]\n{result[:500]}")
                    app.finish_tool(success=True)
                    if name == "web_search":
                        used_search[0] = True
                except Exception as e:
                    result = f"错误: {e}"
                    app.finish_tool(success=False)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result
                })

            # 中断时清理不完整的 tool_calls + partial tool results
            if interrupt and interrupt.is_set():
                del messages[msg_index_before_tools:]
                return reply
            continue

        # 最终文字回复（无工具调用）
        app.stop_thinking()
        if reply and not response_started:
            # 未经流式显示的回复（理论上不会发生，作为兜底）
            app.write_assistant(reply)
        if reply:
            messages.append({"role": "assistant", "content": reply})
        if used_search[0]:
            app.write_warning("以上结果来自网络搜索，内容准确性未经验证，请自行甄别。")
        return reply


def save_memory(client, model_name, simple_md_path, user_input, reply, token_counter):
    """判断是否值得记忆，值得则生成一句记忆写入 simple.md"""
    try:
        memory_response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": """判断这轮对话是否值得记忆。

值得记忆的：项目背景、技术决策、用户偏好、重要操作结果、创建/修改/删除了什么文件。
不值得记忆的：闲聊、打招呼、简单问答、查看帮助、没有实质内容的对话。

如果值得记忆，用一句简短的中文总结这轮对话做了什么，只输出这一句话。
如果不值得记忆，只输出"跳过"两个字。"""},
                {"role": "user", "content": f"用户说: {user_input}\nAI回复: {reply[:200]}"}
            ]
        )
        if hasattr(memory_response, 'usage') and memory_response.usage:
            token_counter["total"] += memory_response.usage.total_tokens
            token_counter["round"] += memory_response.usage.total_tokens
        memory_line = memory_response.choices[0].message.content.strip()
        if memory_line == "跳过":
            return False
        with open(simple_md_path, "a", encoding="utf-8") as f:
            f.write(f"- {memory_line}\n")
        return True
    except Exception:
        return False
