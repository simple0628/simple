"""创建 PPT：AI 生成 SVG → DrawingML 原生形状 → PPTX"""

import os
import json

definition = {
    "type": "function",
    "function": {
        "name": "create_ppt",
        "description": """创建 PowerPoint 演示文稿。AI 生成 SVG 设计 + 演讲稿，自动转换为原生可编辑 PPTX。

在调用此工具之前，必须先通过对话了解清楚：
- 主题和场景
- 是否有参考资料（如有则先用 read_file 读取）
- 页数和风格偏好

参数说明：
- path（必填）：输出文件路径，.pptx 结尾
- pages（必填）：每页内容数组，每个元素包含：
  - title: 页面标题
  - bullets: 要点列表（封面/结尾可空）
  - notes: 演讲稿（口语化，3-5句）
- style（可选）：风格描述，如"科技风"、"古典风"、"极简"等""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "输出 .pptx 文件路径"},
                "pages": {
                    "type": "array",
                    "description": "每页内容",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "bullets": {"type": "array", "items": {"type": "string"}},
                            "notes": {"type": "string"},
                        },
                        "required": ["title"],
                    },
                },
                "style": {"type": "string", "description": "风格描述"},
            },
            "required": ["path", "pages"],
        },
    },
}


def label(args):
    return f"正在设计 PPT: {args.get('path', '')}"


def execute(args, app=None, **kwargs):
    path = args["path"]
    pages = args["pages"]
    style = args.get("style", "")

    # 预览流程
    if app:
        app.finish_tool(success=True)  # "正在设计 PPT" 变绿
        answer = app.preview_ppt(pages)
        if answer == "(用户取消)":
            return "用户取消了 PPT 创建"
        if answer not in ("(用户未输入内容)", ""):
            # 检查是否是确认短语
            confirm = {"ok", "好", "行", "做吧", "确认", "生成", "可以", "没问题",
                       "好的", "OK", "Ok", "是", "对", "就这样", "开始", "done", "yes"}
            if answer.strip().rstrip("。，！.!") not in confirm:
                return f"用户修改意见: {answer}\n请根据意见修改 pages 内容后重新调用 create_ppt。"

        app.write_tool("正在生成 PPT")

    # 调 DeepSeek 生成 SVG
    from openai import OpenAI
    from simple_code.config import get_provider

    provider = get_provider()
    client = OpenAI(api_key=provider["api_key"], base_url=provider["base_url"])

    svg_prompt = """你是顶级 PPT 视觉设计师。根据每页内容生成精美的 SVG 幻灯片。

SVG 元素限制：
1. viewBox="0 0 1280 720"，font-family="Microsoft YaHei"
2. 只用：rect, text, tspan, circle, ellipse, line, path, polygon, linearGradient
3. 禁止：style标签, class, foreignObject, image, mask, use, symbol
4. 用 <g id="xxx"> 组织内容。背景用 id 含 background/bg/chrome/decoration 的组
5. 颜色用 #RRGGBB，透明度用 fill-opacity
6. 所有页面保持统一配色和装饰风格

文字安全规则（违反即失败）：
1. 所有文字必须在 x=80 到 x=1200、y=40 到 y=680 范围内
2. 中文字符宽度约等于 font-size，英文/数字约 font-size×0.6。一行文字总宽度不得超过 1120px
3. 超长文本必须拆成多行，用多个 <text> 元素

设计要求（非常重要）：
1. 封面页：大标题居中，副信息分散排列，加装饰线条和几何图形
2. 数据指标页：用数据卡片展示关键数字，大号数字+小号说明，横向排列。不要用纯列表
3. 内容页（5条以下）：用带圆角的卡片+图标色块排列，左右分栏或网格布局
4. 内容页（6条以上）：可以用双栏布局，左右各放一半内容
5. 每页必须有装饰元素：渐变色块、半透明几何图形、线条分隔、光晕效果等
6. 标题区要有设计感：色条、下划线、背景色块等，不要只是纯文字
7. 页面要饱满，内容和装饰要充分利用整个 1280×720 空间，不要留大片空白

输出 JSON（只输出 JSON，不要```包裹）：
{"pages": [{"svg": "<svg xmlns=\\"http://www.w3.org/2000/svg\\" viewBox=\\"0 0 1280 720\\">...</svg>"}, ...]}"""

    pages_json = json.dumps(pages, ensure_ascii=False)
    user_prompt = f"以下是每页内容，请设计 SVG：\n\n{pages_json}"
    if style:
        user_prompt += f"\n\n风格：{style}"

    try:
        resp = client.chat.completions.create(
            model=provider["model"],
            messages=[
                {"role": "system", "content": svg_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=65536,
        )
        content = resp.choices[0].message.content.strip()

        # 提取 JSON
        if "```" in content:
            for part in content.split("```"):
                cleaned = part.strip()
                if cleaned.startswith("json"): cleaned = cleaned[4:].strip()
                if cleaned.startswith("{"): content = cleaned; break

        # 修复 JSON
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            content = content[start:end + 1]
        content = content.replace(",}", "}").replace(",]", "]")

        data = json.loads(content)
        svg_pages = data.get("pages", [])

    except Exception as e:
        if app:
            app.finish_tool(success=False)
        return f"SVG 生成失败: {e}"

    if app:
        app.finish_tool(success=True)

    # 保存 SVG 草稿（供后续修改使用，不自动删除）
    draft_dir = os.path.join(os.path.dirname(path) or ".", "simple", "草稿")
    os.makedirs(draft_dir, exist_ok=True)
    draft_name = os.path.splitext(os.path.basename(path))[0] + "_svg.json"
    draft_path = os.path.join(draft_dir, draft_name)
    try:
        with open(draft_path, "w", encoding="utf-8") as f:
            json.dump({"pages": svg_pages}, f, ensure_ascii=False, indent=2)
    except Exception:
        draft_path = ""

    # SVG → PPTX
    from simple_code.tools.svg_to_pptx import svgs_to_pptx

    merged = []
    for i, svg_page in enumerate(svg_pages):
        svg_str = svg_page.get("svg", "") if isinstance(svg_page, dict) else svg_page
        merged.append({"svg": svg_str, "notes": ""})

    try:
        count = svgs_to_pptx(merged, path)
        if app:
            app.finish_tool(success=True)
    except Exception as e:
        if app:
            app.finish_tool(success=False)
        return f"PPTX 转换失败: {e}"

    # 生成演讲稿 txt
    notes_path = path.rsplit(".", 1)[0] + "_演讲稿.txt"
    try:
        with open(notes_path, "w", encoding="utf-8") as f:
            for i, page in enumerate(pages, 1):
                title = page.get("title", f"第{i}页")
                notes = page.get("notes", "")
                f.write(f"【第{i}页 - {title}】\n")
                f.write(f"{notes}\n\n")
    except Exception:
        notes_path = ""

    result = f"PPT 已创建: {path}（{count} 页，含动画·转场）"
    if notes_path:
        result += f"\n演讲稿: {notes_path}"
    if draft_path:
        result += f"\nSVG 草稿已保存: {draft_path}"
    return result
