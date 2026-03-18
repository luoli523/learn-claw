<template>
  <div class="toc-wrap">

    <h2 class="toc-title">完整目录</h2>

    <div class="toc-grid">

      <div class="toc-part">
        <a class="part-heading" href="/learn-claw/part1-cognition/">第一部分：认知篇</a>
        <p class="part-desc">建立心智模型，理解 OpenClaw 的整体架构和设计哲学。</p>
        <ul>
          <li><a href="/learn-claw/part1-cognition/ch01-what-is-openclaw">第1章：AI 助手的下一步——从云端对话到本地常驻</a></li>
          <li><a href="/learn-claw/part1-cognition/ch02-mental-model">第2章：OpenClaw 全景图——10 分钟建立心智模型</a></li>
        </ul>
      </div>

      <div class="toc-part">
        <a class="part-heading" href="/learn-claw/part2-quickstart/">第二部分：上手篇</a>
        <p class="part-desc">装好 Gateway，连通第一个渠道，从"看懂了"变成"跑起来了"。</p>
        <ul>
          <li><a href="/learn-claw/part2-quickstart/ch03-install">第3章：安装与启动——15 分钟跑起来</a></li>
          <li><a href="/learn-claw/part2-quickstart/ch04-first-channel">第4章：连接你的第一个聊天渠道</a></li>
        </ul>
      </div>

      <div class="toc-part">
        <a class="part-heading" href="/learn-claw/part3-core/">第三部分：核心篇</a>
        <p class="part-desc">让 AI 知道你是谁、记住重要的事、管理好对话生命周期。</p>
        <ul>
          <li><a href="/learn-claw/part3-core/ch05-workspace">第5章：工作区——AI 的性格与知识库</a></li>
          <li><a href="/learn-claw/part3-core/ch06-memory">第6章：记忆系统——让 AI 真正"记住"你</a></li>
          <li><a href="/learn-claw/part3-core/ch07-sessions">第7章：会话管理——对话的生命周期</a></li>
        </ul>
      </div>

      <div class="toc-part">
        <a class="part-heading" href="/learn-claw/part4-capabilities/">第四部分：能力篇</a>
        <p class="part-desc">给 AI 装上工具和技能，让它真正能干活，同时约束它的行为边界。</p>
        <ul>
          <li><a href="/learn-claw/part4-capabilities/ch08-tools">第8章：内置工具——AI 的"瑞士军刀"</a></li>
          <li><a href="/learn-claw/part4-capabilities/ch09-skills">第9章：Skill 生态——教会 AI 新能力</a></li>
          <li><a href="/learn-claw/part4-capabilities/ch10-security">第10章：安全防线——约束 AI 的行为边界</a></li>
        </ul>
      </div>

      <div class="toc-part">
        <a class="part-heading" href="/learn-claw/part5-advanced/">第五部分：进阶篇</a>
        <p class="part-desc">让 AI 从被动响应变成主动出击：定时、触发、多人格、物理感知。</p>
        <ul>
          <li><a href="/learn-claw/part5-advanced/ch11-automation">第11章：心跳与定时任务——让 AI 主动找你</a></li>
          <li><a href="/learn-claw/part5-advanced/ch12-webhooks">第12章：Webhook 与外部触发——连接世界的钩子</a></li>
          <li><a href="/learn-claw/part5-advanced/ch13-multi-agent">第13章：多智能体——一个 Gateway，多个 AI 人格</a></li>
          <li><a href="/learn-claw/part5-advanced/ch14-nodes">第14章：设备节点——给 AI 装上眼睛和手脚</a></li>
        </ul>
      </div>

      <div class="toc-part">
        <a class="part-heading" href="/learn-claw/part6-projects/">第六部分：实战篇</a>
        <p class="part-desc">把所有能力组合起来，做出四个真实可用、每天都在跑的项目。</p>
        <ul>
          <li><a href="/learn-claw/part6-projects/ch15-personal-assistant">第15章：打造"双手机"全能个人助理</a></li>
          <li><a href="/learn-claw/part6-projects/ch16-browser-automation">第16章：零代码浏览器自动化专家</a></li>
          <li><a href="/learn-claw/part6-projects/ch17-agent-team">第17章：多智能体团队协作</a></li>
          <li><a href="/learn-claw/part6-projects/ch18-smart-home">第18章：智能家居整合（Home Assistant）</a></li>
        </ul>
      </div>

    </div>

    <div class="toc-appendix">
      <span class="apx-label">附录</span>
      <a href="/learn-claw/appendix/a-cli-reference">A：CLI 常用命令速查</a>
      <a href="/learn-claw/appendix/b-config-reference">B：openclaw.json 字段参考</a>
      <a href="/learn-claw/appendix/c-model-providers">C：模型提供商选型指南</a>
      <a href="/learn-claw/appendix/d-troubleshooting">D：常见问题与排错</a>
    </div>

  </div>
</template>

<style scoped>
.toc-wrap {
  max-width: 1152px;
  margin: 0 auto;
  padding: 48px 24px 64px;
}

.toc-banner {
  text-align: center;
  margin-bottom: 40px;
}

.toc-banner-img {
  max-width: 420px;
  width: 100%;
  border-radius: 12px;
}

.toc-title {
  text-align: center;
  font-size: 1.6rem;
  font-weight: 600;
  margin-bottom: 36px;
  border: none !important;
}

.toc-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.toc-part {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  padding: 22px 24px;
  transition: border-color 0.2s;
}

.toc-part:hover {
  border-color: var(--vp-c-brand-1);
}

.part-heading {
  display: block;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  text-decoration: none;
  margin-bottom: 6px;
}

.part-heading:hover {
  color: var(--vp-c-brand-1);
}

.part-desc {
  font-size: 0.82rem;
  color: var(--vp-c-text-2);
  line-height: 1.55;
  margin: 0 0 12px;
}

.toc-part ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.toc-part ul li {
  border-top: 1px solid var(--vp-c-divider);
}

.toc-part ul li a {
  display: block;
  padding: 6px 0;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  text-decoration: none;
  transition: color 0.15s;
}

.toc-part ul li a:hover {
  color: var(--vp-c-brand-1);
}

/* Appendix */
.toc-appendix {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  padding: 16px 24px;
}

.apx-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--vp-c-text-2);
  margin-right: 8px;
}

.toc-appendix a {
  font-size: 0.82rem;
  color: var(--vp-c-text-2);
  text-decoration: none;
  padding: 4px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 20px;
  transition: border-color 0.15s, color 0.15s;
}

.toc-appendix a:hover {
  color: var(--vp-c-brand-1);
  border-color: var(--vp-c-brand-1);
}

@media (max-width: 768px) {
  .toc-grid {
    grid-template-columns: 1fr;
  }
  .toc-appendix {
    gap: 6px;
  }
}
</style>
