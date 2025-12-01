import { useContext, useEffect, useState } from "react";
import { AppContext, type AppContextType } from "../../AppContext";
import { confidenceToString } from "../../utils";

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
        results: results,
        analysis: analysis,
      });
      setHistory([
        ...history,
        {
          image: preview,
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
    <div
      style={{
        margin: "0 auto",
        padding: "20vh 2rem",
        width: "100%",
        textAlign: "center",
      }}
    >
      <h1
        style={{
          fontWeight: 300,
          fontSize: "2rem",
          marginBottom: "1.5rem",
        }}
      >
        GenImageDetector
      </h1>

      <div
        className="card"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "1rem",
        }}
      >
        <input
          type="file"
          accept="image/png, image/jpeg"
          onChange={(e) => {
            if (e.target.files) {
              setImage(e.target.files[0]);
            }
          }}
        />

        {preview && (
          <img
            src={preview}
            alt="Preview"
            style={{
              height: "150px",
              objectFit: "cover",
            }}
          />
        )}
      </div>

      {image && <button onClick={analyzeImage}>Analyze</button>}

      <div style={{ marginTop: "1rem" }}>
        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <div className="spinner" />
            <span>Analyzing image...</span>
          </div>
        )}

        {currentResult && (
          <div style={{ marginTop: "1rem" }}>
            <h2>Results</h2>

            <table
              style={{
                borderCollapse: "collapse",
                width: "100%",
                maxWidth: "648px",
              }}
            >
              <thead>
                <tr>
                  <th
                    style={{
                      padding: "8px 12px",
                      borderBottom: "1px solid #ccc",
                      textAlign: "left",
                    }}
                  >
                    Model
                  </th>
                  <th
                    style={{
                      padding: "8px 12px",
                      borderBottom: "1px solid #ccc",
                    }}
                  >
                    Real Confidence
                  </th>
                  <th
                    style={{
                      padding: "8px 12px",
                      borderBottom: "1px solid #ccc",
                    }}
                  >
                    Verdict
                  </th>
                </tr>
              </thead>

              <tbody>
                {currentResult.results.map((result, idx) => (
                  <tr key={idx}>
                    <td style={{ padding: "8px 12px", textAlign: "left" }}>
                      <code>{result.model}</code>
                    </td>
                    <td style={{ padding: "8px 12px", textAlign: "center" }}>
                      {result.confidence}%
                    </td>
                    <td
                      style={{
                        padding: "8px 12px",
                        textAlign: "center",
                        color: confidenceToString(
                          result.confidence,
                          "var(--success-text, green)",
                          "var(--error-text, red)",
                          undefined,
                          result.model
                        ),
                      }}
                    >
                      {confidenceToString(
                        result.confidence,
                        undefined,
                        undefined,
                        undefined,
                        result.model
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>

              {currentResult.analysis && (
                <tfoot style={{ borderTop: "1px solid #ccc" }}>
                  <tr>
                    <td style={{ padding: "8px 12px", textAlign: "left" }}>
                      Final Analysis
                    </td>
                    <td style={{ padding: "8px 12px", textAlign: "center" }}>
                      {currentResult.analysis.confidence}%
                    </td>
                    <td
                      style={{
                        padding: "8px 12px",
                        textAlign: "center",
                        color: confidenceToString(
                          currentResult.analysis.confidence,
                          "var(--success-text, green)",
                          "var(--error-text, red)",
                          undefined,
                          currentResult.analysis.model
                        ),
                      }}
                    >
                      {confidenceToString(
                        currentResult.analysis.confidence,
                        "Likely Real",
                        "Likely AI-generated",
                        undefined,
                        currentResult.analysis.model
                      )}
                    </td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        )}
      </div>

      <style>{`
        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #ccc;
          border-top-color: #333;
          border-radius: 50%;
          animation: spin 0.6s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
