///Users/apichet/Downloads/cheetah-insurance-app/src/utils/themeToggle.js
// /src/utils/themeToggle.js

export const THEME_KEY = "theme";

export const THEMES = {
  LIGHT: "light-theme",
  DARK: "dark-theme",
};

/**
 * ดึงธีมที่ถูกบันทึกไว้ใน localStorage (หรือ fallback เป็น light)
 */
export function getSavedTheme() {
  return localStorage.getItem(THEME_KEY) || THEMES.LIGHT;
}

/**
 * ตั้งธีมบน <html>, <body>, และบันทึกไว้
 */
export function applyTheme(theme) {
  const html = document.documentElement;
  const body = document.body;

  // ลบธีมเก่าก่อน
  html.classList.remove(THEMES.LIGHT, THEMES.DARK);
  body.classList.remove(THEMES.LIGHT, THEMES.DARK);

  // เพิ่มธีมใหม่
  html.classList.add(theme);
  body.classList.add(theme);

  // สำหรับ Tailwind/MUI ที่ใช้ data-theme
  html.setAttribute("data-theme", theme);

  // บันทึก
  localStorage.setItem(THEME_KEY, theme);
}

/**
 * Toggle ธีม: light <-> dark และ return ธีมใหม่
 */
export function toggleTheme() {
  const current = getSavedTheme();
  const next = current === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;
  applyTheme(next);
  return next;
}
