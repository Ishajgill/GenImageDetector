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
import { AppContext, type AppContextType } from "../../AppContext";
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
          <ListItem key={item.image} disablePadding>
            <ListItemButton
              onClick={() => {
                console.log("clicked");
                setCurrentResult(item);
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
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="caption" color="text.secondary" noWrap>
                  Image {history.length - idx}
                </Typography>
                <Typography
                  variant="body2"
                  fontWeight="medium"
                  sx={{
                    color:
                      confidenceToString(
                        item.analysis.confidence,
                        "success.main",
                        "error.main",
                        24
                      ) || "text.primary",
                  }}
                >
                  {confidenceToString(
                    item.analysis.confidence,
                    "Real",
                    "Fake",
                    24
                  )}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {item.analysis.confidence}%
                </Typography>
              </Box>
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};
