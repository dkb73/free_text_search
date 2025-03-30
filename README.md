# Hostel Search Application

A modern web application for searching hostels using semantic search powered by Google's Gemini AI and FAISS.

## Project Structure

```
.
├── frontend/          # Next.js frontend application
├── backend/          # Python Flask backend API
└── README.md
```

## Prerequisites

- Node.js (v18 or later)
- Python (v3.8 or later)
- MongoDB
- Google Gemini API key

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with your configuration:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   MONGODB_URI=mongodb://localhost:27017/
   ```

5. Start the backend server:
   ```bash
   python app.py
   ```

The backend server will run on `http://localhost:5000`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend application will run on `http://localhost:3000`.

## Features

- Semantic search for hostels using Google's Gemini AI
- Real-time search results with beautiful UI
- Detailed hostel information display
- Responsive design for all devices
- Contact functionality for hostels

## Technologies Used

- Frontend:
  - Next.js
  - TypeScript
  - Tailwind CSS
  - React

- Backend:
  - Python
  - Flask
  - MongoDB
  - FAISS
  - Google Gemini AI

## Deployment

### Backend Deployment

1. Set up a Python hosting service (e.g., Heroku, DigitalOcean, AWS)
2. Configure environment variables
3. Deploy the Flask application

### Frontend Deployment

1. Build the Next.js application:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy to a hosting service (e.g., Vercel, Netlify, AWS)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 