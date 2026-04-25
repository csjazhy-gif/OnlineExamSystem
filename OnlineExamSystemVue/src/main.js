/*
 * @Description: 
 * 
 * @Date: 2023-03-08 20:38:49
 */
// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import echarts from 'echarts'
import axios from 'axios'
import './assets/font/iconfont.css'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

// 全局关闭 Dialog 遮罩淡入动画，彻底消除灰屏闪烁
ElementUI.Dialog.props.modalFade = { type: Boolean, default: false }

import VueCookies from 'vue-cookies'
// import './assets/font2/iconfont.css'
import store from '@/vuex/store'
// 引入设计系统规范
import './assets/styles/design-system.css'
// 引入Element UI图标修复样式（全局修复图标与文字重叠问题）
import './assets/styles/element-icon-fix.css'
import './assets/styles/element-fix.css'

Vue.use(ElementUI)
Vue.use(VueCookies)

Vue.config.productionTip = false
Vue.prototype.bus = new Vue()
Vue.prototype.$echarts = echarts
Vue.prototype.$axios = axios

new Vue({ router, store, render: (h) => h(App) }).$mount('#app')
