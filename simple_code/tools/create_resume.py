"""创建简历：AI 生成 HTML → Edge/Chrome/xhtml2pdf 转 PDF"""

import os

definition = {
    "type": "function",
    "function": {
        "name": "create_resume",
        "description": """创建专业简历 PDF。AI 根据用户信息和岗位 JD 生成 HTML 简历，自动转换为 PDF。

在调用此工具之前，必须通过对话收集足够信息：
- 用户的基本信息（姓名、联系方式）
- 工作经历 / 项目经历 / 教育背景
- 目标岗位的 JD（如果有）
- 旧简历内容（如果有，可通过拖拽文件或粘贴获取）

信息可以来自：旧简历、用户口述、岗位 JD，三者任意组合即可。

参数说明：
- path（必填）：输出文件路径，.pdf 结尾
- content（必填，除非传了 html_file）：用户的简历素材（经历、技能等原始信息，文本格式）
- job_description（可选）：目标岗位 JD，AI 会据此优化简历内容
- style（可选）：风格偏好，如"简约"、"专业"、"创意"等，默认"专业"
- html_file（可选）：已有的 HTML 简历文件路径，传了则跳过 AI 生成，直接转 PDF
- photo（可选）：一寸照片文件路径（jpg/png），会嵌入到简历右上角

两种用法：
1. 从素材生成：传 content → AI 生成 HTML → 转 PDF
2. 直接转换：传 html_file → 跳过 AI → 直接转 PDF""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "输出 .pdf 文件路径"},
                "content": {"type": "string", "description": "用户简历素材（经历、技能等）"},
                "job_description": {"type": "string", "description": "目标岗位 JD（可选）"},
                "style": {"type": "string", "description": "风格偏好（可选）"},
                "html_file": {"type": "string", "description": "已有的 HTML 文件路径，直接转 PDF"},
                "photo": {"type": "string", "description": "一寸照片路径（jpg/png）"},
            },
            "required": ["path"],
        },
    },
}


def label(args):
    return f"正在生成简历"


def _encode_photo(photo_path):
    """将照片转为 base64 data URI"""
    import base64
    ext = os.path.splitext(photo_path)[1].lower()
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}.get(ext, "image/jpeg")
    with open(photo_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{data}"


def execute(args, app=None, **kwargs):
    path = args["path"]
    html_file = args.get("html_file", "")
    photo = args.get("photo", "")

    # 确保输出目录存在
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # 模式1：直接转已有 HTML
    if html_file:
        if not os.path.exists(html_file):
            if app:
                app.finish_tool(success=False)
            return f"文件不存在: {html_file}"

        html_path = html_file
    else:
        # 模式2：AI 生成 HTML
        content = args.get("content", "")
        job_description = args.get("job_description", "")
        style = args.get("style", "专业")

        if not content:
            if app:
                app.finish_tool(success=False)
            return "缺少简历素材（content 参数）"

        if app:
            app.write_tool("正在生成简历 HTML")

        from openai import OpenAI
        from simple_code.config import get_provider

        provider = get_provider()
        client = OpenAI(api_key=provider["api_key"], base_url=provider["base_url"])

        has_photo = bool(photo and os.path.exists(photo))
        prompt = _build_prompt(content, job_description, style, has_photo)

        try:
            response = client.chat.completions.create(
                model=provider["model"],
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "请根据以上信息生成完整的 HTML 简历代码。只输出 HTML 代码，不要任何解释。"},
                ],
            )
            html = response.choices[0].message.content.strip()

            # 清理可能的 markdown 代码块包裹
            if html.startswith("```"):
                lines = html.split("\n")
                lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                html = "\n".join(lines)

        except Exception as e:
            if app:
                app.finish_tool(success=False)
            return f"AI 生成失败: {e}"

        # 嵌入照片
        if photo and os.path.exists(photo):
            try:
                data_uri = _encode_photo(photo)
                html = html.replace("{{PHOTO_DATA_URI}}", data_uri)
            except Exception:
                pass

        # 保存 HTML
        html_path = path.rsplit(".", 1)[0] + ".html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)

    # HTML → PDF
    if app:
        if html_file:
            # html_file 模式：没有"生成 HTML"步骤，直接显示转换
            app.write_tool("正在转换为 PDF")
        else:
            app.finish_tool(success=True)
            app.write_tool("正在转换为 PDF")

    pdf_ok = _html_to_pdf(html_path, path)
    if not pdf_ok:
        if app:
            app.finish_tool(success=False)
        return f"PDF 转换失败\nHTML 已保存到: {html_path}\n你可以在浏览器中打开 HTML，按 Ctrl+P 打印为 PDF。"

    if app:
        app.finish_tool(success=True)

    return f"简历已生成: {path}\nHTML 版本: {html_path}"


def _build_prompt(content, job_description, style, has_photo=False):
    """构建生成简历 HTML 的 prompt"""

    photo_section = ""
    if has_photo:
        photo_section = """
## 照片要求
- 在简历顶部右侧放置一寸照片
- 使用 <img> 标签，src 属性写 {{PHOTO_DATA_URI}}（程序会自动替换为实际图片）
- 照片尺寸：宽 90px，高 120px
- 照片和姓名/联系方式用 table 实现左右布局（姓名左边，照片右边）
"""

    jd_section = ""
    if job_description:
        jd_section = f"""
## 目标岗位 JD
{job_description}

请根据 JD 优化简历内容：
- 突出与岗位相关的经验和技能
- 使用 JD 中的关键词
- 优先展示最匹配的经历
- 但绝不伪造经验，只重新表述和强调
"""

    return f"""你是一个专业的简历设计师。请根据用户提供的信息生成一份完整的 HTML 简历。

## 用户简历素材
{content}

{jd_section}
{photo_section}
## 设计要求
- 风格：{style}
- 输出完整的 HTML 文件（包含 <!DOCTYPE html>、<html>、<head>、<body>）
- 所有样式用内联 CSS 或 <style> 标签，不依赖外部文件
- 字体使用 "SimSun", "Microsoft YaHei", sans-serif
- 页面宽度适合 A4 打印（210mm），合理设置 margin 和 padding
- 排版清晰专业，适合 HR 阅读
- 中文内容为主

## CSS 限制（重要！必须遵守）
- 禁止使用 flexbox（display: flex）
- 禁止使用 grid（display: grid）
- 布局只用 table 或普通 block/inline 元素
- 日期右对齐用 float: right 或 table 两列实现
- 只用基础 CSS：margin、padding、border、font-size、color、font-weight、text-align、width
- 不用 position: absolute/fixed
- body 背景必须是白色（#ffffff），不要灰色背景
- 不要 box-shadow、不要卡片式设计
- 简历直接铺满页面，不要居中的"纸张"容器
- 禁止使用任何 emoji 符号（如📞✉⚙等），全部用纯文字
- 联系方式直接写"电话：xxx"、"邮箱：xxx"，不要用图标代替文字
- 内容必须紧凑，确保在一页 A4 内完成，不要留大量空白
- 禁止设置 min-height（会导致 PDF 出现多余空白页）
- 技能标签不要加背景色，用纯文字列出即可
- body 的 padding 不要超过 15mm

## 简历内容规范

### 核心原则（FAB 模式）
- Feature（做了什么）→ Advantage（比别人好在哪）→ Benefit（给雇主带来什么价值）
- 提供论据而非论点，让数据说话，避免"学习能力强"等空话

### 模块顺序
1. 顶部：姓名 + 联系方式（手机/邮箱/微信等）
2. 求职意向（如果有 JD）
3. 工作经历（按时间倒序）
4. 项目经历（成果 + 量化数据）
5. 教育背景
6. 技能/证书/特长

### 经历描述规范（极其重要）
每段经历必须回答：我负责了什么 → 我的独特贡献 → 量化结果
- 必须有数字：业绩增长百分比、用户量、营收、成本降低、效率提升等
- 格式：「做了什么 → 采取什么方法/策略 → 达到什么效果（数字）」
- 技术岗示例：「设计 Redis 缓存方案，接口响应从 1200ms 降至 40ms」
- 运营岗示例：「策划618活动，单日 GMV 突破 500 万，同比增长 120%」
- 销售岗示例：「负责华东区大客户，年度签约金额 2000 万，超额完成 150%」
- 设计岗示例：「主导品牌视觉升级，官网转化率提升 35%」

### 禁忌
- 不要写主观自我评价（如"热爱学习"、"抗压能力强"、"团队精神"）
- 不要堆砌职责描述而无实际成果
- 不要写与目标岗位无关的经历
- 不要伪造数据和经验
- 如果用户提供的信息缺少数字，可以合理润色但不能编造

## 排版规范
- 整体控制在 1 页 A4 纸（经验丰富最多 2 页）
- 标题和正文层次分明
- 适当使用分割线区分模块
- 关键信息（公司名、职位、核心技能）加粗
- 日期右对齐，格式统一（YYYY.MM - YYYY.MM）
- 技能/证书按相关性排序，最匹配岗位的放前面

只输出 HTML 代码，不要解释。"""


def _html_to_pdf(html_path, pdf_path):
    """HTML 转 PDF：优先用 Edge/Chrome 命令行，fallback 到 xhtml2pdf"""
    import subprocess
    import shutil
    import tempfile

    # 转为绝对路径
    html_path = os.path.abspath(html_path)
    pdf_path = os.path.abspath(pdf_path)

    # 用临时文件避免中文路径问题
    temp_html = os.path.join(tempfile.gettempdir(), "_simple_resume.html")
    temp_pdf = os.path.join(tempfile.gettempdir(), "_simple_resume.pdf")
    shutil.copy2(html_path, temp_html)

    # 方案1：尝试 Edge（Windows 自带）
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for edge in edge_paths:
        if os.path.exists(edge):
            try:
                file_url = f"file:///{temp_html.replace(os.sep, '/')}"
                subprocess.run(
                    [edge, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                     f"--print-to-pdf={temp_pdf}", file_url],
                    capture_output=True, timeout=30
                )
                if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 0:
                    shutil.move(temp_pdf, pdf_path)
                    os.remove(temp_html)
                    return True
            except Exception:
                pass
            break

    # 方案2：尝试 Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    chrome = shutil.which("chrome") or shutil.which("google-chrome")
    if chrome:
        chrome_paths.insert(0, chrome)

    for chrome in chrome_paths:
        if os.path.exists(chrome):
            try:
                file_url = f"file:///{temp_html.replace(os.sep, '/')}"
                subprocess.run(
                    [chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                     f"--print-to-pdf={temp_pdf}", file_url],
                    capture_output=True, timeout=30
                )
                if os.path.exists(temp_pdf) and os.path.getsize(temp_pdf) > 0:
                    shutil.move(temp_pdf, pdf_path)
                    os.remove(temp_html)
                    return True
            except Exception:
                pass
            break

    # 清理临时文件
    if os.path.exists(temp_html):
        os.remove(temp_html)

    # 方案3：fallback 到 xhtml2pdf
    try:
        from xhtml2pdf import pisa
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        with open(pdf_path, "wb") as pdf_file:
            status = pisa.CreatePDF(html, dest=pdf_file)
        if not status.err:
            return True
    except Exception:
        pass

    return False
