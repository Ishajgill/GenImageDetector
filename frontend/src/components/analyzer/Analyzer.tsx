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
} from "@mui/material";
import { AppContext, type AppContextType } from "../../AppContext";
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

export const Analyzer = () => {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  const context = useContext(AppContext);
  const { currentResult, setCurrentResult, history, setHistory } =
    context as AppContextType;

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
    setCurrentResult(null);

    const formData = new FormData();
    formData.append("file", image);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

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

      setCurrentResult({
        image: preview,
        filename: image.name,
        results: results,
        analysis: analysis,
      });
      setHistory([
        ...history,
        {
          image: preview,
          filename: image.name,
          results: results,
          analysis: analysis,
        },
      ]);
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Error analyzing image");
    } finally {
      setLoading(false);
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
          }}
        >
          {!preview ? (
            <Button
              component="label"
              variant="contained"
              sx={{ minWidth: 150 }}
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
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 2,
            justifyContent: "center",
            mt: 2,
          }}
        >
          <CircularProgress size={24} />
          <Typography>Analyzing image...</Typography>
        </Box>
      )}

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

      {currentResult && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ mb: 0.5 }}>
            Results
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
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
                    <TableCell align="center">
                      <Typography fontWeight="medium">
                        {result.confidence}%
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Typography
                        sx={{
                          color:
                            confidenceToString(
                              result.confidence,
                              "success.main",
                              "error.main",
                              undefined,
                              result.model
                            ) || "text.primary",
                          fontWeight: "medium",
                        }}
                      >
                        {confidenceToString(
                          result.confidence,
                          undefined,
                          undefined,
                          undefined,
                          result.model
                        )}
                      </Typography>
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
                      <Typography fontWeight="bold">Final Analysis</Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Typography fontWeight="bold">
                        {currentResult.analysis.confidence}%
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Typography
                        sx={{
                          color:
                            confidenceToString(
                              currentResult.analysis.confidence,
                              "success.main",
                              "error.main",
                              undefined,
                              currentResult.analysis.model
                            ) || "text.primary",
                          fontWeight: "bold",
                        }}
                      >
                        {confidenceToString(
                          currentResult.analysis.confidence,
                          "Likely Real",
                          "Likely AI-generated",
                          undefined,
                          currentResult.analysis.model
                        )}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}
    </Box>
  );
};
