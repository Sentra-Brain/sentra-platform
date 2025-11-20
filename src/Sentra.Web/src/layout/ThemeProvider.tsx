// src/layout/ThemeProvider.tsx
import { useEffect } from "react";
import { useAppSelector } from "@store/hooks";

export default function ThemeProvider() {
  const theme = useAppSelector((s) => s.ui.theme);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return null;
}
