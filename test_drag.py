"""测试：拖拽文件到终端时，Textual 收到什么事件？"""

from textual.app import App, ComposeResult
from textual.widgets import Static, Input
from textual.containers import VerticalScroll
from textual.binding import Binding
from textual import events


class DebugInput(Input):

    def _on_paste(self, event) -> None:
        self.app.log_msg(f"[Input._on_paste] text={repr(event.text[:200]) if event.text else 'None'}")
        if event.text:
            self.insert_text_at_cursor(event.text)
        event.stop()
        event.prevent_default()

    def on_paste(self, event) -> None:
        self.app.log_msg(f"[Input.on_paste] text={repr(event.text[:200]) if event.text else 'None'}")


class TestApp(App):
    CSS = """
    Screen { layout: vertical; }
    #log { height: 1fr; }
    #input { height: 3; }
    """

    BINDINGS = [Binding("ctrl+c", "quit", "退出")]

    def compose(self) -> ComposeResult:
        yield VerticalScroll(Static("=== 拖拽文件到此终端，观察日志 ===\n按 Ctrl+V 粘贴路径也行\nCtrl+C 退出\n", id="messages"), id="log")
        yield DebugInput(placeholder="拖拽文件到这里...", id="input")

    def log_msg(self, text):
        container = self.query_one("#log", VerticalScroll)
        container.mount(Static(text))
        container.scroll_end(animate=False)

    def on_paste(self, event: events.Paste) -> None:
        self.log_msg(f"[App.on_paste] text={repr(event.text[:200]) if event.text else 'None'}")

    async def on_event(self, event: events.Event) -> None:
        await super().on_event(event)
        if isinstance(event, events.Paste):
            self.log_msg(f"[App.on_event Paste] text={repr(event.text[:200]) if event.text else 'None'}")


if __name__ == "__main__":
    TestApp().run()
