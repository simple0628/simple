# simple

一款简单的终端 AI 助手。在终端里和 AI 对话，直接读写文件、执行命令、搜索内容。

<!-- 录一个 GIF 放在这里，展示实际使用效果 -->
<!-- ![demo](./assets/demo.gif) -->

## 安装

```bash
pip install simple-code
```

首次启动会引导你配置 API Key。

## 使用

```bash
# 在你的项目目录下启动
cd your-project
simple
```

## 命令

| 命令 | 功能 |
|------|------|
| `/help` | 显示帮助信息 |
| `/reset` | 重新配置 API Key |
| `/clear` | 清空对话历史 |
| `/自定义` | 执行自定义 Skill |

## 自定义 Skill

在 `~/.simple-code/skills/` 目录下新建 `.md` 文件即可添加自定义 Skill，文件名就是命令名。

例如，创建 `~/.simple-code/skills/review.md`：

```markdown
请审查当前项目的代码，重点检查：
1. 潜在的 bug
2. 安全漏洞
3. 性能问题
4. 代码可读性
```

然后在对话中输入 `/review` 即可触发。也可以附加内容：`/review 只看 main.py`。

## 功能

| 能力 | 说明 |
|------|------|
| 读写文件 | 读取、创建、编辑项目中的任意文件 |
| 执行命令 | 运行终端命令，危险操作会先确认 |
| 搜索代码 | 按文件名或内容搜索，快速定位代码 |
| 联网搜索 | 搜索技术文档，抓取网页内容 |
| 任务管理 | 复杂任务自动拆分步骤，逐步执行 |
| 项目记忆 | 每轮对话自动总结写入 simple.md |
| 流式输出 | 实时显示 AI 回复，Markdown 渲染 |

## 快捷键

| 按键 | 功能 |
|------|------|
| `Enter` | 提交输入 |
| `Ctrl+Enter` | 换行，继续输入 |
| `Ctrl+O` | 展开/折叠工具操作详情 |
| `Ctrl+C × 2` | 退出程序 |

## 项目结构

```
simple_code/
  main.py        # 入口：启动界面、快捷键、主循环
  config.py      # 配置管理：API Key、免责声明、首次引导
  chat.py        # 对话处理：流式 API 调用、工具调度
  ui.py          # 状态面板：计时器、工具调用列表、token 统计
  tools/         # 工具（自动注册，加文件即生效）
    read_file    # 读取文件 / 列出目录
    write_file   # 创建文件（语法高亮预览）
    edit_file    # 编辑文件（红绿 diff 显示）
    run_command  # 执行命令（危险命令确认 + 超时保护）
    glob_files   # 按文件名模式搜索
    grep_files   # 按内容关键词搜索
    web_search   # 联网搜索（多引擎轮询）
    web_fetch    # 抓取网页正文
    ask_user     # 向用户提问确认
    task_list    # 任务清单管理
```

## 技术栈

- **DeepSeek API** — 大模型推理，通过 OpenAI SDK 调用
- **Rich** — 终端 Markdown 渲染、语法高亮、状态面板
- **prompt_toolkit** — 输入框、快捷键绑定、多行编辑
- **BeautifulSoup4** — 网页内容解析

## License

MIT
