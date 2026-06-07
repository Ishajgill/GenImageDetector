import { createTheme, type PaletteMode } from "@mui/material/styles";

export const makeTheme = (mode: PaletteMode) => {
  const isDark = mode === "dark";

  // Mode-dependent surface tokens, reused across the component overrides below.
  const bgDefault = isDark ? "#0d0d17" : "#fafaf8";
  const paper = isDark ? "#181826" : "#ffffff";
  const textPrimary = isDark ? "#e8e8f3" : "#1a1a2e";
  const textSecondary = isDark ? "#9aa0b5" : "#64748b";
  const border = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)";
  const cardShadow = isDark
    ? "0 4px 20px rgba(0,0,0,0.5)"
    : "0 4px 20px rgba(0,0,0,0.06)";
  const tableHeadBg = isDark ? "#20203a" : "#f8faff";
  const tableHeadColor = isDark ? "#6b7394" : "#94a3b8";

  return createTheme({
    palette: {
      mode,
      primary: { main: "#6366f1", light: "#818cf8", dark: "#4f46e5" },
      secondary: { main: "#8b5cf6", light: "#a78bfa", dark: "#7c3aed" },
      error: { main: "#e11d48", light: "#f43f5e", dark: "#be123c" },
      warning: { main: "#f97316", light: "#fb923c", dark: "#ea580c" },
      success: { main: "#16a34a", light: "#22c55e", dark: "#15803d" },
      background: { default: bgDefault, paper },
      text: { primary: textPrimary, secondary: textSecondary },
      divider: border,
    },
    typography: {
      fontFamily: '"DM Sans", "Inter", sans-serif',
      h1: { fontWeight: 800, letterSpacing: "-0.03em" },
      h2: { fontWeight: 700, letterSpacing: "-0.02em" },
      h5: { fontWeight: 700 },
      h6: { fontWeight: 600 },
    },
    shape: { borderRadius: 12 },
    components: {
      MuiCssBaseline: {
        styleOverrides: `
          @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
          * { box-sizing: border-box; }
          body { background: ${bgDefault}; min-height: 100vh; }
          ::-webkit-scrollbar { width: 6px; }
          ::-webkit-scrollbar-track { background: transparent; }
          ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.2); border-radius: 3px; }
        `,
      },
      MuiCard: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
            backgroundColor: paper,
            border: `1px solid ${border}`,
            boxShadow: cardShadow,
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
            backgroundColor: paper,
            border: `1px solid ${border}`,
            boxShadow: cardShadow,
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: "none",
            fontWeight: 700,
            letterSpacing: "0.01em",
            borderRadius: 10,
          },
          contained: {
            background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
            color: "#ffffff",
            boxShadow: "0 4px 14px rgba(99,102,241,0.3)",
            "&:hover": {
              background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
              boxShadow: "0 6px 20px rgba(99,102,241,0.4)",
              transform: "translateY(-1px)",
            },
          },
          outlined: {
            borderColor: "rgba(99,102,241,0.3)",
            color: "#6366f1",
            "&:hover": {
              borderColor: "#6366f1",
              backgroundColor: "rgba(99,102,241,0.04)",
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: { fontWeight: 700, letterSpacing: "0.02em" },
          colorSuccess: {
            backgroundColor: isDark ? "rgba(22,163,74,0.15)" : "#f0fdf4",
            color: isDark ? "#4ade80" : "#16a34a",
            border: `1px solid ${isDark ? "rgba(34,197,94,0.3)" : "#bbf7d0"}`,
          },
          colorError: {
            backgroundColor: isDark ? "rgba(225,29,72,0.15)" : "#fff1f2",
            color: isDark ? "#fb7185" : "#e11d48",
            border: `1px solid ${isDark ? "rgba(244,63,94,0.3)" : "#fecdd3"}`,
          },
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: { backgroundColor: "rgba(99,102,241,0.1)", borderRadius: 4 },
          bar: { borderRadius: 4 },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: { borderColor: border, color: textPrimary },
          head: {
            color: tableHeadColor,
            fontWeight: 700,
            fontSize: "0.72rem",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            backgroundColor: tableHeadBg,
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            "& .MuiOutlinedInput-root": {
              "& fieldset": { borderColor: border },
              "&:hover fieldset": { borderColor: "rgba(99,102,241,0.4)" },
              "&.Mui-focused fieldset": { borderColor: "#6366f1" },
            },
            "& .MuiInputLabel-root.Mui-focused": { color: "#6366f1" },
          },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: "none",
            fontWeight: 600,
            "&.Mui-selected": { color: "#6366f1" },
          },
        },
      },
      MuiTabs: {
        styleOverrides: {
          indicator: { backgroundColor: "#6366f1" },
        },
      },
      MuiDialog: {
        styleOverrides: {
          paper: {
            backgroundColor: paper,
            border: `1px solid ${border}`,
            boxShadow: isDark
              ? "0 20px 60px rgba(0,0,0,0.6)"
              : "0 20px 60px rgba(0,0,0,0.15)",
            backgroundImage: "none",
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            margin: "2px 8px",
            width: "calc(100% - 16px)",
            "&:hover": { backgroundColor: "rgba(99,102,241,0.08)" },
            "&.Mui-selected": {
              backgroundColor: "rgba(99,102,241,0.12)",
              borderLeft: "2px solid #6366f1",
            },
          },
        },
      },
    },
  });
};

export const lightTheme = makeTheme("light");
export const darkTheme = makeTheme("dark");
// Backwards-compatible default export (light).
export const theme = lightTheme;
