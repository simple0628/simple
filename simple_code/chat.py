"""流式对话处理：API 调用、工具调度、记忆保存"""

import os
import json
from datetime import date, timedelta

from simple_code.tools import definitions, executors, labels


def build_system_prompt(cwd, platform):
    """构建系统提示词"""
    return f"""你是 simple，一个终端助手。

## 基本信息
- 当前日期: {date.today().strftime('%Y年%m月%d日')}
- 当前工作目录: {cwd}
- 用户操作系统: {platform}

## 工作原则
- 记忆系统：当前工作���录下的 simple/ 文件夹存放记忆文件
  - 短期记忆.md：最近7天的摘要，已加载到上下文中
  - 长期记忆/ 文件夹：按日期保存的完整记录（格式：YYYY-MM-DD_标题.md），永久保存
  - 当用户想回忆以前的事时，根据日期用 read_file 或 glob_files 去 simple/长期记忆/ 里查找
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
   - 当用户拒绝了某个操作时，立即停止，回复"已取消"即可，不要建议用户手动操作，不要用不同的方式重试
5. 删除文件、执行危险命令时，直接用 run_command 执行即可，不要用 ask_user 提前确认。系统会自动弹出确认选择框让用户决定
6. 当用户需求不明确时（不包括删除确认），使用 ask_user 工具向用户提问，不要用普通文字回复来提问
7. 自定义 Skill 存放在 ~/.simple-code/skills/ 目录下，每个 .md 文件就是一个 skill。用户可以通过 create_skill 工具创建新 skill，也可以用 read_file 读取该目录查看已有的 skill
8. 创建 PPT 时，必须且只能使用 create_ppt 工具，禁止用 write_file 写脚本。流程：
   - 先通过对话了解清楚：主题、是否有资料、页数、风格偏好
   - 如果用户有资料，先用 read_file 读取
   - 信息收集完毕后，调用 create_ppt 工具，传入每页的 title、bullets、notes
   - 结构完整：必须有封面、内容页、结尾页
   - 内容充实：每页至少 5-8 条要点，每条要点要具体详细（不要只写"xxx的介绍"这种概括性短句，而是写出具体的信息和数据）
   - 如果资料丰富，宁可多分几页，也不要把内容压缩成几个概括性短句
   - 演讲稿：每页 notes 写 3-5 句口语化演讲稿
   - 页数：一般不少于 7 页，内容多时可以 10-15 页
9. 创建简历时，必须使用 create_resume 工具。流程：
   - 先通过对话收集信息：基本信息、工作经历、项目经历、教育背景、技能
   - 用户可以拖入旧简历或岗位 JD，也可以口述
   - 必须主动询问用户是否有目标岗位 JD，不要自己假设没有
   - 必须询问用户偏好的简历风格
   - 询问用户是否需要放一寸照片，如果有则让用户拖入照片文件，将路径传给 photo 参数
   - 如果有 JD，根据 JD 优化简历内容（突出相关经验，但不伪造）
   - 所有信息确认后再调用 create_resume，传入素材和 JD
   - 生成后用户可以要求修改，修改后重新调用工具即可
   - 工具内部会自动用 Edge/Chrome 将 HTML 转为 PDF，不要自己用 run_command 转 PDF
   - 不要尝试使用 weasyprint、playwright、pdfkit 等方式转 PDF
   - 用户要求修改简历时，重新调用 create_resume，传入修改后的素材重新生成
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
                if hasattr(chunk.usage, 'prompt_tokens') and chunk.usage.prompt_tokens:
                    token_counter["prompt"] = chunk.usage.prompt_tokens
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

            user_rejected = False
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
                        "content": "工具调用出错，请重试"
                    })
                    continue

                # 用户拒绝了某个操作后，跳过后续所有工具
                if user_rejected:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": "用户已拒绝操作，已跳过"
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

                # 检测用户是否拒绝了操作
                if "用户拒绝了" in result:
                    user_rejected = True

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


def save_memory(client, model_name, memory_dir, session_file, user_input, reply, token_counter):
    """每次对话都保存：长期记忆（追加到 session 文件）+ 短期记忆（摘要）"""
    try:
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M")

        # AI 生成摘要
        memory_response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": """为这轮对话生成一句话摘要，只输出摘要内容，不要多余格式。"""},
                {"role": "user", "content": f"用户说: {user_input[:300]}\nAI回复: {reply[:500]}"}
            ]
        )
        if hasattr(memory_response, 'usage') and memory_response.usage:
            token_counter["total"] += memory_response.usage.total_tokens
            token_counter["round"] += memory_response.usage.total_tokens

        summary = memory_response.choices[0].message.content.strip()
        if not summary:
            summary = user_input[:50]

        # 保存长期记忆（追加到本次 session 文件）
        with open(session_file, "a", encoding="utf-8") as f:
            f.write(f"## {time_str}\n\n")
            f.write(f"**用户:** {user_input}\n\n")
            f.write(f"**AI:** {reply}\n\n---\n\n")

        # 保存短期记忆（追加一行摘要，带日期+时间）
        short_term_path = os.path.join(memory_dir, "短期记忆.md")
        with open(short_term_path, "a", encoding="utf-8") as f:
            f.write(f"- {today_str} {time_str} | {summary}\n")

        # 清理 7 天前的短期记忆
        _clean_short_term_memory(short_term_path, today)

        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False



def compress_context(client, model_name, messages, token_counter, max_prompt_tokens=55000, keep_recent=6):
    """当 prompt tokens 超过阈值时，压缩旧对话为摘要，保留最近几轮"""
    prompt_tokens = token_counter.get("prompt", 0)
    if prompt_tokens < max_prompt_tokens:
        return False

    # 保留 system prompt（第一条）
    system_msg = messages[0]

    # 找到最近 keep_recent 轮的起始位置
    user_count = 0
    split_idx = len(messages)
    for i in range(len(messages) - 1, 0, -1):
        if messages[i]["role"] == "user":
            user_count += 1
            if user_count >= keep_recent:
                split_idx = i
                break

    old_messages = messages[1:split_idx]
    recent_messages = messages[split_idx:]

    if not old_messages:
        return False

    # 用 AI 压缩旧对话
    old_text = ""
    for m in old_messages:
        role = m.get("role", "")
        content = m.get("content", "") or ""
        if role in ("user", "assistant") and content:
            old_text += f"{role}: {content[:200]}\n"

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "将以下对话历史压缩为一段简短的中文摘要，保留关键信息（做了什么、决策、文件路径等），不超过500字。"},
                {"role": "user", "content": old_text[:3000]}
            ]
        )
        if hasattr(response, 'usage') and response.usage:
            token_counter["total"] += response.usage.total_tokens

        summary = response.choices[0].message.content.strip()
    except Exception:
        return False

    # 重建 messages
    messages.clear()
    messages.append(system_msg)
    messages.append({"role": "user", "content": f"[以下是之前对话的摘要]\n{summary}"})
    messages.append({"role": "assistant", "content": "好的，我已了解之前的对话内容。请继续。"})
    messages.extend(recent_messages)

    return True


def _clean_short_term_memory(path, today):
    """删除短期记忆中 7 天前的条目"""
    try:
        cutoff = today - timedelta(days=7)
        cutoff_str = cutoff.strftime("%Y-%m-%d")

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 只保留日期 >= cutoff 的行
        kept = []
        for line in lines:
            # 格式: - 2026-05-01 15:30 | 摘要
            stripped = line.strip()
            if stripped.startswith("- ") and len(stripped) >= 12:
                date_part = stripped[2:12]
                if date_part >= cutoff_str:
                    kept.append(line)
            elif stripped:
                kept.append(line)

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(kept)
    except Exception:
        pass
