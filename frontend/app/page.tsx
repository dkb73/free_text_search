'use client';

import { useState } from 'react';
import SearchBar from '@/components/SearchBar';
import HostelCard from '@/components/HostelCard';

interface Hostel {
  id: string;
  name: string;
  location: string;
  description: string;
  facilities: string[];
  room_types: string[];
  monthly_rent: string;
  ratings: string;
  contact: string;
}

export default function Home() {
  const [searchResults, setSearchResults] = useState<Hostel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiUrl}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.error || 'Search failed');
      }

      const data = await response.json();
      setSearchResults(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Search error:', err);
      setError(
        err instanceof Error
          ? err.message
          : err instanceof DOMException && err.name === 'AbortError'
          ? 'Request timed out. Please try again.'
          : 'Failed to search hostels. Please try again.'
      );
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-blue-800">Hostel Search</h1>
          <p className="text-gray-600 mt-2">Find your perfect hostel accommodation</p>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <SearchBar onSearch={handleSearch} />
        
        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-800 mx-auto"></div>
          </div>
        )}

        {error && (
          <div className="text-center py-8 text-red-600">
            {error}
          </div>
        )}

        {!loading && !error && searchResults.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {searchResults.map((hostel) => (
              <HostelCard key={hostel.id} hostel={hostel} />
            ))}
          </div>
        )}

        {!loading && !error && searchResults.length === 0 && (
          <div className="text-center py-8 text-gray-600">
            No hostels found. Try a different search query.
          </div>
        )}
      </div>
    </main>
  );
}
