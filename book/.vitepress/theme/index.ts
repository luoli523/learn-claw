import DefaultTheme from 'vitepress/theme'
import HomeToc from './HomeToc.vue'
import Lightbox from './Lightbox.vue'
import { h } from 'vue'
import type { Theme } from 'vitepress'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'layout-bottom': () => h(Lightbox),
    })
  },
  enhanceApp({ app }) {
    app.component('HomeToc', HomeToc)
  },
} satisfies Theme
