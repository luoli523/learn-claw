# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

这是《跟鬼哥一起学OpenClaw》一书的写作仓库，使用 VitePress 构建，托管在 GitHub Pages。

## 开发命令

```bash
npm install          # 安装依赖（首次）
npm run docs:dev     # 启动本地预览（热更新）http://localhost:5173/learn-claw/
npm run docs:build   # 构建静态文件
npm run docs:preview # 本地预览构建产物
```

## 目录结构

书稿全部在 `book/` 目录下，按部分和章节组织：
- `book/.vitepress/config.ts` — 站点配置（标题、导航、侧边栏）
- `book/index.md` — 网站首页
- `book/part1-cognition/` 至 `book/part6-projects/` — 六个部分的章节
- `book/appendix/` — 附录

章节文件命名规则：`ch{序号}-{slug}.md`，例如 `ch01-what-is-openclaw.md`。

## 部署

推送到 `main` 分支后，GitHub Actions 自动构建并部署到：
`https://luoli523.github.io/learn-claw/`

## Important Rules

1. Before writing any code, describe your approach and wait for approval.
2. If the requirements I give you are ambiguous, ask clarifying questions before writing any code.
3. After you finish writing any code, list the edge cases and suggest test cases to cover them.
4. If a task requires changes to more than 3 files, stop and break it into smaller tasks first.
5. When there's a bug, start by writing a test that reproduces it, then fix it until the test passes.
6. Every time I correct you, reflect on what you did wrong and come up with a plan to never make the same mistake again.
