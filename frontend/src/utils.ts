const REAL_CONFIDENCE_THRESHOLD = 55;

// Model-specific thresholds based on validation testing
const MODEL_THRESHOLDS: Record<string, number> = {
  CNNSpot: 80, // Real images typically score 90-100%, fake images 0-50%
  "gid-final": 50, // Final result (same as CNNSpot for now)
};

export const confidenceToString = (
  confidence: number,
  highString = "Likely Real",
  lowString = "Likely AI-generated",
  threshold = REAL_CONFIDENCE_THRESHOLD,
  modelName?: string
) => {
  // Use model-specific threshold if provided
  const effectiveThreshold = modelName
    ? MODEL_THRESHOLDS[modelName] ?? threshold
    : threshold;
  return confidence > effectiveThreshold ? highString : lowString;
};
