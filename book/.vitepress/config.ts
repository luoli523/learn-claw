import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/learn-claw/',
  title: '跟鬼哥一起学OpenClaw',
  description: '从零开始，系统掌握本地 AI 助手 OpenClaw',
  lang: 'zh-CN',

  themeConfig: {
    siteTitle: '跟鬼哥一起学OpenClaw',

    nav: [
      { text: '首页', link: '/' },
      { text: '开始阅读', link: '/part1-cognition/' },
      { text: 'OpenClaw 官方文档', link: 'https://docs.openclaw.ai' },
    ],

    sidebar: [
      {
        text: '第一部分：认知篇',
        collapsed: false,
        items: [
          { text: '本部分导读', link: '/part1-cognition/' },
          { text: '第1章：AI 助手的下一步', link: '/part1-cognition/ch01-what-is-openclaw' },
          { text: '第2章：OpenClaw 全景图', link: '/part1-cognition/ch02-mental-model' },
        ],
      },
      {
        text: '第二部分：上手篇',
        collapsed: false,
        items: [
          { text: '本部分导读', link: '/part2-quickstart/' },
          { text: '第3章：安装与启动', link: '/part2-quickstart/ch03-install' },
          { text: '第4章：连接你的第一个渠道', link: '/part2-quickstart/ch04-first-channel' },
        ],
      },
      {
        text: '第三部分：核心篇',
        collapsed: false,
        items: [
          { text: '本部分导读', link: '/part3-core/' },
          { text: '第5章：工作区', link: '/part3-core/ch05-workspace' },
          { text: '第6章：记忆系统', link: '/part3-core/ch06-memory' },
          { text: '第7章：会话管理', link: '/part3-core/ch07-sessions' },
        ],
      },
      {
        text: '第四部分：能力篇',
        collapsed: false,
        items: [
          { text: '本部分导读', link: '/part4-capabilities/' },
          { text: '第8章：内置工具', link: '/part4-capabilities/ch08-tools' },
          { text: '第9章：技能生态', link: '/part4-capabilities/ch09-skills' },
          { text: '第10章：安全防线', link: '/part4-capabilities/ch10-security' },
        ],
      },
      {
        text: '第五部分：进阶篇',
        collapsed: false,
        items: [
          { text: '本部分导读', link: '/part5-advanced/' },
          { text: '第11章：心跳与定时任务', link: '/part5-advanced/ch11-automation' },
          { text: '第12章：Webhook 与外部触发', link: '/part5-advanced/ch12-webhooks' },
          { text: '第13章：多智能体', link: '/part5-advanced/ch13-multi-agent' },
          { text: '第14章：设备节点', link: '/part5-advanced/ch14-nodes' },
        ],
      },
      {
        text: '第六部分：实战篇',
        collapsed: false,
        items: [
          { text: '本部分导读', link: '/part6-projects/' },
          { text: '第15章：打造全能个人助理', link: '/part6-projects/ch15-personal-assistant' },
          { text: '第16章：浏览器自动化专家', link: '/part6-projects/ch16-browser-automation' },
          { text: '第17章：多智能体团队协作', link: '/part6-projects/ch17-agent-team' },
          { text: '第18章：智能家居整合', link: '/part6-projects/ch18-smart-home' },
        ],
      },
      {
        text: '附录',
        collapsed: true,
        items: [
          { text: 'A：CLI 命令速查', link: '/appendix/a-cli-reference' },
          { text: 'B：配置字段参考', link: '/appendix/b-config-reference' },
          { text: 'C：模型提供商选型', link: '/appendix/c-model-providers' },
          { text: 'D：常见问题排错', link: '/appendix/d-troubleshooting' },
        ],
      },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/luoli523/learn-claw' },
    ],

    footer: {
      message: '基于 CC BY-NC-SA 4.0 许可证发布',
      copyright: '© 2026 鬼哥',
    },

    search: {
      provider: 'local',
    },

    docFooter: {
      prev: '上一页',
      next: '下一页',
    },

    outline: {
      label: '本页目录',
      level: [2, 3],
    },

    lastUpdated: {
      text: '最后更新于',
    },

    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '目录',
    darkModeSwitchLabel: '主题',
  },
})
