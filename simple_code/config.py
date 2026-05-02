"""配置管理：API Key、首次引导、Skill 加载"""

import os
import json

from openai import OpenAI

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".simple-code")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
SKILLS_DIR = os.path.join(CONFIG_DIR, "skills")

# --- 模型定义 ---

PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
        "key_url": "https://platform.deepseek.com/api_keys",
    },
}

DISCLAIMER = """[bold white]欢迎使用 simple[/bold white]

在开始之前，请仔细阅读以下免责声明：

[yellow]1. AI 生成内容的局限性[/yellow]
   simple 由大语言模型驱动，AI 可能会生成错误的、不完整的、
   或具有误导性的代码和建议。你不应将其输出视为专业建议。

[yellow]2. 文件操作风险[/yellow]
   simple 具有读取、创建、修改和删除文件的能力，也可以执行终端命令。
   这些操作可能导致数据丢失或系统损坏。请确保重要文件已备份。

[yellow]3. 命令执行风险[/yellow]
   虽然危险命令会在执行前要求确认，但 AI 仍可能通过间接方式
   执行你意料之外的操作。你有责任审查 AI 建议的每一条命令。

[yellow]4. 数据隐私[/yellow]
   你的对话内容、文件内容和命令输出会被发送到第三方 API 进行处理。
   请勿输入密码、密钥、个人身份信息等敏感数据。simple 的开发者
   不对第三方 API 的数据处理方式承担责任。

[yellow]5. 免责条款[/yellow]
   simple 按"原样"提供，不附带任何明示或暗示的保证，包括但不限于
   对适销性、特定用途适用性和非侵权性的保证。在任何情况下，
   simple 的开发者均不对因使用或无法使用本工具而产生的任何直接、
   间接、附带、特殊或后果性损害承担责任。

[yellow]6. 合法使用[/yellow]
   你应确保使用 simple 的行为符合当地法律法规。不得利用本工具
   生成违法内容、恶意代码或进行任何违反法律的活动。

[yellow]7. 用户责任[/yellow]
   使用 simple 即表示你理解并接受上述风险。你有责任审查 AI 的
   所有输出，并对采纳其建议后产生的任何后果自行承担全部责任。

[dim]按回车键表示你已阅读、理解并同意以上全部内容...[/dim]"""


# --- 配置读写 ---

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config):
    """保存配置文件"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def _migrate_old_config(config):
    """兼容旧格式：{"api_key": "xxx"} → providers 格式"""
    if "api_key" in config and "providers" not in config:
        new_config = {
            "current": "deepseek",
            "providers": {
                "deepseek": {"api_key": config["api_key"]}
            }
        }
        save_config(new_config)
        return new_config
    return config


# --- API Key 管理 ---

def get_provider():
    """获取当前模型配置，返回 dict"""
    config = _migrate_old_config(load_config())
    current_id = config.get("current", "deepseek")
    if current_id not in PROVIDERS:
        current_id = "deepseek"

    providers_data = config.get("providers", {})
    api_key = providers_data.get(current_id, {}).get("api_key", "")
    info = PROVIDERS[current_id]

    return {
        "id": current_id,
        "name": info["name"],
        "base_url": info["base_url"],
        "model": info["model"],
        "api_key": api_key,
        "key_url": info["key_url"],
    }


def set_provider_key(provider_id, api_key):
    """设置 API Key"""
    config = _migrate_old_config(load_config())
    if "providers" not in config:
        config["providers"] = {}
    if provider_id not in config["providers"]:
        config["providers"][provider_id] = {}
    config["providers"][provider_id]["api_key"] = api_key
    save_config(config)


def test_provider_key(provider_id, api_key):
    """测试 API Key 是否可用"""
    if provider_id not in PROVIDERS:
        return False
    info = PROVIDERS[provider_id]
    try:
        client = OpenAI(api_key=api_key, base_url=info["base_url"])
        client.chat.completions.create(
            model=info["model"],
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=1
        )
        return True
    except Exception:
        return False


# --- 首次启动（TUI 界面）---

def first_run_setup():
    """首次启动引导：TUI 界面显示免责声明 + 获取 API Key"""
    from textual.app import App, ComposeResult
    from textual.containers import Vertical, VerticalScroll
    from textual.widgets import Static as _Static, Input
    from textual.binding import Binding
    from rich.text import Text

    result = {"api_key": ""}

    class SetupApp(App):
        CSS = """
        Screen {
            background: #000000;
        }
        #disclaimer {
            height: 1fr;
            padding: 1 2;
            background: #000000;
            scrollbar-size: 0 0;
        }
        #disclaimer Static {
            color: #ffffff;
        }
        #bottom-bar {
            height: 3;
            padding: 0 2;
            background: #111111;
        }
        #status {
            height: 1;
            padding: 0 2;
            color: #888888;
        }
        #key-input {
            background: #111111;
            border: none;
        }
        #key-input:focus {
            border: none;
        }
        """

        BINDINGS = [
            Binding("escape", "quit", "退出"),
            Binding("ctrl+c", "quit", "退出", show=False),
        ]

        def __init__(self):
            super().__init__()
            self._phase = "disclaimer"  # disclaimer → input → verifying

        def compose(self) -> ComposeResult:
            with VerticalScroll(id="disclaimer"):
                yield _Static(Text.from_markup(DISCLAIMER))
            with Vertical(id="bottom-bar"):
                yield _Static("", id="status")
                yield Input(placeholder="按回车继续...", id="key-input")

        def on_mount(self):
            self.query_one("#key-input", Input).focus()

        def on_input_submitted(self, event: Input.Submitted):
            inp = self.query_one("#key-input", Input)
            status = self.query_one("#status", _Static)

            if self._phase == "disclaimer":
                # 进入 API Key 输入阶段
                self._phase = "input"
                self.query_one("#disclaimer ._Static", _Static).update(
                    Text.from_markup(
                        "[bold white]配置 DeepSeek API Key[/bold white]\n\n"
                        "[dim]获取地址: https://platform.deepseek.com/api_keys[/dim]\n\n"
                        "[dim]输入后按回车验证[/dim]"
                    )
                ) if False else None
                status.update(Text.from_markup("[bold #ffffff]请在下方输入 API Key，获取地址: https://platform.deepseek.com/api_keys[/bold #ffffff]"))
                inp.placeholder = "请输入 API Key..."
                inp.password = True
                inp.value = ""
                return

            if self._phase == "input":
                api_key = inp.value.strip()
                if not api_key:
                    status.update("[red]API Key 不能为空[/red]")
                    return

                # 验证
                self._phase = "verifying"
                status.update("正在验证...")
                inp.disabled = True

                import threading
                def verify():
                    success = test_provider_key("deepseek", api_key)
                    self.call_from_thread(self._on_verify_result, success, api_key)

                threading.Thread(target=verify, daemon=True).start()

        def _on_verify_result(self, success, api_key):
            inp = self.query_one("#key-input", Input)
            status = self.query_one("#status", _Static)

            if success:
                result["api_key"] = api_key
                save_config({
                    "current": "deepseek",
                    "providers": {"deepseek": {"api_key": api_key}}
                })
                self.exit()
            else:
                self._phase = "input"
                status.update("[red]验证失败，请检查 API Key 是否正确[/red]")
                inp.value = ""
                inp.disabled = False
                inp.focus()

    app = SetupApp()
    app.run()

    if not result["api_key"]:
        # 用户按 ESC 退出，没有配置
        import sys
        sys.exit(0)

    return result["api_key"]


# --- Skill 管理 ---

def load_skills():
    """加载所有自定义 skill，返回 {名称: 内容} 字典"""
    skills = {}
    if not os.path.exists(SKILLS_DIR):
        os.makedirs(SKILLS_DIR, exist_ok=True)
        return skills
    for filename in os.listdir(SKILLS_DIR):
        if filename.endswith(".md"):
            name = filename[:-3]
            filepath = os.path.join(SKILLS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                skills[name] = f.read().strip()
    return skills
