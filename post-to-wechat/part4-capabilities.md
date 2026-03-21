---
title: "跟鬼哥一起学OpenClaw（四）：能力篇"
summary: "给 AI 装上工具和技能，让它真正能干活。内置工具、技能生态、安全防线，三章搞定 AI 的行动边界。"
author: 鬼哥
coverImage: /Users/li.luo/dev/git/learn-claw/book/part4-capabilities/images/part4-index.jpg
---

# 第四部分：能力篇

大脑有了，现在来装双手。

前三部分解决的是"AI 是谁、它记得什么、它的对话怎么管理"。这一部分解决更实际的问题：**AI 能帮你做什么，以及怎么确保它不会做坏事**。

OpenClaw 的能力体系分三层：工具提供底层执行能力，Skill 教会 AI 如何用好这些能力，安全机制确保能力在可控的边界内运作。三层缺一不可。

![](/Users/li.luo/dev/git/learn-claw/book/part4-capabilities/images/part4-index.jpg)

**本部分包含三章：**

- **第8章** 介绍 OpenClaw 的内置工具全景，重点讲解最常用的 exec（终端命令）、browser（浏览器控制）和 web（搜索抓取），以及如何用工具策略设定权限边界。
- **第9章** 讲解 Skill（Skills）生态——Skill 和工具的区别、三层加载机制、ClawHub 社区市场，以及如何从零写一个自己的 Skill。
- **第10章** 建立完整的安全体系：配对机制防止未授权访问，工具策略精细控制权限，Docker 沙箱把 AI 的操作隔离在安全边界内。

---

# 第8章：内置工具——AI 的"瑞士军刀"

到目前为止，你的 AI 助手能聊天、能记忆、能在多个渠道响应你。但本质上，它还只是一个"嘴上厉害"的存在——说得头头是道，却什么都做不了。

工具（Tools）是改变这一切的分水岭。

有了工具，AI 可以执行终端命令、控制浏览器、搜索网络、发送消息、调用设备摄像头。它从一个对话伙伴，变成了一个真正能帮你**干活**的助手。

![](/Users/li.luo/dev/git/learn-claw/book/part4-capabilities/images/ch08-tools.jpg)

---

## 工具全景

OpenClaw 的工具按功能分成九大组：

| 工具组 | 包含工具 | 能做什么 |
|---|---|---|
| `runtime` | exec, process | 执行终端命令，管理后台进程 |
| `fs` | read, write, edit, apply_patch | 读写和编辑本地文件 |
| `web` | search, fetch | 搜索网络，抓取网页内容 |
| `ui` | browser, canvas | 控制浏览器，操作可视化画布 |
| `messaging` | message | 跨平台发送消息（飞书/Slack/Discord 等）|
| `memory` | memory_search, memory_get | 读写记忆文件 |
| `sessions` | session_* | 跨 Agent 通信，生成子 Agent |
| `automation` | cron, webhook | 管理定时任务和 Webhook |
| `nodes` | node_* | 控制配对的手机和电脑设备 |

默认配置（`full` 画像）下，所有工具组都是开放的。AI 会根据你的请求自行判断该用哪个工具。

接下来重点介绍三个你最先会用到的工具组。

---

## exec：让 AI 执行终端命令

`exec` 工具让 AI 在你的机器上运行 shell 命令。这是工具箱里权力最大的一把——也因此最需要谨慎对待。

把终端命令能力交给 AI，大多数时候它用的是 `ls`、`cat`、`git status` 这类温和的命令。但如果你没有设置任何边界，它偶尔会认为 `rm -rf` 是解决问题的好办法。不是因为它坏，是因为它觉得这样最有效。

### 能做什么

```
帮我查看一下 ~/projects 目录下有哪些文件
```

```
运行 pytest，看看有没有失败的测试
```

```
把 nginx 的错误日志最后 50 行给我看看
```

这些都是 `exec` 的典型使用场景。AI 会在执行前告诉你它要运行什么命令，执行后把输出返回给你。

### 后台执行

对于耗时的任务，可以让 AI 在后台运行：

```
帮我在后台运行 npm run build，完成后通知我
```

AI 会启动进程，继续和你对话，等任务完成再告知结果。

### 安全边界

**⚠️ 重要：不要让 exec 裸奔**

默认配置下，`exec` 可以运行任何命令，包括删文件、修改系统配置、访问敏感目录。

在开始大量使用 exec 之前，建议做两件事：

**1. 配置工具策略**（本章末尾会讲）：明确哪些命令允许，哪些不允许。

**2. 启用 Docker 沙箱**（第10章详细讲）：让 AI 的命令在隔离容器里运行，即使它做了什么"过激"的操作，影响也被限制在容器内，不会波及你的宿主机。

---

## browser：控制一个完整的浏览器

`browser` 工具给 AI 配了一台它自己的无头电脑——屏幕你看不见，但鼠标和键盘它全能控制。

这是最能让人"哇"一声的工具。

### 能做什么

**截图和快照：**
```
帮我截一下 https://news.ycombinator.com 的首页
```

AI 会打开浏览器，导航到这个地址，截图后发给你。

**网页交互：**
```
打开 GitHub，帮我搜索 "vitepress"，截图搜索结果
```

AI 可以在网页上点击、输入文字、按回车——和真人操作浏览器完全一样，只是它的"眼睛"靠截图来看页面内容。

**数据抓取：**
```
打开这个招聘页面，把所有职位名称和薪资范围整理成表格
```

**生成 PDF：**
```
把 https://example.com/report 保存成 PDF，放到我的桌面
```

**自动化流程：**
```
帮我登录 Tesco 网站（账号密码在 USER.md 里），
把购物车里的商品清单发给我看看
```

**📌 多个浏览器 Profile**

`browser` 工具支持多个独立的 Profile，每个 Profile 有独立的 Cookie 和登录状态。这样 AI 可以同时管理多个网站的登录会话，互不干扰。

**ℹ️ 浏览器工具的工作原理**

OpenClaw 的 `browser` 工具管理一个独立的 Chrome/Chromium 实例，通过 Chrome DevTools Protocol（CDP）控制它。AI 每次操作后会获取页面快照（无障碍树 + 截图），据此判断下一步该怎么操作——就像一个用截图来"看"屏幕的盲打高手。

---

## web：搜索与网页抓取

`web` 工具解决一个根本问题：AI 的训练数据有截止日期，它不知道昨天发生了什么。

有了 `web` 工具，AI 可以实时搜索网络，获取最新信息。

### 网络搜索

```
帮我搜一下 Claude 4.6 最新的定价信息
```

```
最近有没有关于树莓派 5 的新测评？
```

OpenClaw 支持多个搜索提供商：Brave Search、Firecrawl、Gemini、Grok 等。使用搜索功能需要配置至少一个提供商的 API Key。

推荐从 **Brave Search** 开始，免费额度慷慨，申请简单：在 [Brave Search API](https://api.search.brave.com) 注册后，把 Key 写入配置：

```json
{
  "braveSearch": {
    "apiKey": "你的BraveSearchAPIKey"
  }
}
```

### 网页抓取

除了搜索，`web` 工具还可以直接抓取指定页面的内容：

```
帮我读一下这篇文章的主要内容：https://example.com/article
```

AI 会抓取页面，提取正文，以 Markdown 格式返回——不用你手动复制粘贴。

---

## 工具策略：设定边界

工具很强大，但并非每个场景都需要全部工具。工具策略让你精确控制 AI 能用什么、不能用什么。

### allow / deny 配置

在 `openclaw.json` 里，`tools.allow` 和 `tools.deny` 控制工具的开关：

```json
{
  "agents": {
    "defaults": {
      "tools": {
        "deny": ["exec", "group:nodes"]
      }
    }
  }
}
```

规则说明：
- `deny` 优先于 `allow`——如果一个工具同时出现在两个列表里，以 deny 为准
- 可以指定单个工具名（如 `exec`），也可以指定整组（如 `group:nodes`）
- 支持通配符

### 四种内置工具画像

除了手动配置，OpenClaw 提供了四种开箱即用的工具画像，适合不同场景：

| 画像 | 开放的工具组 | 适合场景 |
|---|---|---|
| `minimal` | 仅会话状态 | 最严格限制，适合对外开放的 Bot |
| `coding` | 文件系统、终端、会话、记忆 | 编程助手场景 |
| `messaging` | 消息发送、会话历史 | 纯消息场景 |
| `full`（默认）| 全部工具 | 个人使用，自己对自己负责 |

切换画像：

```json
{
  "agents": {
    "defaults": {
      "tools": {
        "profile": "coding"
      }
    }
  }
}
```

**📌 个人使用 vs 对外开放**

如果这个 Bot 只有你自己用，`full` 画像完全合理。如果你把 Bot 分享给别人，或者接入了公开群组，**强烈建议切换到更严格的画像**，再根据需要逐步放开，而不是从 `full` 开始往回收。

---

## 动手练习

依次尝试以下两个请求：

**测试 exec：**
```
帮我看一下当前系统的 Node.js 版本和 npm 版本
```

AI 应该会执行 `node --version` 和 `npm --version`，把结果告诉你。

**测试 browser（需要先确认 browser 工具已启用）：**
```
帮我截一张 https://docs.openclaw.ai 首页的图
```

AI 应该会打开浏览器，访问这个地址，截图后发给你。

如果两个都成功了，说明你的工具配置是通畅的。

---

**📌 本章检查清单**

- 你知道 `exec` 和 `browser` 的主要区别是什么吗？（一个在终端，一个在浏览器）
- 你了解为什么 `exec` 需要特别注意安全边界吗？
- 你知道如何用工具画像（profile）快速切换工具权限吗？

---

# 第9章：Skill 生态——教会 AI 新能力

上一章介绍了工具（Tools），这章介绍 Skill。在继续之前，先把两者的区别说清楚，因为这是初学者最容易混淆的地方。

**工具是 AI 的手**——`exec` 让它能执行命令，`browser` 让它能操作浏览器，这是物理能力，内置在 OpenClaw 里。

**Skill 是工具书**——它不添加新的底层能力，而是用文字教 AI 如何调用已有工具完成某个特定任务。没有 Skill，AI 拿着锤子面对一颗螺丝钉，可能真的会用锤子砸；有了 Skill，它知道这种情况应该找螺丝刀。

换句话说：工具决定 AI **能做什么**，Skill 决定它**会不会做好**。

![](/Users/li.luo/dev/git/learn-claw/book/part4-capabilities/images/ch09-skills.jpg)

---

## Skill 的结构

一个 Skill 非常简单：**一个文件夹，里面有一个 `SKILL.md` 文件**。

```
my-skill/
└── SKILL.md
```

`SKILL.md` 分两部分：

**YAML frontmatter（元数据）：**
```yaml
---
name: my-skill
description: 这个 Skill 的一句话描述，AI 靠这句话决定什么时候该调用它
---
```

**Markdown 正文（使用说明）：**
```markdown
## 使用场景
当用户问到 XXX 时，使用此 Skill。

## 操作步骤
1. 先做这个
2. 再做那个
3. 用这种格式返回结果
```

就这些。没有代码，没有编译，没有依赖——一个纯文本文件教会 AI 如何处理特定任务。

**📌 为什么这样设计？**

Skill 本质是注入系统提示词的文本片段。AI 读到这段文字，就学会了这个 Skill 的用法——和你在对话里告诉 AI "遇到这种情况你应该这样做" 是完全一样的机制，只是被固定下来、可复用了。

---

## 三层加载机制

OpenClaw 从三个位置加载 Skill，优先级从低到高：

```
bundled（随安装包）
    ↓ 可被覆盖
managed（~/.openclaw/skills/）
    ↓ 可被覆盖
workspace（~/.openclaw/workspace/skills/）  ← 优先级最高
```

**Bundled Skill**：OpenClaw 安装包自带的 Skill，涵盖基础场景。你不需要做任何事，它们就在那里。

**Managed Skill**：安装在 `~/.openclaw/skills/` 下的 Skill，通常来自 ClawHub（下一节介绍）。所有你管理的 AI Agent 都能看到这里的 Skill。

**Workspace Skill**：放在 `<workspace>/skills/` 下的 Skill，只有这个 Agent 能看到，优先级最高。适合放你自己写的、专属于某个 Agent 的定制 Skill。

实际意义：如果你不满意某个 bundled Skill 的行为，可以在 workspace 里放一个同名 Skill 覆盖它，而不需要修改安装包。

---

## ClawHub：社区 Skill 注册中心

[ClawHub](https://clawhub.com) 是 OpenClaw 的公共 Skill 市场，任何人都可以发布 Skill，任何人都可以安装使用。

截止目前，社区里已经有不少实用 Skill，随手举几个例子：

- **Home Assistant**：用自然语言控制智能家居设备（"把客厅灯调暗一点"）
- **Vienna 公共交通**：查询维也纳实时公交到站时间
- **Oura Ring**：读取你的健康数据和睡眠报告
- **TradingView**：截图 K 线图并进行技术分析
- **Bambu Lab 打印机**：管理 3D 打印任务

大多数 Skill 都聚焦于"教 AI 怎么用某个特定服务或工具"，写法也大同小异——看一眼 SKILL.md，你基本就明白它在做什么。

上架到 ClawHub 的 Skill 都会经过 **VirusTotal 安全扫描**——这不是说 Skill 一定安全，但至少排除了"装了个后门"这种最基础的坏事。至于 Skill 内容本身是否合理，还是需要你自己看一眼再安装。

### 安装与管理

安装 Skill：

```bash
clawhub install home-assistant
```

更新所有已安装的 Skill：

```bash
clawhub update --all
```

在 `openclaw.json` 里可以精细控制 Skill 的启用状态和配置：

```json
{
  "skills": {
    "entries": {
      "home-assistant": {
        "enabled": true,
        "config": {
          "baseUrl": "http://homeassistant.local:8123"
        }
      },
      "某个不想用的 Skill": {
        "enabled": false
      }
    }
  }
}
```

---

## 动手写第一个 Skill

安装别人的 Skill 很容易，但写一个自己的 Skill 才能真正理解它的工作原理。我们来写一个实际有用的：**git 仓库状态速览**。

### 第一步：创建 Skill 目录

在你的 Workspace 下创建 Skill 文件夹：

```bash
mkdir -p ~/.openclaw/workspace/skills/git-summary
```

### 第二步：写 SKILL.md

```bash
code ~/.openclaw/workspace/skills/git-summary/SKILL.md
```

写入以下内容：

```markdown
---
name: git-summary
description: 查看 git 仓库的状态摘要，包括当前分支、未提交变更和最近提交记录
---

## 使用场景

当用户询问代码仓库状态、想了解当前 git 进展，或需要快速了解最近代码变更时，使用此 Skill。

## 操作步骤

使用 exec 工具依次运行以下命令：

1. `git branch --show-current` — 获取当前分支名
2. `git status --short` — 获取未提交的变更列表
3. `git log --oneline -5` — 获取最近 5 条提交记录

## 输出格式

将结果整理成以下格式：

🌿 当前分支：{branch}
📝 未提交变更：{n} 个文件
  - M src/foo.ts（已修改）
  - ? new-file.md（未追踪）

最近提交：
  - a1b2c3d feat: 添加用户认证模块
  - 9f8e7d6 fix: 修复登录页面样式问题
  ...
```

### 第三步：测试

保存文件，无需重启 Gateway。在对话里说：

```
帮我看一下 ~/projects/learn-claw 的 git 状态
```

如果 Skill 生效，AI 会按照你定义的步骤操作，输出格式化的 git 状态报告。

**📌 Skill 即时生效**

默认配置下，OpenClaw 会监视 `SKILL.md` 文件的变化。保存后下一个新会话就会加载新 Skill，不需要重启 Gateway。

---

## 安全注意事项

Skill 的本质是注入系统提示词的文本。一个写得不好的 Skill，可能会让 AI 的行为变得奇怪；一个恶意的 Skill，理论上可以引导 AI 做不该做的事。

几条原则：

1. **ClawHub 的 Skill 安装前看一眼 SKILL.md**：内容透明，看完就知道它在做什么
2. **不要从不明来源安装 Skill**：就像不要随便运行陌生人发来的脚本
3. **敏感 Agent 限制 Skill 加载**：如果某个 Agent 处理重要任务，在配置里限制它只能用特定的 bundled Skill

```json
{
  "skills": {
    "allowBundled": ["web-search", "memory"]
  }
}
```

---

## 动手练习

做两件事：

**安装一个 ClawHub Skill**（如果有感兴趣的）：

```bash
clawhub install <你感兴趣的 Skill 名>
```

安装后在对话里试用，看看效果。

**查看当前加载了哪些 Skill**：

```
/context list
```

在输出里找到 `Skills` 部分，你会看到当前会话加载了哪些 Skill，每个 Skill 占用了多少 Token。这也是诊断"为什么系统提示词这么长"的好方法。

---

**📌 本章检查清单**

- 你能说清楚工具和 Skill 的区别吗？（提示：手 vs 工具书）
- 你知道三层 Skill 加载的优先级顺序吗？
- 你自己写的 `git-summary` Skill 能正常运行了吗？

---

# 第10章：安全防线——约束 AI 的行为边界

前两章给 AI 装上了工具和 Skill——它现在能执行命令、控制浏览器、发送消息。

这是好事，也是坏事。

能力越大，边界越重要。一个没有约束的 AI 助手，就像把一个技术高超但没有任何规矩的员工放进你的服务器机房——大多数时候它会做对的事，但你绝对不希望在它心情不好的某天，发现它把 `/etc` 目录清理了一遍。

这一章，我们来建立 OpenClaw 的安全体系。

![](/Users/li.luo/dev/git/learn-claw/book/part4-capabilities/images/ch10-security.jpg)

---

## 第一道防线：配对机制

### 陌生人发消息会发生什么

假设你把飞书机器人的名称分享出去了，或者有人搜到了你的 Bot。他们给你的 Bot 发了一条消息——会发生什么？

默认情况下，他们会收到一串**配对码**：

```
你好！我是一个私人 AI 助手，不接受未经授权的访问。
如需使用，请提供配对码或联系管理员。
配对码请求 ID：pair_a1b2c3d4
```

这道门就是**配对机制（Pairing）**。就像有人想蹭你 WiFi，你给了他一道需要你本人确认的题，而不是直接给密码。

陌生人无法自行完成配对——他们的请求会等待你审批。你在另一端运行：

```bash
openclaw approvals list        # 查看待审批请求
openclaw approvals approve <id>  # 批准
openclaw approvals reject <id>   # 拒绝
```

### 用白名单彻底关门

配对机制是"需要审批才能进"，白名单是"非名单内的人连门都摸不到"。

在渠道配置里设置 `allowFrom`，只有名单里的号码/ID 才能触发 AI 响应：

```json
{
  "channels": {
    "feishu": {
      "allowFrom": ["ou_xxxxxxxxxxxxxxxxx", "ou_yyyyyyyyyyyyyyyyy"]
    },
    "discord": {
      "allowFrom": ["123456789012345678", "987654321098765432"]
    }
  }
}
```

名单外的消息会被静默忽略。这是最干净的保护方式——自己用，或者只给固定的几个人用，直接白名单搞定。

---

## 第二道防线：工具策略精细化

第8章介绍了 `allow` / `deny` 和工具画像。这里补充两个进阶概念。

### elevated：突破沙箱的后门

`elevated` 工具级别允许 AI 在**宿主机**上直接执行命令，绕过后面要讲的沙箱隔离。

```json
{
  "agents": {
    "defaults": {
      "tools": {
        "elevated": ["exec"]
      }
    }
  }
}
```

这个设置的意思是：即使你启用了沙箱，`exec` 工具依然在宿主机上运行，不受沙箱限制。

**⚠️ 谨慎使用 elevated**

`elevated` 是"紧急情况需要突破沙箱"的设计，不是日常配置。

适合用的场景：你需要 AI 操作宿主机上沙箱无法访问的资源（比如特定硬件、宿主机服务）。

不适合用的场景：懒得配沙箱，直接 elevated 省事——这等于放弃了沙箱提供的全部保护。

### per-agent 工具控制

不同的 Agent 可以有不同的工具权限。第13章会讲多智能体，这里先知道这个能力存在：

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": { "profile": "full" }
      },
      {
        "id": "assistant",
        "tools": {
          "profile": "minimal",
          "allow": ["web_search"]
        }
      }
    ]
  }
}
```

主 Agent 拥有完整权限，对外开放的助理 Agent 只能用 `web_search`。

---

## 第三道防线：Docker 沙箱

配对机制和工具策略控制的是"谁能用"和"能用什么"。Docker 沙箱解决的是更底层的问题：**即使 AI 能用 exec，它的操作也被关在一个隔离的小房间里**。

就算它一时手滑运行了 `rm -rf /`，删的也是那个小房间，不是你的真实文件系统。小房间随时可以重建，你的文件安然无恙。

### 前提：安装 Docker

沙箱基于 Docker，先确保 Docker 已安装并运行：

```bash
docker --version
docker ps  # 能看到输出说明 Docker 正常运行
```

然后构建 OpenClaw 的沙箱镜像：

```bash
# 在 OpenClaw 安装目录下运行
scripts/sandbox-setup.sh
```

这会创建一个名为 `openclaw-sandbox:bookworm-slim` 的镜像，这是沙箱的基础环境。

### 三种启用模式

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main"
      }
    }
  }
}
```

三种 `mode` 值：

| 模式 | 含义 | 推荐场景 |
|---|---|---|
| `off` | 不启用沙箱 | 完全信任自己，个人使用 |
| `non-main`（推荐）| 只有非主会话走沙箱 | 日常使用的最佳平衡点 |
| `all` | 所有会话都走沙箱 | 最严格，适合对外开放的服务 |

**📌 为什么推荐 non-main？**

主会话（你自己的 DM）通常需要访问本地文件和宿主机资源，沙箱会增加摩擦。

非主会话（群组消息、Webhook 触发的任务、陌生人 DM）来源更杂，风险更高，应该在沙箱里运行。

`non-main` 模式正好在"方便"和"安全"之间取得平衡。

### 沙箱作用域

`scope` 决定沙箱容器如何分配：

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main",
        "scope": "session"
      }
    }
  }
}
```

| scope | 含义 |
|---|---|
| `session`（默认）| 每个会话一个独立容器，隔离最彻底 |
| `agent` | 同一个 Agent 的所有会话共用一个容器 |
| `shared` | 所有沙箱会话共用一个容器 |

大多数情况下用默认的 `session` 就好。

### 工作区访问控制

沙箱里的 AI 默认在一个**完全隔离的工作目录**里操作，看不到你的真实 Workspace。可以用 `workspaceAccess` 调整：

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "workspaceAccess": "ro"
      }
    }
  }
}
```

| 值 | 含义 |
|---|---|
| `none`（默认）| 沙箱有独立的隔离工作目录，看不到真实 Workspace |
| `ro` | 真实 Workspace 以只读方式挂载到沙箱的 `/agent` |
| `rw` | 真实 Workspace 以读写方式挂载到沙箱的 `/workspace` |

### 网络隔离

沙箱容器默认**完全没有出口网络**——里面的进程无法访问外部互联网。这对执行本地代码来说够用，且大幅降低了数据泄露的风险。

如果你的任务确实需要在沙箱里访问网络，需要在配置里显式开启，并仔细考虑你在放弃什么。

---

## 安全审计

配置完成后，用 OpenClaw 自带的审计工具检查一遍：

```bash
openclaw security audit
```

这个命令会扫描你当前的配置，指出潜在的安全问题，比如：

- 没有设置 `allowFrom` 白名单
- 工具策略过于宽松
- 沙箱未启用但有高风险工具
- Token 或 API Key 以明文写在配置文件里

每条问题都有严重程度标注（Warning / Critical），按提示逐条处理即可。

---

## 动手练习

开启 `non-main` 沙箱模式：

在 `~/.openclaw/openclaw.json` 里添加：

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main",
        "scope": "session"
      }
    }
  }
}
```

重启 Gateway 后，在群组会话（或者用 Webhook 触发一个任务）里，让 AI 运行：

```
执行命令：ls /
```

如果沙箱生效，AI 看到的 `/` 是容器内的文件系统，不会看到你宿主机上的真实目录结构。对比一下：在主会话（DM）里运行同样的命令，看到的是你真实的文件系统。

这就是 `non-main` 模式的效果。

---

## 能力篇小结

第8、9、10 章，我们完整地走过了"给 AI 装能力、教它用好能力、确保它不乱来"的完整闭环：

- **工具**是物理能力，exec / browser / web 是最常用的三件
- **Skill**是知识沉淀，ClawHub 提供现成的，你也可以自己写
- **安全体系**有三层：配对机制（控制谁能用）、工具策略（控制能用什么）、沙箱隔离（控制影响范围）

下一部分，**进阶篇**，我们来解锁 OpenClaw 最有意思的一面：让 AI 不只是被动响应，而是**主动工作**——定时任务、事件触发、多智能体协作，这些才是真正让 AI 成为"助手"而不是"工具"的关键。

---

**📌 本章检查清单**

- 你知道配对机制和 `allowFrom` 白名单的区别吗？（一个需要审批，一个直接拒绝）
- `elevated` 工具策略会带来什么风险？你知道什么时候才应该用它吗？
- 你已经启用了沙箱的 `non-main` 模式，并验证了它的隔离效果吗？