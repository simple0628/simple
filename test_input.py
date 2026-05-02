"""测试多行输入框"""
from textual.app import App, ComposeResult
from textual.widgets import Static, TextArea
from rich.text import Text


class TestInput(TextArea):
    """测试用输入框"""

    async def _on_key(self, event) -> None:
        # 打印所有按键，方便调试
        self.app.query_one("#log", Static).update(
            Text(f"按键: key={event.key!r} character={event.character!r}")
        )

        if event.key in ("ctrl+enter", "ctrl+j"):
            event.stop()
            event.prevent_default()
            start, end = self.selection
            self._replace_via_keyboard("\n", start, end)
            return

        if event.key == "enter":
            event.stop()
            event.prevent_default()
            self.app.query_one("#output", Static).update(
                Text(f"提交内容: {self.text!r}")
            )
            self.clear()
            return

        await super()._on_key(event)


class TestApp(App):
    CSS = """
    #input {
        height: auto;
        min-height: 1;
        max-height: 5;
        border: solid green;
        background: #111111;
    }
    #log {
        height: 1;
        color: yellow;
    }
    #output {
        height: 3;
        color: cyan;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Enter=提交  Ctrl+Enter=换行  测试输入框：", id="title")
        yield TestInput(id="input")
        yield Static("", id="log")
        yield Static("", id="output")


if __name__ == "__main__":
    TestApp().run()
