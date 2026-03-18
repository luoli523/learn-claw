# 附录 A：OpenClaw CLI 常用命令速查

![](./images/a-cli-reference.webp)

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
  --channel telegram

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
| `--channel <channel>` | 指定推送渠道（telegram/whatsapp 等） |
| `--announce` | 任务完成后推送结果到渠道 |
| `--announce-on-error` | 仅在出错时推送 |
| `--timezone <tz>` | 时区（如 Asia/Shanghai） |
