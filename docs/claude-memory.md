# Claude Memory 备份

> 此文件是 Claude Code 记忆系统的备份，记录了 AI 助手对项目和用户的理解。
> 最后更新：2026-05-03

---

## 用户信息

- 编程初学者，目标是通过做项目来学习
- 正在开发一个终端 AI 工具（simple），后端用 DeepSeek API
- 有强迫症，注重 UI 细节对齐
- 目标是让项目广泛传播、当简历使用
- 当前使用 Python 开发
- 对开源/闭源问题很纠结，担心代码被抄

---

## 项目信息

项目名称：simple
PyPI 包名：simple（v0.0.1，待发布）
口号：更适合中国宝宝体质的终端 AI 编码工具
定位：ToC（面向普通用户），不只是程序员工具

### 技术栈
- Python + Textual（TUI 框架，v3.0+）
- DeepSeek（deepseek-chat），通过 OpenAI SDK 调用
- SVG → DrawingML XML 直写 → 原生可编辑 PPTX
- Edge/Chrome headless → PDF（简历生成）
- xhtml2pdf 作为 PDF fallback
- pyperclip（剪贴板读取）
- rapidocr-onnxruntime（OCR 图片文字识别）
- Rich 用于 Markdown 渲染和语法高亮（Textual 内置）

### 发布状态

- PyPI 包名：simple，版本 v0.0.1（已打包，待上传）
- GitHub 仓库：https://github.com/simple0628/simple（私有，计划公开）
- PyPI 账号：Simple_code（已开启 2FA）
- 协议：MIT

### 项目结构
- simple_code/main.py — 入口、主循环、斜杠命令、文件路径检测
- simple_code/ui.py — Textual TUI 界面（SimpleApp）
- simple_code/widgets.py — 独立组件（SelectableStatic、StatusIndicator、PasteInput）
- simple_code/chat.py — 对话处理、工具调度、记忆保存、上下文压缩
- simple_code/config.py — 配置管理（含 TUI 风格首次引导）
- simple_code/state.py — 全局中断标志
- simple_code/tools/ — 15 个工具，自动注册
- docs/ — 记忆备份

### 已完成功能（15 个工具）
- 读/写/编辑文件、执行命令、搜索文件名/内容
- 联网搜索、阅读网页
- 向用户提问、任务管理
- 创建 Skill、创建 PPT（SVG→PPTX + 演讲稿 txt）
- 创建简历（AI 生成 HTML → Edge 转 PDF，支持照片嵌入）
- 读取剪贴板、PPT 框架查询

### UI 功能
- 文字选中复制（SelectableStatic，支持 Panel/Markdown/跨 widget）
- 文件拖拽自动读取（txt/pdf/docx/pptx/图片文字识别）
- 流式输出 + Markdown 渲染 + 智能自动滚动
- 多行输入（Ctrl+Enter 换行，Enter 提交，TextArea 实现）
- PPT 预览模式（方向键翻页、修改意见、确认后生成）
- 粘贴处理（Ctrl+V，短文本直接输入，长文本摘要显示）
- 输入历史（上下箭头，持久化到 ~/.simple-code/history.txt）
- 斜杠命令自动补全（/指南、/模型）
- ESC 中断 + Ctrl+C 复制/双击退出
- 危险命令选择框（上下选择拒绝/允许，默认拒绝）
- 工具状态闪烁动画（超过 2 秒未完成）
- 点击任意位置自动聚焦输入框
- token 统计 + 计时器
- PageUp/PageDown 翻页

### 记忆系统
- 长期记忆：按 session 保存完整对话（一次启动 = 一个 md 文件），永久保存
- 短期记忆：每轮对话追加一行摘要（日期+时间），7 天自动清理
- 启动时加载短期记忆到系统提示词
- 通过时间戳从短期记忆定位到长期记忆详情
- 自动上下文压缩：prompt_tokens 超过 55K 时压缩旧对话

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

#### 5. SVG→PPTX 转换器
- SVG 中间格式：AI 生成 SVG 比直接生成 DrawingML 容易得多
- 动画不让 AI 决定：代码规则分配，比 AI 更稳定
- 字号转换：SVG px × 0.75 = PPT pt
- 基线偏移：y_box = y - fontSize × 0.85
- 演讲稿独立输出 txt 文件，不写入 PPT 备注区

#### 6. 简历生成
- AI 生成完整 HTML（禁止 flexbox/grid/emoji/min-height）
- Edge headless 转 PDF（临时文件避免中文路径问题）
- 支持一寸照片嵌入（base64 内嵌）
- xhtml2pdf 作为 fallback
- HTML 不暴露给用户，只输出 PDF

#### 7. 危险命令确认
- 输入框变为上下选择列表（拒绝/允许）
- 默认选中拒绝，防误操作
- 拒绝后跳过后续所有工具调用
- 命令描述转为用户能懂的语言（即将删除: xxx）

### 配置
- API Key：~/.simple-code/config.json
- Skill 目录：~/.simple-code/skills/
- 项目记忆：{项目根目录}/simple/（长期记忆/ + 短期记忆.md）
- 输入历史：~/.simple-code/history.txt
- 首次配置：TUI 界面（免责声明 → API Key 输入 → 验证）

### 待做
- 发布到 PyPI（包已打好，等 token 上传）
- README 重写（PyPI 页面需要）
- 录演示视频（Remotion，录屏 + 包装）
- 宣传（掘金/小红书/B站）
- 免责声明精简
- win32.py 修复做成 monkey-patch
- SVG 转换器补充：阴影/发光效果、图片嵌入

### 宣传视频（Remotion）

- 位置：`video/` 目录（独立 JS 项目，不影响主项目）
- 技术栈：Remotion + React + TypeScript
- 当前进度：开头动画已完成初版
- 文案（版本 B）：
  1. 每一款产品，都在要求你学习。
  2. 学习它的界面，学习它的逻辑，学习它的规则。
  3. 如果有一款工具，不需要你学任何东西呢？
  4. 你只需要说出你想做的事。
  5. 对话——就是唯一的操作方式。
- 动画方案：一句一屏，每句独立进场/退场
  - 第1句：从下方滑入 + 淡入
  - 第2句：三段逐词依次出现
  - 中间黑屏留白制造悬念
  - 第3句：Apple 风格（scale 缩小 + blur→clear）
  - 第4句：从下方滑入
  - 第5句（点题）：弹簧放大 + 蓝色脉冲光晕
- 音频：计划用 MiniMax 生成
- 运行方式：`cd video && npm start`（预览）、`npm run build`（渲染 mp4）

---

## PPT 系统

### 架构
- AI 负责：SVG 视觉设计 + 演讲稿（需要创意）
- 代码负责：动画 + 转场（可预测、稳定、省 token）
- 不需要独立 PPT 模式，在主对话里通过 create_ppt 工具完成
- SVG → DrawingML XML 直写（不通过 python-pptx API）

### 核心文件
- `tools/svg_to_pptx.py` — SVG→PPTX 转换器（核心资产，500+ 行）
- `tools/create_ppt.py` — PPT 工具（内部调 DeepSeek 生成 SVG → 转换）
- `tools/ppt_frameworks.py` — 21 套框架 + 22 种动画 + 8 种转场知识库

### 粘贴系统
- Textual Input 默认 _on_paste 只取第一行 → PasteInput 子类覆盖（现改为 TextArea 子类）
- Windows Terminal >5KB 确认后无事件到达 → 修改 win32.py EventMonitor 检测大批量事件
- VK=0 中文字符被 Textual 过滤 → 加 `and key == "\x00"` 条件

---

## 行为反馈

- 用户表达想法时不要擅自改文件，要等明确指令再动手
- 原因：用户想仔细讨论清楚再执行
- 不要过度设计独立模式，能集成到主流程就集成（PPT 模式的教训）
- 用户说"先不做"就先不做，别自作主张
- 不要催促用户（比如反复问"token 拿到了吗"），等用户自己准备好再推进
- 面向 ToC 用户：不暴露技术术语（OCR→图片文字识别、HTML→不提、SVG→不提）
