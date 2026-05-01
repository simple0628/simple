"""创建 PowerPoint 演示文稿"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

THEME = {
    "primary": RGBColor(0x1A, 0x3C, 0x6E),   # 深藏蓝
    "accent": RGBColor(0x2B, 0x6C, 0xB3),     # 中蓝
    "highlight": RGBColor(0xE8, 0x8D, 0x2A),  # 金橙强调色
    "light": RGBColor(0xEC, 0xF0, 0xF5),      # 浅灰蓝背景
    "text": RGBColor(0x33, 0x33, 0x33),        # 正文深灰
    "subtle": RGBColor(0x88, 0x88, 0x88),      # 次要灰
    "white": RGBColor(0xFF, 0xFF, 0xFF),
    "font": "Microsoft YaHei",
}

# 幻灯片尺寸常量（16:9）
SLIDE_W = Emu(12192000)
SLIDE_H = Emu(6858000)

definition = {
    "type": "function",
    "function": {
        "name": "create_ppt",
        "description": """创建 PowerPoint 演示文稿（.pptx）。

参数说明：
- path（必填）：输出文件的完整路径，必须以 .pptx 结尾
- slides（必填）：幻灯片数组，每个元素包含：
  - layout: "title"（标题页）、"content"（内容页，带项目符号）、"section"（章节分隔页）
  - title: 幻灯片标题
  - subtitle: 副标题（title 和 section 布局使用）
  - bullets: 项目符号列表（content 布局使用，字符串数组）
  - notes: 演讲者备注（可选）""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "输出 .pptx 文件的完整路径"},
                "slides": {
                    "type": "array",
                    "description": "幻灯片数组",
                    "items": {
                        "type": "object",
                        "properties": {
                            "layout": {
                                "type": "string",
                                "enum": ["title", "content", "section"],
                                "description": "幻灯片类型",
                            },
                            "title": {"type": "string", "description": "标题文本"},
                            "subtitle": {"type": "string", "description": "副标题文本"},
                            "bullets": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "项目符号列表",
                            },
                            "notes": {"type": "string", "description": "演讲者备注"},
                        },
                        "required": ["layout", "title"],
                    },
                },
            },
            "required": ["path", "slides"],
        },
    },
}

needs_pause = False


def label(args):
    return f"正在设计 PPT 结构: {args.get('path', '')}"


# --- 基础绘图工具 ---

def _set_bg(slide, color):
    """设置纯色背景"""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_shape(slide, left, top, width, height, color, shape_type=MSO_SHAPE.RECTANGLE):
    """添加形状色块（无边框）"""
    shape = slide.shapes.add_shape(shape_type, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


def _add_textbox(slide, text, left, top, width, height,
                 font_size=18, color=None, bold=False,
                 alignment=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
                 line_spacing=1.5):
    """添加文本框"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None

    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.name = THEME["font"]
    p.font.color.rgb = color or THEME["text"]
    p.font.bold = bold
    p.alignment = alignment
    p.line_spacing = Pt(int(font_size * line_spacing))
    return txBox


def _add_page_number(slide, page_num, total, color=None):
    """右下角页码"""
    _add_textbox(
        slide, f"{page_num} / {total}",
        Inches(11.5), Inches(7.0), Inches(1.5), Inches(0.4),
        font_size=10, color=color or THEME["subtle"],
        alignment=PP_ALIGN.RIGHT,
    )


def _add_bullets(slide, bullets, left, top, width, height):
    """添加带圆点的项目符号列表"""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True

    for i, bullet in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = bullet
        p.font.size = Pt(16)
        p.font.name = THEME["font"]
        p.font.color.rgb = THEME["text"]
        p.space_after = Pt(12)
        p.line_spacing = Pt(28)
        p.level = 0

        # 设置圆点符号
        pf = p._pPr
        if pf is None:
            pf = etree.SubElement(p._p, qn("a:pPr"))
        buNone = pf.find(qn("a:buNone"))
        if buNone is not None:
            pf.remove(buNone)
        buChar = pf.find(qn("a:buChar"))
        if buChar is None:
            buChar = etree.SubElement(pf, qn("a:buChar"))
        buChar.set("char", "●")

        # 符号颜色用强调色
        buClr = pf.find(qn("a:buClr"))
        if buClr is None:
            buClr = etree.SubElement(pf, qn("a:buClr"))
        else:
            buClr.clear()
        srgb = etree.SubElement(buClr, qn("a:srgbClr"))
        srgb.set("val", "E88D2A")

        # 缩进
        pf.set("marL", str(Emu(457200)))  # 左缩进
        pf.set("indent", str(Emu(-228600)))  # 悬挂缩进


# --- 页面布局 ---

def _build_title_slide(slide, title, subtitle, page_num, total):
    """封面页：深蓝背景 + 金色装饰线 + 居中标题"""
    _set_bg(slide, THEME["primary"])

    # 顶部装饰细线
    _add_shape(slide, Inches(3), Inches(1.8), Inches(7.3), Pt(2), THEME["highlight"])

    # 标题
    _add_textbox(
        slide, title,
        Inches(1), Inches(2.2), Inches(11.3), Inches(1.5),
        font_size=40, color=THEME["white"], bold=True,
        alignment=PP_ALIGN.CENTER,
    )

    # 装饰线（标题下方）
    _add_shape(slide, Inches(3), Inches(3.8), Inches(7.3), Pt(2), THEME["highlight"])

    # 副标题
    if subtitle:
        _add_textbox(
            slide, subtitle,
            Inches(1), Inches(4.2), Inches(11.3), Inches(0.8),
            font_size=18, color=THEME["light"],
            alignment=PP_ALIGN.CENTER,
        )

    # 底部装饰色块
    _add_shape(slide, 0, Inches(7.1), SLIDE_W, Inches(0.4), THEME["highlight"])


def _build_section_slide(slide, title, subtitle, page_num, total):
    """章节分隔页：白底 + 左侧强调色块 + 大标题"""
    _set_bg(slide, THEME["white"])

    # 左侧竖条装饰
    _add_shape(slide, 0, 0, Inches(0.5), SLIDE_H, THEME["primary"])
    _add_shape(slide, Inches(0.5), 0, Inches(0.08), SLIDE_H, THEME["highlight"])

    # 标题
    _add_textbox(
        slide, title,
        Inches(1.2), Inches(2.5), Inches(10), Inches(1.5),
        font_size=36, color=THEME["primary"], bold=True,
    )

    # 标题下方装饰线
    _add_shape(slide, Inches(1.2), Inches(4.0), Inches(3), Pt(3), THEME["highlight"])

    # 副标题
    if subtitle:
        _add_textbox(
            slide, subtitle,
            Inches(1.2), Inches(4.3), Inches(10), Inches(0.8),
            font_size=16, color=THEME["subtle"],
        )

    _add_page_number(slide, page_num, total)


def _build_content_slide(slide, title, bullets, page_num, total):
    """内容页：顶部标题栏 + 左侧强调条 + 项目符号"""
    _set_bg(slide, THEME["white"])

    # 顶部标题栏
    _add_shape(slide, 0, 0, SLIDE_W, Inches(1.1), THEME["primary"])
    # 标题栏下方金色细线
    _add_shape(slide, 0, Inches(1.1), SLIDE_W, Pt(3), THEME["highlight"])

    # 标题文字
    _add_textbox(
        slide, title,
        Inches(0.8), Inches(0.15), Inches(11.5), Inches(0.8),
        font_size=24, color=THEME["white"], bold=True,
    )

    # 左侧装饰竖条
    _add_shape(slide, Inches(0.5), Inches(1.6), Pt(4), Inches(5.2), THEME["accent"])

    # 项目符号内容
    if bullets:
        _add_bullets(slide, bullets, Inches(0.9), Inches(1.5), Inches(11), Inches(5.3))

    # 底部细线
    _add_shape(slide, Inches(0.5), Inches(7.1), Inches(12.3), Pt(1), THEME["light"])

    _add_page_number(slide, page_num, total)


# --- 主执行函数 ---

def execute(args, app=None, **kwargs):
    path = args["path"]
    slides_data = args["slides"]

    # PPT 预览流程
    if app:
        app.finish_tool(success=True)  # "设计结构" 变绿
        answer = app.preview_ppt(slides_data)
        if answer == "(用户取消)":
            return "用户取消了 PPT 创建"
        if answer not in ("(用户未输入内容)", ""):
            return f"用户修改意见: {answer}\n请根据意见修改 slides 内容后重新调用 create_ppt。"
        app.write_tool(f"正在创建 PPT: {path}")  # 新状态行

    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank_layout = prs.slide_layouts[6]
    total = len(slides_data)

    for idx, s in enumerate(slides_data):
        slide = prs.slides.add_slide(blank_layout)
        layout = s.get("layout", "content")
        title = s.get("title", "")
        subtitle = s.get("subtitle", "")
        bullets = s.get("bullets", [])
        notes = s.get("notes", "")
        page_num = idx + 1

        if layout == "title":
            _build_title_slide(slide, title, subtitle, page_num, total)
        elif layout == "section":
            _build_section_slide(slide, title, subtitle, page_num, total)
        else:
            _build_content_slide(slide, title, bullets, page_num, total)

        if notes:
            slide.notes_slide.notes_text_frame.text = notes

    prs.save(path)

    # 记录到 simple-ppt.md
    try:
        simple_dir = os.path.join(os.getcwd(), "simple")
        ppt_md = os.path.join(simple_dir, "simple-ppt.md")
        from datetime import date
        first_title = slides_data[0].get("title", "未知") if slides_data else "未知"
        line = f"- {date.today()} | {first_title} | {total}页 | {os.path.basename(path)}\n"
        if os.path.exists(simple_dir):
            with open(ppt_md, "a", encoding="utf-8") as f:
                f.write(line)
    except Exception:
        pass

    return f"PPT 已创建: {path}（共 {total} 页）"
