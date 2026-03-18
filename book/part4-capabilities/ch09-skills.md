# 第9章：Skill 生态——教会 AI 新能力

上一章介绍了工具（Tools），这章介绍 Skill。在继续之前，先把两者的区别说清楚，因为这是初学者最容易混淆的地方。

**工具是 AI 的手**——`exec` 让它能执行命令，`browser` 让它能操作浏览器，这是物理能力，内置在 OpenClaw 里。

**Skill 是工具书**——它不添加新的底层能力，而是用文字教 AI 如何调用已有工具完成某个特定任务。没有 Skill，AI 拿着锤子面对一颗螺丝钉，可能真的会用锤子砸；有了 Skill，它知道这种情况应该找螺丝刀。

换句话说：工具决定 AI **能做什么**，Skill 决定它**会不会做好**。

![](./images/ch09-skills.webp)

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

::: tip 为什么这样设计？
Skill 本质是注入系统提示词的文本片段。AI 读到这段文字，就学会了这个 Skill 的用法——和你在对话里告诉 AI "遇到这种情况你应该这样做" 是完全一样的机制，只是被固定下来、可复用了。
:::

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

::: tip Skill 即时生效
默认配置下，OpenClaw 会监视 `SKILL.md` 文件的变化。保存后下一个新会话就会加载新 Skill，不需要重启 Gateway。
:::

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

::: tip 本章检查清单
- [ ] 你能说清楚工具和 Skill 的区别吗？（提示：手 vs 工具书）
- [ ] 你知道三层 Skill 加载的优先级顺序吗？
- [ ] 你自己写的 `git-summary` Skill 能正常运行了吗？
:::
