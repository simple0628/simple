"""可复用 UI 组件：SelectableStatic、StatusIndicator、PasteInput"""

from textual.widgets import Static as _BaseStatic, Input, TextArea
from textual.reactive import reactive
from textual.strip import Strip
from textual.content import Content
from rich.text import Text
from rich.segment import Segment
from rich.style import Style as RichStyle


_SEL_STYLE = RichStyle(bgcolor="dark_cyan")


class SelectableStatic(_BaseStatic):
    """支持文字选中的 Static widget（含 Panel/Markdown 高亮 + 文字提取）"""

    def render_line(self, y):
        strip = super().render_line(y)
        strip = strip.apply_offsets(0, y)

        sel = self.text_selection
        if sel is not None:
            visual = self._render()
            if not isinstance(visual, (Text, Content)):
                strip = self._apply_highlight(strip, y, sel)

        return strip

    def _apply_highlight(self, strip, y, sel):
        """给指定行的选中范围添加高亮背景（支持 None 表示全选）"""
        start_y = sel.start.y if sel.start else 0
        start_x = sel.start.x if sel.start else 0
        end_y = sel.end.y if sel.end else 999999
        end_x = sel.end.x if sel.end else 999999

        if (start_y, start_x) > (end_y, end_x):
            start_y, start_x, end_y, end_x = end_y, end_x, start_y, start_x
        if not (start_y <= y <= end_y):
            return strip

        line_start = start_x if y == start_y else 0
        line_end = end_x if y == end_y else 999999

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
        result = super().get_selection(selection)
        if result is not None:
            return result
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


# 全局别名
Static = SelectableStatic


class StatusIndicator(Static):
    """状态栏指示器：显示模型名称、耗时、token 计数"""

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


class PasteInput(TextArea):
    """多行输入框：Enter 提交，Ctrl+Enter 换行，支持拖拽和粘贴"""

    # 兼容 Input 的 Submitted 事件
    class Submitted:
        def __init__(self, input, value):
            self.input = input
            self.value = value

    def __init__(self, placeholder="", **kwargs):
        super().__init__("", **kwargs)
        self._placeholder = placeholder

    def on_mount(self):
        self.show_line_numbers = False
        self.tab_behavior = "focus"

    @property
    def value(self):
        return self.text

    @value.setter
    def value(self, v):
        self.clear()
        self.insert(v)

    @property
    def cursor_position(self):
        row, col = self.cursor_location
        # 简单转换：计算到光标位置的总字符数
        lines = self.text.split("\n")
        pos = sum(len(lines[i]) + 1 for i in range(row)) + col
        return pos

    @cursor_position.setter
    def cursor_position(self, pos):
        text = self.text
        row = 0
        col = pos
        for line in text.split("\n"):
            if col <= len(line):
                break
            col -= len(line) + 1
            row += 1
        self.cursor_location = (row, max(0, col))

    @property
    def placeholder(self):
        return self._placeholder

    @placeholder.setter
    def placeholder(self, v):
        self._placeholder = v

    @property
    def password(self):
        return False

    @password.setter
    def password(self, v):
        pass  # TextArea 不支持密码模式，忽略

    def check_consume_key(self, key, character):
        """确认模式下拦截所有按键，阻止 TextArea 的默认绑定"""
        if hasattr(self.app, '_in_confirm_mode') and self.app._in_confirm_mode:
            return True
        return super().check_consume_key(key, character)

    async def _on_key(self, event) -> None:
        # 确认模式：只响应左右和回车
        if hasattr(self.app, '_in_confirm_mode') and self.app._in_confirm_mode:
            event.stop()
            event.prevent_default()
            if event.key in ("up", "down", "left", "right"):
                self.app._confirm_index = 1 - self.app._confirm_index
                self.app._update_confirm_display()
            elif event.key == "enter":
                submitted = self.Submitted(input=self, value=self.text)
                self.app.on_input_submitted(submitted)
            return

        if event.key in ("ctrl+enter", "ctrl+j"):
            # Ctrl+Enter = 换行（手动插入）
            event.stop()
            event.prevent_default()
            start, end = self.selection
            self._replace_via_keyboard("\n", start, end)
            return
        if event.key == "enter":
            # Enter = 提交
            event.stop()
            event.prevent_default()
            submitted = self.Submitted(input=self, value=self.text)
            self.app.on_input_submitted(submitted)
            return
        # 其他按键交给 TextArea 处理
        await super()._on_key(event)

    def _on_paste(self, event) -> None:
        event.stop()
        event.prevent_default()
        content = event.text or ""
        if not content:
            try:
                import pyperclip
                content = pyperclip.paste()
            except Exception:
                pass
        if content:
            self.app._handle_paste_content(content)
