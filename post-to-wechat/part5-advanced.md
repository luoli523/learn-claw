---
title: "跟鬼哥一起学OpenClaw（五）：进阶篇"
summary: "让 AI 从被动响应变成主动出击：心跳定时、Webhook 触发、多智能体人格、设备节点感知——四章解锁进阶能力。"
author: 鬼哥
coverImage: /Users/li.luo/dev/git/learn-claw/book/part5-advanced/images/part5-index.jpg
---

# 第五部分：进阶篇

能力篇解决的是"AI 能做什么"，进阶篇解决的是"AI 能主动做什么"。

一个真正有用的 AI 助手，不应该只是等你开口。它应该在每天早上 8 点把日报推送给你，在 CI 构建失败时第一时间通知你，在你说"帮我盯着这件事"后真的一直盯着——不需要你反复提醒，不需要你一直坐在键盘前。

这一部分的四章，覆盖了 OpenClaw 最能体现"主动性"的能力：

![](/Users/li.luo/dev/git/learn-claw/book/part5-advanced/images/part5-index.jpg)

**本部分包含四章：**

- **第11章** 讲解 Heartbeat 心跳和 Cron 定时任务——AI 有了自己的时间感，能按计划主动工作，把结果推送到你的聊天渠道。
- **第12章** 讲解 Webhook 事件触发——外部系统（邮件、CI、监控）发生变化时，立刻叫醒 AI 处理，而不是等到下一个定时周期。
- **第13章** 讲解多智能体架构——一个 Gateway 里运行多个独立的 AI 人格，按渠道、按发送者、按场景路由消息，各司其职。
- **第14章** 讲解设备节点——把手机和电脑配对为 AI 的"手脚"，赋予它访问摄像头、获取位置、执行本地命令的物理能力。

---

# 第11章：心跳与定时任务——让 AI 主动找你

到目前为止，这本书里的 AI 一直处于"被动模式"：你说话，它回应；你不说话，它沉默。

这一章，情况要改变了。

主动型的 AI 助手和被动型的本质区别在于：**它有自己的时间感**——知道现在几点，知道接下来该做什么，不需要等你开口就能给你发消息。OpenClaw 通过两个机制实现这一点：**Heartbeat（心跳）** 和 **Cron（定时任务）**。

![](/Users/li.luo/dev/git/learn-claw/book/part5-advanced/images/ch11-automation.jpg)

---

## Heartbeat：30 分钟的巡逻

Heartbeat 是 OpenClaw 内置的周期触发机制，默认每 **30 分钟**触发一次。

每次触发时，Gateway 会发起一个静默的 AI 对话，把 `HEARTBEAT.md` 的内容作为指令传入。AI 读完指令，决定要不要做什么——如果有需要通知你的事，它就会发消息；如果一切正常，它什么也不说，悄悄等下一个 30 分钟。

就像给 AI 设了一个轻柔的闹钟：每 30 分钟它会睁开眼，扫一眼 HEARTBEAT.md，然后要么继续睡，要么给你发条消息说"嘿，你今天有个 3 点的会，别忘了"。

### 编写 HEARTBEAT.md

`HEARTBEAT.md` 放在你的 Workspace 根目录下。内容是给 AI 的巡逻指令——告诉它每次醒来应该检查什么、在什么情况下通知你：

```markdown
# 心跳指令

每次心跳时，按以下步骤检查：

## 日程检查
查看今天的日历（如果有 Google Calendar Skill），
如果接下来 2 小时内有会议，提前 30 分钟提醒我。

## 天气检查
查询当前位置的天气预报，
如果今天下午有降雨概率超过 60%，提醒我出门带伞。

## 默认行为
如果以上都没有需要提醒的，不要发任何消息，保持安静。
```

**几个写好 HEARTBEAT.md 的原则：**

1. **明确触发条件**：不要写"检查天气"，要写"如果有降雨概率超过 60% 才通知我"——否则 AI 每次都会发天气，很快变成噪音
2. **永远写"默认沉默"**：在末尾加一行"如果没有需要通知的事，不要发消息"，防止 AI 每次都打扰你
3. **从简单开始**：先写 1-2 条指令，确认工作正常后再添加更多

**📌 Heartbeat vs Cron 怎么选？**

Heartbeat 适合"**有条件才通知**"的模糊检查——比如检查邮件、查天气、看日程，只在有需要时才发消息。

Cron 适合"**到时间一定执行**"的精确任务——比如每天早上 8 点发早报，不需要条件判断，时间到了就跑。

---

## Cron：精确调度的定时任务

Heartbeat 是模糊的"有事再说"，Cron 是精确的"到点必做"。

Cron 任务运行在 Gateway 内部，和你的主对话完全独立——即使你几天没有开启任何对话，Cron 任务照常运行。任务配置持久化存储，Gateway 重启后自动恢复。

### 三种调度格式

**一次性任务（at）：**
```bash
openclaw cron add \
  --name "季度报告提醒" \
  --at "2026-04-01T09:00:00+08:00" \
  --session main \
  --system-event "提醒我今天需要提交季度报告"
```

指定一个未来的时间点，触发后自动删除。

**固定间隔（every）：**
```bash
openclaw cron add \
  --name "每小时检查" \
  --every "1h" \
  --session isolated \
  --message "检查一下有没有需要处理的紧急事项"
```

每隔固定时间运行一次，持续有效。

**Cron 表达式：**
```bash
openclaw cron add \
  --name "每日早报" \
  --cron "0 8 * * *" \
  --session isolated \
  --message "生成今天的日程和任务摘要" \
  --announce --channel feishu
```

如果你用过 Linux 的 crontab，看到这五个字段会感到亲切；如果没用过，别怕，记住最常用的几个：

| Cron 表达式 | 含义 |
|---|---|
| `0 8 * * *` | 每天早上 8:00 |
| `0 9 * * 1` | 每周一早上 9:00 |
| `0 */2 * * *` | 每 2 小时 |
| `30 18 * * 1-5` | 周一至周五下午 18:30 |

OpenClaw 支持 IANA 标准时区，添加任务时用 `--timezone Asia/Shanghai` 指定，避免时区混乱。

---

## 三种执行模式

这是 Cron 任务里最需要理解的概念：任务在哪里运行，决定了它的行为和影响范围。

| 模式 | 命令参数 | 含义 | 适合场景 |
|---|---|---|---|
| **主会话** | `--session main` | 注入主会话的 Heartbeat 队列，和你的日常对话共享上下文 | 需要访问近期对话记忆的任务 |
| **隔离会话** | `--session isolated` | 每次运行在全新的独立会话里，不污染主对话历史 | 大多数定时任务的首选 |
| **自定义会话** | `--session "daily-standup"` | 绑定到一个具名的持久会话，每次运行都能访问之前的运行记录 | 需要积累上下文的任务（如每日站会摘要） |

**推荐默认使用隔离会话**。它干净、独立，不会让 AI 的定时输出和你的聊天历史混在一起，出问题时也容易排查。

---

## 推送到聊天渠道

Cron 任务默认在后台静默运行，结果不主动通知你。加上 `--announce` 参数，任务完成后会把结果推送到指定的聊天渠道：

```bash
openclaw cron add \
  --name "每日早报" \
  --cron "0 8 * * *" \
  --timezone "Asia/Shanghai" \
  --session isolated \
  --message "用简洁的格式列出今天的日程、天气和需要注意的事项" \
  --announce \
  --channel feishu
```

支持推送的渠道：飞书、Slack、Discord、Signal、iMessage、Mattermost。

---

## CLI 速览

管理 Cron 任务的常用命令：

```bash
# 查看所有任务
openclaw cron list

# 查看某个任务的运行历史
openclaw cron runs --id <jobId> --limit 10

# 暂停一个任务
openclaw cron pause --id <jobId>

# 恢复一个任务
openclaw cron resume --id <jobId>

# 删除一个任务
openclaw cron remove --id <jobId>
```

---

## 动手练习：创建每日早报任务

我们来创建一个每天早上 8 点运行的日报任务，结果推送到飞书。

**第一步**：创建任务

```bash
openclaw cron add \
  --name "每日早报" \
  --cron "0 8 * * *" \
  --timezone "Asia/Shanghai" \
  --session isolated \
  --message "请生成今天的早报，包含：
1. 今天的日期和星期
2. 如果有 web_search 工具，搜索今天最重要的科技新闻（3条）
3. 今天剩余的工作时间提醒（如果现在是工作日）
保持简洁，控制在 200 字以内。" \
  --announce \
  --channel feishu
```

**第二步**：验证任务已创建

```bash
openclaw cron list
```

你应该能在列表里看到"每日早报"任务，状态为 `active`。

**第三步**：立即触发一次测试

不想等到明天早上 8 点才知道效果，可以手动触发：

```bash
openclaw cron run --id <jobId>
```

几秒后，检查你的飞书，应该能收到 AI 发来的早报。

---

**📌 本章检查清单**

- 你知道 Heartbeat 和 Cron 的适用场景区别吗？（模糊检查 vs 精确调度）
- 你写了一个 HEARTBEAT.md，并且在末尾加了"没有需要通知的事就保持沉默"了吗？
- 你成功创建了一个 Cron 任务，并通过 `openclaw cron run` 手动触发测试了吗？

---

# 第12章：Webhook 与外部触发——连接世界的钩子

上一章的 Cron 任务是提前排好的课程表——无论外面发生什么，时间到了就执行。

Webhook 是另一种逻辑：**门铃**。

不管现在几点，只要外面有动静——收到了一封重要邮件、CI 构建失败了、某个监控指标超阈值了——立刻按响门铃，让 AI 马上处理。

这两者加在一起，就构成了 OpenClaw 自动化的完整图景：时间驱动（Cron）+ 事件驱动（Webhook）。

![](/Users/li.luo/dev/git/learn-claw/book/part5-advanced/images/ch12-webhooks.jpg)

---

## 启用 Webhook

Webhook 默认是关闭的，需要手动开启。在 `openclaw.json` 里添加：

```json
{
  "hooks": {
    "enabled": true,
    "token": "your-secret-token-here"
  }
}
```

`token` 是必填的，不能留空。它是外部系统访问你的 Webhook 端点的凭证。

**⚠️ Token 安全**

Webhook Token 就像你家的门铃密码——设一个有足够长度的随机字符串，不要用 `1234`，不要提交到 git 仓库，不要写在便利贴上贴显示器旁边。

生成一个随机 Token：
```bash
openssl rand -hex 32
```

重启 Gateway 后，Webhook 端点就绪，默认在 `http://127.0.0.1:18789/hooks/`。

---

## 两个核心端点

OpenClaw 提供两个主要的 Webhook 端点，适合不同的使用场景。

### POST /hooks/wake（轻量触发）

`/hooks/wake` 往你的主会话注入一个**系统事件**，AI 在下次心跳时处理它。

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "收到一封来自老板的邮件，主题是：下周一项目评审",
    "mode": "now"
  }'
```

两个参数：
- `text`：事件描述，AI 会基于这段文字决定如何响应
- `mode`：`now`（立即处理）或 `next-heartbeat`（下次心跳时处理）

**适合用 `/hooks/wake` 的场景：** 通知类事件——"你有新邮件"、"构建完成了"、"有人在 GitHub 上给你的 issue 回复了"。事件本身很简单，让 AI 决定后续动作。

### POST /hooks/agent（重量级处理）

`/hooks/agent` 立即启动一个**隔离的 Agent 会话**来处理任务，可以指定模型、设置超时、把结果推送到渠道。

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "分析下面这份错误日志，找出根本原因，给出修复建议：\n[ERROR] Connection timeout...",
    "name": "log-analysis",
    "channel": "feishu",
    "timeoutSeconds": 120
  }'
```

主要参数：

| 参数 | 说明 |
|---|---|
| `message` | 发给 AI 的提示词（必填） |
| `name` | 任务名，用于日志识别 |
| `agentId` | 指定由哪个 Agent 处理（多 Agent 场景） |
| `model` | 覆盖默认模型 |
| `channel` | 把结果推送到哪个渠道 |
| `timeoutSeconds` | 超时限制 |

**适合用 `/hooks/agent` 的场景：** 需要 AI 深度处理的任务——分析日志、摘要长文档、执行一系列操作。

---

## 真实场景：Gmail 邮件触发 AI 摘要

来看一个完整的实际例子，把 Gmail 新邮件和 OpenClaw 连起来。

**目标**：收到新邮件时，AI 自动总结邮件内容，发到飞书。

### 第一步：在 Gmail 设置转发或推送

Gmail 支持 Pub/Sub 推送（需要 Google Cloud 账号），或者更简单的方案：用 Zapier / Make 等自动化工具，在 Gmail 收到邮件时调用 Webhook。

Zapier 的配置大致是：
```
触发器：Gmail - 收到新邮件
动作：Webhooks - POST 请求
URL：http://<你的公网IP>:18789/hooks/agent
Header：Authorization: Bearer your-token
Body：
{
  "message": "请摘要这封邮件：发件人 {{from}}，主题：{{subject}}，内容：{{body}}",
  "channel": "feishu",
  "name": "gmail-summary"
}
```

### 第二步：把 Gateway 暴露到公网

本地的 `127.0.0.1` 外部无法访问。有几种方式让 Webhook 可以被外部调用：

- **Tailscale**：推荐方案，在你的机器和服务器之间建立加密隧道，安全且简单
- **SSH 反向隧道**：临时方案，在有公网 IP 的服务器上打通隧道
- **直接部署到 VPS**：把 Gateway 部署到云服务器，直接暴露端口

**📌 本地测试时**

在本地开发和测试阶段，不需要公网暴露。外部触发用 curl 模拟，验证流程没问题后再考虑打通真实的触发源。

### 第三步：测试链路

用 curl 模拟一次 Gmail 触发：

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请摘要这封邮件：发件人 boss@company.com，主题：下周一项目评审，内容：请各位于下周一上午10点参加Q1项目评审会议，请提前准备各自模块的进度报告。",
    "channel": "feishu",
    "name": "gmail-summary-test"
  }'
```

几秒后，飞书应该收到 AI 发来的摘要。

---

## 自定义映射

外部系统发来的 Webhook 数据格式千奇百怪，不一定符合 OpenClaw 的标准格式。`hooks.mappings` 允许你把自定义路径 `/hooks/<name>` 映射到标准处理逻辑：

```json
{
  "hooks": {
    "enabled": true,
    "token": "your-token",
    "mappings": {
      "github-pr": {
        "kind": "agentTurn",
        "message": "GitHub 有新的 PR 需要 review",
        "channel": "feishu"
      }
    }
  }
}
```

配置后，`POST /hooks/github-pr` 就会触发一个 Agent 任务，不需要调用方关心具体的 payload 格式。

OpenClaw 还内置了一些常用的预设映射（如 Gmail Pub/Sub 格式），无需手动配置解析逻辑。

---

## 安全注意事项

Webhook 端点本质上是一个开放的 HTTP 接口，需要认真对待安全：

**认证**：所有请求必须携带 Token，放在请求头里：
```
Authorization: Bearer your-token
# 或者
x-openclaw-token: your-token
```
不支持 URL 参数传 Token（`?token=xxx` 这种方式会被拒绝）。

**访问控制**：默认情况下 Gateway 只监听 `127.0.0.1`，外部无法直接访问。如果需要外部触发，建议通过 Tailscale 或 VPN 而不是直接暴露端口。

**速率限制**：连续认证失败后会触发 `429 Too Many Requests`，防止暴力破解。

**多 Agent 场景**：如果你有多个 Agent，在配置里用 `allowedAgentIds` 限制 Webhook 只能触发特定 Agent，防止越权调用：

```json
{
  "hooks": {
    "allowedAgentIds": ["main", "assistant"]
  }
}
```

---

## 动手练习

不需要接任何外部服务，用 curl 直接测试本地的 Webhook。

**第一步**：确认 Webhook 已启用，Gateway 正在运行。

**第二步**：触发一个 `/hooks/wake` 事件：

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{"text": "这是一条来自外部系统的测试消息，请确认收到并回复。", "mode": "now"}'
```

观察你的主聊天渠道（飞书或 Web Dashboard），AI 应该很快会响应这条系统消息。

**第三步**：触发一个 `/hooks/agent` 任务：

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "用一句话解释什么是 Webhook，要幽默一点",
    "name": "webhook-test"
  }'
```

这次 AI 在隔离会话里处理，结果不会推送到渠道（没有指定 `channel`），但你可以通过 `openclaw logs` 看到执行记录。

---

**📌 本章检查清单**

- 你知道 `/hooks/wake` 和 `/hooks/agent` 的主要区别吗？（轻量通知 vs 重量处理）
- 你用 curl 成功触发了一次 Webhook，并看到 AI 响应了吗？
- 你的 Webhook Token 是随机生成的，而不是手打的简单字符串吗？

---

# 第13章：多智能体——一个 Gateway，多个 AI 人格

让一个 AI 人格处理所有事情，就像让一个人既当快递员又当外科医生——理论上都能做，但你真的想让同一个人在送完外卖之后直接给你做手术吗？

更实际的场景：你在飞书里跟 AI 闲聊今天吃什么，同时在 Discord 上请它帮你审阅一份技术方案。这两件事对 AI 的要求完全不同：一个需要轻松、快速、随意；另一个需要严谨、深入、专业。

同一个性格设定、同一个模型，很难同时做到两种截然不同的状态。

多智能体就是解法：**一个 Gateway，运行多个相互独立的 AI 人格，各司其职**。

![](/Users/li.luo/dev/git/learn-claw/book/part5-advanced/images/ch13-multi-agent.jpg)

---

## 两个驱动力

### 驱动力一：场景分离

不同的渠道、不同的任务需要不同的 AI：

- 飞书日常助理：随意、快速、会聊天，Workspace 里写的是轻松的性格设定
- Discord 深度分析：严谨、详细、工具齐全，配置了 exec 和 browser 工具
- Slack 技术机器人：只回答编程问题，其他一律拒绝

每个角色有自己独立的 Workspace（独立的 SOUL.md、MEMORY.md、AGENTS.md），完全隔离，互不影响。

### 驱动力二：成本优化

便宜的模型处理"今天吃什么"，贵的处理"帮我审这份合同"——这不是对 AI 的歧视，是合理的人力资源配置。

一个典型的搭配：
- 日常闲聊 → MiniMax 或 Qwen（成本极低，响应快）
- 复杂分析 → Claude Opus 或 GPT（效果好，但按量计费）

每个月下来，成本可以少一个数量级。

---

## 三个核心概念

在配置多智能体之前，先理清三个概念。它们是 OpenClaw 多 Agent 系统的基础。

### agentId：大脑的身份证

每个 Agent 有一个唯一的 `agentId`。它标识的是一个完整的"大脑"：

- 独立的 Workspace 目录（独立的 SOUL.md、MEMORY.md 等）
- 独立的 Auth（独立的模型凭证）
- 独立的 Session 存储（对话历史完全隔离）

两个 Agent 之间，**没有任何共享的上下文**——Agent A 完全不知道 Agent B 今天聊了什么。

### accountId：渠道账号的标识

一个渠道可以有多个账号。比如你有两个飞书机器人：一个用于个人，一个用于工作团队。每个机器人是一个独立的 `accountId`。

```
飞书个人助理      →  accountId: "feishu-personal"
飞书团队助理      →  accountId: "feishu-team"
Discord Bot       →  accountId: "discord-main"
```

### binding：消息的路由规则

`binding` 把"消息从哪里来"映射到"应该由哪个 Agent 处理"。

一条 binding 的基本结构：

```json
{
  "channel": "feishu",
  "accountId": "feishu-personal",
  "agentId": "casual"
}
```

意思是：飞书个人助理收到的消息，交给 `casual` 这个 Agent 处理。

---

## Binding 的路由优先级

当一条消息进来，Gateway 按以下优先级从高到低匹配 binding：

| 优先级 | 匹配条件 | 说明 |
|---|---|---|
| 1 | 精确的发送者 ID | 特定的某个人发来的 DM |
| 2 | 父级 peer（线程继承）| 回复某条消息时，继承原消息的 Agent |
| 3 | Discord Guild ID + 角色 | Discord 里特定身份的成员 |
| 4 | Discord Guild ID | 整个 Discord 服务器 |
| 5 | Slack Team ID | 整个 Slack 工作区 |
| 6 | 渠道账号（accountId）| 特定账号收到的所有消息 |
| 7 | 渠道（channel）| 来自特定渠道的所有消息 |
| 8 | 兜底默认 Agent | `agents.defaults` 配置 |

**同一优先级有多条 binding 匹配时，取配置文件里排在前面的那条。**

这意味着你可以做非常精细的控制：比如同一个飞书机器人，来自你家人的消息路由给"家庭助理 Agent"，来自你老板的消息路由给"工作助理 Agent"，其余的消息走默认 Agent。

---

## 典型配置示例

来看一个完整可用的配置，实现：
- 飞书 → 日常助理（便宜模型，轻松性格）
- Discord → 深度分析师（Opus 模型，严谨性格）

**第一步：创建两个独立的 Workspace**

```bash
# 日常助理的 Workspace
mkdir -p ~/.openclaw/workspace-casual
cat > ~/.openclaw/workspace-casual/SOUL.md << 'EOF'
## 性格
轻松随意，像朋友聊天。回复简短，不废话。
EOF

# 深度分析师的 Workspace
mkdir -p ~/.openclaw/workspace-analyst
cat > ~/.openclaw/workspace-analyst/SOUL.md << 'EOF'
## 性格
严谨专业，注重细节。回复结构清晰，有理有据。
遇到复杂问题时，先分解问题再逐步分析。
EOF
```

**第二步：更新 openclaw.json**

```json
{
  "agents": {
    "list": [
      {
        "id": "casual",
        "workspace": "~/.openclaw/workspace-casual",
        "model": {
          "primary": "minimax/abab6.5s-chat"
        }
      },
      {
        "id": "analyst",
        "workspace": "~/.openclaw/workspace-analyst",
        "model": {
          "primary": "anthropic/claude-opus-4-6"
        },
        "tools": {
          "profile": "coding"
        }
      }
    ]
  },
  "bindings": [
    {
      "channel": "feishu",
      "accountId": "feishu-casual",
      "agentId": "casual"
    },
    {
      "channel": "discord",
      "agentId": "analyst"
    }
  ],
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "discord": {
      "token": "your-discord-bot-token"
    }
  }
}
```

重启 Gateway，两个独立的 AI 就都跑起来了。

**📌 没有两个渠道怎么办？**

只有一个渠道也能测试多 Agent：用 Web Dashboard 测试一个 Agent，用飞书测试另一个。

---

## per-Agent 权限控制

多 Agent 场景下，每个 Agent 可以有完全独立的工具策略和沙箱配置：

```json
{
  "agents": {
    "list": [
      {
        "id": "casual",
        "tools": {
          "profile": "minimal"
        },
        "sandbox": {
          "mode": "all"
        }
      },
      {
        "id": "analyst",
        "tools": {
          "profile": "coding",
          "allow": ["browser"]
        },
        "sandbox": {
          "mode": "non-main"
        }
      }
    ]
  }
}
```

对外开放的 `casual` Agent 用最严格的限制：`minimal` 工具画像 + 全面沙箱。`analyst` Agent 只有你自己用，给了 `coding` 画像加 `browser` 工具。

这是多 Agent 架构最大的安全优势：**不同信任级别的 Agent，给不同的权限边界**，一刀切的全局配置永远无法做到这种精细程度。

---

## 动手练习

按照上面的典型配置示例，完成以下步骤：

1. 创建两个 Workspace 目录，写入不同风格的 SOUL.md
2. 在 `openclaw.json` 里配置两个 Agent，绑定到不同渠道
3. 重启 Gateway，确认两个 Agent 都正常运行：

```bash
openclaw gateway status
```

4. 发同一个问题给两个渠道：

```
你好，能简单介绍一下你自己吗？
```

观察两个 Agent 的回复风格——即使模型相同，不同的 SOUL.md 也会产生截然不同的回答风格；如果模型也不同，差异会更加明显。

---

**📌 本章检查清单**

- 你能说清楚 agentId、accountId、binding 三者的关系吗？
- 你知道当一条消息同时匹配多条 binding 时，Gateway 如何决定用哪条吗？
- 你配置了两个 Agent，并验证了它们的回复风格确实不同吗？

---

# 第14章：设备节点——给 AI 装上眼睛和手脚

想象一下，一个聪明绝顶的大脑，被装在一个密封的玻璃罐子里。

它能帮你分析股票、写代码、规划旅行——但它感知世界的唯一方式，就是你打进去的文字。你说"今天天气不错"，它信了；你说"我家门口来了一只奇怪的动物"，它只能靠想象。

这就是没有设备节点的 OpenClaw：大脑在线，感官缺席。

设备节点（Node）解决的就是这个问题：**把你的手机和电脑配对成 AI 的感官和肢体**。接上之后，AI 可以让手机拍张照片，可以要电脑截个屏，可以读取你的位置，可以在本地执行命令——它终于有了接触物理世界的能力。

![](/Users/li.luo/dev/git/learn-claw/book/part5-advanced/images/ch14-nodes.jpg)

---

## Node 是什么

Node 是一个运行在你设备上的轻量客户端（App 或后台程序），它和 Gateway 之间保持一条持久的 WebSocket 连接。

```
你的手机（Node）
      ↕ WebSocket 长连接
Gateway（大脑）
      ↕
AI 模型
```

每当 AI 需要调用设备能力时，Gateway 通过这条连接向 Node 发指令，Node 执行后把结果返回。整个过程对你来说透明——你问 AI "帮我看看桌上那张纸写的什么"，AI 调 Node 拍张照，分析，给你答案。

一台 Gateway 可以同时连多个 Node，比如同时连着你的 iPhone 和你的 MacBook，各司其职。

---

## 配对：三步连接

Node 和 Gateway 的连接需要先完成**一次性配对**，之后就会自动重连，不需要每次手动操作。

**第一步：生成配对码**

在安装了 Node 的设备上，打开 Node 应用，点击「连接到 Gateway」，它会显示一个 6 位配对码，比如 `847291`。

**第二步：在 Gateway 侧输入**

```bash
openclaw node pair --code 847291
```

或者在 Web Dashboard 的「设备节点」页面输入配对码。

**第三步：确认连接**

```bash
openclaw node list
```

成功后你会看到类似：

```
ID          名称            类型      状态      最后在线
node-a1b2   My iPhone 15    mobile    在线      刚刚
node-c3d4   MacBook Pro     desktop   在线      刚刚
```

配对信息持久保存，Gateway 重启后 Node 会自动重连。

---

## 能力矩阵

不同类型的 Node 提供不同的能力。

### 手机 Node（iOS / Android）

| 能力 | 工具调用 | 说明 |
|---|---|---|
| 拍照 | `node.camera` | 调用摄像头拍一张照片 |
| 位置定位 | `node.location` | 获取当前 GPS 坐标 |
| 推送通知 | `node.notify` | 在设备上弹出系统通知 |
| 读取联系人 | `node.contacts` | 搜索通讯录（需授权） |
| 读取短信 | `node.sms` | 读取收件箱（仅 Android） |

### 桌面 Node（macOS / Windows / Linux）

| 能力 | 工具调用 | 说明 |
|---|---|---|
| 截图 | `node.screenshot` | 截取当前屏幕 |
| 执行命令 | `node.exec` | 在本地 shell 执行命令 |
| 文件访问 | `node.fs` | 读写本地文件系统 |
| 剪贴板 | `node.clipboard` | 读取或写入剪贴板内容 |
| 应用控制 | `node.app` | 打开、关闭、激活应用程序 |

**⚠️ 权限需要手动授权**

Node 能力默认全部关闭，在 `TOOLS.md` 里按需开启，同时设备本身也需要给 Node 应用授予对应的系统权限（相机、位置、联系人等）。这是两道独立的开关——缺一道都不会工作。

---

## 在 TOOLS.md 里启用 Node 工具

Node 能力属于 `nodes` 工具组，需要在 Workspace 的 `TOOLS.md` 里显式列出：

```markdown
# 工具配置

## 启用的工具组

- runtime
- web
- nodes

## Node 工具配置

允许使用以下 Node 能力：
- node.camera（仅限已配对的手机）
- node.location
- node.screenshot（仅限已配对的桌面）
- node.notify
```

如果你有多个 Node，可以用 `nodeId` 指定哪个设备提供哪种能力，防止 AI 搞混：

```markdown
## Node 工具配置

- node.camera: node-a1b2（My iPhone 15）
- node.screenshot: node-c3d4（MacBook Pro）
```

---

## 场景一：让 AI 看一眼桌上的东西

最直观的用法：让手机 Node 拍张照，AI 分析图里的内容。

```
你（飞书）：帮我看看桌上这张收据，总金额是多少？

AI：好的，我来用你的手机拍一张。
    [调用 node.camera → 拍照 → 返回图片]
    收据显示总金额为 ¥386.50，商户是「顺丰超市」，日期 2026 年 3 月 18 日。
```

AI 自己决定要拍照，自己发出指令，自己分析结果，最后只给你一个干净的答案。

整个过程你除了开口问，什么都不用做——包括不需要手动拍照、不需要上传图片。

---

## 场景二：监控桌面，发现问题主动告诉你

结合 Heartbeat（第11章），可以让桌面 Node 定期截图，AI 检查是否有需要注意的情况：

```markdown
# HEARTBEAT.md

每次心跳：
1. 截取桌面截图（node.screenshot）
2. 检查是否有报错弹窗、构建失败通知、或需要操作的系统提示
3. 如果发现异常，把截图和描述发送给我；如果一切正常，保持沉默
```

这相当于给 AI 安了一双眼睛，一直盯着你的屏幕——但只在出问题的时候叫你，而不是每 30 分钟截图发给你看（那就变成噪音了）。

---

## 场景三：本地命令执行

桌面 Node 的 `node.exec` 能力让 AI 可以在你的本地机器上执行 shell 命令，这比第8章里的 `exec` 工具更进一步：

- `exec` 工具：在 Gateway 所在的机器上执行（可能是服务器）
- `node.exec`：在你指定的本地桌面 Node 上执行（你的开发机）

```
你：帮我看看我的 MacBook 上 ~/projects 目录有哪些项目

AI：[调用 node.exec → ls ~/projects]
    你目前有 7 个项目：
    - learn-claw（最近修改：今天）
    - my-blog（最近修改：3天前）
    ...
```

**📌 沙箱隔离依然有效**

Node 能力受到 Workspace 里 `sandbox` 配置的约束。如果你配置了沙箱模式，`node.exec` 执行的命令也会在相应的限制下运行。不会因为是"本地"执行就绕过安全约束。

---

## 多 Node 场景：手机 + 电脑协同

最有意思的场景，是两个 Node 配合起来：

```
你（飞书）：帮我把电脑屏幕上显示的代码，推送到手机上提醒我

AI：好的。
    [node.screenshot → MacBook Pro 截图]
    [node.notify → iPhone 15 推送通知，附带截图预览]
    已经截好图，并推送到你的 iPhone 了。
```

AI 在两台设备之间协调，你一个指令，它两头跑。

---

## 动手练习

**准备**：在你的手机或电脑上安装 OpenClaw Node 应用（在官网下载页可以找到对应平台的版本）。

**第一步**：完成配对

按照本章的三步流程，把 Node 连接到你的 Gateway。用 `openclaw node list` 确认设备出现在列表里，状态为「在线」。

**第二步**：在 TOOLS.md 里启用一个 Node 能力

根据你配对的设备类型，选择一个能力启用：
- 手机：`node.camera` 或 `node.notify`
- 桌面：`node.screenshot`

**第三步**：测试

发送一条消息给 AI，让它使用你刚启用的能力：

```
# 如果是手机 Node
帮我拍张照，看看我桌上有什么东西

# 如果是桌面 Node
截一张当前桌面的截图，简单描述一下屏幕上显示的内容
```

观察 AI 是否成功调用了设备能力，并给出了基于真实感知的回答。

---

**📌 本章检查清单**

- 你知道 Node 和 Gateway 之间是怎么建立连接的吗？（配对码 + WebSocket）
- 你知道启用 Node 能力需要在哪两个地方授权吗？（TOOLS.md + 设备系统权限）
- 你成功配对了至少一个 Node，并验证了它的某项能力正常工作吗？

---

## 进阶篇：小结

走到这里，你已经掌握了 OpenClaw 最能体现「主动性」的四个能力：

- **第11章**：Heartbeat + Cron，AI 有了时间感，会主动找你
- **第12章**：Webhook，外部世界发生变化时能第一时间叫醒 AI
- **第13章**：多 Agent，一个 Gateway 里多个 AI 人格各司其职
- **第14章**：设备节点，AI 长出了手脚，能感知和操控物理世界

这四章合在一起，描绘的是同一幅图景：一个真正「在线」的 AI 助手——不只是等你发消息，而是主动地、持续地、有感知地陪着你工作和生活。

下一部分是实战篇，我们会把学过的所有能力组合起来，从头到尾做出四个真实可用的项目。