import React, { useState, useContext, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  TextField,
  Button,
  Box,
  Alert,
  Tabs,
  Tab,
  Typography,
  IconButton,
} from "@mui/material";
import { Close } from "@mui/icons-material";
import { AuthContext } from "../../contexts/AuthContext";

interface AuthDialogProps {
  open: boolean;
  onClose: () => void;
}

export const AuthDialog: React.FC<AuthDialogProps> = ({ open, onClose }) => {
  const [tab, setTab] = useState(0);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const authContext = useContext(AuthContext);

  useEffect(() => {
    if (open) {
      setTab(0);
      setError("");
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (tab === 0) await authContext?.login(username, password);
      else await authContext?.signup(username, password);
      setUsername("");
      setPassword("");
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={() => {
        setUsername("");
        setPassword("");
        setError("");
        onClose();
      }}
      maxWidth="xs"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          border: "1px solid rgba(0,0,0,0.08)",
          boxShadow: "0 20px 60px rgba(0,0,0,0.12)",
          overflow: "hidden",
        },
      }}
    >
      {/* Purple top accent */}
      <Box
        sx={{
          height: 4,
          background: "linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899)",
        }}
      />

      <DialogContent sx={{ p: 3.5, pt: 3 }}>
        <IconButton
          onClick={onClose}
          size="small"
          sx={{
            position: "absolute",
            top: 16,
            right: 16,
            color: "#94a3b8",
            "&:hover": { color: "#1a1a2e" },
          }}
        >
          <Close fontSize="small" />
        </IconButton>

        <Box sx={{ textAlign: "center", mb: 3 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,
              background: "linear-gradient(135deg,#6366f1,#8b5cf6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              mx: "auto",
              mb: 1.5,
              boxShadow: "0 4px 12px rgba(99,102,241,0.3)",
            }}
          >
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#fff"
              strokeWidth="2"
              strokeLinecap="round"
            >
              <rect x="3" y="3" width="18" height="18" rx="4" />
              <circle cx="8.5" cy="8.5" r="1.5" fill="#fff" />
              <path d="M21 15l-5-5-4 4-2-2-4 4" />
            </svg>
          </Box>
          <Typography
            sx={{
              fontFamily: "'Syne',sans-serif",
              fontWeight: 800,
              fontSize: 18,
              color: "#1a1a2e",
            }}
          >
            GenImageDetector
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {tab === 0 ? "Sign in to your account" : "Create a new account"}
          </Typography>
        </Box>

        <Tabs
          value={tab}
          onChange={(_, v) => setTab(v)}
          centered
          sx={{
            mb: 3,
            "& .MuiTabs-indicator": {
              background: "linear-gradient(135deg,#6366f1,#8b5cf6)",
              height: 2,
            },
          }}
        >
          <Tab label="Login" sx={{ fontWeight: 600, textTransform: "none" }} />
          <Tab
            label="Sign Up"
            sx={{ fontWeight: 600, textTransform: "none" }}
          />
        </Tabs>

        <Box component="form" onSubmit={handleSubmit}>
          {error && (
            <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            label="Username"
            fullWidth
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            margin="normal"
            autoFocus
            size="small"
            sx={{ mb: 1 }}
          />
          <TextField
            label="Password"
            type="password"
            fullWidth
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            margin="normal"
            size="small"
            sx={{ mb: 3 }}
          />
          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={loading}
            size="large"
            sx={{ py: 1.25, borderRadius: 2 }}
          >
            {loading
              ? "Processing..."
              : tab === 0
                ? "Sign In"
                : "Create Account"}
          </Button>
        </Box>
      </DialogContent>
    </Dialog>
  );
};
