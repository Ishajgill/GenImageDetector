import { useState, useMemo } from "react";
import {
  ThemeProvider,
  CssBaseline,
  Box,
  IconButton,
  Tooltip,
} from "@mui/material";
import { Brightness4, Brightness7 } from "@mui/icons-material";
import { darkTheme, lightTheme } from "./theme";
import "./App.css";
import { Analyzer } from "./components/analyzer/Analyzer";
import { Sidebar } from "./components/sidebar/Sidebar";
import { AuthProvider } from "./providers/AuthProvider";
import { AppProvider } from "./providers/AppProvider";

export const App = () => {
  const [darkMode, setDarkMode] = useState(true);
  const theme = useMemo(() => (darkMode ? darkTheme : lightTheme), [darkMode]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <AppProvider>
          <Box
            sx={{
              display: "flex",
              height: "100vh",
              width: "100vw",
              overflow: "hidden",
              bgcolor: "background.default",
            }}
          >
            <Sidebar />
            <Box
              component="main"
              sx={{
                flex: 1,
                overflow: "auto",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                position: "relative",
              }}
            >
              {/* Theme toggle button */}
              <Tooltip
                title={
                  darkMode ? "Switch to light mode" : "Switch to dark mode"
                }
              >
                <IconButton
                  onClick={() => setDarkMode(!darkMode)}
                  sx={{
                    position: "absolute",
                    top: 16,
                    right: 16,
                    zIndex: 1,
                  }}
                  color="inherit"
                >
                  {darkMode ? <Brightness7 /> : <Brightness4 />}
                </IconButton>
              </Tooltip>
              <Analyzer />
            </Box>
          </Box>
        </AppProvider>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
