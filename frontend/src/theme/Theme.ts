export const theme = {
  colors: {
    primary: '#10b981',
    primaryHover: '#059669',
    bgPrimary: 'var(--bg-primary)',
    bgSecondary: 'var(--bg-secondary)',
    bgTertiary: 'var(--bg-tertiary)',
    bgHover: 'var(--bg-hover)',
    textPrimary: 'var(--text-primary)',
    textSecondary: 'var(--text-secondary)',
    textTertiary: 'var(--text-tertiary)',
    borderColor: 'var(--border-color)',
    borderColorDark: 'var(--border-color-dark)',
    codeBg: 'var(--code-bg)',
    codeBorder: 'var(--code-border)',
    codeText: 'var(--code-text)',
    shadow: 'var(--shadow)',
    danger: '#ef4444',
    dangerHover: '#dc2626',
    success: '#10b981',
    successHover: '#059669',
  },
  breakpoints: {
    mobile: '768px',
    tablet: '1024px',
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
  },
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    xxl: '20px',
  },
};

export type ThemeType = typeof theme;
