"""Textual TUI 界面：仿 OpenCode 风格，固定底部输入框 + 可滚动聊天区"""

import os
import re
import time
import threading
import queue
from textual.app import App, ComposeResult
from textual.widgets import Input, OptionList
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.binding import Binding
from textual import work
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.box import Box

from simple_code.widgets import Static, StatusIndicator, PasteInput

HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".simple-code", "history.txt")
MAX_HISTORY = 50

# 自定义 Box：只显示左侧竖线
_LEFT_BAR_BOX = Box(
    "    \n"
    "▐   \n"
    "    \n"
    "▐   \n"
    "▐   \n"
    "    \n"
    "▐   \n"
    "    \n"
)


class SimpleApp(App):
    """simple 主界面 — VerticalScroll 聊天区 + 固定底部输入框"""

    AUTO_FOCUS = "#input-field"

    CSS = """
    Screen {
        layout: vertical;
        background: #000000;
    }

    #header-bar {
        height: 1;
        layout: horizontal;
        background: #111111;
    }

    #header-left {
        width: 1fr;
    }

    #header-right {
        width: auto;
    }

    #chat-view {
        height: 1fr;
        padding: 0 2;
        scrollbar-size: 1 1;
        scrollbar-color: #30363d;
        scrollbar-color-hover: #484f58;
    }

    #bottom-section {
        height: auto;
    }

    #status-bar {
        height: 1;
        layout: horizontal;
        background: #111111;
        padding: 0 2;
    }

    #status-left {
        width: 1fr;
    }

    #status-indicator {
        width: auto;
        min-width: 20;
    }

    #status-right {
        width: auto;
    }

    #slash-menu {
        display: none;
        height: auto;
        max-height: 8;
        background: #111111;
        color: #e6edf3;
        border: solid #30363d;
        padding: 0 1;
    }

    #slash-menu:focus {
        border: solid #30363d;
    }

    #input-area {
        height: auto;
        min-height: 3;
        max-height: 6;
        border-top: solid #30363d;
        border-bottom: solid #30363d;
        background: #000000;
        layout: horizontal;
    }

    #input-prompt {
        width: 3;
        padding: 0 0 0 1;
        color: #58a6ff;
        background: #000000;
    }

    #input-field {
        width: 1fr;
        height: auto;
        min-height: 1;
        max-height: 4;
        border: none;
        background: #000000;
        color: #ffffff;
        padding: 0;
    }

    #input-field:focus {
        border: none;
    }

    #input-field.confirm-mode {
        background: #000000;
        color: #ffffff;
    }

    #input-field.confirm-mode .text-area--cursor {
        color: transparent;
        background: transparent;
    }

    """

    BINDINGS = [
        Binding("escape", "interrupt", "中断", show=False),
        Binding("ctrl+c", "copy_or_quit", "复制/退出", show=False, priority=True),
        Binding("tab", "complete_slash", "补全", show=False),
        Binding("ctrl+v", "smart_paste", "粘贴", show=False, priority=True),
        Binding("pageup", "scroll_up_page", "上翻", show=False),
        Binding("pagedown", "scroll_down_page", "下翻", show=False),
    ]

    def __init__(self, on_submit=None):
        super().__init__()
        self._on_submit = on_submit
        self._start_time = 0
        self._last_ctrl_c = 0.0
        self._streaming_widget = None
        self._last_stream_time = 0.0
        self._inline_event = None
        self._inline_result = None
        self._mount_queue = queue.Queue()
        self._update_queue = queue.Queue()
        self._current_tool_widget = None
        self._current_tool_text = ""
        self._preparing_tool_widget = None
        self._tool_blink_active = False
        self._ppt_slides = None
        self._ppt_index = 0
        self._ppt_preview_widget = None
        self._history = []
        self._history_index = 0
        self._history_draft = ""
        self._paste_content = None
        self._in_confirm_mode = False
        self._confirm_event = None
        self._confirm_result = None
        self._confirm_options = []
        self._confirm_index = 0
        self.version = ""
        self.cwd = ""
        self.has_memory = False
        self.provider_name = "DeepSeek"
        self.model_name = "deepseek-chat"

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-bar"):
            yield Static("", id="header-left")
            yield Static("", id="header-right")
        yield VerticalScroll(id="chat-view")
        with Vertical(id="bottom-section"):
            yield OptionList(id="slash-menu")
            with Horizontal(id="status-bar"):
                yield StatusIndicator(id="status-indicator")
                yield Static("", id="status-left")
                yield Static("", id="status-right")
            with Horizontal(id="input-area"):
                yield Static("> ", id="input-prompt")
                yield PasteInput(placeholder="Ctrl+Enter 换行", id="input-field")

    def on_mount(self):
        self._chat_view = self.query_one("#chat-view", VerticalScroll)
        self._status_indicator = self.query_one("#status-indicator", StatusIndicator)
        self._header_left = self.query_one("#header-left", Static)
        self._status_left = self.query_one("#status-left", Static)
        self._status_right = self.query_one("#status-right", Static)

        self._header_right = self.query_one("#header-right", Static)
        self._header_right.update(Text("Ctrl+Enter换行 · ESC中断 · Ctrl+C×2退出 ", style="bold #ffffff"))
        self._status_right.update(Text(""))
        self._status_indicator.provider_name = self.provider_name
        self.update_header()
        self._load_history()

        # 欢迎消息
        self._chat_view.mount(Static(Text("")))
        self._chat_view.mount(Static(Text("  一款简单的终端助手", style="bold #ffffff")))
        self._chat_view.mount(Static(Text(
            f"  模型: {self.model_name}  ·  输入 /指南 查看帮助", style="bold #ffffff"
        )))
        if self.has_memory:
            self._chat_view.mount(Static(Text("  已加载 simple/ 记忆", style="bold #ffffff")))
        self._chat_view.mount(Static(Text("")))

        self.set_interval(0.05, self._flush_queues)

    # --- 输入历史 ---

    def _load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self._history = [l.strip() for l in f if l.strip()][-MAX_HISTORY:]
        except Exception:
            self._history = []
        self._history_index = len(self._history)

    def _save_history(self, text):
        if not text.strip() or text.startswith("/") or len(text) > 500:
            return
        if text in self._history:
            self._history.remove(text)
        self._history.append(text)
        if len(self._history) > MAX_HISTORY:
            self._history = self._history[-MAX_HISTORY:]
        self._history_index = len(self._history)
        self._history_draft = ""
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(self._history) + "\n")
        except Exception:
            pass

    def _history_up(self):
        if not self._history:
            return
        inp = self.query_one("#input-field", PasteInput)
        if self._history_index == len(self._history):
            self._history_draft = inp.value
        if self._history_index > 0:
            self._history_index -= 1
            inp.value = self._history[self._history_index]
            inp.cursor_position = len(inp.value)

    def _history_down(self):
        if not self._history:
            return
        inp = self.query_one("#input-field", PasteInput)
        if self._history_index < len(self._history):
            self._history_index += 1
            if self._history_index == len(self._history):
                inp.value = self._history_draft
            else:
                inp.value = self._history[self._history_index]
            inp.cursor_position = len(inp.value)

    def update_header(self):
        header = Text()
        header.append(" simple", style="bold #e6edf3")
        header.append(f"  v{self.version}  ·  ", style="#484f58")
        header.append(self.provider_name, style="bold #4D6BFE")
        header.append(f"  ·  {self.cwd}", style="#484f58")
        try:
            self.call_from_thread(self._header_left.update, header)
        except RuntimeError:
            self._header_left.update(header)
        self._status_indicator.provider_name = self.provider_name

    # --- 队列式渲染 ---

    def _flush_queues(self):
        mounts = []
        while True:
            try:
                mounts.append(self._mount_queue.get_nowait())
            except queue.Empty:
                break

        updates = []
        while True:
            try:
                updates.append(self._update_queue.get_nowait())
            except queue.Empty:
                break

        if not mounts and not updates:
            return

        at_bottom = (
            self._chat_view.max_scroll_y == 0
            or self._chat_view.scroll_y >= self._chat_view.max_scroll_y - 3
        )

        with self.batch_update():
            for w in mounts:
                self._chat_view.mount(w)
            for widget, content in updates:
                widget.update(content)
            if at_bottom and (mounts or updates):
                self._chat_view.scroll_end(animate=False)

    def _enqueue(self, *widgets):
        for w in widgets:
            self._mount_queue.put(w)

    def _enqueue_update(self, widget, content):
        self._update_queue.put((widget, content))

    # --- 输入处理 ---

    def on_input_submitted(self, event):
        # 确认模式：Enter = 提交选择
        if self._in_confirm_mode and self._confirm_event and not self._confirm_event.is_set():
            self._confirm_result["confirmed"] = (self._confirm_index == 1)  # 1 = 允许
            self._confirm_event.set()
            return

        menu = self.query_one("#slash-menu", OptionList)
        if menu.display and menu.highlighted is not None:
            option = menu.get_option_at_index(menu.highlighted)
            text = str(option.prompt).strip()
        else:
            text = event.value.strip()
        menu.display = False

        paste = self._paste_content
        self._paste_content = None
        event.input.value = ""

        # 交互式提问
        if self._inline_event and not self._inline_event.is_set():
            if self._inline_result is not None:
                self._inline_result["answer"] = text if text else "(用户未输入内容)"
            self._inline_event.set()
            return

        # 粘贴摘要还原
        if paste:
            additional = re.sub(r'\[已粘贴 ~\d+ 行\]\s*', '', text).strip()
            text = paste + "\n\n" + additional if additional else paste

        if not text:
            return

        self._save_history(text)
        if self._on_submit:
            self._on_submit(text)

    # --- 斜杠菜单 ---

    def _get_slash_commands(self):
        from simple_code.config import load_skills
        commands = ["/指南", "/模型"]
        commands.extend(f"/{name}" for name in sorted(load_skills()))
        return commands

    def on_input_changed(self, event: Input.Changed):
        if event.input.id != "input-field":
            return
        if self._paste_content and "[已粘贴" not in event.value:
            self._paste_content = None

        menu = self.query_one("#slash-menu", OptionList)
        value = event.value
        if value.startswith("/"):
            all_cmds = self._get_slash_commands()
            matches = [c for c in all_cmds if c.startswith(value) and c != value]
            if matches:
                menu.clear_options()
                for m in matches:
                    menu.add_option(m)
                menu.highlighted = 0
                menu.display = True
                return
        menu.display = False

    def on_key(self, event):
        # PPT 预览翻页
        if self._ppt_slides and self._ppt_preview_widget:
            if event.key == "left":
                if self._ppt_index > 0:
                    self._ppt_index -= 1
                    self._enqueue_update(self._ppt_preview_widget, self._render_slide(self._ppt_index))
                event.prevent_default()
                return
            elif event.key == "right":
                if self._ppt_index < len(self._ppt_slides) - 1:
                    self._ppt_index += 1
                    self._enqueue_update(self._ppt_preview_widget, self._render_slide(self._ppt_index))
                event.prevent_default()
                return

        menu = self.query_one("#slash-menu", OptionList)
        if menu.display:
            if event.key == "up":
                if menu.highlighted is not None and menu.highlighted > 0:
                    menu.highlighted -= 1
            elif event.key == "down":
                if menu.highlighted is not None and menu.highlighted < menu.option_count - 1:
                    menu.highlighted += 1
            return

        if event.key == "up":
            self._history_up()
            event.prevent_default()
        elif event.key == "down":
            self._history_down()
            event.prevent_default()

    def action_complete_slash(self):
        menu = self.query_one("#slash-menu", OptionList)
        if not menu.display:
            return
        self._accept_slash_option()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        inp = self.query_one("#input-field", PasteInput)
        inp.value = str(event.option.prompt)
        inp.cursor_position = len(inp.value)
        self.query_one("#slash-menu", OptionList).display = False
        inp.focus()

    def _accept_slash_option(self):
        menu = self.query_one("#slash-menu", OptionList)
        if menu.highlighted is not None:
            option = menu.get_option_at_index(menu.highlighted)
            inp = self.query_one("#input-field", PasteInput)
            inp.value = str(option.prompt)
            inp.cursor_position = len(inp.value)
        menu.display = False
        self.query_one("#input-field", PasteInput).focus()

    # --- 点击时保持输入框焦点 ---

    def on_click(self, event):
        """任何点击都把焦点还给输入框，确保拖拽文件等操作正常"""
        self.query_one("#input-field", PasteInput).focus()

    # --- 键盘动作 ---

    def action_interrupt(self):
        from simple_code import state
        state.interrupt.set()
        if self._inline_event and not self._inline_event.is_set():
            if self._inline_result is not None:
                self._inline_result["answer"] = "(用户取消)"
            self._inline_event.set()

    def action_scroll_up_page(self):
        self._chat_view.scroll_page_up(animate=False)

    def action_scroll_down_page(self):
        self._chat_view.scroll_page_down(animate=False)

    def action_smart_paste(self):
        try:
            import pyperclip
            content = pyperclip.paste()
            if content:
                self._handle_paste_content(content)
        except Exception:
            pass


    def _handle_paste_content(self, content):
        inp = self.query_one("#input-field", PasteInput)
        lines = content.count('\n') + 1

        if lines < 3 and len(content) <= 150:
            pos = inp.cursor_position
            inp.value = inp.value[:pos] + content + inp.value[pos:]
            inp.cursor_position = pos + len(content)
        else:
            self._paste_content = content
            existing = inp.value.strip()
            summary = f"[已粘贴 ~{lines} 行] "
            if existing:
                inp.value = existing + " " + summary
            else:
                inp.value = summary
            inp.cursor_position = len(inp.value)

    def action_copy_or_quit(self):
        selected = self.screen.get_selected_text()
        if selected:
            self.copy_to_clipboard(selected)
            self.screen.clear_selection()
            return
        now = time.time()
        if now - self._last_ctrl_c < 2:
            self.exit()
            return
        self._last_ctrl_c = now
        self._chat_view.mount(Static(Text("  再按一次 Ctrl+C 退出", style="#8b949e")))
        self._chat_view.scroll_end(animate=False)

    # --- 公开接口（全部走队列）---

    def write_user(self, text):
        display = text if len(text) <= 300 else text[:300] + "..."
        panel = Panel(
            Text(display, style="bold #ffffff"),
            border_style="#58a6ff",
            box=_LEFT_BAR_BOX,
            padding=(0, 1),
            style="on #2a2a2a",
            expand=True,
        )
        self._enqueue(Static(Text("")), Static(panel))

    def write_assistant(self, markdown_text):
        self._enqueue(Static(Text("")), Static(Markdown(markdown_text)))

    def write_assistant_footer(self, elapsed):
        footer = Text()
        footer.append("  ◻ ", style="#30363d")
        footer.append("simple", style="bold #8b949e")
        footer.append(f" · {self.model_name} · {elapsed}s", style="#484f58")
        self._enqueue(Static(footer))

    def write_system(self, text):
        self._enqueue(Static(Text(f"  {text}", style="#8b949e")))

    def write_warning(self, text):
        self._enqueue(Static(Text(f"  {text}", style="bold #f85149")))

    _TOOL_NAME_MAP = {
        "edit_file": "正在编辑",
        "write_file": "正在写入",
        "read_file": "正在读取",
        "run_command": "正在执行",
        "glob_files": "正在搜索文件",
        "grep_files": "正在搜索内容",
        "web_search": "正在搜索",
        "web_fetch": "正在阅读",
        "create_ppt": "正在设计 PPT 结构",
        "create_skill": "创建 Skill",
        "ask_user": "等待用户回答",
        "task_list": "任务清单",
        "read_clipboard": "正在读取剪贴板",
    }

    def write_tool_preparing(self, tool_name):
        # 如果上一个 preparing 还没被消耗，跳过（等实际执行时再显示）
        if self._preparing_tool_widget:
            return

        display = self._TOOL_NAME_MAP.get(tool_name, tool_name)
        msg = Text()
        msg.append(display, style="bold white")
        msg.append("...", style="#8b949e")
        w = Static(msg)
        self._preparing_tool_widget = w
        self._enqueue(w)

    def write_tool(self, text):
        # 停止上一个工具的闪烁
        self._tool_blink_active = False

        msg = Text()
        parts = text.split(" ", 1)
        msg.append(parts[0], style="bold white")
        if len(parts) > 1:
            msg.append(" " + parts[1], style="#8b949e")

        if self._preparing_tool_widget:
            w = self._preparing_tool_widget
            self._enqueue_update(w, msg)
            self._preparing_tool_widget = None
        elif self._current_tool_widget:
            w = self._current_tool_widget
            self._enqueue_update(w, msg)
        else:
            w = Static(msg)
            self._enqueue(w)

        self._current_tool_widget = w
        self._current_tool_text = text

        # 启动闪烁
        self._tool_blink_active = True
        self._start_tool_blink()

    @work(thread=True)
    def _start_tool_blink(self):
        """2秒后开始闪烁当前工具状态行"""
        import time as _time
        # 捕获启动时的 widget 引用，避免竞态
        target_widget = self._current_tool_widget
        target_text = self._current_tool_text
        _time.sleep(2)
        dots = 0
        while self._tool_blink_active and self._current_tool_widget is target_widget:
            if not target_widget or not target_text:
                break
            dots = (dots + 1) % 4
            suffix = "." * dots + " " * (3 - dots)
            msg = Text()
            parts = target_text.split(" ", 1)
            msg.append(parts[0], style="bold white")
            if len(parts) > 1:
                msg.append(" " + parts[1], style="#8b949e")
            msg.append(f" {suffix}", style="#8b949e")
            self._enqueue_update(target_widget, msg)
            _time.sleep(0.5)

    def finish_tool(self, success=True):
        self._tool_blink_active = False
        w = self._current_tool_widget
        if not w:
            return
        text = self._current_tool_text
        msg = Text()
        parts = text.split(" ", 1)
        color = "bold #00cc66" if success else "bold #ff4444"
        msg.append(parts[0], style=color)
        if len(parts) > 1:
            msg.append(" " + parts[1], style="#8b949e")
        self._enqueue_update(w, msg)
        self._current_tool_widget = None

    def write_code(self, renderable):
        self._enqueue(Static(renderable))

    def write_diff(self, old_text, new_text):
        table = Table(
            show_header=False, show_edge=False, box=None,
            pad_edge=False, expand=True, padding=(0, 1),
        )
        table.add_column("new", ratio=1, style="#00cc66")
        table.add_column("old", ratio=1, style="#ff4444")
        new_lines = new_text.splitlines()
        old_lines = old_text.splitlines()
        for i in range(max(len(old_lines), len(new_lines))):
            new_line = f"+ {new_lines[i]}" if i < len(new_lines) else "+"
            old_line = f"- {old_lines[i]}" if i < len(old_lines) else "-"
            table.add_row(new_line, old_line)
        self._enqueue(Static(table))

    # --- 流式输出 ---

    def begin_response(self):
        w = Static("")
        self._streaming_widget = w
        self._last_stream_time = 0.0
        self._enqueue(Static(Text("")), w)

    def stream_chunk(self, accumulated_text):
        if not self._streaming_widget:
            return
        now = time.time()
        if now - self._last_stream_time < 0.05:
            return
        self._last_stream_time = now
        self._enqueue_update(self._streaming_widget, Markdown(accumulated_text))

    def end_response(self, final_text=""):
        if self._streaming_widget and final_text:
            def _do():
                with self.batch_update():
                    self._streaming_widget.update(Markdown(final_text))
                    self._chat_view.scroll_end(animate=False)
            try:
                self.call_from_thread(_do)
            except Exception:
                self._enqueue_update(self._streaming_widget, Markdown(final_text))
        self._streaming_widget = None

    # --- PPT 预览 ---

    def _render_slide(self, index):
        slide = self._ppt_slides[index]
        total = len(self._ppt_slides)
        layout = slide.get("layout", "content")
        layout_name = {"title": "封面", "section": "章节", "content": "内容"}.get(layout, layout)

        content = Text()
        content.append(slide.get("title", ""), style="bold #ffffff")
        if slide.get("subtitle"):
            content.append(f"\n{slide['subtitle']}", style="#8b949e")
        if slide.get("bullets"):
            content.append("\n")
            for b in slide["bullets"]:
                content.append(f"\n  ● {b}", style="#e6edf3")
        if slide.get("notes"):
            content.append(f"\n\n讲稿: {slide['notes']}", style="dim")

        return Panel(
            content,
            title=f"第 {index + 1}/{total} 页 · {layout_name}",
            border_style="#FF8C00",
            padding=(1, 2),
        )

    def preview_ppt(self, slides_data):
        self._ppt_slides = slides_data
        self._ppt_index = 0

        widget = Static(self._render_slide(0))
        self._ppt_preview_widget = widget
        self._enqueue(Static(Text("")), widget)
        self._enqueue(Static(Text(
            "  ◀ ▶ 翻页  ·  输入修改意见  ·  直接回车确认生成", style="#8b949e"
        )))

        event = threading.Event()
        result = {"answer": ""}
        self._inline_event = event
        self._inline_result = result
        event.wait()

        self._ppt_slides = None
        self._ppt_preview_widget = None
        return result["answer"]

    def request_user_input(self, question):
        event = threading.Event()
        result = {"answer": ""}
        self._inline_event = event
        self._inline_result = result
        is_danger = "危险命令" in question or "删除" in question
        color = "bold #ff4444" if is_danger else "bold yellow"
        self._enqueue(Static(Text(question, style=color)))
        event.wait()
        return result["answer"]

    def request_danger_confirm(self, command):
        event = threading.Event()
        result = {"confirmed": False}
        self._confirm_event = event
        self._confirm_result = result
        self._confirm_options = ["拒绝", "允许"]
        self._confirm_index = 0  # 默认选中"拒绝"

        # 把命令转成用户能懂的描述
        import re
        cmd_lower = command.lower()
        if re.search(r'\brm\b|\bdel\b|\brd\b|\brmdir\b', cmd_lower):
            # 提取文件名
            parts = re.findall(r'"([^"]+)"|(\S+)', command)
            names = [p[0] or p[1] for p in parts if not re.match(r'^(rm|del|rd|rmdir|/[sqf]|-rf?)', p[0] or p[1], re.I)]
            import os
            names = [os.path.basename(n) for n in names if n]
            desc = "即将删除: " + "、".join(names) if names else "即将删除文件"
        elif "format" in cmd_lower:
            desc = "即将格式化磁盘（危险操作）"
        elif re.search(r'\bdrop\b|\btruncate\b', cmd_lower):
            desc = "即将删除数据库数据（危险操作）"
        else:
            desc = "即将执行可能有风险的操作"

        self._enqueue(Static(Text(desc, style="bold #ff4444")))

        # 把输入框变成上下选择列表
        def setup_confirm():
            inp = self.query_one("#input-field", PasteInput)
            inp.read_only = True
            inp.show_line_numbers = False
            inp.cursor_blink = False
            # 隐藏光标：移到不可见位置
            inp.add_class("confirm-mode")
            self._in_confirm_mode = True
            self._update_confirm_display()

        self.call_from_thread(setup_confirm)
        event.wait()

        # 先同步清除确认状态（防止下一次 request 进来时状态错乱）
        self._in_confirm_mode = False
        confirmed = result["confirmed"]

        # 恢复输入框
        def restore_input():
            inp = self.query_one("#input-field", PasteInput)
            inp.read_only = False
            inp.cursor_blink = True
            inp.remove_class("confirm-mode")
            inp.value = ""

        self.call_from_thread(restore_input)
        return confirmed

    def _update_confirm_display(self):
        """更新确认选择列表（上下排列）"""
        inp = self.query_one("#input-field", PasteInput)
        idx = self._confirm_index
        line0 = "❯ 拒绝" if idx == 0 else "  拒绝"
        line1 = "❯ 允许" if idx == 1 else "  允许"
        inp.value = f"{line0}\n{line1}"

    # --- 状态控制 ---

    def start_thinking(self):
        self._start_time = time.time()
        self._status_indicator.thinking = True
        self._update_timer()

    def stop_thinking(self):
        self._status_indicator.thinking = False

    def update_tokens(self, round_tokens, total_tokens):
        self._status_indicator.round_tokens = round_tokens
        self._status_indicator.total_tokens = total_tokens

    def show_stats(self, elapsed, round_k, total_k):
        self._enqueue_update(
            self._status_left,
            Text(f" {round_k} · 累计 {total_k}", style="#484f58")
        )
        self.write_assistant_footer(elapsed)

    @work(thread=True)
    def _update_timer(self):
        while self._status_indicator.thinking:
            self._status_indicator.elapsed = int(time.time() - self._start_time)
            time.sleep(1)
