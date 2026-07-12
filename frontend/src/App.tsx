import { C1Chat, ThemeProvider } from "@thesysai/genui-sdk";
import "@crayonai/react-ui/styles/index.css";
import "./App.css";

const apiURL = import.meta.env.VITE_API_URL ?? "/api/chat";

function App() {
  return (
    <div className="app-container">
      <ThemeProvider mode="dark">
        <C1Chat apiUrl={apiURL} />
      </ThemeProvider>
    </div>
  );
}

export default App;
