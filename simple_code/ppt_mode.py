"""PPT 模式：/ppt 命令进入，独立对话流程生成 PPT

流程：
1. 问主题 → 2. 问资料 → 3. 问页数/风格 → 4. AI 生成 SVG + 演讲稿 → 5. 预览 → 6. 转换 PPTX

AI 负责：SVG 设计 + 演讲稿
代码负责：动画 + 转场 + SVG→PPTX 转换
"""

import os
import json
import time
from rich.text import Text
from rich.panel import Panel


# PPT 模式的系统提示词
_SVG_SYSTEM_PROMPT = """你是 PPT 设计大师兼演讲教练。为每页生成 SVG 设计和演讲稿。

SVG 限制：
1. viewBox="0 0 1280 720"，font-family="Microsoft YaHei"
2. 只用：rect, text, tspan, circle, ellipse, line, path, polygon, linearGradient
3. 禁止：style标签, class, foreignObject, image, mask, use, symbol
4. 用 <g id="xxx"> 组织内容区域
5. 背景/装饰用 id 含 background/bg/chrome/decoration 的组（这些不会被加动画）
6. 颜色用 #RRGGBB，透明度用 fill-opacity

演讲稿要求：
- 口语化，不是读稿
- 每页 3-5 句话
- 有过渡语（"接下来我们看..."、"值得注意的是..."）
- 有数据解读，不只是念数字

输出 JSON（只输出 JSON，不要解释）：
{"pages": [{"svg": "<svg xmlns=\\"http://www.w3.org/2000/svg\\" viewBox=\\"0 0 1280 720\\">...</svg>", "notes": "演讲稿"}, ...]}"""


def _set_ppt_header(app):
    """切换 header 为 PPT 模式样式"""
    header = Text()
    header.append(" simple", style="bold #e6edf3")
    header.append("  PPT 模式", style="bold #F5A623")
    header.append(f"  ·  {app.cwd}", style="#484f58")
    try:
        app.call_from_thread(app._header_left.update, header)
    except RuntimeError:
        app._header_left.update(header)


def _restore_header(app):
    """恢复普通 header"""
    app.update_header()


def _ask(app, question, placeholder=""):
    """在聊天区显示问题，等待用户输入"""
    app.write_system(question)
    answer = app.request_user_input(placeholder)
    if answer in ("(用户取消)", ):
        return None
    if answer == "(用户未输入内容)":
        return ""
    return answer


def _read_material(app, client, model_name, user_input):
    """解析用户提供的资料（文本/文件路径/无）"""
    if not user_input:
        return ""

    text = user_input.strip().strip('"').strip("'")

    # 检查是否是文件路径
    if os.path.isfile(text):
        ext = os.path.splitext(text)[1].lower()
        try:
            if ext in (".txt", ".md"):
                with open(text, "r", encoding="utf-8") as f:
                    content = f.read()
                app.write_system(f"已读取文件: {os.path.basename(text)}（{len(content)} 字符）")
                return content

            elif ext == ".pdf":
                import pdfplumber
                with pdfplumber.open(text) as pdf:
                    content = "\n".join(p.extract_text() or "" for p in pdf.pages)
                app.write_system(f"已读取 PDF: {os.path.basename(text)}（{len(content)} 字符）")
                return content

            elif ext == ".docx":
                from docx import Document
                doc = Document(text)
                content = "\n".join(p.text for p in doc.paragraphs)
                app.write_system(f"已读取 Word: {os.path.basename(text)}（{len(content)} 字符）")
                return content

            elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".webp"):
                from rapidocr_onnxruntime import RapidOCR
                ocr = RapidOCR()
                result, _ = ocr(text)
                if result:
                    content = "\n".join([line[1] for line in result])
                    app.write_system(f"已识别图片: {os.path.basename(text)}（{len(content)} 字符）")
                    return content
                app.write_warning("图片识别失败")
                return ""

            else:
                with open(text, "r", encoding="utf-8") as f:
                    content = f.read()
                app.write_system(f"已读取: {os.path.basename(text)}（{len(content)} 字符）")
                return content

        except Exception as e:
            app.write_warning(f"读取文件失败: {e}")
            return ""

    # 不是文件路径，当作文本资料
    return text


def _generate_svgs(app, client, model_name, topic, material, pages_count, style_hint):
    """调用 DeepSeek 生成 SVG + 演讲稿"""
    user_prompt = f"主题：{topic}\n页数：{pages_count} 页"
    if style_hint:
        user_prompt += f"\n风格：{style_hint}"
    if material:
        user_prompt += f"\n\n参考资料：\n{material[:8000]}"  # 限制资料长度

    app.write_system("正在设计 PPT...")
    app.start_thinking()

    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": _SVG_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=16000,
        )

        content = resp.choices[0].message.content.strip()

        # 提取 JSON
        if "```" in content:
            for part in content.split("```"):
                cleaned = part.strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
                if cleaned.startswith("{"):
                    content = cleaned
                    break

        data = json.loads(content)
        return data.get("pages", [])

    except json.JSONDecodeError:
        app.write_warning("AI 输出格式错误，请重试")
        return None
    except Exception as e:
        app.write_warning(f"生成失败: {e}")
        return None
    finally:
        app.stop_thinking()


def _preview_pages(app, pages):
    """在 TUI 中预览每页内容（文字版）"""
    total = len(pages)
    current = [0]  # 用列表以便在闭包中修改

    def _render_preview(idx):
        page = pages[idx]
        notes = page.get("notes", "无")[:200]

        content = Text()
        content.append(f"演讲稿:\n", style="bold #F5A623")
        content.append(notes, style="#e6edf3")

        return Panel(
            content,
            title=f"第 {idx + 1}/{total} 页",
            border_style="#F5A623",
            padding=(1, 2),
        )

    # 显示预览
    from simple_code.widgets import Static
    preview_widget = Static(_render_preview(0))
    app._ppt_slides = pages  # 复用翻页逻辑的标志
    app._ppt_index = 0
    app._ppt_preview_widget = preview_widget
    app._enqueue(Static(Text("")), preview_widget)
    app._enqueue(Static(Text(
        "  ◀ ▶ 翻页  ·  输入修改意见  ·  直接回车确认生成", style="#8b949e"
    )))

    import threading
    event = threading.Event()
    result = {"answer": ""}
    app._inline_event = event
    app._inline_result = result
    event.wait()

    app._ppt_slides = None
    app._ppt_preview_widget = None
    return result["answer"]


def _convert_and_save(app, pages, output_path):
    """SVG → PPTX 转换"""
    from simple_code.tools.svg_to_pptx import svgs_to_pptx

    app.write_system("正在生成 PPTX...")
    app.start_thinking()

    try:
        count = svgs_to_pptx(pages, output_path)
        return count
    except Exception as e:
        app.write_warning(f"转换失败: {e}")
        return 0
    finally:
        app.stop_thinking()


def start(app, client, model_name):
    """PPT 模式入口"""

    # 切换 header
    _set_ppt_header(app)
    app.write_system("")
    app.write_system("━━━ PPT 模式 ━━━")
    app.write_system("")

    # === 第 1 步：问主题 ===
    app.write_system("第 1/3 步 · 主题")
    topic = _ask(app, "你想做什么 PPT？（描述主题和场景）")
    if topic is None:
        app.write_system("已退出 PPT 模式")
        _restore_header(app)
        return

    # === 第 2 步：问资料 ===
    app.write_system("")
    app.write_system("第 2/3 步 · 资料")
    material_input = _ask(app, "有参考资料吗？（粘贴文字 / 拖入文件 / 直接回车跳过）")
    if material_input is None:
        app.write_system("已退出 PPT 模式")
        _restore_header(app)
        return

    material = _read_material(app, client, model_name, material_input)

    # === 第 3 步：问页数和风格 ===
    app.write_system("")
    app.write_system("第 3/3 步 · 偏好")
    prefs = _ask(app, "几页？风格偏好？（如：8页 科技风 / 直接回车用默认）")
    if prefs is None:
        app.write_system("已退出 PPT 模式")
        _restore_header(app)
        return

    # 解析页数和风格
    pages_count = 8  # 默认
    style_hint = ""
    if prefs:
        import re
        num_match = re.search(r"(\d+)\s*页", prefs)
        if num_match:
            pages_count = int(num_match.group(1))
            pages_count = max(4, min(20, pages_count))  # 限制 4-20 页
        style_hint = re.sub(r"\d+\s*页", "", prefs).strip()

    app.write_system(f"准备生成: {pages_count} 页" + (f", {style_hint}" if style_hint else ""))
    app.write_system("")

    # === 生成 SVG ===
    pages = _generate_svgs(app, client, model_name, topic, material, pages_count, style_hint)
    if not pages:
        _restore_header(app)
        return

    app.write_system(f"已设计 {len(pages)} 页")

    # === 预览 ===
    answer = _preview_pages(app, pages)
    if answer == "(用户取消)":
        app.write_system("已取消")
        _restore_header(app)
        return

    if answer and answer != "(用户未输入内容)":
        # 用户有修改意见，重新生成
        app.write_system(f"收到修改意见: {answer}")
        app.write_system("正在根据意见重新设计...")
        topic_with_feedback = f"{topic}\n\n用户修改意见: {answer}"
        pages = _generate_svgs(app, client, model_name, topic_with_feedback, material, pages_count, style_hint)
        if not pages:
            _restore_header(app)
            return
        app.write_system(f"已重新设计 {len(pages)} 页")

    # === 转换 PPTX ===
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c for c in topic[:20] if c.isalnum() or c in " _-")
    output_path = os.path.join(app.cwd, f"{safe_topic}_{timestamp}.pptx")

    count = _convert_and_save(app, pages, output_path)
    if count > 0:
        app.write_system("")
        app.write_system(f"✓ PPT 已生成: {output_path}")
        app.write_system(f"  {count} 页 · 含动画 · 含转场 · 含演讲稿")
        app.write_system(f"  按 F5 播放 · 备注栏查看演讲稿")

    app.write_system("")
    app.write_system("━━━ 退出 PPT 模式 ━━━")
    _restore_header(app)
