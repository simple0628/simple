# Claude Memory 备份

> 此文件是 Claude Code 记忆系统的备份，记录了 AI 助手对项目和用户的理解。
> 最后更新：2026-05-05

---

## 用户信息

- Python 工程师，在一家非一线互联网公司上班
- 独立开发了 simple（终端 AI 工具），不是公司项目
- 有强迫症，注重 UI 细节对齐
- 目标是让项目广泛传播、当简历使用，招聘方会看 GitHub 星数
- 不打算靠 simple 赚钱，收益点是自媒体粉丝 + 简历亮点
- 计划在抖音、小红书等平台宣传

---

## 项目信息

项目名称：simple
PyPI 包名：jiandanai（v0.0.4，已发布）
GitHub 仓库：https://github.com/simple0628/simple（公开）
口号：更适合中国宝宝体质的终端 AI 编码工具
定位：ToC（面向普通用户），不只是程序员工具
协议：GPL-3.0
GitHub 简介：中文原生终端AI助手 | 类似 Claude Code / Codex 的低配平替 | 基于 DeepSeek | 中文友好 | 超低成本 | Terminal AI Assistant | Open Source Alternative to Claude Code & Codex | Powered by DeepSeek

### 发布历史

- v0.0.1：首次发布，包名 jiandanai
- v0.0.2：修复 README 安装命令（pip install simple-code → pip install jiandanai）
- v0.0.3：降低 rapidocr-onnxruntime 版本要求（>=1.4 → >=1.2），兼容 Python 3.13
- v0.0.4：修复 ppt_frameworks 引用缺失（动画/转场数据内联到 svg_to_pptx.py），更新 .gitignore

### PyPI 账号

- 账号名：Simple_code（已开启 2FA）
- 上传方式：upload.py 脚本（已加入 .gitignore，不会提交）
- API Token：通过 pypi.org/manage/account/token 生成，scope 为 Entire account

### Git 配置

- 用户名：simple0628
- 邮箱：simple0628@users.noreply.github.com
- 重要：commit 不要加 Co-Authored-By Claude 署名，用户不希望显示 Claude 作为贡献者

### npm 旧版本

- 包名：simple-code-cli（npm）
- 版本：0.1.7（已停止维护，转为 Python 版）
- 总下载量约 1068 次（大部分为镜像同步和机器人）

### 技术栈

- Python + Textual（TUI 框架，v3.0+）
- DeepSeek（deepseek-chat），通过 OpenAI SDK 调用
- SVG → DrawingML XML 直写 → 原生可编辑 PPTX
- Edge/Chrome headless → PDF（简历生成）
- xhtml2pdf 作为 PDF fallback
- pyperclip（剪贴板读取）
- rapidocr-onnxruntime（OCR 图片文字识别，>=1.2 兼容 Python 3.13）
- Rich 用于 Markdown 渲染和语法高亮（Textual 内置）

### 项目结构

- simple_code/main.py — 入口、主循环、斜杠命令、文件路径检测
- simple_code/ui.py — Textual TUI 界面（SimpleApp）
- simple_code/widgets.py — 独立组件（SelectableStatic、StatusIndicator、PasteInput）
- simple_code/chat.py — 对话处理、工具调度、记忆保存、上下文压缩
- simple_code/config.py — 配置管理（含 TUI 风格首次引导）
- simple_code/state.py — 全局中断标志
- simple_code/tools/ — 13 个工具文件，自动注册
- docs/ — 记忆备份

### 已完成功能（工具列表）

tools/ 目录下 13 个工具文件（自动注册）：
- ask_user.py — 向用户提问
- create_ppt.py — 创建 PPT（两步 DeepSeek 调用 + SVG→PPTX）
- create_resume.py — 创建简历（AI 生成 HTML → Edge 转 PDF）
- create_skill.py — 创建自定义 Skill
- edit_file.py — 编辑文件
- glob_files.py — 搜索文件名
- grep_files.py — 搜索文件内容
- read_file.py — 读取文件
- run_command.py — 执行命令
- svg_to_pptx.py — SVG→PPTX 转换器（不注册为工具，被 create_ppt 内部调用）
- task_list.py — 任务管理
- web_fetch.py — 阅读网页
- web_search.py — 联网搜索
- write_file.py — 创建新文件

已删除的工具：
- ppt_frameworks.py — 21 套框架模板已删除（用户希望 AI 自由发挥不受模板限制），动画和转场数据已内联到 svg_to_pptx.py
- read_clipboard.py — 剪贴板读取工具已删除

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

### 配置

- API Key：~/.simple-code/config.json
- Skill 目录：~/.simple-code/skills/
- 项目记忆：{项目根目录}/simple/（长期记忆/ + 短期记忆.md）
- 输入历史：~/.simple-code/history.txt
- 首次配置：TUI 界面（免责声明 → API Key 输入 → 验证）

---

## PPT 系统

### 架构

- AI 负责：内容规划 + SVG 视觉设计 + 演讲稿（需要创意）
- 代码负责：动画 + 转场（可预测、稳定、省 token）
- 不需要独立 PPT 模式，在主对话里通过 create_ppt 工具完成
- SVG → DrawingML XML 直写（不通过 python-pptx API）
- 演讲稿独立输出 txt 文件，不写入 PPT 备注区

### PPT 生成两步流程

**第一步（主对话 DeepSeek）：** 规划内容
- AI 根据用户需求（或用户提供的资料）拆分为 pages 数组
- 每页包含 title、bullets（5-8 条具体要点）、notes（演讲稿）
- 调用 create_ppt 工具传入 pages

**第二步（create_ppt 内部再调 DeepSeek）：** 生成 SVG
- 根据 pages 内容生成每页的 SVG 视觉设计
- max_tokens=65536（从 16000 调高，避免多页时后面页面偷工减料）
- SVG → PPTX 转换复用 svg_to_pptx.py

### SVG 生成提示词优化历程（2026-05-05）

**问题：** DeepSeek 生成的 PPT 文字超出页面、布局单一（纯列表）

**老提示词（原始版）：**
- 只有 SVG 元素限制，没有排版规则
- DeepSeek 自由发挥，坐标不准导致文字超出
- 布局单调，所有页面都是竖排列表

**中间版（加排版规则）：**
- 加了安全区域（x=80-1200, y=40-680）
- 加了字符数限制（一行最多 22 个中文字）
- 加了间距规则
- 效果：文字不超出了，但布局更保守，装饰也少了

**最终版（当前使用）：**
- 定位改为"顶级 PPT 视觉设计师"
- 文字安全规则精简为 3 条核心规则（安全区域、宽度计算、超长换行）
- 新增"设计要求"7 条，按内容类型指定布局：
  1. 封面页：大标题居中 + 分散排列副信息
  2. 数据指标页：数据卡片（大号数字+小号说明），不用列表
  3. 内容页（5条以下）：卡片+图标色块，分栏或网格
  4. 内容页（6条以上）：双栏布局
  5. 必须有装饰元素（渐变色块、几何图形、光晕）
  6. 标题区要有设计感（色条、下划线、背景色块）
  7. 页面要饱满，充分利用 1280×720 空间
- 效果：数据页用卡片展示关键数字，内容页用双栏+彩色编号，底部有总结条

### 系统提示词优化（chat.py）

PPT 内容规划部分的改进：
- bullets 从"3-5 条"提高到"5-8 条"
- 要求每条要点写具体信息和数据，不要概括性短句
- 如果资料丰富，宁可多分几页
- 页数从"不少于 6 页"改为"不少于 7 页，内容多时 10-15 页"

### 核心文件

- `tools/svg_to_pptx.py` — SVG→PPTX 转换器（核心资产）
  - 包含 22 种入场动画定义（ENTRANCE_ANIMATIONS）
  - 包含 16 种混合动画池（ENTRANCE_MIXED_POOL）
  - 包含 8 种转场效果（TRANSITIONS）
  - 文本框 wrap 属性已改为 "square"（自动换行，防止文字超出）
- `tools/create_ppt.py` — PPT 工具
  - 两步 DeepSeek 调用：规划内容 → 生成 SVG
  - max_tokens=65536
  - "正在生成 PPT" 只显示一次（之前重复显示两次）
  - 演讲稿输出为独立 txt 文件

### 兼容性

- Python 3.9-3.12：所有功能正常
- Python 3.13：rapidocr-onnxruntime 只能装到 1.2.3 版本（1.4 版本未适配），OCR 功能仍可用
- 依赖要求：rapidocr-onnxruntime>=1.2（从 >=1.4 降低）

---

## 关键技术方案（原创）

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
- 文本框 wrap="square" 自动换行

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

---

## 宣传视频（Remotion）

- 位置：`video/` 目录（独立 JS 项目，不影响主项目）
- 技术栈：Remotion + React + TypeScript
- 当前进度：开头动画已完成初版
- 新文案（2026-05-05）：
  1. 我一直在线
  2. 最好用的软件应该长什么样子
  3. 思考许久后，我觉得我的答案是
  4. 这样
  5. 这是我个人开发的工具，我给它取名叫simple
  6. 它能做什么？
  7. 理论上来说，它什么都能做，帮你搜索资料，写程序，改程序，整理桌面，等等
- 旧文案（版本 B）：
  1. 每一款产品，都在要求你学习。
  2. 学习它的界面，学习它的逻辑，学习它的规则。
  3. 如果有一款工具，不需要你学任何东西呢？
  4. 你只需要说出你想做的事。
  5. 对话——就是唯一的操作方式。
- 运行方式：`cd video && npm start`（预览）、`npm run build`（渲染 mp4）

---

## 待做

- 录演示视频（Remotion）
- 宣传（掘金/小红书/B站/抖音）
- 免责声明精简
- win32.py 修复做成 monkey-patch
- SVG 转换器补充：阴影/发光效果、图片嵌入
- git 历史中残留 95MB webpack 缓存文件（video/node_modules），不影响当前代码，但 push 时会有警告

---

## 行为反馈

- 用户表达想法时不要擅自改文件，要等明确指令再动手
- 原因：用户想仔细讨论清楚再执行
- 不要过度设计独立模式，能集成到主流程就集成（PPT 模式的教训）
- 用户说"先不做"就先不做，别自作主张
- 不要催促用户（比如反复问"token 拿到了吗"），等用户自己准备好再推进
- 面向 ToC 用户：不暴露技术术语（OCR→图片文字识别、HTML→不提、SVG→不提）
- commit 不要加 Co-Authored-By Claude 署名
- 不要加模板限制 AI 的创意，用户删掉 ppt_frameworks.py 就是为了让 AI 自由发挥
- PPT 工具状态只显示一次"正在生成 PPT"，不要暴露 SVG 转换等技术细节给用户
