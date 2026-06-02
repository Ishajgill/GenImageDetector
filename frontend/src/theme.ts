import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#6366f1",
      light: "#818cf8",
      dark: "#4f46e5",
    },
    secondary: {
      main: "#8b5cf6",
      light: "#a78bfa",
      dark: "#7c3aed",
    },
    error: {
      main: "#e11d48",
      light: "#f43f5e",
      dark: "#be123c",
    },
    warning: {
      main: "#f97316",
      light: "#fb923c",
      dark: "#ea580c",
    },
    success: {
      main: "#16a34a",
      light: "#22c55e",
      dark: "#15803d",
    },
    background: {
      default: "#fafaf8",
      paper: "#ffffff",
    },
    text: {
      primary: "#1a1a2e",
      secondary: "#64748b",
    },
    divider: "rgba(0,0,0,0.06)",
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
        body { background: #fafaf8; min-height: 100vh; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.2); border-radius: 3px; }
      `,
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          backgroundColor: "#ffffff",
          border: "1px solid rgba(0,0,0,0.06)",
          boxShadow: "0 4px 20px rgba(0,0,0,0.06)",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          backgroundColor: "#ffffff",
          border: "1px solid rgba(0,0,0,0.06)",
          boxShadow: "0 4px 20px rgba(0,0,0,0.06)",
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
          backgroundColor: "#f0fdf4",
          color: "#16a34a",
          border: "1px solid #bbf7d0",
        },
        colorError: {
          backgroundColor: "#fff1f2",
          color: "#e11d48",
          border: "1px solid #fecdd3",
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
        root: { borderColor: "rgba(0,0,0,0.06)", color: "#1a1a2e" },
        head: {
          color: "#94a3b8",
          fontWeight: 700,
          fontSize: "0.72rem",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          backgroundColor: "#f8faff",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            "& fieldset": { borderColor: "rgba(0,0,0,0.12)" },
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
          backgroundColor: "#ffffff",
          border: "1px solid rgba(0,0,0,0.08)",
          boxShadow: "0 20px 60px rgba(0,0,0,0.15)",
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
          "&:hover": { backgroundColor: "rgba(99,102,241,0.04)" },
          "&.Mui-selected": {
            backgroundColor: "rgba(99,102,241,0.06)",
            borderLeft: "2px solid #6366f1",
          },
        },
      },
    },
  },
});

export const darkTheme = theme;
export const lightTheme = theme;
