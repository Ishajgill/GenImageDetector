import { useState, useMemo, useContext, useEffect } from "react";
import {
  ThemeProvider,
  CssBaseline,
  Box,
  IconButton,
  Tooltip,
  Button,
  Link,
  Typography,
} from "@mui/material";
import { Brightness4, Brightness7, Login, Logout } from "@mui/icons-material";
import { darkTheme, lightTheme } from "./theme";
import "./App.css";
import { Analyzer } from "./components/analyzer/Analyzer";
import { Sidebar } from "./components/sidebar/Sidebar";
import { AuthProvider } from "./providers/AuthProvider";
import { AppProvider } from "./providers/AppProvider";
import { AuthDialog } from "./components/auth/AuthDialog";
import { AuthContext } from "./contexts/AuthContext";

const AppContent = () => {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    return saved !== null ? JSON.parse(saved) : true;
  });
  const [authDialogOpen, setAuthDialogOpen] = useState(false);
  const theme = useMemo(() => (darkMode ? darkTheme : lightTheme), [darkMode]);
  const authContext = useContext(AuthContext);

  useEffect(() => {
    localStorage.setItem("darkMode", JSON.stringify(darkMode));
  }, [darkMode]);

  const handleLogout = () => {
    console.log("Logout clicked", authContext);
    if (authContext) {
      authContext.logout();
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
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
          {/* Top right buttons */}
          <Box
            sx={{
              position: "absolute",
              top: 16,
              right: 16,
              zIndex: 1000,
              display: "flex",
              gap: 1,
            }}
          >
            {/* Auth button */}
            {authContext?.user ? (
              <Tooltip title="Logout">
                <Button
                  key={`auth-${authContext.user.id}`}
                  variant="outlined"
                  startIcon={<Logout />}
                  onClick={handleLogout}
                  size="small"
                >
                  {authContext.user.username}
                </Button>
              </Tooltip>
            ) : (
              <Button
                key="auth-login"
                variant="outlined"
                startIcon={<Login />}
                onClick={() => setAuthDialogOpen(true)}
                size="small"
              >
                Login
              </Button>
            )}

            {/* Theme toggle button */}
            <Tooltip
              title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
            >
              <IconButton
                onClick={() => setDarkMode(!darkMode)}
                color="inherit"
              >
                {darkMode ? <Brightness7 /> : <Brightness4 />}
              </IconButton>
            </Tooltip>
          </Box>

          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              width: "100%",
              minHeight: "100%",
              pt: 4,
              pb: 2,
            }}
          >
            <Box sx={{ flex: 1, display: "flex", alignItems: "center" }}>
              <Analyzer />
            </Box>

            {/* Footer */}
            <Box
              component="footer"
              sx={{
                textAlign: "center",
                color: "text.secondary",
              }}
            >
              <Typography variant="body2">
                <Link
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ mx: 1 }}
                >
                  API Docs
                </Link>
                •
                <Link
                  href="https://github.com/RyanAIIen/GenImageDetector"
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ mx: 1 }}
                >
                  GitHub
                </Link>
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>

      <AuthDialog
        open={authDialogOpen}
        onClose={() => {
          console.log("Closing auth dialog");
          setAuthDialogOpen(false);
        }}
      />
    </ThemeProvider>
  );
};

export const App = () => {
  return (
    <AuthProvider>
      <AppProvider>
        <AppContent />
      </AppProvider>
    </AuthProvider>
  );
};

export default App;
