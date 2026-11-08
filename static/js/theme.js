(() => {
  const themeButton = document.querySelector('.theme-toggle');
  if (!themeButton) return;

  const savedTheme = localStorage.getItem('codeblog-theme');
  const initialTheme = savedTheme === 'dark' ? 'dark' : 'light';

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    const isDark = theme === 'dark';
    themeButton.textContent = isDark ? 'Light mode' : 'Dark mode';
    themeButton.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} mode`);
    themeButton.setAttribute('aria-pressed', String(isDark));
  }

  applyTheme(initialTheme);
  themeButton.addEventListener('click', () => {
    const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('codeblog-theme', theme);
    applyTheme(theme);
  });
})();
