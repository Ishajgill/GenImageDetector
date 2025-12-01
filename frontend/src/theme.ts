import { createTheme, type ThemeOptions } from "@mui/material/styles";

// Shared theme options
const commonTheme: ThemeOptions = {
  typography: {
    fontFamily:
      '"Inter", "Segoe UI", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: "-0.02em",
    },
    h2: {
      fontWeight: 600,
      letterSpacing: "-0.01em",
    },
    h3: {
      fontWeight: 600,
    },
    button: {
      textTransform: "none",
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: "10px 24px",
          fontSize: "0.95rem",
        },
        contained: {
          boxShadow: "none",
          "&:hover": {
            boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderColor: "rgba(0, 0, 0, 0.10)",
        },
      },
    },
  },
};

// Dark theme - prioritized, high-class aesthetic
export const darkTheme = createTheme({
  ...commonTheme,
  palette: {
    mode: "dark",
    primary: {
      main: "#6366f1", // Indigo
      light: "#818cf8",
      dark: "#4f46e5",
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#8b5cf6", // Purple
      light: "#a78bfa",
      dark: "#7c3aed",
    },
    success: {
      main: "#10b981", // Emerald
      light: "#34d399",
      dark: "#059669",
    },
    error: {
      main: "#ef4444", // Red
      light: "#f87171",
      dark: "#dc2626",
    },
    warning: {
      main: "#f59e0b", // Amber
      light: "#fbbf24",
      dark: "#d97706",
    },
    background: {
      default: "#0f172a", // Slate 900
      paper: "#1e293b", // Slate 800
    },
    text: {
      primary: "#f1f5f9", // Slate 100
      secondary: "#cbd5e1", // Slate 300
    },
    divider: "#334155", // Slate 700
  },
});

// Light theme - clean and professional
export const lightTheme = createTheme({
  ...commonTheme,
  palette: {
    mode: "light",
    primary: {
      main: "#4f46e5", // Indigo 600
      light: "#6366f1",
      dark: "#4338ca",
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#7c3aed", // Purple 600
      light: "#8b5cf6",
      dark: "#6d28d9",
    },
    success: {
      main: "#059669", // Emerald 600
      light: "#10b981",
      dark: "#047857",
    },
    error: {
      main: "#dc2626", // Red 600
      light: "#ef4444",
      dark: "#b91c1c",
    },
    warning: {
      main: "#d97706", // Amber 600
      light: "#f59e0b",
      dark: "#b45309",
    },
    background: {
      default: "#f8fafc", // Slate 50
      paper: "#ffffff",
    },
    text: {
      primary: "#0f172a", // Slate 900
      secondary: "#475569", // Slate 600
    },
    divider: "#e2e8f0", // Slate 200
  },
});
