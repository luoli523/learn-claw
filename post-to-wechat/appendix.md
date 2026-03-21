---
title: "跟鬼哥一起学OpenClaw（附录）：速查手册"
summary: "CLI 命令速查、openclaw.json 配置参考、模型提供商选型指南、常见问题与排错——四篇附录，随用随查。"
author: 鬼哥
coverImage: /Users/li.luo/dev/git/learn-claw/book/appendix/images/a-cli-reference.jpg
---

# 附录 A：OpenClaw CLI 常用命令速查

![](/Users/li.luo/dev/git/learn-claw/book/appendix/images/a-cli-reference.jpg)

## Gateway 管理

```bash
# 启动 Gateway（前台运行）
openclaw gateway start

# 启动 Gateway（后台守护进程）
openclaw gateway start --daemon

# 停止 Gateway
openclaw gateway stop

# 重启 Gateway
openclaw gateway restart

# 查看运行状态
openclaw gateway status

# 查看实时日志
openclaw gateway logs

# 查看最近 N 行日志
openclaw gateway logs --tail 100
```

---

## Onboard（首次配置向导）

```bash
# 启动交互式配置向导
openclaw onboard
```

---

## Cron 定时任务

```bash
# 添加任务（Cron 表达式）
openclaw cron add \
  --name "任务名称" \
  --cron "0 8 * * *" \
  --timezone "Asia/Shanghai" \
  --session isolated \
  --message "任务内容" \
  --announce \
  --channel feishu

# 添加任务（固定间隔）
openclaw cron add \
  --name "任务名称" \
  --every "1h" \
  --session isolated \
  --message "任务内容"

# 添加一次性任务
openclaw cron add \
  --name "任务名称" \
  --at "2026-04-01T09:00:00+08:00" \
  --session main \
  --system-event "提醒内容"

# 查看所有任务
openclaw cron list

# 立即手动触发一次
openclaw cron run --id <jobId>

# 查看任务运行历史
openclaw cron runs --id <jobId> --limit 10

# 暂停任务
openclaw cron pause --id <jobId>

# 恢复任务
openclaw cron resume --id <jobId>

# 删除任务
openclaw cron remove --id <jobId>
```

**常用 Cron 表达式：**

| 表达式 | 含义 |
|---|---|
| `0 8 * * *` | 每天 08:00 |
| `0 9 * * 1` | 每周一 09:00 |
| `30 18 * * 1-5` | 周一至周五 18:30 |
| `0 */2 * * *` | 每 2 小时整点 |
| `0 0 1 * *` | 每月 1 日 00:00 |

---

## 设备节点（Node）

```bash
# 配对新设备
openclaw node pair --code <6位配对码>

# 查看所有已配对设备
openclaw node list

# 解除配对
openclaw node unpair --id <nodeId>
```

---

## 会话管理

```bash
# 查看所有活跃会话
openclaw session list

# 重置指定会话（清除对话历史）
openclaw session reset --id <sessionId>

# 重置主会话
openclaw session reset --main

# 删除会话
openclaw session delete --id <sessionId>
```

---

## Skill 管理

```bash
# 查看已安装的 Skill
openclaw skill list

# 从 ClawHub 安装 Skill
openclaw skill install <skill-name>

# 更新 Skill
openclaw skill update <skill-name>

# 更新所有 Skill
openclaw skill update --all

# 卸载 Skill
openclaw skill remove <skill-name>

# 搜索 ClawHub 上的 Skill
openclaw skill search <keyword>
```

---

## 配置与调试

```bash
# 验证 openclaw.json 语法
openclaw config validate

# 查看当前生效的完整配置（含默认值）
openclaw config show

# 查看版本信息
openclaw version

# 检查环境依赖（Node.js、Docker 等）
openclaw doctor
```

---

## 常用参数说明

| 参数 | 说明 |
|---|---|
| `--agent <agentId>` | 指定操作作用于哪个 Agent |
| `--session main` | 使用主会话 |
| `--session isolated` | 使用隔离会话（每次全新） |
| `--session <name>` | 使用具名持久会话 |
| `--channel <channel>` | 指定推送渠道（feishu/discord 等） |
| `--announce` | 任务完成后推送结果到渠道 |
| `--announce-on-error` | 仅在出错时推送 |
| `--timezone <tz>` | 时区（如 Asia/Shanghai） |

---

# 附录 B：配置文件 openclaw.json 核心字段参考

![](/Users/li.luo/dev/git/learn-claw/book/appendix/images/b-config-reference.jpg)

`openclaw.json` 是 Gateway 的主配置文件，默认位于 `~/.openclaw/openclaw.json`。

---

## 顶层结构

```json
{
  "agents": { ... },
  "bindings": [ ... ],
  "channels": { ... },
  "hooks": { ... },
  "heartbeat": { ... },
  "env": { ... }
}
```

---

## agents

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "workspace": "~/.openclaw/workspace",
        "model": {
          "primary": "anthropic/claude-sonnet-4-6",
          "fallback": "openai/gpt-4o"
        },
        "auth": "default",
        "tools": {
          "profile": "coding",
          "allow": ["browser"],
          "deny": ["messaging"]
        },
        "sandbox": {
          "mode": "non-main"
        },
        "env": {
          "MY_VAR": "value"
        }
      }
    ],
    "defaults": "main"
  }
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | Agent 唯一标识符（必填） |
| `workspace` | string | Workspace 目录路径（必填） |
| `model.primary` | string | 主模型，格式 `provider/model-id` |
| `model.fallback` | string | 主模型不可用时的备用模型 |
| `auth` | string | 使用哪套 Auth 配置（对应 `auths` 字段） |
| `tools.profile` | string | 工具画像：`minimal` / `coding` / `full` |
| `tools.allow` | array | 在 profile 基础上额外启用的工具 |
| `tools.deny` | array | 在 profile 基础上额外禁用的工具 |
| `sandbox.mode` | string | 沙箱模式：`off` / `non-main` / `all` |
| `env` | object | Agent 专属环境变量 |
| `agents.defaults` | string | 没有匹配 binding 时使用的默认 Agent ID |

---

## bindings

```json
{
  "bindings": [
    {
      "channel": "feishu",
      "agentId": "work"
    },
    {
      "channel": "feishu",
      "accountId": "feishu-personal",
      "agentId": "life"
    },
    {
      "channel": "feishu",
      "senderId": "ou_xxxxxxxxxxxxxxxxx",
      "agentId": "vip"
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `channel` | string | 渠道名称（必填） |
| `agentId` | string | 目标 Agent ID（必填） |
| `accountId` | string | 渠道账号 ID（同渠道多账号时区分） |
| `senderId` | string | 精确匹配某个发送者 ID（优先级最高） |
| `guildId` | string | Discord 服务器 ID |
| `teamId` | string | Slack 工作区 ID |

**路由优先级**（高到低）：`senderId` > 父级 peer > `guildId+role` > `guildId` > `teamId` > `accountId` > `channel` > 默认 Agent

---

## channels

各渠道的连接配置，以下为常用渠道示例：

```json
{
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    },
    "discord": {
      "token": "your-discord-token",
      "guildId": "your-guild-id"
    },
    "slack": {
      "botToken": "xoxb-...",
      "signingSecret": "..."
    },
    "web": {
      "enabled": true,
      "port": 18788
    }
  }
}
```

---

## hooks（Webhook）

```json
{
  "hooks": {
    "enabled": true,
    "token": "your-secret-token",
    "allowedAgentIds": ["main", "assistant"],
    "mappings": {
      "github-pr": {
        "kind": "agentTurn",
        "message": "GitHub 有新的 PR 需要 review",
        "channel": "feishu",
        "agentId": "work"
      }
    }
  }
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `enabled` | boolean | 是否启用 Webhook 端点 |
| `token` | string | 认证 Token（必填） |
| `allowedAgentIds` | array | 允许通过 Webhook 触发的 Agent ID 列表 |
| `mappings` | object | 自定义路径到处理逻辑的映射 |
| `mappings[name].kind` | string | 处理类型：`agentTurn`（隔离会话）/ `systemEvent`（注入心跳队列） |
| `mappings[name].messageTemplate` | string | 支持 `{{变量名}}` 替换 payload 字段 |

---

## heartbeat

```json
{
  "heartbeat": {
    "intervalMinutes": 30
  }
}
```

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `intervalMinutes` | number | `30` | 心跳间隔（分钟） |

---

## env

Gateway 全局环境变量，所有 Agent 均可访问：

```json
{
  "env": {
    "HA_TOKEN": "your-home-assistant-token",
    "HA_URL": "http://homeassistant.local:8123"
  }
}
```

Agent 级别的 `env` 字段仅该 Agent 可见，会覆盖同名的全局 `env`。

---

## 工具画像（profile）速查

| Profile | 包含工具组 |
|---|---|
| `minimal` | runtime（只读）、memory、sessions |
| `coding` | runtime（读写）、fs、web、exec、memory、sessions |
| `full` | 所有工具组，包含 browser、messaging、nodes、automation |

---

## 沙箱模式（sandbox.mode）速查

| Mode | 行为 |
|---|---|
| `off` | 不使用沙箱，直接在宿主机执行 |
| `non-main` | 非主会话的任务在 Docker 沙箱里运行 |
| `all` | 所有任务（包括主会话）在 Docker 沙箱里运行 |

---

# 附录 C：模型提供商选型指南

![](/Users/li.luo/dev/git/learn-claw/book/appendix/images/c-model-providers.jpg)

OpenClaw 支持通过统一的 `provider/model-id` 格式对接多家模型提供商。本附录帮你在成本、能力、速度之间找到适合自己场景的组合。

---

## 快速选型矩阵

| 场景 | 推荐模型 | 理由 |
|---|---|---|
| 日常闲聊、简单问答 | MiniMax abab6.5s / Qwen-Turbo | 成本极低，响应快 |
| 代码编写、技术分析 | Claude Sonnet / GPT-4o | 代码能力强，性价比高 |
| 复杂推理、长文档分析 | Claude Opus / o1 | 最强推理，按需使用 |
| 本地隐私场景 | Ollama（本地） | 完全离线，数据不出本地 |
| 中文优化场景 | Qwen-Max / DeepSeek | 中文理解和生成更自然 |

---

## 主流提供商

### Anthropic（Claude 系列）

```json
"model": {
  "primary": "anthropic/claude-sonnet-4-6"
}
```

| 模型 ID | 特点 | 适合场景 |
|---|---|---|
| `anthropic/claude-opus-4-6` | 最强推理，最高成本 | 复杂分析、长文档、高精度任务 |
| `anthropic/claude-sonnet-4-6` | 能力与成本均衡 | **日常首选**，代码、分析、写作 |
| `anthropic/claude-haiku-4-5-20251001` | 速度快，成本低 | 简单任务、高频调用 |

**优势**：指令遵循能力强，代码质量高，长上下文支持好。

**获取 API Key**：[console.anthropic.com](https://console.anthropic.com)

---

### OpenAI（GPT 系列）

```json
"model": {
  "primary": "openai/gpt-4o"
}
```

| 模型 ID | 特点 | 适合场景 |
|---|---|---|
| `openai/gpt-4o` | 多模态，能力全面 | 需要视觉理解的任务 |
| `openai/gpt-4o-mini` | 轻量快速 | 日常问答，成本敏感 |
| `openai/o1` | 深度推理 | 数学、逻辑、复杂问题 |

**获取 API Key**：[platform.openai.com](https://platform.openai.com)

---

### 阿里云（Qwen 系列）

```json
"model": {
  "primary": "qwen/qwen-max"
}
```

| 模型 ID | 特点 |
|---|---|
| `qwen/qwen-max` | 中文能力强，综合性能好 |
| `qwen/qwen-turbo` | 速度快，成本低 |
| `qwen/qwen-long` | 超长上下文（最高 100 万 token） |

**优势**：中文理解和生成质量高，国内访问无网络问题，有免费额度。

**获取 API Key**：[dashscope.aliyuncs.com](https://dashscope.aliyuncs.com)

---

### MiniMax

```json
"model": {
  "primary": "minimax/abab6.5s-chat"
}
```

| 模型 ID | 特点 |
|---|---|
| `minimax/abab6.5s-chat` | 成本极低，中文流畅 |
| `minimax/abab6.5-chat` | 能力更强，成本略高 |

**优势**：日常闲聊场景性价比最高，中文对话体验好。

---

### DeepSeek

```json
"model": {
  "primary": "deepseek/deepseek-chat"
}
```

| 模型 ID | 特点 |
|---|---|
| `deepseek/deepseek-chat` | 综合能力强，价格低廉 |
| `deepseek/deepseek-reasoner` | 深度推理（类 o1） |

**优势**：代码能力出色，价格在同等能力模型中极具竞争力。

---

### Ollama（本地模型）

```json
"model": {
  "primary": "ollama/llama3.2"
}
```

| 常用模型 | 参数量 | 最低显存 |
|---|---|---|
| `ollama/llama3.2` | 3B | 4GB |
| `ollama/llama3.1` | 8B | 8GB |
| `ollama/qwen2.5` | 7B | 8GB |
| `ollama/mistral` | 7B | 8GB |
| `ollama/deepseek-r1` | 7B | 8GB |

**优势**：完全本地运行，数据不出设备，无 API 费用，适合隐私敏感场景。

**前提**：需要先安装 Ollama 并下载对应模型：
```bash
ollama pull llama3.2
```

---

## 成本对比（粗略参考）

> 价格随时变化，以官网为准。以下为相对量级参考。

| 模型 | 输入（每百万 token） | 输出（每百万 token） | 相对成本 |
|---|---|---|---|
| Claude Opus 4 | ~$15 | ~$75 | 🔴 高 |
| Claude Sonnet 4 | ~$3 | ~$15 | 🟡 中 |
| GPT-4o | ~$2.5 | ~$10 | 🟡 中 |
| Claude Haiku | ~$0.25 | ~$1.25 | 🟢 低 |
| GPT-4o-mini | ~$0.15 | ~$0.6 | 🟢 低 |
| DeepSeek Chat | ~$0.14 | ~$0.28 | 🟢 低 |
| Qwen-Turbo | ~$0.05 | ~$0.15 | 🟢 很低 |
| MiniMax abab6.5s | ~$0.01 | ~$0.02 | 🟢 极低 |
| Ollama（本地） | $0 | $0 | 免费 |

---

## 配置多提供商认证

如果你同时用多家提供商，在 `openclaw.json` 里分别配置：

```json
{
  "auths": {
    "anthropic": {
      "apiKey": "sk-ant-..."
    },
    "openai": {
      "apiKey": "sk-..."
    },
    "qwen": {
      "apiKey": "sk-..."
    },
    "ollama": {
      "baseUrl": "http://localhost:11434"
    }
  }
}
```

然后在 Agent 里引用：

```json
{
  "agents": {
    "list": [
      {
        "id": "casual",
        "model": { "primary": "minimax/abab6.5s-chat" },
        "auth": "minimax"
      },
      {
        "id": "analyst",
        "model": { "primary": "anthropic/claude-opus-4-6" },
        "auth": "anthropic"
      }
    ]
  }
}
```

---

## 选型建议

**刚开始上手**：用 Claude Sonnet 或 GPT-4o，能力全面，踩坑少。

**控制成本**：主模型用 Claude Haiku 或 Qwen-Turbo 处理日常，重要任务用 `model.fallback` 升级。

**注重隐私**：Ollama 本地运行，数据不离开你的机器。

**中文场景为主**：Qwen-Max 或 DeepSeek，中文质量更稳定，且无网络问题。

---

# 附录 D：常见问题与排错

![](/Users/li.luo/dev/git/learn-claw/book/appendix/images/d-troubleshooting.jpg)

遇到问题时，先运行这条命令，它能诊断出大多数常见环境问题：

```bash
openclaw doctor
```

---

## Gateway 无法启动

**症状**：`openclaw gateway start` 报错或立即退出。

**排查步骤**：

1. 查看详细错误日志：
   ```bash
   openclaw gateway start --verbose
   ```

2. 检查端口是否被占用（默认 18789）：
   ```bash
   lsof -i :18789
   ```
   如果有其他进程占用，要么结束那个进程，要么在 `openclaw.json` 里修改端口：
   ```json
   { "gateway": { "port": 18790 } }
   ```

3. 检查配置文件语法：
   ```bash
   openclaw config validate
   ```
   JSON 格式错误（多了逗号、少了引号）是最常见的启动失败原因。

4. 检查 Node.js 版本（需要 18+）：
   ```bash
   node --version
   ```

---

## AI 不回复消息

**症状**：发了消息，渠道里没有任何回复，也没有报错。

**排查步骤**：

1. 确认 Gateway 正在运行：
   ```bash
   openclaw gateway status
   ```

2. 查看实时日志，发消息，观察是否有请求进来：
   ```bash
   openclaw gateway logs --tail 50
   ```

3. 检查 API Key 是否有效——最常见的原因是 Key 过期或余额不足：
   ```bash
   openclaw config validate --test-auth
   ```

4. 检查渠道配置，以飞书为例，确认 App ID 和 App Secret 正确且应用已发布：
   ```bash
   openclaw gateway logs | grep -i feishu
   ```

5. 检查 `allowFrom` 配置——飞书等渠道有白名单，你的用户 ID 是否在列表里：
   ```json
   "feishu": { "allowFrom": ["ou_xxxxxxxxxxxxxxxxx"] }
   ```

---

## Cron 任务没有按时触发

**症状**：到了设定时间，任务没有运行。

**排查步骤**：

1. 检查任务状态是否为 `active`：
   ```bash
   openclaw cron list
   ```
   如果是 `paused`，运行 `openclaw cron resume --id <jobId>`。

2. 确认时区设置正确：
   ```bash
   openclaw cron list --verbose
   ```
   `0 8 * * *` 配合 `--timezone Asia/Shanghai` 才是北京时间 8 点，不加时区默认 UTC（差 8 小时）。

3. 检查 Gateway 在任务应该触发时是否在运行——Cron 依赖 Gateway 持续运行。如果 Gateway 重启了，在重启之前应该触发的任务会跳过（不补跑）。

4. 查看任务的运行历史，看是否有错误信息：
   ```bash
   openclaw cron runs --id <jobId> --limit 5
   ```

---

## Webhook 返回 401 或 403

**症状**：`curl` 调用 Webhook 返回 `401 Unauthorized` 或 `403 Forbidden`。

**原因和修复**：

- `401`：Token 不正确或格式错误。确认请求头是 `Authorization: Bearer your-token`，不是 `Authorization: your-token`。
- `403`：Token 正确，但请求的 `agentId` 不在 `allowedAgentIds` 白名单里。检查 `hooks.allowedAgentIds` 配置。
- `429`：连续认证失败触发了速率限制，等几分钟再试。

---

## Docker 沙箱相关错误

**症状**：启用沙箱后，exec 工具调用报错 `docker: command not found` 或 `permission denied`。

**排查步骤**：

1. 确认 Docker 已安装且在运行：
   ```bash
   docker ps
   ```

2. 确认当前用户在 docker 组里（Linux）：
   ```bash
   groups $USER
   # 如果没有 docker，执行：
   sudo usermod -aG docker $USER
   # 然后重新登录
   ```

3. macOS 上确认 Docker Desktop 正在运行（菜单栏有图标）。

4. 临时关闭沙箱确认问题是否出在 Docker：
   ```json
   "sandbox": { "mode": "off" }
   ```
   如果关掉沙箱后正常，问题就在 Docker 配置。

---

## 记忆（MEMORY.md）不更新

**症状**：和 AI 说过的事情，下次对话它完全不记得。

**排查步骤**：

1. 确认 `MEMORY.md` 文件存在于 Workspace 目录：
   ```bash
   ls ~/.openclaw/workspace/
   ```

2. 查看 `MEMORY.md` 是否有内容，如果是空文件，AI 可能认为不需要记录：
   ```bash
   cat ~/.openclaw/workspace/MEMORY.md
   ```

3. 检查 `SOUL.md` 里是否有记忆相关的指令。如果没有，AI 可能不知道应该主动记录。可以在 `SOUL.md` 末尾加上：
   ```markdown
   ## 记忆规则
   当用户分享个人信息、偏好、重要事项时，及时更新 MEMORY.md。
   每次对话开始前，先读取 MEMORY.md 了解用户信息。
   ```

4. 确认 `memory` 工具组已启用（`minimal` 和 `coding` 画像默认包含）。

---

## 模型回复中文但质量差

**症状**：AI 能回复中文，但用词生硬，或者回复内容不符合预期。

**可能原因和改进**：

1. **使用了对中文优化不足的模型**：切换到 Qwen 或 DeepSeek 系列，中文效果更好。

2. **SOUL.md 里没有指定语言**：明确加上 `使用中文回复` 或 `始终用简体中文交流`。

3. **SOUL.md 太短**：给 AI 更多上下文，比如你的职业、使用场景、偏好的回复风格。

---

## 性能问题：响应太慢

**症状**：每条消息要等 10 秒以上才有回复。

**排查和优化**：

1. **换更快的模型**：Claude Haiku、GPT-4o-mini、Qwen-Turbo 的响应速度显著快于大模型。

2. **检查网络**：模型 API 在海外，网络延迟会直接影响响应速度。使用代理或选择有国内节点的提供商（如 Qwen）。

3. **缩短 Workspace 文件**：`SOUL.md`、`MEMORY.md` 过长会增加每次请求的 token 数，影响速度和成本。定期清理不再需要的内容。

4. **减少工具数量**：工具越多，AI 思考"要不要调用工具"的时间越长。只启用真正需要的工具组。

---

## 获取更多帮助

- **官方文档**：[docs.openclaw.ai](https://docs.openclaw.ai)
- **社区论坛**：[community.openclaw.ai](https://community.openclaw.ai)
- **GitHub Issues**：[github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)

提交 issue 时，附上 `openclaw doctor` 的输出和相关日志，能帮助更快定位问题。