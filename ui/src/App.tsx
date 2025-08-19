import { useEffect, useState } from "react";
import "./App.css";

interface Result {
  model: string;
  confidence: number;
  verdict: string;
}

function App() {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Result[] | null>(null);

  useEffect(() => {
    if (!image) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result === "string") {
        setPreview(reader.result);
      }
    };
    reader.readAsDataURL(image);
  }, [image]);

  const analyzeImage = () => {
    if (!image) return;

    setLoading(true);
    setResults(null);

    // Simulate backend processing
    setTimeout(() => {
      setLoading(false);

      setResults([
        { model: "Swin Transformer V2", confidence: 78, verdict: "Likely AI" },
        { model: "EfficientNet-B7", confidence: 65, verdict: "Uncertain" },
        { model: "CLIP ViT-L/14", confidence: 84, verdict: "Likely AI" },
      ]);
    }, 2000);
  };

  return (
    <>
      <h1>GenImageDetector</h1>
      <div
        className="card"
        style={{
          display: "flex",
          alignItems: "center",
          gap: "1rem", // space between items
        }}
      >
        <input
          type="file"
          accept="image/*"
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

      <button onClick={analyzeImage}>Analyze</button>

      <div style={{ marginTop: "1rem" }}>
        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <div className="spinner" />
            <span>Analyzing image...</span>
          </div>
        )}

        {results && (
          <div style={{ marginTop: "1rem" }}>
            <h3>Analysis Results</h3>
            <table
              style={{
                borderCollapse: "collapse",
                width: "100%",
                maxWidth: "500px",
              }}
            >
              <thead>
                <tr>
                  <th
                    style={{
                      borderBottom: "1px solid #ccc",
                      textAlign: "left",
                    }}
                  >
                    Model
                  </th>
                  <th style={{ borderBottom: "1px solid #ccc" }}>Confidence</th>
                  <th style={{ borderBottom: "1px solid #ccc" }}>Verdict</th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, idx) => (
                  <tr key={idx}>
                    <td style={{ padding: "4px 8px" }}>{r.model}</td>
                    <td style={{ padding: "4px 8px", textAlign: "center" }}>
                      {r.confidence}%
                    </td>
                    <td
                      style={{
                        padding: "4px 8px",
                        textAlign: "center",
                        color:
                          r.verdict === "Likely AI"
                            ? "var(--error-text, red)"
                            : r.verdict === "Likely Human"
                            ? "var(--success-text, green)"
                            : "var(--warning-text, yellow)",
                      }}
                    >
                      {r.verdict}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop: "0.5rem", fontWeight: "bold" }}>
              Final conclusion:{" "}
              {Math.round(
                results.reduce((sum, r) => sum + r.confidence, 0) /
                  results.length
              ) > 70
                ? "Image is likely AI-generated"
                : "Image origin is uncertain"}
            </div>
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
    </>
  );
}

export default App;
