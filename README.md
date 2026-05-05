# simple

> 更适合中国宝宝体质的终端 AI 助手

在终端里和 AI 对话，直接读写文件、执行命令、生成 PPT、制作简历。不只是程序员的工具，任何人都能用。

<!-- ![demo](./assets/demo.gif) -->

## 特性

- **对话即操作** — 用自然语言读写文件、执行命令、搜索代码
- **一句话做 PPT** — AI 生成设计稿，自动转换为原生可编辑 PPTX
- **AI 简历生成** — 提供信息 + 岗位 JD，直接输出 PDF 简历
- **项目记忆** — 自动记住你项目的上下文，跨会话延续对话
- **自定义 Skill** — 用 Markdown 定义工作流，一个命令触发
- **危险操作保护** — 高危命令自动弹出确认，不会误删你的代码
- **流式输出** — 实时显示回复，终端内 Markdown 渲染

## 安装

```bash
pip install simple-code
```

需要 Python >= 3.9。首次启动会引导你配置 DeepSeek API Key。

## 快速开始

```bash
# 在你的项目目录下启动
cd your-project
simple
```

然后直接用中文对话：

```
> 帮我看看这个项目的结构
> 把 main.py 里的报错修一下
> 做一个10页的产品介绍PPT
> 帮我写一份投递字节的简历
```

## 快捷键

| 按键 | 功能 |
|------|------|
| `Enter` | 提交输入 |
| `Ctrl+Enter` | 换行 |
| `Ctrl+O` | 展开/折叠工具调用详情 |
| `Ctrl+C × 2` | 退出 |

## 自定义 Skill

在 `~/.simple-code/skills/` 目录下创建 `.md` 文件即可：

```markdown
<!-- ~/.simple-code/skills/review.md -->
请审查当前项目的代码，重点检查：
1. 潜在的 bug
2. 安全漏洞
3. 性能问题
```

对话中输入 `/review` 触发，也可以附加参数：`/review 只看 main.py`。

## 技术栈

- **DeepSeek API** — 大模型推理
- **Textual** — 现代终端 TUI 框架
- **Rich** — Markdown 渲染、语法高亮
- **python-pptx** — PPT 生成
- **xhtml2pdf** — PDF 生成

## License

GPL-3.0
