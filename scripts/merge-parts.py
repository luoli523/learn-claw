#!/usr/bin/env python3
"""
合并每个部分的 index.md + 所有章节，生成适合公众号发布的 Markdown 文件。
输出到 post-to-wechat/ 目录。
"""

import os
import re
from pathlib import Path

BOOK_DIR = Path(__file__).parent.parent / "book"
OUT_DIR = Path(__file__).parent.parent / "post-to-wechat"

PARTS = [
    {
        "dir": "part1-cognition",
        "title": "跟鬼哥一起学OpenClaw（一）：认知篇",
        "summary": "在动手安装之前，先花两章建立心智模型。理解 OpenClaw 是什么、为什么存在，以及它的六个核心角色如何协作。",
        "chapters": ["ch01-what-is-openclaw", "ch02-mental-model"],
        "cover": "part1-cognition/images/part1-index.jpg",
    },
    {
        "dir": "part2-quickstart",
        "title": "跟鬼哥一起学OpenClaw（二）：上手篇",
        "summary": "心智模型建立好了，现在动手。15 分钟装好 Gateway，连通第一个聊天渠道，从「看懂了」变成「跑起来了」。",
        "chapters": ["ch03-install", "ch04-first-channel"],
        "cover": "part2-quickstart/images/part2-index.jpg",
    },
    {
        "dir": "part3-core",
        "title": "跟鬼哥一起学OpenClaw（三）：核心篇",
        "summary": "AI 跑起来了，现在让它真正认识你。Workspace、记忆系统、会话管理——三章讲清楚 OpenClaw 的灵魂所在。",
        "chapters": ["ch05-workspace", "ch06-memory", "ch07-sessions"],
        "cover": "part3-core/images/part3-index.jpg",
    },
    {
        "dir": "part4-capabilities",
        "title": "跟鬼哥一起学OpenClaw（四）：能力篇",
        "summary": "给 AI 装上工具和技能，让它真正能干活。内置工具、技能生态、安全防线，三章搞定 AI 的行动边界。",
        "chapters": ["ch08-tools", "ch09-skills", "ch10-security"],
        "cover": "part4-capabilities/images/part4-index.jpg",
    },
    {
        "dir": "part5-advanced",
        "title": "跟鬼哥一起学OpenClaw（五）：进阶篇",
        "summary": "让 AI 从被动响应变成主动出击：心跳定时、Webhook 触发、多智能体人格、设备节点感知——四章解锁进阶能力。",
        "chapters": ["ch11-automation", "ch12-webhooks", "ch13-multi-agent", "ch14-nodes"],
        "cover": "part5-advanced/images/part5-index.jpg",
    },
    {
        "dir": "part6-projects",
        "title": "跟鬼哥一起学OpenClaw（六）：实战篇",
        "summary": "把所有能力组合起来，做出四个真实可用的项目：全能个人助理、浏览器自动化、多智能体团队、智能家居整合。",
        "chapters": ["ch15-personal-assistant", "ch16-browser-automation", "ch17-agent-team", "ch18-smart-home"],
        "cover": "part6-projects/images/part6-index.jpg",
    },
]


def remove_frontmatter(text: str) -> str:
    """去掉 YAML frontmatter"""
    return re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL).lstrip()


def convert_vitepress_containers(text: str) -> str:
    """把 ::: tip / warning / info / details 块转成普通文字段落"""
    # ::: tip 标题 → **📌 标题**（保留内容）
    def replace_container(m):
        kind = m.group(1).strip()  # tip / warning / info / details
        label = m.group(2).strip() if m.group(2) else ""
        content = m.group(3).strip()

        icon_map = {"tip": "📌", "warning": "⚠️", "info": "ℹ️", "details": "📋"}
        icon = icon_map.get(kind, "📌")

        # 把 [ ] 变成 -，[x] 变成 -
        content = re.sub(r"- \[[ x]\]", "-", content)

        if label:
            return f"**{icon} {label}**\n\n{content}"
        else:
            return content

    text = re.sub(
        r"^:::\s*(tip|warning|info|details)[ \t]*(.*?)\n(.*?)^:::",
        replace_container,
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    # 兜底：清理残余的 :::
    text = re.sub(r"^:::\s*\w*\s*$", "", text, flags=re.MULTILINE)
    return text


def fix_image_paths(text: str, part_dir: str) -> str:
    """把相对图片路径转成绝对路径，并将 .webp 替换为 .jpg（微信不支持 WebP）"""
    abs_base = BOOK_DIR / part_dir
    def replace_img(m):
        path = m.group(1)
        if path.startswith("http"):
            return m.group(0)
        abs_path = (abs_base / path).resolve()
        # 换成 jpg
        abs_path = abs_path.with_suffix(".jpg")
        return f"![]({abs_path})"
    return re.sub(r"!\[.*?\]\((.*?)\)", replace_img, text)


def clean(text: str, part_dir: str) -> str:
    text = remove_frontmatter(text)
    text = convert_vitepress_containers(text)
    text = fix_image_paths(text, part_dir)
    # 去掉多余空行（超过 2 个连续空行压缩为 2 个）
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def merge_part(part: dict) -> str:
    part_dir = part["dir"]
    sections = []

    # 1. index.md
    index_path = BOOK_DIR / part_dir / "index.md"
    if index_path.exists():
        sections.append(clean(index_path.read_text(encoding="utf-8"), part_dir))

    # 2. 各章节
    for ch in part["chapters"]:
        ch_path = BOOK_DIR / part_dir / f"{ch}.md"
        if ch_path.exists():
            sections.append(clean(ch_path.read_text(encoding="utf-8"), part_dir))

    body = "\n\n---\n\n".join(sections)

    # 封面图绝对路径
    cover_abs = (BOOK_DIR / part["cover"]).resolve()

    frontmatter = f"""---
title: "{part['title']}"
summary: "{part['summary']}"
author: 鬼哥
coverImage: {cover_abs}
---

"""
    return frontmatter + body


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for i, part in enumerate(PARTS, 1):
        out_path = OUT_DIR / f"part{i}-{part['dir'].split('-', 1)[1]}.md"
        content = merge_part(part)
        out_path.write_text(content, encoding="utf-8")
        print(f"✓ {out_path.name}  ({len(content):,} chars)")
    print(f"\n全部生成到 {OUT_DIR}/")


if __name__ == "__main__":
    main()
