# Detail.design 设计灵感库

[English README](README.en.md) · 中文

## 来源、范围与致谢

内容来源：[detail.design](https://detail.design)。归档聚焦公开英文目录、详情 API 返回的内容，以及首页、Resources、About Detail 和 Support 页面；不包含网站代码、私有内容或媒体文件本体，媒体 URL 按源站数据保留。内容和版权归原作者及其权利人所有；本项目用于研究、检索和辅助设计，使用者应保留来源归属，并遵守源站条款及适用许可。

这是定期刷新的快照，不是实时镜像。抓取时间、条目数量和完整性信息见 [`capture-manifest.json`](detail-design-skill/references/capture-manifest.json)。欢迎提交问题和改进建议。

**给 Agent 一份可检索、可引用的设计实践资料库。** 本项目将 [detail.design](https://detail.design) 的公开英文目录、文章正文与站点页面整理为结构化数据，并打包成可直接交给 Agent 使用的 Skill。

> 项目提供的是内容归档与检索 Skill，不是网站源代码或网站镜像。引用具体设计建议时，建议让 Agent 同时给出对应条目和来源链接。

## 你可以让 Agent 做什么

下载或安装 [`detail-design-skill/`](detail-design-skill/) 后，可以这样提问：

- “使用 `detail-design-reference` Skill，帮我检查这个设置页的设计规范和可访问性问题，并按严重程度列出建议。”
- “使用 `detail-design-reference` Skill，评估这段 onboarding 流程，找出可以优化的交互、文案和反馈状态；每条建议附上资料库依据。”
- “使用 `detail-design-reference` Skill，针对我的移动端表单提出改进建议，重点检查错误提示、输入体验和键盘操作。”
- “从资料库中找出和空状态、加载状态、动效相关的实践，比较它们的适用场景，再给我的产品提出方案。”
- “根据这些设计稿截图，检查视觉层级、对齐、信息密度和交互状态；区分资料库中的原文依据与新的推断。”
- “搜索资料库里与无障碍、微文案或性能优化有关的条目，汇总成一份可执行的设计评审清单。”

把最后的“设置页 / onboarding / 截图 / 设计规范”替换成你的产品上下文即可。Agent 能否直接识图，取决于你使用的 Agent 和运行环境。

## 安装与使用

Skill 位于 [`detail-design-skill/`](detail-design-skill/)。将该目录复制或安装到你的 Agent 所支持的 Skills 目录，然后在对话中点名 `detail-design-reference`。

也可以把 `detail-design-skill/` 目录提供给支持本地 Skill / Agent instructions 的工具。具体安装位置依工具而异，请以相应 Agent 的 Skills 文档为准。

## 资料结构

```text
.
├── README.md                        # 默认中文说明
├── README.en.md                     # English README
├── scripts/                         # 更新与验证脚本
│   ├── update_archive.py
│   └── verify_archive.py
└── detail-design-skill/             # 可直接提供给 Agent 的 Skill
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
        ├── catalog.json
        ├── entries/<slug>.json
        ├── site-pages.json
        └── capture-manifest.json
```

大体量正文按 slug 分文件保存，便于 Agent 按需读取，避免每次把整个资料库塞进上下文。`detail-design-skill/references/catalog.json` 用于先搜索和定位，命中后再读取对应 `detail-design-skill/references/entries/<slug>.json`。如果源站对某条内容返回空正文，归档会保留源站的空值，不会用摘要伪装成完整正文。

## 更新资料库

需要 Python 3，无第三方 Python 依赖。在仓库根目录手动刷新：

```bash
python3 scripts/update_archive.py
```

脚本会遍历源站公开分页，拉取每条详情与收录的站点页面，校验响应后再发布；遇到不完整数据会中止并保留旧归档。内容无变化时不会产生提交。有变化时，脚本会在 Git 仓库中创建自动更新提交，并推送当前分支到其已配置的 upstream。首次使用前需要先配置 Git remote、upstream 和可用的推送凭据；没有这些配置时脚本会报告错误，归档更新仍保留在本地，不会回滚已验证的数据。

初始化后可按需设置远端：

```bash
git remote add origin <你的 GitHub 仓库地址>
git push -u origin main
```

