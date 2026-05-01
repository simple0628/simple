# 更新日志

## 2026-05-01

### 新功能

#### 文字选中复制（全新实现）
- **鼠标拖选复制**：直接拖选聊天区文字，Ctrl+C 复制到剪贴板
- **支持所有内容类型**：用户消息（Panel）、AI 回复（Markdown）、系统消息（Text）均可选中
- **跨多轮对话选中**：从第一条消息一直拖到最后一条，连续高亮不断裂
- **智能高亮**：选中区域显示深青色背景，松开鼠标后保持高亮直到复制或取消
- **Ctrl+C 双功能**：有选中文字时复制，无选中时双击退出

技术实现：自定义 `SelectableStatic` widget，为 Panel/Markdown 注入 offset 元数据 + 手动渲染选中高亮，解决了 Textual 框架不支持复杂渲染对象选中的问题。

#### 文件拖拽自动读取
- **拖拽文件到终端**：自动识别路径并读取内容发送给 AI
- 支持格式：`.txt` `.md` `.pdf` `.docx` `.pptx` `.png` `.jpg`（OCR）及文件夹
- 无需额外操作，拖进来按 Enter 即可

#### 流式输出自动滚动
- AI 回复时自动跟随滚动到底部
- 用户往上翻阅历史时不打扰（不会被强制拉回底部）
- PageUp/PageDown 键盘翻页

### 优化

#### 代码重构
- `ui.py` 拆分：独立组件（SelectableStatic、StatusIndicator、PasteInput）移至 `widgets.py`
- `ui.py` 从 870 行瘦身到 ~710 行
- `_TOOL_NAME_MAP` 提升为类属性，避免每次调用重建

#### 清理
- 移除 F5 粘贴长文本快捷键（Ctrl+V 已覆盖所有场景）
- 移除无效的"已复制到剪贴板"提示
- 简化输入框 placeholder 和顶栏提示文字

### 修复

- 修复跨多轮对话选中时中间 widget 高亮断裂的问题（Selection 的 None start/end 未处理）

---

### 文件变更

| 文件 | 变更 |
|------|------|
| `simple_code/widgets.py` | 新增，独立组件模块 |
| `simple_code/ui.py` | 重构精简，移除冗余 |
| `simple_code/main.py` | 新增文件路径检测 `_process_file_paths` |
