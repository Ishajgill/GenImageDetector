import { useEffect, useState } from "react";
import "./App.css";

const REAL_CONFIDENCE_THRESHOLD = 85;

interface Result {
  model: string;
  confidence: number;
}

const confidenceToString = (
  confidence: number,
  highString = "Likely Real",
  lowString = "Likely AI-generated",
  threshold = REAL_CONFIDENCE_THRESHOLD
) => (confidence > threshold ? highString : lowString);

function App() {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Result[] | null>(null);
  const [analysis, setAnalysis] = useState<Result | null>(null);

  useEffect(() => {
    if (!image) return;

    // reset results & analysis
    setResults(null);
    setAnalysis(null);

    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result === "string") {
        setPreview(reader.result);
      }
    };
    reader.readAsDataURL(image);
  }, [image]);

  const analyzeImage = async () => {
    if (!image) return;

    setLoading(true);
    setResults(null);

    const formData = new FormData();
    formData.append("file", image);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      setResults(data.results);
      setAnalysis(data.analysis);
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Error analyzing image");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h1>GenImageDetector</h1>

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
            <h2>Results</h2>

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
                        color: confidenceToString(
                          r.confidence,
                          "var(--success-text, green)",
                          "var(--error-text, red)"
                        ),
                      }}
                    >
                      {confidenceToString(r.confidence)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {analysis && (
              <h3 style={{ marginTop: "1rem" }}>
                Final Analysis: {confidenceToString(analysis.confidence)} (
                {analysis.confidence}%)
              </h3>
            )}
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
