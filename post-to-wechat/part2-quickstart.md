---
title: "跟鬼哥一起学OpenClaw（二）：上手篇"
summary: "心智模型建立好了，现在动手。15 分钟装好 Gateway，连通第一个聊天渠道，从「看懂了」变成「跑起来了」。"
author: 鬼哥
coverImage: /Users/li.luo/dev/git/learn-claw/book/part2-quickstart/images/part2-index.jpg
---

# 第二部分：上手篇

心智模型建立好了，现在动手。

这一部分只有一个目标：让你的 OpenClaw **真正跑起来**，并且能从你日常使用的聊天工具里和 AI 对话。不是在文档里读懂，而是在终端里装好、在手机上测通。

两章内容，按顺序来：

![](/Users/li.luo/dev/git/learn-claw/book/part2-quickstart/images/part2-index.jpg)

**本部分包含两章：**

- **第3章** 从零开始安装 OpenClaw，完成引导向导，配置第一个 AI 模型，启动 Gateway，通过 Web Dashboard 完成第一次对话。
- **第4章** 把 AI 接入你已有的聊天工具——飞书机器人配置详解，其他渠道速览。章末你应该能从手机上直接跟 AI 发消息。

---

# 第3章：安装与启动——15 分钟跑起来

这一章结束的时候，你会拥有一个真正运行在本地的 OpenClaw 实例，能通过 Web 界面和 AI 完成第一次对话。

不需要 Docker，不需要数据库，不需要云服务账号（模型 API Key 除外）。就是一个跑在你电脑上的进程。

准备好了？开始。

![](/Users/li.luo/dev/git/learn-claw/book/part2-quickstart/images/ch03-install.jpg)

---

## 第一步：检查环境

OpenClaw 基于 Node.js 运行。打开终端，先确认版本：

```bash
node --version
```

你需要看到 `v22.x.x` 或更高版本。官方推荐 Node 24，Node 22 LTS 也完全支持。

**⚠️ 踩坑提醒**

如果版本低于 22，后续安装会报错，而且错误信息不一定直白。先升级再继续。

推荐用 [nvm](https://github.com/nvm-sh/nvm) 管理 Node 版本，一行命令切换，不影响系统其他项目：
```bash
nvm install 24
nvm use 24
```

npm 一般随 Node 一起安装，也顺手检查一下：

```bash
npm --version
```

有输出就行，版本无特殊要求。

---

## 第二步：安装 OpenClaw

**macOS / Linux：**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Windows（PowerShell）：**

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

脚本会自动下载最新版本，安装到系统路径。安装完成后，验证一下：

```bash
openclaw --version
```

能看到版本号，说明安装成功了。

**ℹ️ 其他安装方式**

如果你习惯用 Docker、Nix 或者想部署到服务器，官方文档的 [Install](https://docs.openclaw.ai/install) 章节有对应的详细指引，包括 Docker、Kubernetes、Railway、Fly.io 等平台的部署方案。本书聚焦本地安装，服务器部署不展开讲。

---

## 第三步：运行引导向导

这是整个安装过程最重要的一步。运行：

```bash
openclaw onboard --install-daemon
```

`--install-daemon` 的意思是：把 Gateway 注册为系统服务，开机自动启动。强烈建议加上这个参数——你不会希望每次重启电脑都要手动启动 Gateway 的。

向导会依次问你几个问题，我们逐一解释：

### 选择 AI 模型提供商

向导会让你选一个 AI 模型的来源。这里先选一个能用的，后续随时可以改。

- **Anthropic（Claude）**：效果最好，需要 API Key
- **OpenAI（GPT）**：同样优秀，需要 API Key
- **Ollama（本地模型）**：免费，完全离线，但需要先安装 Ollama 并下载模型

三条路的具体配置方法在下一步详细说明。

### 配置 Workspace 目录

Workspace 是 AI 的文件柜（第2章介绍过），向导会问你放在哪里。

直接回车接受默认值 `~/.openclaw/workspace` 即可。除非你有特殊需求，不建议改。

### 是否配置渠道（Channel）

向导会问要不要现在连接一个聊天渠道（飞书、Discord 等）。

**这里选"跳过"**。渠道配置有独立的步骤，第4章专门来讲。现在先把 Gateway 跑起来，渠道后面加。

**📌 为什么这样设计？**

向导之所以叫 `onboard`（而不是 `install`），是因为它做的不只是安装——它在帮你完成一次"入职"：配置认证、初始化 Workspace、建立系统服务。这个过程只需要走一次。

---

## 第四步：配置 AI 模型

根据你在向导里的选择，按对应的路径操作。

### 路径 A：使用 Anthropic Claude

在 [Anthropic Console](https://console.anthropic.com) 注册账号，创建一个 API Key。然后配置：

```bash
openclaw models auth anthropic
```

按提示粘贴你的 API Key。完成后验证：

```bash
openclaw models list
```

能看到 Claude 系列模型，说明认证成功。

### 路径 B：使用 OpenAI GPT

在 [OpenAI Platform](https://platform.openai.com) 获取 API Key，然后：

```bash
openclaw models auth openai
```

同样粘贴 Key，`openclaw models list` 验证。

### 路径 C：使用 Ollama 本地模型（完全免费离线）

先安装 Ollama（如果还没装）：

```bash
# macOS
brew install ollama

# 或直接从官网下载：https://ollama.com
```

下载一个模型，推荐从 Llama3 开始：

```bash
ollama pull llama3.2
ollama serve  # 启动 Ollama 服务
```

OpenClaw 会自动检测本地运行的 Ollama，无需额外配置。

**⚠️ 踩坑提醒**

Ollama 本地模型的效果和云端模型有明显差距，尤其在复杂推理和中文理解上。建议入门阶段先用云端模型，熟悉了 OpenClaw 的整体流程后再试本地模型。

---

## 第五步：启动并验证

向导完成后，Gateway 应该已经作为系统服务在后台运行了。检查状态：

```bash
openclaw gateway status
```

你应该看到类似这样的输出：

```
Runtime:    running
RPC probe:  ok
Port:       18789
Uptime:     2m 34s
```

`Runtime: running` 和 `RPC probe: ok` 是关键，有这两行说明 Gateway 健康运行中。

接下来，打开 Web 控制台：

```bash
openclaw dashboard
```

这条命令会自动在浏览器里打开 `http://127.0.0.1:18789/`，你会看到 OpenClaw 的 Web 界面——聊天窗口、状态信息、配置入口都在这里。

**⚠️ 踩坑提醒**

如果浏览器打开是空白页或者报"无法连接"，通常有两个原因：

1. **Gateway 没有正常启动**：运行 `openclaw gateway start` 手动启动，或检查 `openclaw logs` 看报错
2. **端口被占用**：默认端口是 18789，如果被其他程序占用，Gateway 会启动失败。可以在配置里改端口，或者先关掉占用 18789 的进程

---

## 动手练习：第一次对话

Gateway 跑起来了，Dashboard 打开了，现在做一件事：

在 Web 聊天窗口里，发送这条消息：

```
你好！请做个自我介绍，告诉我你是谁，你能帮我做什么。
```

如果一切正常，你会收到 AI 的回复。它可能还没什么"个性"——那是因为我们还没有编辑 Workspace 里的文件。这是下一章的任务。

现在，你只需要确认：**它真的回复了**。这意味着完整的链路——Gateway → 模型提供商 → 回复——都通了。

**📌 如果它没有回复**

先别慌。运行 `openclaw logs --follow`，实时查看 Gateway 的日志，通常能直接看到哪里出了问题。最常见的原因是 API Key 配置有误，或者网络无法连接到模型服务商。

---

**📌 本章检查清单**

- `openclaw gateway status` 输出的 `Runtime` 和 `RPC probe` 都是 ok 状态了吗？
- `openclaw dashboard` 能成功打开 Web 界面吗？
- AI 回复了你的自我介绍请求吗？

---

# 第4章：连接你的第一个聊天渠道

上一章，你通过浏览器的 Web 界面和 AI 完成了第一次对话。这很好，但说实话——有多少人愿意专门打开一个网页来找 AI 聊天？

真正让 AI 助手融入日常生活的方式，是让它住进你**已经在用的聊天工具**里。在飞书里直接发消息给 AI，得到秒回——就像找同事沟通一样自然。

这一章，我们来完成这个连接。

![](/Users/li.luo/dev/git/learn-claw/book/part2-quickstart/images/ch04-first-channel.jpg)

---

## 渠道的本质

回顾一下第2章的类比：渠道是 Gateway 上的插口，飞书是一个插头，Discord 是另一个。

更具体地说：渠道连接建立之后，你在那个 App 里发给 Bot 的每一条消息，都会被路由到 OpenClaw 的 AI 处理，然后 AI 的回复会通过同一个渠道发回来。从你的角度看，就是在和一个聊天联系人对话。

OpenClaw 目前支持超过 20 个渠道，我们从对国内用户最友好的飞书开始。

---

## 飞书：对国内用户最友好的渠道

飞书是国内企业用户使用最广泛的协作工具之一，也是 OpenClaw 支持的渠道里对国内用户最友好的——不需要翻墙，不需要备用手机号，不需要扫码配对，全程在飞书开放平台上操作。

接入分四步：创建应用 → 开启机器人 → 填写配置 → 重启测试。

### 第一步：在飞书开放平台创建应用

打开 [飞书开放平台](https://open.feishu.cn/app)，用飞书账号登录，点击右上角**"创建企业自建应用"**。

填写应用名称（比如 `AI 助手`）和描述，点击确认。创建成功后，进入应用管理页面，顶部就有 **App ID** 和 **App Secret**——先复制保存好。

**⚠️ 踩坑提醒**

如果你没有企业飞书账号，可以在飞书里创建一个测试企业（免费）。个人版飞书账号无法使用开放平台的自建应用功能。

### 第二步：开启机器人能力并配置权限

在应用管理页面，点击左侧菜单**"添加应用能力"**，选择**"机器人"**，点击开启。

然后进入**"权限管理"**，搜索并添加以下权限：

- `im:message`（发送和接收消息的基础权限）
- `im:message.group_at_msg:readonly`（如果你需要在群里 @ 机器人触发 AI）

### 第三步：发布应用

进入**"版本管理与发布"**，点击**"创建版本"**，填写版本号（比如 `1.0.0`），点击**"保存并发布"**。

企业自建应用默认免审核，发布后立即生效。

### 第四步：填写配置，重启 Gateway

打开 `~/.openclaw/openclaw.json`，在 `channels` 字段里添加飞书配置：

```json
{
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }
  }
}
```

把 `appId` 和 `appSecret` 替换为你刚才复制的实际值，然后重启 Gateway：

```bash
openclaw gateway restart
```

**📌 为什么不需要配置回调地址？**

OpenClaw 使用飞书的 **WebSocket 长连接**模式接收消息——Gateway 主动向飞书服务器建立连接，飞书把消息推过来。这意味着你不需要公网 IP，不需要配置 Webhook 回调地址，在家里的局域网里就能正常工作。

### 第五步：测试

在飞书里搜索你创建的机器人名称，找到后发一条消息：

```
你好！
```

如果 AI 回复了，恭喜——飞书渠道配通了。

**⚠️ 踩坑提醒**

如果没有收到回复，先检查以下几点：

1. 应用是否已发布（未发布的版本权限不生效）
2. App ID 和 App Secret 是否填写正确（注意复制时有没有多余空格）
3. 运行 `openclaw gateway logs | grep feishu` 查看是否有报错信息

---

## 其他渠道速览

OpenClaw 支持的渠道远不止飞书。下表列出了常用渠道的基本情况：

| 渠道 | 上手难度 | 适用场景 | 参考文档 |
|---|---|---|---|
| Discord | ★★☆ 中 | 服务器协作、开发者社群 | [官方文档](https://docs.openclaw.ai/channels/discord) |
| Slack | ★★☆ 中 | 工作团队、企业内部 | [官方文档](https://docs.openclaw.ai/channels/slack) |
| Telegram | ★☆☆ 易 | 个人用户，需要科学上网 | [官方文档](https://docs.openclaw.ai/channels/telegram) |
| iMessage | ★★★ 较难 | macOS 用户，需配合 BlueBubbles | [官方文档](https://docs.openclaw.ai/channels/imessage) |
| Signal | ★★★ 较难 | 注重隐私，需安装 signal-cli | [官方文档](https://docs.openclaw.ai/channels/signal) |
| Matrix | ★★★ 较难 | 开源去中心化 IM | [官方文档](https://docs.openclaw.ai/channels/matrix) |
| Line | ★★☆ 中 | 东南亚、日本用户 | [官方文档](https://docs.openclaw.ai/channels/line) |

各渠道的配置方式大同小异：申请对应平台的 Bot 账号或 Token，填入 `openclaw.json` 的 `channels` 字段，重启 Gateway。官方文档里每个渠道都有详细的步骤说明。

---

## 多渠道并行

OpenClaw 支持同时连接多个渠道——飞书、Discord、Slack 可以同时开着，消息默认都路由到同一个 AI 实例。

配置文件里把多个渠道并排写就行：

```json
{
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "discord": {
      "token": "你的DiscordBotToken"
    }
  }
}
```

这意味着你可以在飞书里和 AI 聊，也可以在 Discord 里，AI 都会响应——但它们共享同一个对话上下文（同一个"大脑"）。

如果你希望不同渠道对应不同的 AI 人格、不同的模型，那是第13章"多智能体"要解决的问题，我们到时候再说。

---

## 动手练习

连上飞书渠道之后，做一个小测试：

发送这条消息给你的 AI：

```
帮我用三句话介绍一下你自己，然后告诉我现在几点了。
```

如果 AI 不仅回了自我介绍，还正确报出了当前时间——说明 AI 不只是在"聊天"，它已经能感知外部信息了。

**📌 本章检查清单**

- 飞书开放平台的应用已创建并发布了吗？
- App ID 和 App Secret 正确填入配置文件了吗？
- 从飞书发消息，AI 能正常回复吗？