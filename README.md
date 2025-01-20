# Crisis Aid Coordination System

A real-time system for coordinating humanitarian aid delivery between NGOs and crisis areas.

## Architecture

The system consists of three main components:

1. **Frontend**: Next.js application with Material-UI and Leaflet for mapping
2. **Backend**: FastAPI service with SQLAlchemy for database operations
3. **Database**: PostgreSQL for data persistence

### Key Features

- Real-time heatmap visualization of crisis areas
- NGO and crisis area management
- Supply tracking and coordination
- Authentication and authorization
- Automated aid matching algorithm

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd crisis-aid-system
```

2. Start the services:

```bash
docker-compose up --build
```

The services will be available at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development Setup

#### Backend (FastAPI)

```bash
cd logic
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

#### Frontend (Next.js)

```bash
cd sos
npm install
npm run dev
```

## Project Structure

```
.
├── docker-compose.yml
├── logic/                  # Backend service
│   ├── Dockerfile
│   ├── api.py             # FastAPI application
│   ├── database.py        # Database models and connection
│   ├── algorithm.py       # Aid matching algorithm
│   └── validation.py      # Input validation
├── sos/                   # Frontend service
│   ├── Dockerfile
│   ├── components/        # React components
│   ├── lib/              # Shared utilities
│   └── app/              # Next.js pages
└── README.md
```

## Data Flow

1. **Authentication**:

   - Frontend sends credentials to `/api/token`
   - Backend validates and returns JWT token
   - Token is stored in localStorage and used for subsequent requests

2. **Map Interaction**:

   - User moves map or changes filters
   - Frontend requests heatmap data with current bounds
   - Backend calculates intensities and returns points
   - Frontend renders heatmap layer

3. **Aid Matching**:
   - Backend periodically runs matching algorithm
   - NGOs are matched with crisis areas based on:
     - Distance and reach radius
     - Supply availability and needs
     - Urgency levels
     - NGO specializations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
