import { useContext } from "react";
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  Typography,
  Avatar,
  Divider,
} from "@mui/material";
import { AppContext, type AppContextType } from "../../contexts/AppContext";
import { confidenceToString } from "../../utils";

export const Sidebar = () => {
  const context = useContext(AppContext);

  const { history, setCurrentResult } = context as AppContextType;

  // Don't render sidebar if history is empty
  if (history.length === 0) {
    return null;
  }

  return (
    <Box
      sx={{
        width: 280,
        minWidth: 280,
        height: "100vh",
        overflowY: "auto",
        borderRight: 1,
        borderColor: "divider",
        bgcolor: "background.paper",
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" fontWeight="bold">
          History
        </Typography>
      </Box>
      <Divider />
      <List sx={{ p: 0 }}>
        {history.map((item, idx) => (
          <ListItem key={item.id || `${item.timestamp}-${idx}`} disablePadding>
            <ListItemButton
              onClick={() => {
                console.log("clicked");
                setCurrentResult(item);
                // Update URL if item has an ID
                if (item.id) {
                  window.history.pushState({}, "", `/analysis/${item.id}`);
                } else {
                  window.history.pushState({}, "", "/");
                }
              }}
              sx={{
                display: "flex",
                gap: 1.5,
                py: 1.5,
                px: 2,
              }}
            >
              <Avatar
                src={item.image}
                alt="Preview"
                variant="rounded"
                sx={{
                  width: 56,
                  height: 56,
                }}
              />
              <Box
                sx={{
                  flex: 1,
                  minWidth: 0,
                  display: "flex",
                  flexDirection: "column",
                  gap: 0.5,
                }}
              >
                <Typography variant="body2" fontWeight="medium" noWrap>
                  {item.filename || `Image ${history.length - idx}`}
                </Typography>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <Typography
                    variant="body2"
                    sx={{
                      color:
                        confidenceToString(
                          item.analysis.confidence,
                          "success.main",
                          "error.main",
                          undefined,
                          item.analysis.model
                        ) || "text.primary",
                    }}
                  >
                    {confidenceToString(
                      item.analysis.confidence,
                      "Real",
                      "Fake",
                      undefined,
                      item.analysis.model
                    )}
                  </Typography>
                  <Typography variant="body2">
                    {item.analysis.confidence}%
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {(() => {
                    const date = new Date(item.timestamp);
                    const today = new Date();
                    const isToday =
                      date.getDate() === today.getDate() &&
                      date.getMonth() === today.getMonth() &&
                      date.getFullYear() === today.getFullYear();
                    return isToday
                      ? date.toLocaleTimeString()
                      : date.toLocaleString();
                  })()}
                </Typography>
              </Box>
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};
