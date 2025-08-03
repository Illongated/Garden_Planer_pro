# Agrotique Garden Planner - Intelligent Irrigation Design System

This project is a complete, production-ready intelligent irrigation design system for the Agrotique Garden Planner. It features a modern, full-stack architecture with a FastAPI backend and a React frontend, providing comprehensive irrigation planning, simulation, and visualization capabilities.

## Features

The Intelligent Irrigation Design System provides comprehensive irrigation planning and design capabilities:

### Core Features
- **Hydraulic Calculations**: Advanced flow and pressure calculations using Darcy-Weisbach equations
- **Plant Clustering**: K-means and DBSCAN clustering for optimal zone design
- **Equipment Selection**: Intelligent selection of irrigation equipment based on zone requirements
- **Weather Integration**: Real-time weather data integration for scheduling
- **Cost Estimation**: Detailed cost analysis and ROI calculations
- **System Validation**: Engineering validation of irrigation system designs
- **Pipe Network Optimization**: Optimal pipe sizing and routing
- **Flow Distribution**: Intelligent flow distribution across zones
- **Pressure Management**: Comprehensive pressure analysis and optimization
- **Technical Reports**: Professional technical documentation and reports
- **Professional Export**: PDF technical reports and SVG technical drawings

### Advanced Capabilities
- **Real-time Weather Integration**: Live weather data for irrigation scheduling
- **Scientific Validation**: Industry-standard hydraulic calculations and engineering validation
- **Multi-format Export**: PDF technical reports and SVG technical drawings
- **Interactive Design**: Visual irrigation system design with real-time feedback
- **Cost Optimization**: Budget-aware equipment selection and system design
- **Professional Documentation**: Comprehensive technical reports for installation

## Tech Stack

### Backend
- **Framework**: FastAPI with Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Hydraulic Engine**: Custom implementation with Darcy-Weisbach equations
- **Clustering**: Scikit-learn for plant clustering algorithms
- **Weather Integration**: aiohttp for async weather API calls
- **PDF Generation**: ReportLab for professional technical reports
- **Documentation**: Pydantic for strict type validation

### Frontend
- **Framework**: React with TypeScript
- **UI Components**: Shadcn UI with Tailwind CSS
- **State Management**: React hooks and Zustand
- **Visualization**: SVG-based technical drawings
- **Export**: Client-side file download capabilities
- **Icons**: Lucide React for consistent iconography

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database Migrations**: Alembic for schema management
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Development**: Hot reload for both frontend and backend

## Project Structure

```
.
├── app/
│   ├── api/v1/endpoints/     # FastAPI route handlers
│   ├── crud/                 # Database CRUD operations
│   ├── models/               # SQLAlchemy database models
│   ├── schemas/              # Pydantic validation schemas
│   ├── services/             # Business logic services
│   │   ├── hydraulic_engine.py      # Hydraulic calculations
│   │   ├── clustering_engine.py     # Plant clustering
│   │   ├── weather_service.py       # Weather integration
│   │   ├── irrigation_planner.py    # Main orchestration
│   │   └── technical_export.py      # PDF/SVG export
│   └── core/                 # Configuration and utilities
├── src/
│   ├── features/irrigation/  # React irrigation components
│   ├── components/ui/        # Reusable UI components
│   └── lib/                  # Utility functions
├── alembic/                  # Database migrations
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Docker (optional)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd agrotique-garden-planner
   ```

2. **Backend Setup:**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your database and API settings
   
   # Run database migrations
   alembic upgrade head
   
   # Start the backend server
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup:**
   ```bash
   cd src
   npm install
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Endpoints

### Core Design Endpoints
- `POST /api/v1/irrigation/design-system` - Complete system design
- `POST /api/v1/irrigation/clustering` - Plant clustering
- `POST /api/v1/irrigation/hydraulics` - Hydraulic calculations
- `POST /api/v1/irrigation/equipment-selection` - Equipment optimization
- `POST /api/v1/irrigation/weather-forecast` - Weather-based scheduling
- `POST /api/v1/irrigation/cost-estimation` - Cost analysis

### Export Endpoints
- `POST /api/v1/irrigation/export/pdf` - PDF technical report
- `POST /api/v1/irrigation/export/svg/layout` - System layout SVG
- `POST /api/v1/irrigation/export/svg/pipe-network` - Pipe network SVG
- `POST /api/v1/irrigation/export/technical-plans` - All formats

### CRUD Endpoints
- Full CRUD operations for zones, equipment, schedules, weather data, and projects

## Usage Examples

### Python Service Usage

```python
from app.services.irrigation_planner import IrrigationPlanner
from app.services.technical_export import TechnicalExportService

# Initialize services
planner = IrrigationPlanner()
export_service = TechnicalExportService()

# Design complete system
system_design = planner.design_complete_irrigation_system(
    garden_id="garden-123",
    plants_data=[...],
    water_source_pressure_bar=2.5,
    water_source_flow_lph=1000,
    max_zones=5,
    budget_constraint=3000.0
)

# Generate PDF technical report
pdf_content = export_service.generate_pdf_technical_report(
    garden_id="garden-123",
    system_design=system_design,
    project_name="My Irrigation System"
)

# Generate SVG technical drawing
svg_content = export_service.generate_svg_technical_drawing(
    system_design=system_design,
    width=800,
    height=600
)
```

### React Component Usage

```typescript
import { IrrigationDesigner } from '@/features/irrigation/components/IrrigationDesigner';

function App() {
  return (
    <div className="app">
      <IrrigationDesigner />
    </div>
  );
}
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/agrotique

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=Agrotique Garden Planner

# Weather API (optional)
WEATHER_API_KEY=your_api_key
WEATHER_API_URL=https://api.openweathermap.org/data/2.5

# Export Settings
EXPORT_TEMP_DIR=/tmp/exports
MAX_EXPORT_SIZE_MB=50
```

### Hydraulic Parameters

The system uses industry-standard hydraulic parameters:

- **Water Density**: 998.2 kg/m³
- **Dynamic Viscosity**: 0.001002 Pa·s
- **Gravity**: 9.81 m/s²
- **Pipe Roughness**: PVC (0.0015mm), PE (0.007mm), Copper (0.0015mm)

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_hydraulic_engine.py
pytest tests/test_clustering_engine.py
pytest tests/test_weather_service.py
```

### Frontend Tests
```bash
# Run component tests
npm test

# Run specific test files
npm test IrrigationDesigner.test.tsx
```

## Performance Optimizations

- **Incremental Calculations**: Only recalculate affected components
- **Caching**: Multi-level caching for hydraulic and clustering results
- **Async Processing**: Background tasks for heavy calculations
- **Database Indexing**: Optimized queries for large datasets
- **Frontend Optimization**: React Query for intelligent caching

## Security Considerations

- **Input Validation**: Strict Pydantic validation for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **Rate Limiting**: API rate limiting for export endpoints
- **File Upload Security**: Secure file handling for exports
- **Authentication**: JWT-based authentication (when implemented)

## Monitoring and Logging

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Performance Metrics**: Calculation time tracking
- **Error Tracking**: Comprehensive error logging with context
- **Health Checks**: API health endpoints for monitoring

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env
   - Run `alembic upgrade head`

2. **Hydraulic Calculation Errors**
   - Check input parameters are within valid ranges
   - Verify pipe material properties
   - Review system design constraints

3. **Export Generation Failures**
   - Check available disk space
   - Verify ReportLab installation
   - Review export size limits

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload --log-level debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript strict mode for frontend
- Write comprehensive tests
- Update documentation for new features
- Use conventional commits

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the troubleshooting section above

## Roadmap

### Planned Features
- **3D Visualization**: Interactive 3D pipe network visualization
- **Real-time Collaboration**: Multi-user editing capabilities
- **Advanced Scheduling**: Machine learning-based irrigation scheduling
- **Mobile App**: Native mobile application
- **IoT Integration**: Sensor data integration for smart irrigation
- **Advanced Analytics**: Predictive analytics for crop optimization

### Performance Improvements
- **WebSocket Integration**: Real-time updates for collaborative editing
- **GraphQL API**: More efficient data fetching
- **Service Workers**: Offline capabilities
- **Progressive Web App**: PWA features for mobile access
