import requests
from bs4 import BeautifulSoup

definition = {
    "type": "function",
    "function": {
        "name": "web_fetch",
        "description": """抓取指定网页的正文内容。用于读取搜索结果中的具体页面、技术文档、API参考等。

参数说明：
- url（必填）：要抓取的网页完整地址，例如 "https://docs.python.org/3/library/json.html"

返回值：网页的正文文本内容（已去除导航栏、广告等干扰元素）""",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "要抓取的网页URL"}
            },
            "required": ["url"]
        }
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 需要去掉的干扰标签
REMOVE_TAGS = ["script", "style", "nav", "header", "footer", "iframe", "noscript", "aside"]

MAX_LENGTH = 8000  # 最多返回的字符数


def label(args):
    url = args.get("url", "")
    if len(url) > 60:
        url = url[:60] + "..."
    return f"正在阅读 {url}"


def execute(args, **kwargs):
    url = args["url"]
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = resp.apparent_encoding or "utf-8"
    except Exception as e:
        return f"请求失败: {e}"

    soup = BeautifulSoup(resp.text, "html.parser")

    # 移除干扰标签
    for tag in REMOVE_TAGS:
        for el in soup.find_all(tag):
            el.decompose()

    # 优先取 article 或 main 标签
    main = soup.find("article") or soup.find("main") or soup.find("body")
    if not main:
        return "无法解析页面内容"

    text = main.get_text(separator="\n", strip=True)

    # 合并连续空行
    lines = []
    for line in text.split("\n"):
        line = line.strip()
        if line or (lines and lines[-1]):
            lines.append(line)

    result = "\n".join(lines)

    if len(result) > MAX_LENGTH:
        result = result[:MAX_LENGTH] + f"\n\n... (内容已截断，共 {len(result)} 字符)"

    return result if result.strip() else "页面内容为空"
