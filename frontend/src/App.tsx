import {
  C1Chat,
  ThemeProvider,
  type ConversationStartersConfig,
  type WelcomeMessageConfig,
} from "@thesysai/genui-sdk";
import "@crayonai/react-ui/styles/index.css";
import "./App.css";

const apiURL = import.meta.env.VITE_API_URL ?? "/api/chat";

const welcomeMessage: WelcomeMessageConfig = {
  title:
    "Hi, I'm Glen, your AI stock analysis assistant! How can I help with stocks today?",
  description:
    'Ready to fetch prices, history, news, or fundamentals. Try: "Show AAPL price" or "MSFT news today".',
};

const conversationStarters: ConversationStartersConfig = {
  variant: "long",
  options: [
    {
      displayText: "Show me the price of AAPL",
      prompt: "Show me the price of AAPL",
    },
    {
      displayText: "Show me the news for MSFT",
      prompt: "Show me the news for MSFT",
    },
  ],
};

function App() {
  return (
    <div className="app-container">
      <ThemeProvider mode="dark">
        <C1Chat
          apiUrl={apiURL}
          agentName="GLEN"
          welcomeMessage={welcomeMessage}
          conversationStarters={conversationStarters}
        />
      </ThemeProvider>
    </div>
  );
}

export default App;
