import { Box, Typography, Button } from "@mui/material";
import { ArrowBack } from "@mui/icons-material";

interface HowItWorksProps {
  onBack: () => void;
}

export const HowItWorks = ({ onBack }: HowItWorksProps) => {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');
        @keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
        @keyframes float1{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
      `}</style>

      <Box
        sx={{
          width: "100%",
          maxWidth: 780,
          mx: "auto",
          px: { xs: 2, md: 4 },
          py: 5,
          display: "flex",
          flexDirection: "column",
          gap: 5,
          animation: "fadeUp .5s ease forwards",
        }}
      >
        {/* Back button */}
        <Box>
          <Button
            startIcon={<ArrowBack />}
            onClick={onBack}
            sx={{
              color: "#6366f1",
              fontWeight: 600,
              "&:hover": { bgcolor: "rgba(99,102,241,0.06)" },
            }}
          >
            Back to detector
          </Button>
        </Box>

        {/* Header */}
        <Box sx={{ textAlign: "center" }}>
          <Box
            sx={{
              display: "inline-flex",
              alignItems: "center",
              gap: 1,
              bgcolor: "rgba(99,102,241,0.06)",
              border: "1px solid rgba(99,102,241,0.15)",
              borderRadius: 20,
              px: 2,
              py: 0.75,
              mb: 3,
            }}
          >
            <Box
              sx={{
                width: 7,
                height: 7,
                borderRadius: "50%",
                bgcolor: "#6366f1",
              }}
            />
            <Typography
              sx={{
                fontSize: 11,
                fontWeight: 700,
                color: "#6366f1",
                letterSpacing: ".06em",
              }}
            >
              UNDER THE HOOD
            </Typography>
          </Box>
          <Typography
            sx={{
              fontFamily: "'Syne',sans-serif",
              fontSize: { xs: "2rem", md: "2.8rem" },
              fontWeight: 800,
              color: "text.primary",
              lineHeight: 1.1,
              letterSpacing: "-.03em",
              mb: 2,
            }}
          >
            How we detect
            <br />
            <Box
              component="span"
              sx={{
                background: "linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              AI-generated images
            </Box>
          </Typography>
          <Typography
            sx={{
              fontSize: 16,
              color: "text.secondary",
              lineHeight: 1.7,
              maxWidth: 520,
              mx: "auto",
            }}
          >
            AI image generators aren't perfect — they leave behind subtle traces
            that our models are trained to find.
          </Typography>
        </Box>

        {/* Main explanation cards */}
        <Box sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
          {/* Card 1 */}
          <Box
            sx={{
              bgcolor: "background.paper",
              borderRadius: 3,
              p: { xs: 3, md: 4 },
              boxShadow: (t) =>
                t.palette.mode === "dark"
                  ? "0 4px 20px rgba(0,0,0,0.5)"
                  : "0 4px 20px rgba(0,0,0,0.06)",
              border: 1,
              borderColor: "divider",
              display: "flex",
              gap: 3,
              alignItems: "flex-start",
              flexWrap: "wrap",
            }}
          >
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: 2,
                bgcolor: "rgba(99,102,241,0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 26,
                flexShrink: 0,
              }}
            >
              🔍
            </Box>
            <Box sx={{ flex: 1, minWidth: 240 }}>
              <Typography
                sx={{
                  fontFamily: "'Syne',sans-serif",
                  fontWeight: 800,
                  fontSize: 18,
                  color: "text.primary",
                  mb: 1,
                }}
              >
                AI generators leave fingerprints
              </Typography>
              <Typography
                sx={{ fontSize: 14, color: "text.secondary", lineHeight: 1.8 }}
              >
                Every AI image generator — whether it's Midjourney, DALL-E,
                Stable Diffusion, or others — introduces subtle patterns into
                the pixels it creates. These patterns are invisible to the human
                eye but detectable by neural networks trained specifically to
                look for them. Think of it like a printer leaving microscopic
                dots that identify which machine printed a page.
              </Typography>
            </Box>
          </Box>

          {/* Card 2 */}
          <Box
            sx={{
              bgcolor: "background.paper",
              borderRadius: 3,
              p: { xs: 3, md: 4 },
              boxShadow: (t) =>
                t.palette.mode === "dark"
                  ? "0 4px 20px rgba(0,0,0,0.5)"
                  : "0 4px 20px rgba(0,0,0,0.06)",
              border: 1,
              borderColor: "divider",
              display: "flex",
              gap: 3,
              alignItems: "flex-start",
              flexWrap: "wrap",
            }}
          >
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: 2,
                bgcolor: "rgba(236,72,153,0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 26,
                flexShrink: 0,
              }}
            >
              🧠
            </Box>
            <Box sx={{ flex: 1, minWidth: 240 }}>
              <Typography
                sx={{
                  fontFamily: "'Syne',sans-serif",
                  fontWeight: 800,
                  fontSize: 18,
                  color: "text.primary",
                  mb: 1,
                }}
              >
                Our ensemble of detection models
              </Typography>
              <Typography
                sx={{ fontSize: 14, color: "text.secondary", lineHeight: 1.8 }}
              >
                We currently run your image through{" "}
                <Box component="strong" sx={{ color: "text.primary" }}>
                  {" "}
                  Different deep learning classifiers
                </Box>{" "}
                — CNNSpot, Effort, NYUAD, and Nebula. Each model was trained on
                different datasets and looks for different artifacts. By
                combining their votes into a weighted aggregate, we get a more
                reliable result than any single model alone.
              </Typography>
            </Box>
          </Box>

          {/* Card 3 */}
          <Box
            sx={{
              bgcolor: "background.paper",
              borderRadius: 3,
              p: { xs: 3, md: 4 },
              boxShadow: (t) =>
                t.palette.mode === "dark"
                  ? "0 4px 20px rgba(0,0,0,0.5)"
                  : "0 4px 20px rgba(0,0,0,0.06)",
              border: 1,
              borderColor: "divider",
              display: "flex",
              gap: 3,
              alignItems: "flex-start",
              flexWrap: "wrap",
            }}
          >
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: 2,
                bgcolor: "rgba(34,211,238,0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 26,
                flexShrink: 0,
              }}
            >
              📊
            </Box>
            <Box sx={{ flex: 1, minWidth: 240 }}>
              <Typography
                sx={{
                  fontFamily: "'Syne',sans-serif",
                  fontWeight: 800,
                  fontSize: 18,
                  color: "text.primary",
                  mb: 1,
                }}
              >
                What the confidence score means
              </Typography>
              <Typography
                sx={{ fontSize: 14, color: "text.secondary", lineHeight: 1.8 }}
              >
                Each model outputs a score from 0–100% representing how
                confident it is that the image is{" "}
                <strong style={{ color: "#16a34a" }}>real</strong>. A score
                above the model's threshold means it believes the image is
                authentic. The final aggregate weighs models that are more
                "certain" (further from 50%) more heavily, giving you a reliable
                combined verdict.
              </Typography>
            </Box>
          </Box>

          {/* Card 4 */}
          <Box
            sx={{
              bgcolor: "background.paper",
              borderRadius: 3,
              p: { xs: 3, md: 4 },
              boxShadow: (t) =>
                t.palette.mode === "dark"
                  ? "0 4px 20px rgba(0,0,0,0.5)"
                  : "0 4px 20px rgba(0,0,0,0.06)",
              border: 1,
              borderColor: "divider",
              display: "flex",
              gap: 3,
              alignItems: "flex-start",
              flexWrap: "wrap",
            }}
          >
            <Box
              sx={{
                width: 52,
                height: 52,
                borderRadius: 2,
                bgcolor: "rgba(251,191,36,0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 26,
                flexShrink: 0,
              }}
            >
              ⚠️
            </Box>
            <Box sx={{ flex: 1, minWidth: 240 }}>
              <Typography
                sx={{
                  fontFamily: "'Syne',sans-serif",
                  fontWeight: 800,
                  fontSize: 18,
                  color: "text.primary",
                  mb: 1,
                }}
              >
                Why it's not always perfect
              </Typography>
              <Typography
                sx={{ fontSize: 14, color: "text.secondary", lineHeight: 1.8 }}
              >
                Detection is an arms race. As generators improve, their
                fingerprints become harder to detect. Heavily edited,
                compressed, or screenshotted AI images may fool our models.
                That's why we show you each model's individual score — so you
                can judge the confidence yourself rather than blindly trusting a
                single verdict.
              </Typography>
            </Box>
          </Box>
        </Box>
        {/* CTA */}
        <Box sx={{ textAlign: "center", pb: 2 }}>
          <Button
            variant="contained"
            size="large"
            onClick={onBack}
            sx={{
              px: 5,
              py: 1.5,
              fontSize: 15,
              fontWeight: 700,
              borderRadius: 2,
              background: "linear-gradient(135deg,#6366f1,#8b5cf6)",
            }}
          >
            Try it yourself →
          </Button>
        </Box>
      </Box>
    </>
  );
};
