import './WelcomeContent.css';

export function WelcomeContent() {
  return (
    <div className="welcome-content">
      <h1>Experience Ethan: AI Voice Assistant Demo</h1>

      <div className="features-section">
        <div className="feature-item">
          <h3>🎯 Quick Start</h3>
          <p>Click <strong>"Connect"</strong> to start talking with Ethan, our AI voice assistant. Speak naturally as you would with a person.</p>
        </div>

        <div className="feature-item">
          <h3>💡 Key Features</h3>
          <ul>
            <li>Natural conversations with human-like responses</li>
            <li>Personalized solutions for your needs</li>
            <li>Active listening and empathetic engagement</li>
          </ul>
        </div>
      </div>

      <div className="note-section">
        <p><strong>Note:</strong> Due to CPU resource limitations (only 0.1 CPU), you will experience a slight delay in Ethan's responses. For a better demo experience, please contact me via <a href="https://www.linkedin.com/in/thinh-dang/" target="_blank" rel="noopener noreferrer">LinkedIn</a> - I'll be happy to support you!</p>
      </div>
    </div>
  );
}
