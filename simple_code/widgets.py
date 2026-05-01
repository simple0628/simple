"""可复用 UI 组件：SelectableStatic、StatusIndicator、PasteInput"""

from textual.widgets import Static as _BaseStatic, Input
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


class PasteInput(Input):
    """自定义输入框：拦截粘贴，支持拖拽文件路径 + 剪贴板读取"""

    def _on_paste(self, event) -> None:
        event.stop()
        event.prevent_default()
        # 优先用 event.text（拖拽文件路径在这里），为空时再读剪贴板
        content = event.text or ""
        if not content:
            try:
                import pyperclip
                content = pyperclip.paste()
            except Exception:
                pass
        if content:
            self.app._handle_paste_content(content)
