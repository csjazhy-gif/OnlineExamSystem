// 高端主题管理系统 - Premium Edition
export const themes = {
  // 深紫渐变主题（默认）
  default: {
    name: '深紫渐变',
    primary: '#667eea',
    primaryLight: '#818cf8',
    primaryDark: '#4f46e5',
    primaryRgb: '102, 126, 234',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
    background: 'linear-gradient(135deg, #e0e7ff 0%, #ede9fe 50%, #fce7f3 100%)',
  },
  
  // 海洋蓝主题
  ocean: {
    name: '海洋蓝',
    primary: '#0ea5e9',
    primaryLight: '#38bdf8',
    primaryDark: '#0284c7',
    primaryRgb: '14, 165, 233',
    gradient: 'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 50%, #22d3ee 100%)',
    background: 'linear-gradient(135deg, #e0f2fe 0%, #cffafe 50%, #ecfeff 100%)',
  },
  
  // 翡翠绿主题
  emerald: {
    name: '翡翠绿',
    primary: '#10b981',
    primaryLight: '#34d399',
    primaryDark: '#059669',
    primaryRgb: '16, 185, 129',
    gradient: 'linear-gradient(135deg, #10b981 0%, #14b8a6 50%, #06b6d4 100%)',
    background: 'linear-gradient(135deg, #d1fae5 0%, #ccfbf1 50%, #cffafe 100%)',
  },
  
  // 日落橙主题
  sunset: {
    name: '日落橙',
    primary: '#f97316',
    primaryLight: '#fb923c',
    primaryDark: '#ea580c',
    primaryRgb: '249, 115, 22',
    gradient: 'linear-gradient(135deg, #f97316 0%, #ef4444 50%, #ec4899 100%)',
    background: 'linear-gradient(135deg, #ffedd5 0%, #fee2e2 50%, #fce7f3 100%)',
  },
  
  // 深空黑主题
  midnight: {
    name: '深空黑',
    primary: '#818cf8',
    primaryLight: '#a5b4fc',
    primaryDark: '#6366f1',
    primaryRgb: '129, 140, 248',
    gradient: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%)',
    background: 'linear-gradient(135deg, #1e1b4b 0%, #1e293b 50%, #0f172a 100%)',
    isDark: true,
  },
  
  // 玫瑰粉主题
  rose: {
    name: '玫瑰粉',
    primary: '#ec4899',
    primaryLight: '#f472b6',
    primaryDark: '#db2777',
    primaryRgb: '236, 72, 153',
    gradient: 'linear-gradient(135deg, #ec4899 0%, #f43f5e 50%, #f97316 100%)',
    background: 'linear-gradient(135deg, #fce7f3 0%, #ffe4e6 50%, #fff7ed 100%)',
  },
};

// 应用主题
export function applyTheme(themeName = 'default') {
  const theme = themes[themeName] || themes.default;
  const root = document.documentElement;
  
  // 设置CSS变量
  root.style.setProperty('--theme-primary', theme.primary);
  root.style.setProperty('--theme-primary-light', theme.primaryLight);
  root.style.setProperty('--theme-primary-dark', theme.primaryDark);
  root.style.setProperty('--theme-primary-rgb', theme.primaryRgb);
  root.style.setProperty('--theme-gradient', theme.gradient);
  root.style.setProperty('--theme-background', theme.background);
  
  // 深色模式特殊处理
  if (theme.isDark) {
    root.style.setProperty('--text-primary', '#ffffff');
    root.style.setProperty('--text-regular', '#e0e0e0');
    root.style.setProperty('--text-secondary', '#b0b0b0');
    root.style.setProperty('--background-white', '#1e1e1e');
    root.style.setProperty('--border-light', '#404040');
    root.classList.add('dark-mode');
  } else {
    root.style.setProperty('--text-primary', '#303133');
    root.style.setProperty('--text-regular', '#606266');
    root.style.setProperty('--text-secondary', '#909399');
    root.style.setProperty('--background-white', '#ffffff');
    root.style.setProperty('--border-light', '#e4e7ed');
    root.classList.remove('dark-mode');
  }
  
  // 保存到本地存储
  localStorage.setItem('theme', themeName);
  
  // 触发主题变更事件
  window.dispatchEvent(new CustomEvent('theme-changed', { detail: { themeName, theme } }));
  
  return theme;
}

// 获取当前主题
export function getCurrentTheme() {
  return localStorage.getItem('theme') || 'default';
}

// 初始化主题
export function initTheme() {
  const savedTheme = getCurrentTheme();
  return applyTheme(savedTheme);
}
