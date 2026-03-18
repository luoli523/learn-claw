# 第11章：心跳与定时任务——让 AI 主动找你

到目前为止，这本书里的 AI 一直处于"被动模式"：你说话，它回应；你不说话，它沉默。

这一章，情况要改变了。

主动型的 AI 助手和被动型的本质区别在于：**它有自己的时间感**——知道现在几点，知道接下来该做什么，不需要等你开口就能给你发消息。OpenClaw 通过两个机制实现这一点：**Heartbeat（心跳）** 和 **Cron（定时任务）**。

![](./images/ch11-automation.webp)

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

::: tip Heartbeat vs Cron 怎么选？
Heartbeat 适合"**有条件才通知**"的模糊检查——比如检查邮件、查天气、看日程，只在有需要时才发消息。

Cron 适合"**到时间一定执行**"的精确任务——比如每天早上 8 点发早报，不需要条件判断，时间到了就跑。
:::

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
  --announce --channel telegram
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
  --channel telegram
```

支持推送的渠道：Telegram、WhatsApp、Slack、Discord、Signal、iMessage、Mattermost。

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

我们来创建一个每天早上 8 点运行的日报任务，结果推送到 Telegram。

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
  --channel telegram
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

几秒后，检查你的 Telegram，应该能收到 AI 发来的早报。

---

::: tip 本章检查清单
- [ ] 你知道 Heartbeat 和 Cron 的适用场景区别吗？（模糊检查 vs 精确调度）
- [ ] 你写了一个 HEARTBEAT.md，并且在末尾加了"没有需要通知的事就保持沉默"了吗？
- [ ] 你成功创建了一个 Cron 任务，并通过 `openclaw cron run` 手动触发测试了吗？
:::
