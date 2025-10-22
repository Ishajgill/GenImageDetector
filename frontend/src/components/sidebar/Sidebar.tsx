import { useContext } from "react";
import { AppContext, type AppContextType } from "../../AppContext";
import { confidenceToString } from "../../utils";

export const Sidebar = () => {
  const context = useContext(AppContext);

  const { history, setCurrentResult } = context as AppContextType;

  return (
    <div
      style={{
        width: "40rem",
        height: "100%",
      }}
    >
      <ul>
        {history.map((item) => (
          <li
            key={item.image}
            style={{
              listStyle: "none",
              display: "flex",
              gap: "4px",
              marginBottom: "8px",
              cursor: "pointer",
            }}
            onClick={() => {
              console.log("clicked");
              setCurrentResult(item);
            }}
          >
            <img
              src={item.image}
              alt="Preview"
              style={{
                height: "50px",
                objectFit: "cover",
              }}
            />
            <span
              style={{
                color: confidenceToString(
                  item.analysis.confidence,
                  "var(--success-text, green)",
                  "var(--error-text, red)",
                  24
                ),
              }}
            >
              {item.analysis.confidence}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};
