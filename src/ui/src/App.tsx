import { RTVIClientAudio } from "@pipecat-ai/client-react";
import { RTVIProvider } from "./providers/RTVIProvider";
import { ConnectButton } from "./components/ConnectButton";
import { StatusDisplay } from "./components/StatusDisplay";
import { DebugDisplay } from "./components/DebugDisplay";
import { WelcomeContent } from "./components/WelcomeContent";
import "./App.css";

// function BotVideo() {
//   const transportState = useRTVIClientTransportState();
//   const isConnected = transportState !== 'disconnected';

//   return (
//     <div className="bot-container">
//       <div className="video-container">
//         {isConnected && <RTVIClientVideo participant="bot" fit="cover" />}
//       </div>
//     </div>
//   );
// }

function AppContent() {
  return (
    <div className="app">
      <div className="status-bar">
        <StatusDisplay />
        <ConnectButton />
      </div>

      <WelcomeContent />
      {/* <div className="main-content">
        <BotVideo />
      </div> */}

      <DebugDisplay />
      <RTVIClientAudio />
      
      <footer className="app-footer">
        <p className="version-info">
          Version: {import.meta.env.VITE_GIT_VERSION || 'development'}
        </p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <RTVIProvider>
      <AppContent />
    </RTVIProvider>
  );
}

export default App;
