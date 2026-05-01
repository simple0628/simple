# PPT 技术约束

> 生成 PPT 时必须遵守的技术限制。

## 画布规格

| 格式 | 宽度 | 高度 | 用途 |
|------|------|------|------|
| 16:9 标准 | 1280px / 12192000 EMU | 720px / 6858000 EMU | 默认，绝大多数场景 |
| 4:3 传统 | 960px / 9144000 EMU | 720px / 6858000 EMU | 旧投影仪 |

当前仅支持 16:9。

## python-pptx 能力边界

### 支持
- 矩形、椭圆、三角形等基本形状
- 纯色填充、渐变填充（线性/径向）
- 透明度设置（通过 XML 操作）
- 文本框（字体、大小、颜色、粗体、对齐）
- 项目符号列表
- 页面转场效果（fade/push/wipe/split/strips/cover/random）
- 入场动画（22 种，per-element）
- 演讲者备注

### 不支持或受限
- 圆角矩形（需要 XML 操作设置 adjValue）
- 自定义路径/贝塞尔曲线（需要 freeform 的 XML）
- 图片插入（支持但需要文件路径）
- 图表（需要 python-pptx 的 chart API，复杂）
- 表格（支持但样式控制有限）
- 文字阴影/发光效果（需要 XML）
- 多元素序列动画（需要复杂的 timing XML）

## SVG 生成约束（未来方向）

如果使用 SVG 作为中间格式，需遵守：

### 必须
- viewBox="0 0 1280 720"
- 所有坐标使用绝对定位（不用百分比）
- 颜色使用 HEX（#RRGGBB），不用 rgb()
- 透明度使用 fill-opacity / stroke-opacity
- 渐变定义在 `<defs>` 中
- 文字使用 `<text>` + `<tspan>`（不用 foreignObject）

### 禁止
- `<style>` 标签（用行内样式）
- `class` 属性
- `<foreignObject>`
- `<use>` / `<symbol>` 引用
- CSS 动画
- 外部资源引用（图片用 base64 或本地路径）
- `mask` / `clip-path`（除图片裁剪外）

### 命名规范
- 每个需要动画的顶层 `<g>` 必须有 `id` 属性
- id 格式：`element-类型-序号`（如 `element-title-1`）
- 背景/装饰元素的 `<g>` 标记为 `id="chrome-xxx"`（不参与动画）
