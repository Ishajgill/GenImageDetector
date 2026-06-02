import { useContext } from "react";
import { Box, List, ListItem, ListItemButton, Typography } from "@mui/material";
import { HistoryOutlined } from "@mui/icons-material";
import { AppContext, type AppContextType } from "../../contexts/AppContext";
import { confidenceToString } from "../../utils";

export const Sidebar = () => {
  const context = useContext(AppContext);
  if (!context) return null;
  const { history, setCurrentResult, currentResult } = context;
  if (history.length === 0) return null;

  const formatTime = (ts: string) => {
    const date = new Date(ts); const today = new Date();
    return date.getDate()===today.getDate()&&date.getMonth()===today.getMonth()&&date.getFullYear()===today.getFullYear()
      ? date.toLocaleTimeString() : date.toLocaleDateString();
  };

  return (
    <Box sx={{ width:260, minWidth:260, height:"100vh", overflowY:"auto", bgcolor:"#fff", borderRight:"1px solid rgba(0,0,0,0.06)", display:"flex", flexDirection:"column", boxShadow:"2px 0 12px rgba(0,0,0,0.04)" }}>
      <Box sx={{ px:2.5, py:2.5, display:"flex", alignItems:"center", gap:1.5, borderBottom:"1px solid rgba(0,0,0,0.06)" }}>
        <Box sx={{ width:30, height:30, borderRadius:1.5, background:"linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.1))", border:"1px solid rgba(99,102,241,0.15)", display:"flex", alignItems:"center", justifyContent:"center" }}>
          <HistoryOutlined sx={{ color:"#6366f1", fontSize:16 }}/>
        </Box>
        <Typography sx={{ fontSize:"11px", fontWeight:700, color:"#94a3b8", letterSpacing:".08em", textTransform:"uppercase" }}>History</Typography>
        <Box sx={{ ml:"auto", bgcolor:"rgba(99,102,241,0.06)", border:"1px solid rgba(99,102,241,0.12)", borderRadius:10, px:1, py:0.25 }}>
          <Typography sx={{ fontSize:"11px", color:"#6366f1", fontWeight:700 }}>{history.length}</Typography>
        </Box>
      </Box>

      <List sx={{ p:1, flex:1 }}>
        {history.map((item, idx) => {
          const isActive = currentResult?.id ? currentResult.id===item.id : currentResult?.timestamp===item.timestamp;
          const isReal = item.analysis.confidence >= 50;
          return (
            <ListItem key={item.id||`${item.timestamp}-${idx}`} disablePadding sx={{ mb:0.5 }}>
              <ListItemButton selected={isActive}
                onClick={()=>{ setCurrentResult(item); window.history.pushState({},"",item.id?`/analysis/${item.id}`:`/`); }}
                sx={{ borderRadius:2, py:1.5, px:1.5, gap:1.5, border:"1px solid transparent", ...(isActive&&{ border:"1px solid rgba(99,102,241,0.2)", bgcolor:"rgba(99,102,241,0.04)!important" }) }}>
                <Box component="img" src={item.image} alt="thumb" sx={{ width:44, height:44, borderRadius:1.5, objectFit:"cover", border:"1px solid rgba(0,0,0,0.06)", flexShrink:0 }}/>
                <Box sx={{ flex:1, minWidth:0 }}>
                  <Typography sx={{ fontSize:"12px", fontWeight:600, color:"#1a1a2e", whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis", mb:0.4 }}>
                    {item.filename || `Image ${history.length-idx}`}
                  </Typography>
                  <Box sx={{ display:"flex", alignItems:"center", gap:0.75, mb:0.3 }}>
                    <Box sx={{ width:5, height:5, borderRadius:"50%", bgcolor:isReal?"#16a34a":"#e11d48", flexShrink:0 }}/>
                    <Typography sx={{ fontSize:"11px", fontWeight:600, color:isReal?"#16a34a":"#e11d48" }}>
                      {confidenceToString(item.analysis.confidence,"Real","AI Generated",undefined,item.analysis.model)}
                    </Typography>
                    <Typography sx={{ fontSize:"10px", color:"#94a3b8" }}>· {item.analysis.confidence}%</Typography>
                  </Box>
                  <Typography sx={{ fontSize:"10px", color:"#94a3b8" }}>{formatTime(item.timestamp)}</Typography>
                </Box>
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );
};
