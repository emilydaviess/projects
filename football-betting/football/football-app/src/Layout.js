import { Link } from 'react-router-dom';

function Layout({ children }) {
  return (
    <div className="flex min-h-screen bg-gray-100">
      <nav className="p-5 bg-blue-500 text-white w-64">
        <ul className="space-y-4">
          <li><Link to="/" className="block hover:text-gray-300">Home</Link></li>
          <li><Link to="/about" className="block hover:text-gray-300">About</Link></li>
          {/* Add more navigation links as needed */}
        </ul>
      </nav>

      <main className="flex-grow p-5">
        {children}
      </main>
    </div>
  );
}

export default Layout;