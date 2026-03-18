# 跟鬼哥一起学 OpenClaw

> 从零开始，系统掌握本地优先的个人 AI 助手平台。

在线阅读：**https://luoli523.github.io/learn-claw/**

## 内容简介

本书共 18 章 + 4 篇附录，按「认知 → 上手 → 核心 → 能力 → 进阶 → 实战」六个阶段循序渐进：

| 部分 | 章节 | 主题 |
|------|------|------|
| 第一部分：认知篇 | 第 1–2 章 | 建立心智模型，理解架构与设计哲学 |
| 第二部分：上手篇 | 第 3–4 章 | 安装 Gateway，连通第一个渠道 |
| 第三部分：核心篇 | 第 5–7 章 | Workspace、记忆系统、会话管理 |
| 第四部分：能力篇 | 第 8–10 章 | 内置工具、Skill 生态、安全防线 |
| 第五部分：进阶篇 | 第 11–14 章 | 定时任务、Webhook、多智能体、设备节点 |
| 第六部分：实战篇 | 第 15–18 章 | 四个完整项目：个人助理、浏览器自动化、团队协作、智能家居 |

## 本地开发

```bash
npm install
npm run docs:dev      # 启动开发服务器 http://localhost:5173/learn-claw/
npm run docs:build    # 构建静态文件
npm run docs:preview  # 预览构建产物
```

## 技术栈

- [VitePress](https://vitepress.dev/) 静态站点生成
- [Waline](https://waline.js.org/) 评论系统
- GitHub Actions 自动部署到 GitHub Pages
