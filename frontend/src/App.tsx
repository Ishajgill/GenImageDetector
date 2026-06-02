import { useState, useContext } from "react";
import { ThemeProvider, CssBaseline, Box, Button, Typography, Avatar, Tooltip, IconButton, Link } from "@mui/material";
import { Login, Logout } from "@mui/icons-material";
import { theme } from "./theme";
import "./App.css";
import { Analyzer } from "./components/analyzer/Analyzer";
import { Sidebar } from "./components/sidebar/Sidebar";
import { AuthProvider } from "./providers/AuthProvider";
import { AppProvider } from "./providers/AppProvider";
import { AuthDialog } from "./components/auth/AuthDialog";
import { AuthContext } from "./contexts/AuthContext";
import { AppContext } from "./contexts/AppContext";
import { HowItWorks } from "./components/HowItWorks";

const AppContent = () => {
  const [authDialogOpen, setAuthDialogOpen] = useState(false);
  const [page, setPage] = useState<"home" | "how-it-works">("home");
  const authContext = useContext(AuthContext);
  const appContext = useContext(AppContext);
  const user = authContext?.user;

  const goHome = () => {
    appContext?.setCurrentResult(null);
    setPage("home");
    window.history.pushState({}, "", "/");
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      {/* Animated background blobs */}
      <Box sx={{ position:"fixed", inset:0, pointerEvents:"none", zIndex:0, overflow:"hidden" }}>
        <Box sx={{ position:"absolute", width:600, height:600, borderRadius:"60% 40% 30% 70%/60% 30% 70% 40%", background:"linear-gradient(135deg,rgba(99,102,241,0.07),rgba(139,92,246,0.05))", top:-200, right:-100, animation:"blob 10s ease-in-out infinite" }}/>
        <Box sx={{ position:"absolute", width:450, height:450, borderRadius:"30% 60% 70% 40%/50% 60% 30% 60%", background:"linear-gradient(135deg,rgba(236,72,153,0.05),rgba(251,146,60,0.04))", bottom:0, left:-100, animation:"blob 12s ease-in-out infinite 3s" }}/>
        <Box sx={{ position:"absolute", width:350, height:350, borderRadius:"50% 50% 30% 70%/40% 60% 40% 60%", background:"linear-gradient(135deg,rgba(34,211,238,0.05),rgba(99,102,241,0.04))", top:"40%", left:"40%", animation:"blob 8s ease-in-out infinite 5s" }}/>
      </Box>

      <Box sx={{ display:"flex", height:"100vh", overflow:"hidden", position:"relative", zIndex:1 }}>
        {page === "home" && <Sidebar />}

        <Box sx={{ flex:1, display:"flex", flexDirection:"column", overflow:"hidden", minWidth:0 }}>
          {/* Navbar */}
          <Box sx={{ display:"flex", alignItems:"center", gap:1.5, px:3, py:1.5, background:"rgba(255,255,255,0.85)", backdropFilter:"blur(20px)", borderBottom:"1px solid rgba(0,0,0,0.06)", boxShadow:"0 1px 20px rgba(0,0,0,0.04)" }}>
            {/* Logo */}
            <Box sx={{ display:"flex", alignItems:"center", gap:1.25, cursor:"pointer" }} onClick={goHome}>
              <Box sx={{ width:34, height:34, borderRadius:2, background:"linear-gradient(135deg,#6366f1,#8b5cf6)", display:"flex", alignItems:"center", justifyContent:"center", boxShadow:"0 4px 12px rgba(99,102,241,0.3)" }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round">
                  <rect x="3" y="3" width="18" height="18" rx="4"/>
                  <circle cx="8.5" cy="8.5" r="1.5" fill="#fff"/>
                  <path d="M21 15l-5-5-4 4-2-2-4 4"/>
                </svg>
              </Box>
              <Typography sx={{ fontFamily:"'Syne',sans-serif", fontWeight:800, fontSize:"15px", color:"#1a1a2e" }}>
                GenImage<Box component="span" sx={{ color:"#6366f1" }}>Detector</Box>
              </Typography>
            </Box>

            {/* Nav links */}
            <Box sx={{ display:{ xs:"none", md:"flex" }, gap:0.5, ml:2 }}>
              <Button size="small" onClick={goHome}
                sx={{ color: page==="home" ? "#6366f1" : "#64748b", fontWeight:600, fontSize:"13px", bgcolor: page==="home" ? "rgba(99,102,241,0.06)" : "transparent", "&:hover":{ color:"#1a1a2e", bgcolor:"#f1f5f9" } }}>
                Home
              </Button>
              <Button size="small" onClick={() => setPage("how-it-works")}
                sx={{ color: page==="how-it-works" ? "#6366f1" : "#64748b", fontWeight:600, fontSize:"13px", bgcolor: page==="how-it-works" ? "rgba(99,102,241,0.06)" : "transparent", "&:hover":{ color:"#1a1a2e", bgcolor:"#f1f5f9" } }}>
                How it works
              </Button>
              <Button size="small" onClick={() => window.open("http://localhost:8000/docs","_blank")}
                sx={{ color:"#64748b", fontWeight:600, fontSize:"13px", "&:hover":{ color:"#1a1a2e", bgcolor:"#f1f5f9" } }}>
                API
              </Button>
            </Box>

            <Box sx={{ flex:1 }}/>

            {/* Status */}
            <Box sx={{ display:"flex", alignItems:"center", gap:0.75, bgcolor:"rgba(99,102,241,0.06)", border:"1px solid rgba(99,102,241,0.15)", borderRadius:20, px:1.25, py:0.5 }}>
              <Box sx={{ width:7, height:7, borderRadius:"50%", bgcolor:"#22c55e", boxShadow:"0 0 6px rgba(34,197,94,0.5)" }}/>
              <Typography sx={{ fontSize:"11px", fontWeight:700, color:"#6366f1" }}>LIVE</Typography>
            </Box>

            {/* Auth */}
            {user ? (
              <Box sx={{ display:"flex", alignItems:"center", gap:1.5 }}>
                <Avatar sx={{ width:30, height:30, bgcolor:"rgba(99,102,241,0.1)", color:"#6366f1", fontSize:"0.75rem", fontWeight:700, border:"1px solid rgba(99,102,241,0.2)" }}>
                  {user.username[0].toUpperCase()}
                </Avatar>
                <Typography sx={{ fontSize:"13px", fontWeight:600, color:"#1a1a2e", display:{ xs:"none", sm:"block" } }}>{user.username}</Typography>
                <Tooltip title="Sign out">
                  <IconButton size="small" onClick={authContext?.logout} sx={{ color:"#94a3b8", "&:hover":{ color:"#e11d48" } }}>
                    <Logout fontSize="small"/>
                  </IconButton>
                </Tooltip>
              </Box>
            ) : (
              <Button variant="contained" size="small" startIcon={<Login/>} onClick={() => setAuthDialogOpen(true)} sx={{ fontSize:"13px" }}>
                Sign In
              </Button>
            )}
          </Box>

          {/* Page content */}
          <Box sx={{ flex:1, overflowY:"auto", display:"flex", justifyContent:"center" }}>
            {page === "home" ? <Analyzer /> : <HowItWorks onBack={goHome} />}
          </Box>

          {/* Footer */}
          <Box sx={{ textAlign:"center", py:1.5, borderTop:"1px solid rgba(0,0,0,0.06)", bgcolor:"rgba(255,255,255,0.7)" }}>
            <Typography variant="body2" color="text.secondary" sx={{ fontSize:"12px" }}>
              <Link href="http://localhost:8000/docs" target="_blank" sx={{ mx:1, color:"inherit", "&:hover":{ color:"#6366f1" } }}>API Docs</Link>·
              <Link component="button" onClick={() => setPage("how-it-works")} sx={{ mx:1, color:"inherit", cursor:"pointer", "&:hover":{ color:"#6366f1" }, textDecoration:"none", fontSize:"12px", background:"none", border:"none" }}>How it works</Link>·
              <Link href="https://github.com/danielcobb/GenImageDetector" target="_blank" sx={{ mx:1, color:"inherit", "&:hover":{ color:"#6366f1" } }}>GitHub</Link>
            </Typography>
          </Box>
        </Box>
      </Box>

      <AuthDialog open={authDialogOpen} onClose={() => setAuthDialogOpen(false)}/>
    </ThemeProvider>
  );
};

export const App = () => (
  <AuthProvider>
    <AppProvider>
      <AppContent/>
    </AppProvider>
  </AuthProvider>
);

export default App;
