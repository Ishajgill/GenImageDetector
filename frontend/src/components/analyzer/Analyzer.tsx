import { useContext, useEffect, useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Paper,
  styled,
  LinearProgress,
  Chip,
  Skeleton,
} from "@mui/material";
import { CheckCircle, Warning } from "@mui/icons-material";
import { AppContext, type AppContextType } from "../../contexts/AppContext";
import { AuthContext } from "../../contexts/AuthContext";
import { confidenceToString } from "../../utils";

const VisuallyHiddenInput = styled("input")(() => ({
  clip: "rect(0 0 0 0)",
  clipPath: "inset(50%)",
  height: 1,
  overflow: "hidden",
  position: "absolute",
  bottom: 0,
  left: 0,
  whiteSpace: "nowrap",
  width: 1,
}));

// Confidence bar component
const ConfidenceBar = ({ confidence }: { confidence: number }) => {
  const isReal = confidence >= 50;

  return (
    <Box sx={{ width: "100%", maxWidth: 200, mx: "auto" }}>
      <LinearProgress
        variant="determinate"
        value={confidence}
        sx={{
          height: 8,
          borderRadius: 4,
          bgcolor: "action.hover",
          "& .MuiLinearProgress-bar": {
            bgcolor: isReal ? "success.main" : "error.main",
            transition: "transform 1s ease-in-out",
          },
        }}
      />
    </Box>
  );
};

// Animated gauge for final verdict
const ConfidenceGauge = ({ confidence }: { confidence: number }) => {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedValue(confidence);
    }, 100);
    return () => clearTimeout(timer);
  }, [confidence]);

  const isReal = confidence >= 50;
  const rotation = (animatedValue / 100) * 180 - 90; // -90 to 90 degrees

  return (
    <Box
      sx={{
        width: 120,
        height: 60,
        mx: "auto",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <Box
        sx={{
          position: "relative",
          width: 120,
          height: 60,
          mx: "auto",
          mb: 1,
        }}
      >
        {/* Background arc */}
        <Box
          sx={{
            position: "absolute",
            width: "100%",
            height: "100%",
            borderRadius: "120px 120px 0 0",
            border: "8px solid",
            borderColor: "action.hover",
            borderBottom: "none",
          }}
        />
        {/* Colored arc */}
        <Box
          sx={{
            position: "absolute",
            width: "100%",
            height: "100%",
            borderRadius: "120px 120px 0 0",
            border: "8px solid",
            borderColor: isReal ? "success.main" : "error.main",
            borderBottom: "none",
            clipPath: `polygon(0 100%, 50% 100%, 50% 0, ${
              animatedValue < 50 ? "0" : "100%"
            } 0, ${animatedValue < 50 ? "0" : "100%"} 100%)`,
            transform: `rotate(${Math.min(rotation, 0)}deg)`,
            transformOrigin: "bottom center",
            transition: "transform 1.5s cubic-bezier(0.4, 0, 0.2, 1)",
          }}
        />
        {/* Percentage text */}
        <Typography
          variant="h6"
          fontWeight="bold"
          sx={{
            position: "absolute",
            bottom: -5,
            left: "50%",
            transform: "translateX(-50%)",
          }}
        >
          {Math.round(animatedValue)}%
        </Typography>
      </Box>
    </Box>
  );
};

export const Analyzer = () => {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState("");
  const [loadingProgress, setLoadingProgress] = useState(0);

  const context = useContext(AppContext);
  const {
    currentResult,
    setCurrentResult,
    history,
    setHistory,
    refreshHistory,
  } = context as AppContextType;

  const authContext = useContext(AuthContext);
  const token = authContext?.token;

  // Reset image and preview on logout
  useEffect(() => {
    const handleLogout = () => {
      console.log("Analyzer: auth:logout event received, clearing image state");
      setImage(null);
      setPreview(undefined);
    };

    window.addEventListener("auth:logout", handleLogout);
    return () => window.removeEventListener("auth:logout", handleLogout);
  }, []);

  useEffect(() => {
    if (!image) return;

    // reset current result
    setCurrentResult(null);

    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result === "string") {
        setPreview(reader.result);
      }
    };
    reader.readAsDataURL(image);
  }, [image, setCurrentResult]);

  useEffect(() => {
    setPreview(currentResult?.image);
  }, [currentResult]);

  const analyzeImage = async () => {
    if (!image) return;

    setLoading(true);
    setLoadingProgress(0);
    setCurrentResult(null);

    const formData = new FormData();
    formData.append("file", image);

    // Helper to add random delay
    const randomDelay = (min: number, max: number) =>
      new Promise((resolve) =>
        setTimeout(resolve, Math.random() * (max - min) + min)
      );

    try {
      setLoadingStage("Uploading image...");
      setLoadingProgress(20);
      await randomDelay(400, 800);

      const headers: HeadersInit = {};
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      setLoadingStage("Running AI detection models...");
      setLoadingProgress(40);
      await randomDelay(300, 600);

      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers,
        body: formData,
      });

      setLoadingStage("Processing results...");
      setLoadingProgress(80);
      await randomDelay(500, 900);

      const data = await res.json();

      // Dynamically convert API response to results array
      const results = Object.entries(data).map(([model, confidence]) => ({
        model,
        confidence: confidence as number,
      }));

      // Calculate aggregate analysis (weighted average, favoring higher confidence)
      const confidences = results.map((r) => r.confidence);
      const weights = confidences.map((c) => Math.abs(c - 50)); // Weight by distance from 50%
      const totalWeight = weights.reduce((sum, w) => sum + w, 0);
      const weightedSum = confidences.reduce(
        (sum, c, i) => sum + c * weights[i],
        0
      );
      const aggregateConfidence =
        totalWeight > 0 ? weightedSum / totalWeight : 50;

      const analysis = {
        model: "Aggregate",
        confidence: Math.round(aggregateConfidence * 10) / 10, // Round to 1 decimal
      };

      const newHistoryItem = {
        image: preview,
        filename: image.name,
        results: results,
        analysis: analysis,
      };

      setLoadingStage("Complete!");
      setLoadingProgress(100);

      // Small delay before showing results to smooth the transition
      await randomDelay(300, 500);

      // Set currentResult FIRST, then clear loading to prevent container disappearing
      setCurrentResult(newHistoryItem);

      // Clear loading state immediately after
      setLoading(false);
      setLoadingStage("");
      setLoadingProgress(0);

      // Only add to history for anonymous users
      // For logged-in users, the backend saves it and we'll refetch
      if (!token) {
        setHistory([...history, newHistoryItem]);
      } else {
        // Refetch history from backend to get the newly saved item
        await refreshHistory();
      }
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Error analyzing image");
      setLoading(false);
      setLoadingStage("");
      setLoadingProgress(0);
    }
  };

  return (
    <Box
      sx={{
        maxWidth: "800px",
        width: "100%",
        p: 4,
        textAlign: "center",
      }}
    >
      <Typography
        variant="h1"
        sx={{
          fontWeight: 300,
          fontSize: "2.5rem",
          mb: 4,
        }}
      >
        GenImageDetector
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 2,
            flexWrap: "wrap",
            justifyContent: "center",
            "&:last-child": {
              pb: 2,
            },
          }}
        >
          {!preview ? (
            <Button
              component="label"
              variant="contained"
              sx={{ minWidth: 150 }}
              size="large"
            >
              Choose Image
              <VisuallyHiddenInput
                type="file"
                accept="image/png, image/jpeg"
                onChange={(e) => {
                  if (e.target.files) {
                    setImage(e.target.files[0]);
                  }
                }}
              />
            </Button>
          ) : (
            <Box
              component="img"
              src={preview}
              alt="Preview"
              sx={{
                height: 150,
                maxWidth: "100%",
                objectFit: "contain",
                borderRadius: 2,
              }}
            />
          )}
        </CardContent>
      </Card>

      {image && !currentResult && (
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={analyzeImage}
          disabled={loading}
          sx={{ mb: 3 }}
        >
          {loading ? "Analyzing..." : "Analyze Image"}
        </Button>
      )}

      {loading && (
        <Box sx={{ width: "100%", maxWidth: 600, mx: "auto" }}>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
              mb: 3,
            }}
          >
            <CircularProgress size={40} />
            <Typography variant="body1" fontWeight="medium">
              {loadingStage}
            </Typography>
            <Box sx={{ width: "100%", mt: 1 }}>
              <LinearProgress
                variant="determinate"
                value={loadingProgress}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </Box>
        </Box>
      )}

      {(loading || currentResult) && (
        <Box sx={{ width: "100%", maxWidth: 800, mx: "auto", minHeight: 400 }}>
          {currentResult && (
            <Box sx={{ mb: 3, textAlign: "center" }}>
              <Button
                component="label"
                variant="outlined"
                size="small"
                sx={{ textTransform: "none" }}
              >
                Analyze New Image
                <VisuallyHiddenInput
                  type="file"
                  accept="image/png, image/jpeg"
                  onChange={(e) => {
                    if (e.target.files) {
                      setImage(e.target.files[0]);
                    }
                  }}
                />
              </Button>
            </Box>
          )}

          {loading ? (
            // Skeleton loading for results table
            <Paper sx={{ p: 2 }}>
              {[1, 2, 3, 4].map((i) => (
                <Box key={i} sx={{ mb: 2 }}>
                  <Skeleton
                    variant="rectangular"
                    height={40}
                    sx={{ borderRadius: 1 }}
                  />
                </Box>
              ))}
              <Skeleton
                variant="rectangular"
                height={54}
                sx={{ borderRadius: 1, mt: 2 }}
              />
            </Paper>
          ) : (
            currentResult && (
              <Box>
                <Typography variant="h5" sx={{ mb: 0.5 }}>
                  Results
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  {image?.name}
                </Typography>

                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>
                          <Typography variant="subtitle2" fontWeight="bold">
                            Model
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Typography variant="subtitle2" fontWeight="bold">
                            Real Confidence
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Typography variant="subtitle2" fontWeight="bold">
                            Verdict
                          </Typography>
                        </TableCell>
                      </TableRow>
                    </TableHead>

                    <TableBody>
                      {currentResult.results.map((result, idx) => (
                        <TableRow key={idx} hover>
                          <TableCell>
                            <Typography
                              component="code"
                              sx={{
                                fontFamily: "monospace",
                                fontSize: "0.9rem",
                                bgcolor: "action.hover",
                                px: 1,
                                py: 0.5,
                                borderRadius: 1,
                              }}
                            >
                              {result.model}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 2,
                              }}
                            >
                              <Typography
                                fontWeight="medium"
                                sx={{ minWidth: 45 }}
                              >
                                {result.confidence}%
                              </Typography>
                              <ConfidenceBar confidence={result.confidence} />
                            </Box>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={confidenceToString(
                                result.confidence,
                                undefined,
                                undefined,
                                undefined,
                                result.model
                              )}
                              color={
                                result.confidence >= 50 ? "success" : "error"
                              }
                              variant="outlined"
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}

                      {currentResult.analysis && (
                        <TableRow
                          sx={{
                            bgcolor: "action.hover",
                            "& td": { borderTop: 2, borderColor: "divider" },
                          }}
                        >
                          <TableCell>
                            <Typography fontWeight="bold">
                              Final Analysis
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ py: 1 }}>
                              <ConfidenceGauge
                                confidence={currentResult.analysis.confidence}
                              />
                            </Box>
                          </TableCell>
                          <TableCell align="center" sx={{ width: 180 }}>
                            <Chip
                              icon={
                                currentResult.analysis.confidence >= 50 ? (
                                  <CheckCircle />
                                ) : (
                                  <Warning />
                                )
                              }
                              label={confidenceToString(
                                currentResult.analysis.confidence,
                                "Likely Real",
                                "Likely AI-generated",
                                undefined,
                                currentResult.analysis.model
                              )}
                              color={
                                currentResult.analysis.confidence >= 50
                                  ? "success"
                                  : "error"
                              }
                              size="medium"
                              sx={{ fontWeight: "bold", px: 1 }}
                            />
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )
          )}
        </Box>
      )}
    </Box>
  );
};
