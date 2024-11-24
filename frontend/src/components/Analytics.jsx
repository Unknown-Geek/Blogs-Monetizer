import { useState, useEffect } from 'react';
import { API_URL } from '../config';

export default function Analytics() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/analytics`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(console.error);
  }, []);

  if (!stats) return null;

  return (
    <div className="mt-8 bg-white p-6 rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Analytics</h2>
      {/* Add your analytics display here */}
    </div>
  );
}