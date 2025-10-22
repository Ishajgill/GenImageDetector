const REAL_CONFIDENCE_THRESHOLD = 55;

export const confidenceToString = (
  confidence: number,
  highString = "Likely Real",
  lowString = "Likely AI-generated",
  threshold = REAL_CONFIDENCE_THRESHOLD
) => (confidence > threshold ? highString : lowString);
