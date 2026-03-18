# 第12章：Webhook 与外部触发——连接世界的钩子

上一章的 Cron 任务是提前排好的课程表——无论外面发生什么，时间到了就执行。

Webhook 是另一种逻辑：**门铃**。

不管现在几点，只要外面有动静——收到了一封重要邮件、CI 构建失败了、某个监控指标超阈值了——立刻按响门铃，让 AI 马上处理。

这两者加在一起，就构成了 OpenClaw 自动化的完整图景：时间驱动（Cron）+ 事件驱动（Webhook）。

![](./images/ch12-webhooks.webp)

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

::: warning Token 安全
Webhook Token 就像你家的门铃密码——设一个有足够长度的随机字符串，不要用 `1234`，不要提交到 git 仓库，不要写在便利贴上贴显示器旁边。

生成一个随机 Token：
```bash
openssl rand -hex 32
```
:::

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
    "channel": "telegram",
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

**目标**：收到新邮件时，AI 自动总结邮件内容，发到 Telegram。

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
  "channel": "telegram",
  "name": "gmail-summary"
}
```

### 第二步：把 Gateway 暴露到公网

本地的 `127.0.0.1` 外部无法访问。有几种方式让 Webhook 可以被外部调用：

- **Tailscale**：推荐方案，在你的机器和服务器之间建立加密隧道，安全且简单
- **SSH 反向隧道**：临时方案，在有公网 IP 的服务器上打通隧道
- **直接部署到 VPS**：把 Gateway 部署到云服务器，直接暴露端口

::: tip 本地测试时
在本地开发和测试阶段，不需要公网暴露。外部触发用 curl 模拟，验证流程没问题后再考虑打通真实的触发源。
:::

### 第三步：测试链路

用 curl 模拟一次 Gmail 触发：

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请摘要这封邮件：发件人 boss@company.com，主题：下周一项目评审，内容：请各位于下周一上午10点参加Q1项目评审会议，请提前准备各自模块的进度报告。",
    "channel": "telegram",
    "name": "gmail-summary-test"
  }'
```

几秒后，Telegram 应该收到 AI 发来的摘要。

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
        "channel": "telegram"
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

观察你的主聊天渠道（Telegram 或 Web Dashboard），AI 应该很快会响应这条系统消息。

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

::: tip 本章检查清单
- [ ] 你知道 `/hooks/wake` 和 `/hooks/agent` 的主要区别吗？（轻量通知 vs 重量处理）
- [ ] 你用 curl 成功触发了一次 Webhook，并看到 AI 响应了吗？
- [ ] 你的 Webhook Token 是随机生成的，而不是手打的简单字符串吗？
:::
