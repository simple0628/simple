# PPT 系统升级清单（2026-05-01）

> 本次升级由 Claude Opus 4.6 实施，涵盖 PPT 生成管线重构、粘贴系统修复、SVG→PPTX 转换器。

---

## 一、SVG → PPTX 转换器（核心成果）

**新文件：`simple_code/tools/svg_to_pptx.py`**

直接写 DrawingML XML（参考 ppt-master），不通过 python-pptx API 创建形状。

支持的 SVG 元素：
- `<rect>` → `<a:prstGeom prst="rect">`（含圆角 roundRect + adjValue）
- `<circle>` / `<ellipse>` → `<a:prstGeom prst="ellipse">`
- `<line>` → 细矩形模拟
- `<text>` + `<tspan>` → 多运行文本（`<a:r>`），支持独立坐标、字号、颜色、粗体
- `<path d="">` → `<a:custGeom>`（M/L/C/Z → moveTo/lnTo/cubicBezTo）
- `<polygon>` → 转换为 path
- `<linearGradient>` → `<a:gradFill>`（角度计算、多 stop）
- 透明度 → `<a:alpha>`
- 描边 → `<a:ln>`

关键转换公式：
- 坐标：px × 9525 = EMU
- 字号：SVG px × 75 = DrawingML 百分之一磅（sz 属性）
- 基线：y_box = y - fontSize × 0.85
- 宽度估算：CJK=1.0, 空格=0.3, 窄字符=0.3, 宽字符=0.75, 默认=0.55, 粗体×1.05, 总量×1.15
- 文本框：bodyPr wrap="none" lIns/tIns/rIns/bIns="0" + spAutoFit
- 东亚字体：`<a:ea typeface="Microsoft YaHei"/>`

动画系统（对齐 ppt-master）：
- chrome 过滤：id 含 background/bg/chrome/decoration 的 `<g>` 不参与动画
- 多元素序列动画：after-previous 触发，可配置间隔和时长
- mixed 模式：首元素 fade，其余循环 16 种效果池
- bldLst：`<p:bldLst>` 让 PPT 动画面板正确显示
- 转场在 timing 之前插入（OOXML schema 要求）

SVG 自动修复：
- 未关闭的 g/text/tspan/defs 标签自动补全
- & 符号修复
- 缺失的 </svg> 补全

---

## 二、PPT 生成管线重构

**改动文件：`simple_code/tools/create_ppt.py`**

旧方案：AI 输出 JSON（title/bullets）→ python-pptx API 硬编码布局
新方案：AI 输出 JSON → 内部二次调 DeepSeek 生成 SVG → svg_to_pptx 转换 → 原生可编辑 PPTX

流程：
1. 用户在主对话中说"做个 PPT"
2. DeepSeek 通过对话收集需求（主题、资料、页数、风格）
3. DeepSeek 调用 create_ppt 工具，传入每页 title/bullets/notes
4. 工具内部调 DeepSeek 生成 SVG
5. SVG → DrawingML → PPTX（含动画+转场+演讲稿）

---

## 三、PPT 框架知识库

**新文件：`simple_code/tools/ppt_frameworks.py`**

- 21 套设计框架（配色+装饰描述+封面/章节/内容/目录/结尾布局）
- 8 种转场效果（fade/push/wipe/split/strips/cover/random/none）
- 22 种入场动画（完整 filter + presetID 映射）
- 3 种触发模式（after-previous/on-click/with-previous）
- mixed/random 动画池

---

## 四、设计规范知识库

**新目录：`simple_code/knowledge/ppt/`**

- `design-system.md` — 配色(60-30-10法则)、字体层级、间距系统、布局原则、装饰指南、动画指南、Do/Don't
- `styles.md` — 8 种风格详细定义（商务蓝/暗色科技/学术白/政务蓝/活力现代/赛博像素/暗色咨询/温暖柔和）+ 快速推荐矩阵
- `constraints.md` — 画布规格、python-pptx 边界、SVG 生成约束

---

## 五、粘贴系统修复

### Windows 大文本粘贴（>5KB）
- **根因**：Windows Terminal 确认对话框后数据到达但 Textual EventMonitor 未读取
- **解决**：修改 textual/drivers/win32.py，检测 500+ 事件批量到达时排空缓冲区 → 重建 parser → call_from_thread 直接调 _handle_paste_content

### VK=0 中文字符过滤修复
- **根因**：Textual win32 驱动过滤 `dwControlKeyState && wVirtualKeyCode==0`，NUMLOCK 开启时中文字符（VK=0）被丢弃
- **解决**：加 `and key == "\x00"` 条件，只过滤真正的空字符

### PasteInput 自定义输入框
- **根因**：Textual Input 默认 `_on_paste` 只取 `splitlines()[0]`（第一行）
- **解决**：自定义 PasteInput 子类覆盖 `_on_paste`，用 pyperclip 读完整剪贴板

### 粘贴摘要显示
- 长内容（≥3行或>150字符）→ 显示 `[已粘贴 ~X 行]`
- 提交时还原完整内容
- 解决 on_input_changed 清空 _paste_content 的竞态

### read_clipboard 工具
- 新增工具让 AI 主动读取剪贴板内容

---

## 六、输入历史

- 上下箭头回溯/前进历史（最多 50 条）
- 持久化到 `~/.simple-code/history.txt`
- 浏览历史时当前输入自动暂存

---

## 七、其他改动

- `chat.py` 系统提示词更新 PPT 创建流程
- `config.py` 清理多模型残留（switch_provider/get_provider_key/reset_config/get_api_key/_test_api_key）
- `pyproject.toml` 添加 pyperclip/rapidocr-onnxruntime 依赖
- `.gitignore` 添加 simple/、*.pptx、~$*
- 提交异常保护（_safe_handle_submit）

---

## 八、删除的文件/功能

- `ppt_mode.py` — 独立 PPT 模式（改为主对话内完成）
- `/ppt` 斜杠命令（不再需要）
- MiniMax 多模型支持（简化为单模型 DeepSeek）
- `/模型使用` 命令
- `/粘贴` 命令（改为 F5 快捷键）
- 旧的 python-pptx 硬编码布局代码（21 框架 9 分支）

---

## 九、参考项目

- [ppt-master](https://github.com/hugohe3/ppt-master) — SVG→DrawingML 转换逻辑、动画系统、设计规范
- [pptx-design-styles](https://github.com/corazzon/pptx-design-styles) — 30 种设计风格定义
- [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills) — 设计 token 系统
- [open-design](https://github.com/nexu-io/open-design) — 9 段式设计系统 schema
- [Codex CLI](https://github.com/openai/codex) — Paste Burst 状态机
- [OpenCode](https://github.com/nicepkg/opencode) — TUI 架构参考
