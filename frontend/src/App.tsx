import { useState, useMemo, useContext } from "react";
import {
  ThemeProvider,
  CssBaseline,
  Box,
  IconButton,
  Tooltip,
  Button,
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
  const [darkMode, setDarkMode] = useState(true);
  const [authDialogOpen, setAuthDialogOpen] = useState(false);
  const theme = useMemo(() => (darkMode ? darkTheme : lightTheme), [darkMode]);
  const authContext = useContext(AuthContext);

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

          <Analyzer />
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
