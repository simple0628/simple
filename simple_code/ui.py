"""Textual TUI 界面：仿 OpenCode 风格，固定底部输入框 + 可滚动聊天区"""

import os
import re
import time
import threading
import queue
from textual.app import App, ComposeResult
from textual.widgets import Static as _BaseStatic, Input, OptionList
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.binding import Binding
from textual.strip import Strip
from textual.content import Content
from textual import work
from rich.text import Text
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.box import Box
from rich.segment import Segment
from rich.style import Style as RichStyle

HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".simple-code", "history.txt")


_SEL_STYLE = RichStyle(bgcolor="dark_cyan")


class SelectableStatic(_BaseStatic):
    """支持文字选中的 Static widget（含 Panel/Markdown 高亮 + 文字提取）"""

    def render_line(self, y):
        strip = super().render_line(y)
        strip = strip.apply_offsets(0, y)

        # 对 Panel/Markdown 等非 Text/Content，手动渲染选中高亮
        sel = self.text_selection
        if sel is not None and sel.start is not None and sel.end is not None:
            visual = self._render()
            if not isinstance(visual, (Text, Content)):
                strip = self._apply_highlight(strip, y, sel)

        return strip

    def _apply_highlight(self, strip, y, sel):
        """给指定行的选中范围添加高亮背景"""
        start, end = sel.start, sel.end
        if (start.y, start.x) > (end.y, end.x):
            start, end = end, start
        if not (start.y <= y <= end.y):
            return strip

        line_start = start.x if y == start.y else 0
        line_end = end.x if y == end.y else 999999

        new_segs = []
        x = 0
        for seg in strip._segments:
            seg_len = len(seg.text)
            if seg_len > 0 and x < line_end and x + seg_len > line_start:
                new_segs.append(Segment(
                    seg.text,
                    (seg.style + _SEL_STYLE) if seg.style else _SEL_STYLE,
                ))
            else:
                new_segs.append(seg)
            x += seg_len
        return Strip(new_segs, strip._cell_length)

    def get_selection(self, selection):
        # 默认逻辑：Text/Content 直接可用
        result = super().get_selection(selection)
        if result is not None:
            return result
        # Panel/Markdown/Table 等：从渲染后的行中提取纯文本
        try:
            lines = []
            for y in range(self.content_size.height):
                strip = super().render_line(y)
                line = "".join(seg.text for seg in strip._segments if seg.text)
                lines.append(line.rstrip())
            text = "\n".join(lines)
            if text.strip():
                return selection.extract(text), "\n"
        except Exception:
            pass
        return None


# 用 SelectableStatic 替代 Static，全局生效
Static = SelectableStatic
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


class StatusIndicator(Static):
    """状态指示器"""

    thinking = reactive(False)
    elapsed = reactive(0)
    round_tokens = reactive(0)
    total_tokens = reactive(0)
    provider_name = reactive("DeepSeek")

    def render(self):
        parts = Text()
        if self.thinking:
            round_k = f"{self.round_tokens / 1000:.1f}k"
            total_k = f"{self.total_tokens / 1000:.1f}k"
            parts.append(" ◉ ", style="bold #4D6BFE")
            parts.append(self.provider_name, style="bold #4D6BFE")
            parts.append(f"  {self.elapsed}s", style="#4D6BFE")
            parts.append(f"  {round_k}/{total_k} ", style="dim")
        else:
            parts.append(" ◉ ", style="#333333")
            parts.append(self.provider_name, style="#333333")
        return parts


class PasteInput(Input):
    """自定义输入框：拦截粘贴，用 pyperclip 读完整剪贴板"""

    def _on_paste(self, event) -> None:
        """括号粘贴（<5KB）：直接读剪贴板"""
        event.stop()
        event.prevent_default()
        try:
            import pyperclip
            content = pyperclip.paste()
        except Exception:
            content = event.text or ""
        if content:
            self.app._handle_paste_content(content)


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
        height: 3;
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
        border: none;
        background: #000000;
        color: #ffffff;
        padding: 0;
    }

    #input-field:focus {
        border: none;
    }

    """

    BINDINGS = [
        Binding("escape", "interrupt", "中断", show=False),
        Binding("ctrl+c", "copy_or_quit", "复制/退出", show=False),
        Binding("tab", "complete_slash", "补全", show=False),
        Binding("ctrl+v", "smart_paste", "粘贴", show=False, priority=True),
        Binding("f5", "force_paste", "粘贴剪贴板", show=False, priority=True),
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
        self._ppt_slides = None
        self._ppt_index = 0
        self._ppt_preview_widget = None
        # 输入历史
        self._history = []
        self._history_index = 0
        self._history_draft = ""
        # 粘贴
        self._paste_content = None
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
                yield PasteInput(placeholder="输入消息...  Ctrl+V 粘贴 · F5 粘贴长文本", id="input-field")

    def on_mount(self):
        self._chat_view = self.query_one("#chat-view", VerticalScroll)
        self._status_indicator = self.query_one("#status-indicator", StatusIndicator)
        self._header_left = self.query_one("#header-left", Static)
        self._status_left = self.query_one("#status-left", Static)
        self._status_right = self.query_one("#status-right", Static)

        self._header_right = self.query_one("#header-right", Static)
        self._header_right.update(Text("选中文字Ctrl+C复制 · PageUp/Down翻页 · ESC中断 · Ctrl+C×2退出 ", style="bold #ffffff"))
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

        # 启动队列刷新定时器
        self.set_interval(0.05, self._flush_queues)

    # --- 输入历史 ---

    def _load_history(self):
        """从文件加载历史"""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self._history = [l.strip() for l in f if l.strip()][-MAX_HISTORY:]
        except Exception:
            self._history = []
        self._history_index = len(self._history)

    def _save_history(self, text):
        """保存一条记录到历史"""
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
        """上箭头：回溯历史"""
        if not self._history:
            return
        inp = self.query_one("#input-field", Input)
        if self._history_index == len(self._history):
            self._history_draft = inp.value
        if self._history_index > 0:
            self._history_index -= 1
            inp.value = self._history[self._history_index]
            inp.cursor_position = len(inp.value)

    def _history_down(self):
        """下箭头：前进历史"""
        if not self._history:
            return
        inp = self.query_one("#input-field", Input)
        if self._history_index < len(self._history):
            self._history_index += 1
            if self._history_index == len(self._history):
                inp.value = self._history_draft
            else:
                inp.value = self._history[self._history_index]
            inp.cursor_position = len(inp.value)

    def update_header(self):
        """更新 header 显示（切换模型时调用）"""
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

    # --- 队列式渲染（零 call_from_thread，消除闪烁）---

    def _flush_queues(self):
        """定时批量处理挂载和更新，单次重绘"""
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

        # 判断用户是否在底部附近（距底部 3 行以内）
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
        """线程安全：将 widget 放入挂载队列"""
        for w in widgets:
            self._mount_queue.put(w)

    def _enqueue_update(self, widget, content):
        """线程安全：将 widget 更新放入更新队列"""
        self._update_queue.put((widget, content))

    # --- 输入处理 ---

    def on_input_submitted(self, event: Input.Submitted):
        menu = self.query_one("#slash-menu", OptionList)
        if menu.display and menu.highlighted is not None:
            option = menu.get_option_at_index(menu.highlighted)
            text = str(option.prompt).strip()
        else:
            text = event.value.strip()
        menu.display = False

        # 先取出粘贴内容，再清空输入框（清空会触发 on_input_changed 导致 _paste_content 被清除）
        paste = self._paste_content
        self._paste_content = None
        event.input.value = ""

        # 交互式提问（ask_user / 危险确认 / PPT 预览）
        if self._inline_event and not self._inline_event.is_set():
            if self._inline_result is not None:
                self._inline_result["answer"] = text if text else "(用户未输入内容)"
            self._inline_event.set()
            return

        # 处理粘贴摘要：还原完整内容
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
        commands = ["/指南", "/模型", "/清空"]
        commands.extend(f"/{name}" for name in sorted(load_skills()))
        return commands

    def on_input_changed(self, event: Input.Changed):
        if event.input.id != "input-field":
            return
        # 用户改动了输入，清除粘贴摘要
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
            # 斜杠菜单导航
            if event.key == "up":
                if menu.highlighted is not None and menu.highlighted > 0:
                    menu.highlighted -= 1
            elif event.key == "down":
                if menu.highlighted is not None and menu.highlighted < menu.option_count - 1:
                    menu.highlighted += 1
            return

        # 输入历史导航
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
        inp = self.query_one("#input-field", Input)
        inp.value = str(event.option.prompt)
        inp.cursor_position = len(inp.value)
        self.query_one("#slash-menu", OptionList).display = False
        inp.focus()

    def _accept_slash_option(self):
        menu = self.query_one("#slash-menu", OptionList)
        if menu.highlighted is not None:
            option = menu.get_option_at_index(menu.highlighted)
            inp = self.query_one("#input-field", Input)
            inp.value = str(option.prompt)
            inp.cursor_position = len(inp.value)
        menu.display = False
        self.query_one("#input-field", Input).focus()

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
        """Ctrl+V / F5：从剪贴板读取"""
        try:
            import pyperclip
            content = pyperclip.paste()
            if content:
                self._handle_paste_content(content)
        except Exception:
            pass

    action_force_paste = action_smart_paste

    def _handle_paste_content(self, content):
        """统一处理粘贴内容：短内容进输入框，长内容显示摘要"""
        inp = self.query_one("#input-field", Input)
        lines = content.count('\n') + 1

        if lines < 3 and len(content) <= 150:
            # 短内容：直接插入输入框
            pos = inp.cursor_position
            inp.value = inp.value[:pos] + content + inp.value[pos:]
            inp.cursor_position = pos + len(content)
        else:
            # 长内容：显示摘要，完整内容存内部
            self._paste_content = content
            summary = f"[已粘贴 ~{lines} 行] "
            inp.value = summary
            inp.cursor_position = len(summary)

    def action_copy_or_quit(self):
        selected = self.screen.get_selected_text()
        if selected:
            self.copy_to_clipboard(selected)
            self.screen.clear_selection()
            self._enqueue(Static(Text("  已复制到剪贴板", style="bold #00cc66")))
            return
        # 无选中文字：双击 Ctrl+C 退出
        now = time.time()
        if now - self._last_ctrl_c < 2:
            self.exit()
            return
        self._last_ctrl_c = now
        self._chat_view.mount(Static(Text("  再按一次 Ctrl+C 退出", style="#8b949e")))
        self._chat_view.scroll_end(animate=False)

    # --- 公开接口（全部走队列，不触发即时重绘）---

    def write_user(self, text):
        """用户消息：蓝色左竖线 + 深色背景"""
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
        """AI 回复（非流式，一次性显示）"""
        self._enqueue(Static(Text("")), Static(Markdown(markdown_text)))

    def write_assistant_footer(self, elapsed):
        """AI 回复底部：模型名 + 耗时"""
        footer = Text()
        footer.append("  ◻ ", style="#30363d")
        footer.append("simple", style="bold #8b949e")
        footer.append(f" · {self.model_name} · {elapsed}s", style="#484f58")
        self._enqueue(Static(footer))

    def write_system(self, text):
        """系统消息"""
        self._enqueue(Static(Text(f"  {text}", style="#8b949e")))

    def write_warning(self, text):
        """警告消息"""
        self._enqueue(Static(Text(f"  {text}", style="bold #f85149")))

    def write_tool_preparing(self, tool_name):
        """流式阶段：工具名已知但参数还在传，立即显示白色状态"""
        _NAME_MAP = {
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
        display = _NAME_MAP.get(tool_name, tool_name)
        msg = Text()
        msg.append("  ")
        msg.append(display, style="bold white")
        msg.append("...", style="#8b949e")
        w = Static(msg)
        self._preparing_tool_widget = w
        self._enqueue(w)

    def write_tool(self, text):
        """工具开始执行：更新为完整信息（带路径/参数）"""
        msg = Text()
        msg.append("  ")
        parts = text.split(" ", 1)
        action = parts[0]
        rest = " " + parts[1] if len(parts) > 1 else ""
        msg.append(action, style="bold white")
        msg.append(rest, style="#8b949e")

        if self._preparing_tool_widget:
            w = self._preparing_tool_widget
            self._enqueue_update(w, msg)
            self._preparing_tool_widget = None
        else:
            w = Static(msg)
            self._enqueue(w)

        self._current_tool_widget = w
        self._current_tool_text = text

    def finish_tool(self, success=True):
        """工具执行完毕 — 成功深绿，失败红色"""
        w = self._current_tool_widget
        if not w:
            return
        text = self._current_tool_text
        msg = Text()
        msg.append("  ")
        parts = text.split(" ", 1)
        action = parts[0]
        rest = " " + parts[1] if len(parts) > 1 else ""
        color = "bold #00cc66" if success else "bold #ff4444"
        msg.append(action, style=color)
        msg.append(rest, style="#8b949e")
        self._enqueue_update(w, msg)
        self._current_tool_widget = None

    def write_code(self, renderable):
        """显示语法高亮代码块"""
        self._enqueue(Static(renderable))

    def write_diff(self, old_text, new_text):
        """左右并排 diff：左边新增（绿），右边删除（红）"""
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

    # --- 流式输出（也走队列）---

    def begin_response(self):
        """开始流式 AI 回复"""
        w = Static("")
        self._streaming_widget = w
        self._last_stream_time = 0.0
        self._enqueue(Static(Text("")), w)

    def stream_chunk(self, accumulated_text):
        """更新流式回复内容（节流 50ms）"""
        if not self._streaming_widget:
            return
        now = time.time()
        if now - self._last_stream_time < 0.05:
            return
        self._last_stream_time = now
        self._enqueue_update(self._streaming_widget, Markdown(accumulated_text))

    def end_response(self, final_text=""):
        """结束流式回复，同步更新完整文本并滚动到底部"""
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
        """渲染单页幻灯片预览"""
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
            content.append(f"\n\n备注: {slide['notes']}", style="dim")

        return Panel(
            content,
            title=f"第 {index + 1}/{total} 页 · {layout_name}",
            border_style="#FF8C00",
            padding=(1, 2),
        )

    def preview_ppt(self, slides_data):
        """PPT 预览模式：翻页浏览，输入修改意见或回车确认"""
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
        """后台线程调用：在聊天区显示问题，等待用户通过底部输入框回答"""
        event = threading.Event()
        result = {"answer": ""}
        self._inline_event = event
        self._inline_result = result
        is_danger = "危险命令" in question or "删除" in question
        color = "bold #ff4444" if is_danger else "bold yellow"
        self._enqueue(Static(Text(f"AI 提问: {question}", style=color)))
        event.wait()
        return result["answer"]

    def request_danger_confirm(self, command):
        """后台线程调用：确认危险命令。返回 True 表示用户确认执行"""
        answer = self.request_user_input(
            f"即将执行危险命令: {command}\n按 Enter 确认，输入任何内容取消"
        )
        return answer == "(用户未输入内容)"

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
