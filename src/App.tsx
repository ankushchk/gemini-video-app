import { useState } from 'react';
import ContentFactory from './ContentFactory';
import LandingPage from './LandingPage';

function App() {
  const [showLanding, setShowLanding] = useState(true);

  if (showLanding) {
    return <LandingPage onStart={() => setShowLanding(false)} />;
  }

  return <ContentFactory />;
}

export default App;