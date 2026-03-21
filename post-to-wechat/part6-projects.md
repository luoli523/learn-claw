---
title: "跟鬼哥一起学OpenClaw（六）：实战篇"
summary: "把所有能力组合起来，做出四个真实可用的项目：全能个人助理、浏览器自动化、多智能体团队、智能家居整合。"
author: 鬼哥
coverImage: /Users/li.luo/dev/git/learn-claw/book/part6-projects/images/part6-index.jpg
---

# 第六部分：实战篇

前五部分，你学的是"零件"。

这一部分，我们来拼整台机器。

![](/Users/li.luo/dev/git/learn-claw/book/part6-projects/images/part6-index.jpg)

---

实战篇的四个项目，每一个都是真实可用的系统——不是玩具 demo，不是"你可以想象有这么个东西"，而是跑起来之后每天真正帮你干活的那种。

**本部分包含四章：**

- **第15章** 打造"双手机"全能个人助理——工作号和个人号背后各跑一个 AI，性格不同、工具不同、早报不同，从零配置到完整跑通。

- **第16章** 零代码浏览器自动化专家——商品降价了发通知、技术论坛每周精选、CI 失败自动截图分析，不写一行爬虫代码。

- **第17章** 多智能体团队协作——PM、工程师、审查员三个 AI 角色组成流水线，你发一句需求，它们自动接力，最后把代码审查报告推到你手机上。

- **第18章** 智能家居整合（Home Assistant）——用自然语言控制家里的设备，到家自动开灯，每晚 11 点 AI 替你巡查门窗。

---

每章都遵循同一个结构：**项目目标 → 架构设计 → 逐步配置 → 验收测试**。

读完能直接用，不读也能回来当参考手册查。

---

# 第15章：项目一——打造"双手机"全能个人助理

前面十四章，你学了一堆概念：Workspace、记忆系统、会话管理、工具、Skill、多 Agent、Webhook、Node……

是时候把这些拼在一起，做出一个真正能用的东西了。

这一章的项目是**双手机全能个人助理**：一个工作号，一个生活号，背后共享一个 Gateway，各自对接独立的 AI 人格。工作手机发消息，得到的是严谨专业的回答；个人手机发消息，得到的是随意轻松的回答。两台手机每天早上各自收到一份定制早报。

![](/Users/li.luo/dev/git/learn-claw/book/part6-projects/images/ch15-personal-assistant.jpg)

---

## 项目目标

完成本章后，你将拥有：

| | 工作助理 | 生活助理 |
|---|---|---|
| **渠道** | 飞书（工作版机器人） | 飞书（生活版机器人） |
| **性格** | 严谨、精确、有条理 | 轻松、友好、会聊天 |
| **工具** | coding 画像 + browser | minimal 画像 + 日历 Skill |
| **早报** | 每天 8:30 推送工作摘要 | 每天 8:00 推送生活摘要 |
| **记忆** | 独立 Workspace | 独立 Workspace |

两个 Agent，一个 Gateway，互不干扰。

---

## 整体架构

```
你的两个飞书机器人
  ├── 飞书工作机器人（accountId=feishu-work）
  │       ↓ binding: channel=feishu, accountId=feishu-work → agentId=work
  └── 飞书生活机器人（accountId=feishu-life）
          ↓ binding: channel=feishu, accountId=feishu-life → agentId=life

                 ↓
           OpenClaw Gateway
          ┌──────┬──────────┐
          │      │          │
        work   life    Cron 调度器
        Agent  Agent   ├─ 8:00 → life Agent → 飞书（生活版）
          │      │     └─ 8:30 → work Agent → 飞书（工作版）
       工作区   生活区
    workspace  workspace
```

---

## 第一步：创建两个 Workspace

```bash
# 工作助理 Workspace
mkdir -p ~/.openclaw/workspace-work

cat > ~/.openclaw/workspace-work/SOUL.md << 'EOF'
## 身份

你是一位专业的工作助理。

## 性格

- 回答准确、简洁，避免废话
- 用结构化格式（列表、代码块）组织信息
- 遇到技术问题，给出可执行的具体方案，而不是模糊的建议
- 不主动寒暄，直接进入正题

## 工作风格

- 代码问题：给出可运行的代码，附上简短说明
- 文档/方案：用 Markdown 格式，层次清晰
- 如果问题不清楚，先确认需求再回答
EOF

# 生活助理 Workspace
mkdir -p ~/.openclaw/workspace-life

cat > ~/.openclaw/workspace-life/SOUL.md << 'EOF'
## 身份

你是一位贴心的生活助理，像一个知心朋友。

## 性格

- 轻松随意，不端着
- 适当幽默，但不过分
- 关心细节，记得用户说过的事情
- 回复不必太长，够用就好

## 工作风格

- 日常问题：口语化回答，简短直接
- 需要帮助时：先表示理解，再提供建议
- 闲聊时：自然接话，不要每次都转向"我能帮你做什么"
EOF
```

---

## 第二步：配置 TOOLS.md

给工作助理更强的工具能力，给生活助理保持轻量：

```bash
cat > ~/.openclaw/workspace-work/TOOLS.md << 'EOF'
# 工具配置

工具画像：coding

## 额外启用

- browser（用于查阅技术文档）

## 禁用

- messaging（工作场景不需要代发消息）
EOF

cat > ~/.openclaw/workspace-life/TOOLS.md << 'EOF'
# 工具配置

工具画像：minimal

## Skill

- google-calendar（查看和创建日程）
- weather（查询天气）
EOF
```

---

## 第三步：配置 openclaw.json

这是核心配置，把两个 Agent 和对应的渠道绑定起来：

```json
{
  "agents": {
    "list": [
      {
        "id": "work",
        "workspace": "~/.openclaw/workspace-work",
        "model": {
          "primary": "anthropic/claude-sonnet-4-6"
        },
        "tools": {
          "profile": "coding",
          "allow": ["browser"]
        }
      },
      {
        "id": "life",
        "workspace": "~/.openclaw/workspace-life",
        "model": {
          "primary": "minimax/abab6.5s-chat"
        },
        "tools": {
          "profile": "minimal"
        }
      }
    ],
    "defaults": "life"
  },
  "bindings": [
    {
      "channel": "feishu",
      "accountId": "feishu-work",
      "agentId": "work"
    },
    {
      "channel": "feishu",
      "accountId": "feishu-life",
      "agentId": "life"
    }
  ],
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }
  }
}
```

**📌 只有一个飞书应用？**

没有两个机器人也没关系——用飞书 + Web Dashboard 分别测试两个 Agent：

```json
"bindings": [
  { "channel": "feishu", "agentId": "work" },
  { "channel": "web", "agentId": "life" }
]
```

飞书机器人测试工作助理，Web Dashboard 测试生活助理，效果完全一样。

---

## 第四步：添加 Cron 早报任务

两个 Agent 各自收到适合自己场景的早报：

```bash
# 生活助理早报（8:00，个人手机）
openclaw cron add \
  --name "生活早报" \
  --cron "0 8 * * *" \
  --timezone "Asia/Shanghai" \
  --session isolated \
  --agent life \
  --message "生成今天的生活早报，包含：
1. 今天的日期和天气概况（如果有天气工具）
2. 今天的日程提醒（如果有日历工具）
3. 一句轻松的早安问候
控制在 150 字以内，口语化风格。" \
  --announce \
  --channel feishu

# 工作助理早报（8:30，工作手机）
openclaw cron add \
  --name "工作早报" \
  --cron "30 8 * * 1-5" \
  --timezone "Asia/Shanghai" \
  --session isolated \
  --agent work \
  --message "生成今天的工作早报，包含：
1. 今天是周几，距离周末还有几天
2. 今天的工作日程（如果有日历工具）
3. 如果有 web 工具，简要列出今日科技/开发领域重要动态（2条）
格式简洁，用列表，不超过 200 字。" \
  --announce \
  --channel feishu
```

注意工作早报用了 `0-5`（周一至周五），周末不打扰。

---

## 第五步：验收测试

重启 Gateway：

```bash
openclaw gateway restart
openclaw gateway status
```

确认两个 Agent 都处于运行状态。

**测试一：性格差异**

分别向两个渠道发同一句话：

```
帮我推荐一部好看的电影
```

- 飞书工作版（工作助理）：应该给一个结构化列表，注明类型、评分、推荐原因
- 飞书生活版（生活助理）：应该随意地聊几句，像朋友推荐

**测试二：工具能力差异**

向工作助理发：

```
帮我写一个 Python 函数，判断一个字符串是否是有效的 IPv4 地址
```

它应该给出完整的代码和测试用例。

向生活助理发同样的请求——它应该坦诚地说自己不擅长代码，或者给出更简单的回答（工具画像限制了它的代码能力）。

**测试三：早报**

手动触发一次，不等明天早上：

```bash
# 查看任务 ID
openclaw cron list

# 立即触发生活早报
openclaw cron run --id <life-morning-id>

# 立即触发工作早报
openclaw cron run --id <work-morning-id>
```

检查两个渠道是否收到了风格完全不同的早报。

---

## 进阶：给特定联系人单独路由

你的工作手机上，有一个特别重要的客户，你希望它的消息被更高级的模型处理：

```json
{
  "bindings": [
    {
      "channel": "feishu",
      "senderId": "ou_特定客户的飞书OpenID",
      "agentId": "analyst"
    },
    {
      "channel": "feishu",
      "accountId": "feishu-work",
      "agentId": "work"
    }
  ]
}
```

根据第13章的路由优先级，`senderId` 精确匹配优先级最高——这位客户的消息会被 `analyst` Agent 处理，其他人的消息走普通的 `work` Agent。

---

## 本章小结

你刚刚完成的，是把以下章节的内容有机地组合在一起：

| 用到的概念 | 来自 |
|---|---|
| Workspace + SOUL.md | 第5章 |
| TOOLS.md 工具控制 | 第8章 |
| Skill 集成 | 第9章 |
| Cron 定时推送 | 第11章 |
| 多 Agent + Binding 路由 | 第13章 |

单独看每章的时候，这些是孤立的功能点；组合起来，就是一个每天真实运转的个人助理系统。

这就是实战篇的意义：验证你真正理解了这些概念，而不只是读懂了文字。

---

**📌 本章检查清单**

- 两个 Agent 的回复风格确实不同了吗？（飞书工作版严谨 vs 飞书生活版轻松）
- 两个 Cron 早报任务都触发成功，并推送到了正确的渠道吗？
- 你能说清楚这个项目分别用到了哪几章的内容吗？

---

# 第16章：项目二——零代码浏览器自动化专家

每个人的收藏夹里，都躺着一批"需要定期去看一眼"的网页。

某件商品什么时候降价？竞品有没有更新定价？招聘网站有没有新坑位？技术论坛今天有没有值得读的文章？

以前你只有两个选择：要么自己每天手动打开，要么花时间写爬虫脚本。现在有第三个选择：**让 AI 开着浏览器替你盯着，有动静才叫你**。

这一章，我们用三个真实任务，把 `browser` 工具和 Cron + Webhook 组合起来，搭出一套零代码浏览器自动化监控系统。

![](/Users/li.luo/dev/git/learn-claw/book/part6-projects/images/ch16-browser-automation.jpg)

---

## browser 工具能做什么

在开始之前，快速回顾一下 `browser` 工具的核心能力（第8章详细讲过，这里只列项目里会用到的）：

| 能力 | 说明 |
|---|---|
| 打开网页 | 加载任意 URL，等待页面渲染完成 |
| 截图 | 截取当前页面或指定区域 |
| 提取文本 | 读取页面上指定元素的文本内容 |
| 点击/填表 | 模拟用户操作，支持登录等交互 |
| 执行 JS | 在页面上下文里执行 JavaScript |

关键一点：**AI 不是用正则表达式解析 HTML，而是真的"看"着渲染好的页面**——就像你眼睛看网页一样。这意味着即使网站没有 API，AI 也能从视觉上理解页面内容。

---

## 准备工作：启用 browser 工具

确认你的 Workspace 里的 `TOOLS.md` 启用了 `browser`：

```markdown
# 工具配置

工具画像：minimal

## 额外启用

- browser
```

或者直接用 `coding` 或 `full` 画像，它们默认包含 `browser`。

---

## 任务一：商品降价监控

**目标**：每天检查某商品的价格，如果比目标价低，立刻发飞书通知。

### 配置 Cron 任务

```bash
openclaw cron add \
  --name "耳机降价监控" \
  --cron "0 10 * * *" \
  --timezone "Asia/Shanghai" \
  --session isolated \
  --message "请完成以下任务：
1. 打开 https://www.amazon.cn/dp/B09XS7JWHH（替换为你要监控的商品链接）
2. 找到当前售价
3. 如果价格低于 ¥800，立刻通过 messaging 工具发飞书消息给我，内容包含当前价格和商品链接
4. 如果价格高于或等于 ¥800，不要发任何消息，静默结束" \
  --announce-on-error \
  --channel feishu
```

注意这里没有用 `--announce`，而是用了 `--announce-on-error`——任务出错时才通知，正常执行不打扰你。降价通知是在 `message` 里让 AI 用 `messaging` 工具主动发的，只在真的降价时才发。

### 测试

手动触发一次，看 AI 是否能正确读取页面价格：

```bash
openclaw cron run --id <job-id>
openclaw cron runs --id <job-id> --limit 1
```

查看运行日志，确认 AI 找到了价格，并根据条件判断是否发送通知。

---

## 任务二：Hacker News 每周精选

**目标**：每周一早上，抓取 Hacker News 头版，摘要最值得读的 5 篇文章，推送到飞书。

这是一个纯内容聚合任务，不需要任何 API Key，完全靠 browser 工具读取公开页面。

```bash
openclaw cron add \
  --name "HN 周报" \
  --cron "0 9 * * 1" \
  --timezone "Asia/Shanghai" \
  --session isolated \
  --message "请完成以下任务：
1. 打开 https://news.ycombinator.com
2. 读取首页所有文章标题、链接和分数
3. 从中筛选分数最高的 5 篇（排除招聘帖和 Ask HN）
4. 对每篇文章，打开链接，读取正文摘要（50字以内）
5. 整理成简洁的 Markdown 列表，格式如下：
   ### HN 本周精选（日期）
   1. [标题](链接) — 一句话摘要
   2. ...
6. 发送到飞书" \
  --announce \
  --channel feishu
```

**📌 让 AI 自己判断要不要读全文**

步骤4里让 AI 读每篇文章的正文——如果有些链接打不开（付费墙、超时），AI 会自动跳过并用标题替代摘要，不会卡死在那里。这是用自然语言指令的好处：不需要写异常处理逻辑。

---

## 任务三：GitHub CI 失败自动分析

**目标**：当 GitHub Actions 构建失败时，Webhook 触发 AI 自动打开 CI 页面，截图并分析错误原因，把结论推送到飞书。

这个任务把 Webhook（第12章）和 browser 工具结合起来。

### 第一步：在 openclaw.json 里配置 Webhook

```json
{
  "hooks": {
    "enabled": true,
    "token": "your-webhook-token",
    "mappings": {
      "github-ci-failed": {
        "kind": "agentTurn",
        "channel": "feishu",
        "messageTemplate": "GitHub CI 构建失败了。\n失败的 workflow URL：{{run_url}}\n\n请完成以下任务：\n1. 打开上面的 URL\n2. 截取页面截图\n3. 找到失败的 step 和错误信息\n4. 用简洁的语言解释是什么错误，给出可能的修复方向\n5. 把截图和分析结果发给我"
      }
    }
  }
}
```

### 第二步：在 GitHub 仓库里设置 Webhook

在 GitHub 仓库 → Settings → Webhooks → Add webhook：

```
Payload URL: http://<你的公网IP或Tailscale地址>:18789/hooks/github-ci-failed
Content type: application/json
Secret: （留空，认证在请求头里）
Events: Workflow runs
```

等等，GitHub 原生 Webhook 的请求头格式和 OpenClaw 预期的不完全一致。更简单的方案是用 GitHub Actions 里的 `curl` 步骤主动推送：

```yaml
# .github/workflows/notify-failure.yml
name: Notify on Failure

on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

jobs:
  notify:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - name: Notify OpenClaw
        run: |
          curl -X POST http://${{ secrets.OPENCLAW_HOST }}/hooks/agent \
            -H "Authorization: Bearer ${{ secrets.OPENCLAW_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "message": "GitHub CI 构建失败。失败链接：${{ github.event.workflow_run.html_url }}\n\n请打开这个链接，截图并分析失败原因，用中文告诉我哪一步失败了以及可能的原因。",
              "channel": "feishu",
              "name": "ci-failure-analysis"
            }'
```

把 `OPENCLAW_HOST`（你的 Tailscale 地址）和 `OPENCLAW_TOKEN` 添加到仓库的 Secrets 里，就配好了。

### 测试

故意让一个 CI 构建失败（比如在代码里引入一个语法错误并推送），观察几分钟后飞书是否收到了带有截图和分析的消息。

---

## 处理需要登录的页面

有些监控任务需要登录——比如监控内网系统、需要账号的平台。

OpenClaw 的 browser 工具支持**保存和复用 cookie**：

```markdown
# TOOLS.md

## Browser 配置

会话持久化：enabled
Cookie 存储路径：~/.openclaw/browser-sessions/
```

第一次使用时，让 AI 执行登录操作：

```
请打开 https://example-internal-system.com，用用户名 myuser、密码 [密码] 登录，
登录成功后保存 cookie，之后就不需要再登录了
```

之后的 Cron 任务里，AI 会自动复用保存的 cookie，无需每次重新登录。

**⚠️ 密码安全**

不要把密码直接写在 Cron 任务的 `message` 里——那会被记录到日志。正确做法是先手动执行一次登录操作（一次性交互），保存 cookie，之后的自动化任务复用 cookie，完全不需要密码。

---

## 完整配置汇总

三个任务都配置好后，`openclaw cron list` 应该显示：

```
ID        名称              状态    下次运行
job-001   耳机降价监控      active  明天 10:00
job-002   HN 周报           active  下周一 09:00
job-003   （CI 由 Webhook 触发，无固定计划）
```

---

## 本章小结

这三个任务背后的模式是一样的：

```
触发（Cron 或 Webhook）
  → AI 开浏览器执行任务
  → 判断是否需要通知
  → 只在有价值时推送
```

传统爬虫需要你了解 CSS 选择器、处理各种异常、维护脆弱的正则表达式。这套方案的核心是**用自然语言描述任务**，AI 自己决定怎么操作浏览器——网站改版了不需要你改代码，AI 会适应新的页面结构。

代价是速度略慢、成本略高（AI 需要真正渲染和理解页面）。但对于每天跑几次的监控任务来说，这个代价完全值得。

---

**📌 本章检查清单**

- 你成功配置了至少一个定时浏览器监控任务，并手动触发验证它能读取页面内容了吗？
- 你理解为什么这里用 `--announce-on-error` 而不是 `--announce` 了吗？
- 你知道如何处理需要登录的页面（cookie 持久化）了吗？

---

# 第17章：项目三——多智能体团队协作

一个聪明的人，也有他做不好的事情。

让同一个人既写代码又审代码，几乎没有意义——写代码的人看自己的代码，大脑会自动脑补掉 bug，这是认知偏差，不是能力问题。真正有效的代码审查需要另一双眼睛。

AI 也一样。让同一个 Agent 既理解需求又写代码又自我审查，质量上限很有限。但如果你有三个 Agent——一个专门拆解需求，一个专门写代码，一个专门挑毛病——它们互相传递结果、互相检验，整体输出质量会高得多。

这一章，我们用三个 Agent 搭一条迷你 AI 流水线：需求 → 代码 → 审查 → 结果。

![](/Users/li.luo/dev/git/learn-claw/book/part6-projects/images/ch17-agent-team.jpg)

---

## 项目目标

搭建一个三角色 AI 团队，完成从需求到交付的完整链路：

```
你发需求
    ↓
[PM Agent] 拆解需求，制定任务清单
    ↓
[Engineer Agent] 根据任务清单写代码
    ↓
[Reviewer Agent] 审查代码质量，给出评分和改进建议
    ↓
最终结果推送到你的飞书
```

整个流程你只需要在开头发一句话，其余全部由三个 Agent 自动接力完成。

---

## 整体架构

```
你（飞书）
  ↓ 发送需求
[PM Agent]（飞书渠道，工具：minimal + messaging）
  ↓ 调用 /hooks/agent 触发
[Engineer Agent]（隔离会话，工具：coding）
  ↓ 输出代码，再次调用 /hooks/agent 触发
[Reviewer Agent]（隔离会话，工具：minimal）
  ↓ 审查完毕
最终结果 → 飞书
```

三个 Agent 不直接"对话"，而是通过 `/hooks/agent` 端点互相触发——每个 Agent 完成工作后，调用 Webhook 把接力棒传给下一个。

---

## 第一步：创建三个 Workspace

```bash
# PM Agent
mkdir -p ~/.openclaw/workspace-pm
cat > ~/.openclaw/workspace-pm/SOUL.md << 'EOF'
## 角色

你是一位有经验的产品经理 AI。

## 职责

接收用户的功能需求，把它拆解成清晰的开发任务清单。

## 工作风格

- 需求拆解时，关注边界情况和异常处理
- 输出标准化的任务清单，格式：
  1. 核心功能：xxx
  2. 输入验证：xxx
  3. 错误处理：xxx
  4. 测试用例：xxx
- 拆解完成后，把完整的任务清单传递给工程师 Agent 执行

## 重要

你只负责需求拆解，不写代码。代码由工程师 Agent 负责。
EOF

# Engineer Agent
mkdir -p ~/.openclaw/workspace-engineer
cat > ~/.openclaw/workspace-engineer/SOUL.md << 'EOF'
## 角色

你是一位专注的软件工程师 AI。

## 职责

根据 PM 给出的任务清单，编写高质量的代码实现。

## 工作风格

- 严格按照任务清单实现，不遗漏任何要点
- 代码要有完整的类型注释和必要的注释
- 包含完整的错误处理
- 输出完整可运行的代码，不要省略任何部分
- 写完后，把代码和简短的实现说明传递给审查 Agent

## 重要

你只负责编写代码，不评价需求合理性，不做代码审查。
EOF

# Reviewer Agent
mkdir -p ~/.openclaw/workspace-reviewer
cat > ~/.openclaw/workspace-reviewer/SOUL.md << 'EOF'
## 角色

你是一位严格的代码审查员 AI。

## 职责

审查工程师提交的代码，从以下维度评估：

1. **正确性**：逻辑是否正确，是否覆盖边界情况
2. **健壮性**：错误处理是否完善
3. **可读性**：命名、注释、代码结构
4. **潜在问题**：安全风险、性能问题、未考虑的边界

## 输出格式

评分（满分10分）：X/10

优点（2-3条）：
- ...

需要改进（按优先级）：
- [高] ...
- [中] ...
- [低] ...

总结：一句话概括这段代码的整体质量。

## 重要

审查要客观严格，不要因为是 AI 写的代码就客气，有问题必须指出。
EOF
```

---

## 第二步：配置 openclaw.json

```json
{
  "agents": {
    "list": [
      {
        "id": "pm",
        "workspace": "~/.openclaw/workspace-pm",
        "model": {
          "primary": "anthropic/claude-sonnet-4-6"
        },
        "tools": {
          "profile": "minimal",
          "allow": ["messaging", "runtime.webhook"]
        }
      },
      {
        "id": "engineer",
        "workspace": "~/.openclaw/workspace-engineer",
        "model": {
          "primary": "anthropic/claude-sonnet-4-6"
        },
        "tools": {
          "profile": "coding"
        }
      },
      {
        "id": "reviewer",
        "workspace": "~/.openclaw/workspace-reviewer",
        "model": {
          "primary": "anthropic/claude-sonnet-4-6"
        },
        "tools": {
          "profile": "minimal",
          "allow": ["messaging"]
        }
      }
    ],
    "defaults": "pm"
  },
  "bindings": [
    {
      "channel": "feishu",
      "agentId": "pm"
    }
  ],
  "hooks": {
    "enabled": true,
    "token": "your-internal-pipeline-token",
    "allowedAgentIds": ["pm", "engineer", "reviewer"]
  }
}
```

注意 `allowedAgentIds`——Webhook 只允许触发这三个 Agent，防止误触发其他 Agent。

---

## 第三步：让 Agent 互相传递接力棒

三个 Agent 之间通过 `/hooks/agent` 接力。每个 Agent 完成任务后，在 `message` 里让它调用 Webhook 触发下一个。

**PM Agent 的工作提示（你每次发需求时自动生效）**：

在 PM Agent 的 `SOUL.md` 末尾追加：

```bash
cat >> ~/.openclaw/workspace-pm/SOUL.md << 'EOF'

## 交接流程

完成任务清单后，调用以下 Webhook 把任务交给工程师：

```
POST http://127.0.0.1:18789/hooks/agent
Authorization: Bearer your-internal-pipeline-token
Content-Type: application/json

{
  "agentId": "engineer",
  "message": "请根据以下任务清单编写代码：\n[任务清单内容]\n\n完成后请调用 Webhook 把代码交给 reviewer Agent 审查：POST http://127.0.0.1:18789/hooks/agent，agentId: reviewer",
  "name": "engineer-task",
  "channel": "feishu"
}
```

用 runtime.webhook 工具执行这个请求。
EOF
```

**为什么让 Agent 在 message 里带着"继续传递"的指令？**

因为 Engineer Agent 是隔离会话启动的，它没有任何上下文——它只能从 `message` 里知道自己要做什么，以及做完之后该怎么办。整个接力链路的逻辑都靠 `message` 传递。

---

## 第四步：完整流程演示

配置好之后，你只需要向飞书发一条消息：

```
帮我写一个 Python 函数，输入一个字符串，返回其中所有的 URL（需要支持 http 和 https，要处理带参数的 URL）
```

接下来会发生：

**T+0s**：PM Agent 收到需求，开始拆解

```
[PM Agent] 正在分析需求...

任务清单：
1. 核心功能：使用正则表达式匹配 http/https URL
2. 输入验证：处理 None 和空字符串输入
3. URL 边界：正确处理 URL 结尾（逗号、句号不算 URL 的一部分）
4. 参数支持：URL 中的查询参数和 fragment 都要保留
5. 测试用例：至少 5 个测试用例，包含有 URL、无 URL、多个 URL、带参数的 URL

正在转交给工程师...
```

**T+15s**：Engineer Agent 被触发，开始写代码

**T+45s**：Reviewer Agent 被触发，审查代码

**T+60s**：你的飞书收到最终结果：

```
[代码审查报告]

评分：8/10

优点：
- 正则表达式覆盖了常见 URL 格式，包括带参数的情况
- 边界情况（None 输入）处理得当
- 测试用例完整，覆盖了主要场景

需要改进：
- [高] URL 结尾处理不完善：URL 后跟着右括号 ) 时会被误包含
- [中] 没有处理 IP 地址格式的 URL（如 http://192.168.1.1/path）
- [低] 函数文档字符串可以更完整

总结：基本可用，建议修复高优先级的括号问题后上线。

---
[附：工程师编写的代码]
import re
from typing import Optional

def extract_urls(text: Optional[str]) -> list[str]:
    ...
```

整个过程全自动，你全程没有参与中间步骤。

---

## 扩展：加入人工审批节点

如果你不想完全自动化，可以在 PM 和 Engineer 之间加一个"你的确认"环节：

PM Agent 完成拆解后，先把任务清单发给你（飞书），**等你回复"确认"后，才触发 Engineer Agent**。

实现方式：让 PM Agent 把任务清单用 `messaging` 工具发给你，然后用 Cron 每分钟检查你是否回复了"确认"，收到确认再触发 Engineer。

这个模式叫**人在回路（Human-in-the-Loop）**——在关键节点保留人工判断，其余步骤自动化。复杂或风险较高的任务特别适合这种模式。

---

## 这个项目用到了哪些章节

| 用到的概念 | 来自 |
|---|---|
| Workspace + SOUL.md 角色设定 | 第5章 |
| 工具画像（coding / minimal） | 第8章 |
| 多 Agent + agentId | 第13章 |
| Webhook /hooks/agent 触发 | 第12章 |
| Binding 路由（飞书 → PM） | 第13章 |

---

**📌 本章检查清单**

- 三个 Agent 都配置好了，`openclaw gateway status` 显示它们都在运行吗？
- 你发了一个功能需求，三个 Agent 成功接力，最终结果推送到了飞书吗？
- 你理解为什么 Agent 之间要通过 Webhook 传递而不是直接"对话"吗？

---

# 第18章：项目四——智能家居整合（Home Assistant）

智能家居的"智能"，有时候名不副实。

你说"打开客厅灯"，得先解锁手机，找到 App，点进去，找到客厅，找到灯，点开。这个过程比直接走过去按开关慢不了多少。

真正的智能应该是：你进门，灯自己亮了；你说一句"我要睡了"，该关的关，该调暗的调暗，温度自动降两度。你不需要操作任何设备——AI 知道你的意图，替你跑腿。

这一章，我们把 OpenClaw 和 Home Assistant 连起来，把"说一句话"变成真正的家居控制入口，同时让 AI 主动承担夜间安全巡查这样的周期性任务。

![](/Users/li.luo/dev/git/learn-claw/book/part6-projects/images/ch18-smart-home.jpg)

---

## 前提条件

本章假设你：
- 已经有一个运行中的 Home Assistant 实例（本地网络或通过 Nabu Casa 云访问）
- 家里有一些已接入 HA 的设备（灯、温控、门窗传感器等）
- OpenClaw Gateway 和 HA 在同一局域网，或通过 Tailscale 互通

如果你还没有 Home Assistant，这一章作为参考阅读也完全值得——它展示的"AI 通过 REST API 控制外部系统"的模式，适用于任何有 API 的平台。

---

## 项目目标

完成本章后，你将拥有：

| 场景 | 触发方式 | AI 的动作 |
|---|---|---|
| 自然语言控制 | 飞书发消息 | 调用 HA API 执行指令 |
| 到家自动化 | 手机 Node 位置触发 | 执行"到家"场景 |
| 夜间安全巡查 | Cron 每晚 23:00 | 检查门窗状态并汇报 |

---

## 第一步：获取 Home Assistant Token

在 HA Web 界面：用户头像 → 安全 → 长期访问令牌 → 创建令牌

复制这个 Token，接下来会用到。

**⚠️ Token 保存**

不要把 HA Token 写进 SOUL.md 或 openclaw.json——这些文件可能被分享或提交到 git。正确做法是存入 Gateway 的环境变量：

在 openclaw.json 里：
```json
{
  "env": {
    "HA_TOKEN": "your-ha-long-lived-token",
    "HA_URL": "http://homeassistant.local:8123"
  }
}
```

AI 在调用时引用 `$HA_TOKEN`，Token 本身不出现在任何对话记录里。

---

## 第二步：在 AGENTS.md 里描述你的家

AI 需要知道家里有哪些设备，以及它们在 HA 里对应的 entity_id。把设备清单写进 `AGENTS.md`：

```markdown
# 家居设备清单

## Home Assistant 接入信息

- HA 地址：$HA_URL
- 认证 Token：$HA_TOKEN
- API 基础路径：$HA_URL/api

## 设备列表

### 灯光

| 设备名称 | entity_id | 说明 |
|---|---|---|
| 客厅主灯 | light.living_room_main | 支持调光，0-255 |
| 客厅氛围灯 | light.living_room_ambient | 支持 RGB |
| 卧室顶灯 | light.bedroom_ceiling | 开关，不支持调光 |
| 玄关灯 | light.hallway | 开关 |

### 温控

| 设备名称 | entity_id | 说明 |
|---|---|---|
| 客厅空调 | climate.living_room_ac | 支持制冷/制热/送风 |
| 卧室空调 | climate.bedroom_ac | 支持制冷/制热 |

### 传感器

| 设备名称 | entity_id | 说明 |
|---|---|---|
| 前门门锁 | lock.front_door | 锁定/解锁状态 |
| 后门门磁 | binary_sensor.back_door | open/closed |
| 客厅窗户 | binary_sensor.living_room_window | open/closed |
| 卧室窗户 | binary_sensor.bedroom_window | open/closed |

### 场景（Scenes）

| 场景名称 | entity_id | 触发动作 |
|---|---|---|
| 到家模式 | scene.arrive_home | 开玄关灯、客厅主灯，空调开制冷 26° |
| 离家模式 | scene.leave_home | 关所有灯、关所有空调 |
| 睡眠模式 | scene.sleep | 关客厅灯，卧室调暗至 10%，空调制冷 24° |
| 影院模式 | scene.cinema | 关主灯，氛围灯调至橙色低亮度 |

## 常用 API

### 查询设备状态
GET $HA_URL/api/states/{entity_id}
Authorization: Bearer $HA_TOKEN

### 控制设备
POST $HA_URL/api/services/{domain}/{service}
Authorization: Bearer $HA_TOKEN
Content-Type: application/json

### 触发场景
POST $HA_URL/api/services/scene/turn_on
Body: {"entity_id": "scene.arrive_home"}
```

这份设备清单越详细，AI 的控制越精准。你不需要告诉它"调用 API"——它读了 `AGENTS.md` 就知道怎么操作了。

---

## 第三步：配置 openclaw.json

```json
{
  "agents": {
    "list": [
      {
        "id": "home",
        "workspace": "~/.openclaw/workspace-home",
        "model": {
          "primary": "anthropic/claude-sonnet-4-6"
        },
        "tools": {
          "profile": "minimal",
          "allow": ["web", "nodes"]
        },
        "env": {
          "HA_TOKEN": "your-ha-token",
          "HA_URL": "http://homeassistant.local:8123"
        }
      }
    ]
  },
  "bindings": [
    {
      "channel": "feishu",
      "agentId": "home"
    }
  ]
}
```

---

## 场景一：自然语言控制设备

配置好之后，打开飞书，直接说：

```
把客厅灯调暗一点，开个影院模式，我要看电影了
```

AI 会：
1. 读取 `AGENTS.md` 里的设备信息
2. 识别出需要触发"影院模式"场景
3. 调用 `POST /api/services/scene/turn_on`，`entity_id: scene.cinema`
4. 回复你"好的，影院模式已开启，氛围灯调成橙色了"

你不需要说 `entity_id`，也不需要说 API 路径。自然语言 → AI 翻译成 API 调用，这就是整合的价值所在。

**更多例子**：

```
查一下客厅现在温度是多少

把所有灯关了，我要出门了

帮我开到家模式

卧室空调设成 26 度制冷
```

每一句话，AI 都会翻译成对应的 HA API 调用。

---

## 场景二：到家自动化

结合第14章的手机 Node 位置能力，实现真正的"到家自动触发"。

**思路**：手机 Node 持续上报位置，Heartbeat 每 15 分钟检查一次，如果位置从"不在家"变成"在家附近"，触发"到家模式"。

在 `HEARTBEAT.md` 里添加：

```markdown
# HEARTBEAT.md

## 位置检查

1. 获取手机当前位置（node.location）
2. 判断是否在家附近（距离家庭坐标 200 米以内，家庭坐标：纬度 XX.XXXX，经度 XX.XXXX）
3. 如果上次检查不在家、这次在家了（到家事件），执行：
   - POST $HA_URL/api/services/scene/turn_on，body: {"entity_id": "scene.arrive_home"}
   - 发消息告诉我"你已到家，已开启到家模式"
4. 如果上次在家、这次不在家了（离家事件），执行：
   - POST $HA_URL/api/services/scene/turn_on，body: {"entity_id": "scene.leave_home"}
   - 发消息告诉我"检测到你已离家，已关闭所有设备"
5. 其他情况：保持沉默

## 状态记忆

把上次的位置状态（在家/不在家）写入 MEMORY.md，供下次心跳判断。
```

**📌 频率与电量**

Heartbeat 默认 30 分钟一次，对于到家/离家检测有点慢。可以在 `openclaw.json` 里把心跳频率调短：

```json
{
  "heartbeat": {
    "intervalMinutes": 5
  }
}
```

手机 Node 的位置获取会消耗一定电量，根据你的需求平衡精度和电池寿命。

---

## 场景三：夜间安全巡查

每天晚上 11 点，AI 自动检查所有门窗状态，只在发现问题时才提醒你。

```bash
openclaw cron add \
  --name "夜间安全巡查" \
  --cron "0 23 * * *" \
  --timezone "Asia/Shanghai" \
  --session isolated \
  --agent home \
  --message "执行夜间安全巡查：
1. 查询以下传感器的当前状态：
   - binary_sensor.back_door（后门）
   - binary_sensor.living_room_window（客厅窗户）
   - binary_sensor.bedroom_window（卧室窗户）
   - lock.front_door（前门门锁）
2. 如果所有门窗都关闭且门锁锁定：不要发任何消息，静默结束
3. 如果发现任何门窗开着或门锁未锁：立刻通过 messaging 工具发飞书消息提醒我，
   列出具体哪些设备状态异常，建议我去检查
4. 绝对不要因为一切正常就发消息告诉我'一切正常'——没有问题就不打扰我" \
  --announce-on-error
```

注意最后一点强调"一切正常不要发消息"——这个细节非常重要。如果不写清楚，AI 每晚都会礼貌地汇报"所有设备状态正常"，很快就会变成你忽略的噪音。

---

## 完整 SOUL.md

给家居助理一个合适的性格设定：

```bash
cat > ~/.openclaw/workspace-home/SOUL.md << 'EOF'
## 身份

你是家庭的智能管家，负责管理和控制家里的智能设备。

## 性格

- 简洁高效，执行指令后简短确认结果
- 主动性强，能从上下文推断意图（"我要睡了" = 触发睡眠模式）
- 出错时诚实，明确说哪个设备调用失败了，而不是假装成功

## 能力边界

- 能控制的设备都在 AGENTS.md 里列出了
- 不在列表里的设备，如实告知"这个设备我还没有权限控制"
- 遇到歧义先确认，比如"调暗一点"——先问"调到多少亮度比较合适？"还是直接调到 30%？
EOF
```

---

## 测试验收

**测试一**：发消息"查一下后门现在是开的还是关的"
→ AI 应该调用 HA API，返回真实的传感器状态

**测试二**：发消息"我要睡了"
→ AI 应该识别意图，触发睡眠场景，回复简短确认

**测试三**：手动触发夜间巡查
```bash
openclaw cron run --id <job-id>
```
→ 如果门窗全关，没有消息；如果你故意开着一扇窗，应该收到提醒

---

## 本章小结

这个项目展示的核心模式是：

**AI 作为 API 的自然语言翻译层**

Home Assistant 有完整的 REST API，但它需要你知道 entity_id、service 名称、参数格式。OpenClaw 在中间做了一层翻译——你说人话，AI 把它翻译成 API 调用，结果返回给你。

这个模式不局限于 Home Assistant。任何有 REST API 的系统都可以用同样的方式接入：

- Notion API → AI 帮你整理笔记
- GitHub API → AI 帮你管理 issue
- Jira API → AI 帮你更新任务状态

只要在 `AGENTS.md` 里写清楚 API 文档，AI 就知道怎么用了。

---

**📌 本章检查清单**

- AI 成功调用了 HA API，并根据你的自然语言指令控制了至少一个设备吗？
- 夜间巡查任务触发后，在门窗关闭时保持了沉默，在有异常时才发送了提醒吗？
- 你理解"AI 作为 API 翻译层"这个模式，知道如何把它应用到其他系统吗？

---

## 实战篇：完结

四个项目，从简单到复杂，从单 Agent 到多 Agent，从主动触发到被动响应，从纯对话到物理世界控制——你把整本书的核心概念都走了一遍。

这不是终点，这是起点。

你现在有了构建自己专属 AI 助手系统的完整工具箱。接下来的附录是参考资料，需要时随时查阅。

剩下的，都是你的了。