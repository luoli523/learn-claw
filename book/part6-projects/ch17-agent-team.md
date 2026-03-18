# 第17章：项目三——多智能体团队协作

一个聪明的人，也有他做不好的事情。

让同一个人既写代码又审代码，几乎没有意义——写代码的人看自己的代码，大脑会自动脑补掉 bug，这是认知偏差，不是能力问题。真正有效的代码审查需要另一双眼睛。

AI 也一样。让同一个 Agent 既理解需求又写代码又自我审查，质量上限很有限。但如果你有三个 Agent——一个专门拆解需求，一个专门写代码，一个专门挑毛病——它们互相传递结果、互相检验，整体输出质量会高得多。

这一章，我们用三个 Agent 搭一条迷你 AI 流水线：需求 → 代码 → 审查 → 结果。

![](./images/ch17-agent-team.webp)

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
最终结果推送到你的 Telegram
```

整个流程你只需要在开头发一句话，其余全部由三个 Agent 自动接力完成。

---

## 整体架构

```
你（Telegram）
  ↓ 发送需求
[PM Agent]（Telegram 渠道，工具：minimal + messaging）
  ↓ 调用 /hooks/agent 触发
[Engineer Agent]（隔离会话，工具：coding）
  ↓ 输出代码，再次调用 /hooks/agent 触发
[Reviewer Agent]（隔离会话，工具：minimal）
  ↓ 审查完毕
最终结果 → Telegram
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
      "channel": "telegram",
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
  "channel": "telegram"
}
```

用 runtime.webhook 工具执行这个请求。
EOF
```

**为什么让 Agent 在 message 里带着"继续传递"的指令？**

因为 Engineer Agent 是隔离会话启动的，它没有任何上下文——它只能从 `message` 里知道自己要做什么，以及做完之后该怎么办。整个接力链路的逻辑都靠 `message` 传递。

---

## 第四步：完整流程演示

配置好之后，你只需要向 Telegram 发一条消息：

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

**T+60s**：你的 Telegram 收到最终结果：

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

PM Agent 完成拆解后，先把任务清单发给你（Telegram），**等你回复"确认"后，才触发 Engineer Agent**。

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
| Binding 路由（Telegram → PM） | 第13章 |

---

::: tip 本章检查清单
- [ ] 三个 Agent 都配置好了，`openclaw gateway status` 显示它们都在运行吗？
- [ ] 你发了一个功能需求，三个 Agent 成功接力，最终结果推送到了 Telegram 吗？
- [ ] 你理解为什么 Agent 之间要通过 Webhook 传递而不是直接"对话"吗？
:::
