"""创建简历：AI 生成 HTML → weasyprint 转 PDF"""

import os
import json

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
- content（必填）：用户的简历素材（经历、技能等原始信息，文本格式）
- job_description（可选）：目标岗位 JD，AI 会据此优化简历内容
- style（可选）：风格偏好，如"简约"、"专业"、"创意"等，默认"专业"

工具会调用 AI 生成完整 HTML 简历并转为 PDF。""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "输出 .pdf 文件路径"},
                "content": {"type": "string", "description": "用户简历素材（经历、技能等）"},
                "job_description": {"type": "string", "description": "目标岗位 JD（可选）"},
                "style": {"type": "string", "description": "风格偏好（可选）"},
            },
            "required": ["path", "content"],
        },
    },
}


def label(args):
    return f"正在生成简历: {args.get('path', '')}"


def execute(args, app=None, **kwargs):
    path = args["path"]
    content = args["content"]
    job_description = args.get("job_description", "")
    style = args.get("style", "专业")

    # 确保输出目录存在
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # 调 AI 生成 HTML 简历
    if app:
        app.finish_tool(success=True)
        app.write_tool("正在生成简历 HTML")

    from openai import OpenAI
    from simple_code.config import get_provider

    provider = get_provider()
    client = OpenAI(api_key=provider["api_key"], base_url=provider["base_url"])

    prompt = _build_prompt(content, job_description, style)

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
            # 去掉首行 ```html 和末行 ```
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            html = "\n".join(lines)

    except Exception as e:
        if app:
            app.finish_tool(success=False)
        return f"AI 生成失败: {e}"

    # 保存 HTML（调试用，和 PDF 同名）
    html_path = path.rsplit(".", 1)[0] + ".html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # HTML → PDF
    if app:
        app.write_tool("正在转换为 PDF")

    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(path)
    except ImportError:
        if app:
            app.finish_tool(success=False)
        return (
            f"PDF 转换需要 weasyprint 库，请运行以下命令安装：\n"
            f"  pip install weasyprint\n\n"
            f"HTML 简历已保存到: {html_path}\n"
            f"你可以在浏览器中打开 HTML，按 Ctrl+P 打印为 PDF。"
        )
    except Exception as e:
        if app:
            app.finish_tool(success=False)
        return f"PDF 转换失败: {e}\nHTML 已保存到: {html_path}\n你可以在浏览器中打开 HTML，按 Ctrl+P 打印为 PDF。"

    if app:
        app.finish_tool(success=True)

    return f"简历已生成: {path}\nHTML 版本: {html_path}"


def _build_prompt(content, job_description, style):
    """构建生成简历 HTML 的 prompt"""

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

## 设计要求
- 风格：{style}
- 输出完整的 HTML 文件（包含 <!DOCTYPE html>、<html>、<head>、<body>）
- 所有样式用内联 CSS 或 <style> 标签，不依赖外部文件
- 字体使用 "Microsoft YaHei", "SimHei", sans-serif
- 页面宽度适合 A4 打印（210mm），合理设置 margin 和 padding
- 排版清晰专业，适合 HR 阅读
- 中文内容为主

## 简历结构建议
- 顶部：姓名 + 联系方式（手机/邮箱/GitHub 等）
- 求职意向（如果有 JD）
- 工作经历（倒序，突出成果和数字）
- 项目经历（技术栈 + 成果）
- 教育背景
- 技能清单

## 排版规范
- 标题和正文层次分明
- 适当使用分割线
- 关键信息加粗
- 日期右对齐
- 整体控制在 1-2 页 A4 纸

只输出 HTML 代码，不要解释。"""
