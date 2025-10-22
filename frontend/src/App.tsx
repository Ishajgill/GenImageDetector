import "./App.css";
import { Analyzer } from "./components/analyzer/Analyzer";
import { Sidebar } from "./components/sidebar/Sidebar";
import { AppProvider } from "./AppProvider";

export const App = () => {
  return (
    <AppProvider>
      <div
        style={{
          display: "flex",
          height: "100%",
        }}
      >
        <Sidebar />
        <Analyzer />
      </div>
    </AppProvider>
  );
};

export default App;
