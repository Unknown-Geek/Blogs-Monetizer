import { useState } from 'react';
import BlogForm from './components/BlogForm';
import Preview from './components/Preview';
import Analytics from './components/Analytics';

function App() {
  const [blogData, setBlogData] = useState(null);
  
  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-800">Blog Generator</h1>
        </div>
      </nav>
      
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <BlogForm onBlogGenerated={setBlogData} />
          <Preview blogData={blogData} />
        </div>
        <Analytics />
      </main>
    </div>
  );
}

export default App;