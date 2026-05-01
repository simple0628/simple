import requests
from bs4 import BeautifulSoup

definition = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": """联网搜索，通过国内搜索引擎（百度、搜狗、360）查询信息，返回相关网页的标题、链接和摘要。
自动尝试多个搜索引擎，确保返回结果。

参数说明：
- keyword（必填）：搜索关键词，例如 "Python Flask 教程" 或 "asyncio 用法"

适用场景：查找技术文档、解决报错、了解最新信息等""",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "搜索关键词"}
            },
            "required": ["keyword"]
        }
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def label(args):
    return f"正在搜索 \"{args.get('keyword', '')}\""

def _search_baidu(keyword):
    url = f"https://www.baidu.com/s?wd={requests.utils.quote(keyword)}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for item in soup.select(".result.c-container")[:5]:
        title_tag = item.select_one("h3 a")
        snippet_tag = item.select_one(".c-abstract") or item.select_one(".content-right_2s-H4")
        if title_tag:
            results.append({
                "title": title_tag.get_text(strip=True),
                "href": title_tag.get("href", ""),
                "snippet": snippet_tag.get_text(strip=True) if snippet_tag else ""
            })
    return results

def _search_sogou(keyword):
    url = f"https://www.sogou.com/web?query={requests.utils.quote(keyword)}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for item in soup.select(".vrwrap, .rb")[:5]:
        title_tag = item.select_one("h3 a") or item.select_one("a")
        snippet_tag = item.select_one(".str-text-info") or item.select_one(".space-txt")
        if title_tag:
            results.append({
                "title": title_tag.get_text(strip=True),
                "href": title_tag.get("href", ""),
                "snippet": snippet_tag.get_text(strip=True) if snippet_tag else ""
            })
    return results

def _search_360(keyword):
    url = f"https://www.so.com/s?q={requests.utils.quote(keyword)}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for item in soup.select("li.res-list")[:5]:
        title_tag = item.select_one("h3 a")
        snippet_tag = item.select_one(".res-desc")
        if title_tag:
            results.append({
                "title": title_tag.get_text(strip=True),
                "href": title_tag.get("href", ""),
                "snippet": snippet_tag.get_text(strip=True) if snippet_tag else ""
            })
    return results

ENGINES = [
    ("百度", _search_baidu),
    ("搜狗", _search_sogou),
    ("360", _search_360),
]

def execute(args, **kwargs):
    keyword = args["keyword"]

    for engine_name, search_fn in ENGINES:
        try:
            results = search_fn(keyword)
            if results:
                output = [f"[来源: {engine_name}]\n"]
                for i, r in enumerate(results, 1):
                    output.append(f"{i}. {r['title']}\n   {r['href']}\n   {r['snippet']}")
                return "\n\n".join(output)
        except Exception:
            continue

    return f"所有搜索引擎均未找到关于 \"{keyword}\" 的结果"
