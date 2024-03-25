import { BrowserRouter as Router, Route, Link, Routes } from 'react-router-dom';
import About from './About';
import Layout from './Layout';
import './App.css';

function App() {
  return (
    <Router>
      <Layout>
      <Routes>
          <Route path="/about" element={<About />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;