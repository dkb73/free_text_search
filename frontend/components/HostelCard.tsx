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

interface HostelCardProps {
  hostel: Hostel;
}

export default function HostelCard({ hostel }: HostelCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="p-6">
        <h2 className="text-xl font-semibold text-blue-800 mb-2">{hostel.name}</h2>
        
        <div className="flex items-center text-gray-600 mb-3">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span>{hostel.location}</span>
        </div>

        <p className="text-gray-600 mb-4 line-clamp-3">{hostel.description}</p>

        <div className="mb-4">
          <h3 className="font-semibold mb-2">Facilities:</h3>
          <div className="flex flex-wrap gap-2">
            {hostel.facilities.map((facility, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
              >
                {facility}
              </span>
            ))}
          </div>
        </div>

        <div className="mb-4">
          <h3 className="font-semibold mb-2">Room Types:</h3>
          <ul className="list-disc list-inside text-gray-600">
            {hostel.room_types.map((type, index) => (
              <li key={index}>{type}</li>
            ))}
          </ul>
        </div>

        <div className="flex justify-between items-center">
          <div className="text-lg font-semibold text-blue-800">
            {hostel.monthly_rent}
          </div>
          <div className="flex items-center text-yellow-500">
            <svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.363 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.363-1.118l-2.8-2.034c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span>{hostel.ratings}</span>
          </div>
        </div>

        <div className="mt-4">
          <a
            href={`tel:${hostel.contact}`}
            className="block w-full text-center px-4 py-2 bg-blue-800 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Contact Now
          </a>
        </div>
      </div>
    </div>
  );
} 