# Claude Memory 备份

> 此文件是 Claude Code 记忆系统的备份，记录了 AI 助手对项目和用户的理解。

---

## 用户信息

- 编程初学者，目标是通过做项目来学习
- 正在开发一个类似 Claude Code 的 CLI 工具（simple），后端用 DeepSeek API
- 有强迫症，注重 UI 细节对齐
- 目标是让项目广泛传播、当简历使用，招聘方会看 GitHub 星数
- 当前使用 Python 开发

---

## 项目信息

项目名称：simple-code
口号：更适合中国宝宝体质的终端 AI 编码工具
定位：ToC（面向普通用户），不只是程序员工具

### 技术栈
- Python + Textual（TUI 框架，v3.0+）
- DeepSeek（deepseek-chat），通过 OpenAI SDK 调用
- pyperclip（剪贴板读取）
- rapidocr-onnxruntime（OCR 图片文字识别）
- Rich 用于 Markdown 渲染和语法高亮（Textual 内置）

### 发布状态

- PyPI 包名：simple-code，版本 v0.1.0（准备中）
- GitHub 仓库：https://github.com/simple0628/simple
- 协议：MIT

### 项目结构
- simple_code/main.py — 入口、主循环、斜杠命令、文件路径检测
- simple_code/ui.py — Textual TUI 界面（SimpleApp）
- simple_code/widgets.py — 独立组件（SelectableStatic、StatusIndicator、PasteInput）
- simple_code/chat.py — 对话处理、工具调度、记忆保存
- simple_code/config.py — 配置管理
- simple_code/state.py — 全局中断标志
- simple_code/tools/ — 14 个工具，自动注册
- docs/ — 优化日志

### 已完成功能
- 14个工具（读/写/编辑文件、执行命令、搜索文件名/内容、联网搜索、阅读网页、向用户提问、任务管理、创建Skill、创建PPT、读取剪贴板、PPT框架查询）
- 文字选中复制（SelectableStatic，支持 Panel/Markdown/跨 widget）
- 文件拖拽自动读取（拖入终端自动识别路径，读取 txt/pdf/docx/pptx/图片OCR）
- 流式输出 + Markdown 渲染 + 智能自动滚动
- PPT 预览模式（方向键翻页、修改意见、确认后生成）
- 粘贴处理（Ctrl+V，短文本直接输入，长文本摘要显示）
- 输入历史（上下箭头，持久化到 ~/.simple-code/history.txt）
- 斜杠命令自动补全（/指南、/模型、/ppt、/清空）
- ESC 中断 + Ctrl+C 复制/双击退出
- 智能记忆（AI 判断是否值得记忆）
- 危险命令确认
- token 统计 + 计时器
- PageUp/PageDown 翻页

### 关键技术方案（原创）

#### 1. Windows 大文本粘贴（>5KB）
Textual 的 win32 驱动直接修改了两处：
1. VK=0 过滤修复：加 `and key == "\x00"` 防止中文字符被过滤
2. 大文本检测：ReadConsoleInputW 读到 500+ 事件时，排空缓冲区 → 重建 parser → call_from_thread 直接调 _handle_paste_content
文件位置：textual/drivers/win32.py（用户机器上直接修改的，发布时需要做成 monkey-patch 或提 PR）

#### 2. SelectableStatic（Panel/Markdown 文字选中）
- 为所有 Static widget 注入 offset 元数据（render_line + apply_offsets）
- 对非 Text/Content 渲染对象手动渲染选中高亮（_apply_highlight）
- 从渲染后的 Strip 中提取纯文本用于复制（get_selection fallback）
- 处理 Selection(None, None) 全选情况，修复跨 widget 高亮断裂

#### 3. 智能自动滚动
- 检测用户是否在底部附近（距底部 ≤3 行）
- 在底部时：新内容自动滚动跟随
- 往上翻时：不打扰，保持当前位置

#### 4. 文件拖拽自动读取
- Windows Terminal 拖拽文件 = paste 事件（event.text 包含路径）
- PasteInput 优先使用 event.text，fallback 到 pyperclip
- 提交时 _process_file_paths 检测路径、自动读取内容

### 配置
- API Key：~/.simple-code/config.json
- Skill 目录：~/.simple-code/skills/
- 项目记忆：{项目根目录}/simple/simple.md
- 输入历史：~/.simple-code/history.txt

### 待做
- README 重写
- 发布到 PyPI（需要把 win32.py 修复做成 monkey-patch）
- 录演示 GIF
- 简历生成功能
- 掘金/小红书发帖

---

## PPT 系统（Claude Opus 4.6 补充）

### 架构
- AI 负责：SVG 视觉设计 + 演讲稿（需要创意）
- 代码负责：动画 + 转场（可预测、稳定、省 token）
- 不需要独立 PPT 模式，在主对话里通过 create_ppt 工具完成
- SVG → DrawingML XML 直写（不通过 python-pptx API），参考 ppt-master

### 核心文件
- `tools/svg_to_pptx.py` — SVG→PPTX 转换器（核心资产，500+ 行）
- `tools/create_ppt.py` — PPT 工具（内部调 DeepSeek 生成 SVG → 转换）
- `tools/ppt_frameworks.py` — 21 套框架 + 22 种动画 + 8 种转场知识库
- `knowledge/ppt/` — 设计规范文档

### 重要决策记录
- SVG 中间格式：AI 生成 SVG 比直接生成 DrawingML 容易得多（训练数据多）
- 动画不让 AI 决定：ppt-master 也是代码规则分配，AI 决定动画不比规则好
- 不做独立 PPT 模式：集成到主对话更自然，读秒/工具状态/token 计数自动工作
- 字号转换：SVG px × 0.75 = PPT pt（或 px × 75 = DrawingML sz 百分之一磅）
- 基线偏移：y_box = y - fontSize × 0.85（ppt-master 的值，在直写 XML 场景下准确）

### 粘贴系统
- Textual Input 默认 _on_paste 只取第一行 → PasteInput 子类覆盖
- Windows Terminal >5KB 确认后无事件到达 → 修改 win32.py EventMonitor 检测大批量事件
- VK=0 中文字符被 Textual 过滤 → 加 `and key == "\x00"` 条件

### 待做
- 记忆系统重构（index.md + 分文件存储）
- SVG 转换器补充：阴影/发光效果、图片嵌入
- 发布 PyPI 时 win32.py 修复需做成 monkey-patch

---

## 行为反馈

- 用户表达想法时不要擅自改文件，要等明确指令再动手
- 原因：用户想仔细讨论清楚再执行
- 不要过度设计独立模式，能集成到主流程就集成（PPT 模式的教训）
- 修改其他 Claude 负责的文件前要确认（ui.py、widgets.py 是另一个 Claude 的地盘）
- 用户说"先不做"就先不做，别自作主张
