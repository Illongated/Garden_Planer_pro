# Intelligent Irrigation Design System

## Overview

The Intelligent Irrigation Design System is a comprehensive, production-ready solution for designing, analyzing, and optimizing irrigation systems for gardens and agricultural applications. The system integrates advanced hydraulic calculations, plant clustering algorithms, weather-based scheduling, and cost optimization to provide professional-grade irrigation design capabilities.

## Features

### 🔧 Core Functionality

- **Advanced Hydraulic Calculations**: Darcy-Weisbach equations, Reynolds number analysis, pressure loss calculations
- **Intelligent Plant Clustering**: K-means clustering with multiple features (water needs, spatial distribution, crop coefficients)
- **Equipment Selection Optimization**: Automatic selection of optimal irrigation equipment based on zone requirements
- **Weather Integration**: Real-time weather data integration for evapotranspiration calculations and scheduling
- **Cost Estimation**: Comprehensive cost analysis including equipment, pipes, installation, and ROI calculations
- **System Validation**: Complete validation of irrigation system design for viability and efficiency

### 🎯 Advanced Capabilities

- **Pipe Network Optimization**: Automatic generation of optimal pipe networks with diameter optimization
- **Flow Distribution**: Intelligent flow distribution among zones based on area and water needs
- **Pressure Management**: Advanced pressure loss calculations and system pressure validation
- **Equipment Database**: Comprehensive database of real-world irrigation equipment
- **Technical Reports**: Professional-grade technical reports with detailed analysis

### 🌦️ Weather Integration

- **Evapotranspiration Calculation**: FAO Penman-Monteith equation implementation
- **Weather-Based Scheduling**: Dynamic irrigation scheduling based on weather forecasts
- **Water Efficiency Analysis**: Water use efficiency calculations and recommendations
- **Rainfall Integration**: Automatic adjustment for rainfall events

## Architecture

### Backend Components

```
app/
├── models/
│   └── irrigation.py          # SQLAlchemy models for irrigation system
├── schemas/
│   └── irrigation.py          # Pydantic schemas for API validation
├── services/
│   ├── hydraulic_engine.py    # Advanced hydraulic calculations
│   ├── clustering_engine.py   # Plant clustering algorithms
│   ├── weather_service.py     # Weather integration and ET calculations
│   └── irrigation_planner.py  # Main orchestration service
├── crud/
│   └── irrigation.py          # Database CRUD operations
└── api/v1/endpoints/
    └── irrigation.py          # REST API endpoints
```

### Frontend Components

```
src/features/irrigation/
└── components/
    └── IrrigationDesigner.tsx # Main React component for irrigation design
```

## Database Schema

### Core Tables

1. **irrigation_equipment**: Equipment catalog with specifications
2. **irrigation_zones**: Clustered plant zones with hydraulic properties
3. **irrigation_pipes**: Pipe network with hydraulic calculations
4. **irrigation_schedules**: Irrigation scheduling with weather integration
5. **weather_data**: Historical and forecast weather data
6. **irrigation_projects**: Complete irrigation system projects

### Key Relationships

- Gardens → Irrigation Zones (one-to-many)
- Zones → Equipment (many-to-many via junction table)
- Zones → Pipes (one-to-many)
- Zones → Schedules (one-to-many)
- Gardens → Weather Data (one-to-many)

## API Endpoints

### Core Design Endpoints

```http
POST /api/v1/irrigation/clustering
POST /api/v1/irrigation/hydraulics
POST /api/v1/irrigation/equipment-selection
POST /api/v1/irrigation/design-system
POST /api/v1/irrigation/cost-estimation
POST /api/v1/irrigation/technical-report
```

### CRUD Endpoints

```http
# Zones
GET    /api/v1/irrigation/zones
POST   /api/v1/irrigation/zones
GET    /api/v1/irrigation/zones/{zone_id}
PUT    /api/v1/irrigation/zones/{zone_id}
DELETE /api/v1/irrigation/zones/{zone_id}

# Equipment
GET    /api/v1/irrigation/equipment
POST   /api/v1/irrigation/equipment
GET    /api/v1/irrigation/equipment/{equipment_id}
PUT    /api/v1/irrigation/equipment/{equipment_id}
DELETE /api/v1/irrigation/equipment/{equipment_id}

# Schedules
GET    /api/v1/irrigation/schedules
POST   /api/v1/irrigation/schedules
GET    /api/v1/irrigation/schedules/{schedule_id}
PUT    /api/v1/irrigation/schedules/{schedule_id}
DELETE /api/v1/irrigation/schedules/{schedule_id}

# Weather Data
GET    /api/v1/irrigation/weather-data
POST   /api/v1/irrigation/weather-data

# Projects
GET    /api/v1/irrigation/projects
POST   /api/v1/irrigation/projects
GET    /api/v1/irrigation/projects/{project_id}
PUT    /api/v1/irrigation/projects/{project_id}
DELETE /api/v1/irrigation/projects/{project_id}
```

### Advanced Analysis Endpoints

```http
POST /api/v1/irrigation/optimize-schedule
POST /api/v1/irrigation/validate-system
POST /api/v1/irrigation/optimize-pipe-diameter
POST /api/v1/irrigation/weather-forecast
```

## Usage Examples

### 1. Complete System Design

```python
from app.services.irrigation_planner import IrrigationPlanner

planner = IrrigationPlanner()

# Design complete irrigation system
system_design = planner.design_complete_irrigation_system(
    garden_id="garden-123",
    plants_data=[
        {
            "plant_id": 1,
            "x": 10.0,
            "y": 15.0,
            "water_needs": "high",
            "area_m2": 2.0
        },
        # ... more plants
    ],
    water_source_pressure_bar=2.5,
    water_source_flow_lph=1000,
    max_zones=5,
    budget_constraint=500.0
)

print(f"System viable: {system_design['is_system_viable']}")
print(f"Total cost: ${system_design['total_cost']:.2f}")
```

### 2. Hydraulic Calculations

```python
from app.services.hydraulic_engine import HydraulicEngine

engine = HydraulicEngine()

# Calculate pressure loss for a pipe
pressure_loss, velocity, reynolds, friction = engine.calculate_pressure_loss_darcy_weisbach(
    flow_rate_lph=150,
    diameter_m=0.02,
    length_m=50.0,
    roughness_m=0.0015
)

print(f"Pressure loss: {pressure_loss:.3f} bar")
print(f"Flow velocity: {velocity:.2f} m/s")
```

### 3. Plant Clustering

```python
from app.services.clustering_engine import ClusteringEngine

clustering = ClusteringEngine()

# Perform plant clustering
clustering_input = ClusteringInput(
    plants=plants_data,
    max_zones=5,
    min_plants_per_zone=1
)

result = clustering.perform_clustering(clustering_input)
print(f"Created {len(result.zones)} zones")
print(f"Clustering efficiency: {result.efficiency_score:.2f}")
```

### 4. Weather-Based Scheduling

```python
from app.services.weather_service import WeatherService

weather_service = WeatherService()

# Get weather forecast and recommendations
forecast = await weather_service.get_weather_forecast(
    WeatherForecastInput(
        garden_id="garden-123",
        days_ahead=7
    )
)

for rec in forecast.irrigation_recommendations:
    print(f"{rec['date']}: {rec['recommendation']} - {rec['reason']}")
```

## Frontend Usage

### React Component Integration

```tsx
import { IrrigationDesigner } from '@/features/irrigation/components/IrrigationDesigner';

function App() {
  return (
    <div>
      <IrrigationDesigner />
    </div>
  );
}
```

### Key Features of the UI

1. **Interactive Garden Layout**: Visual representation of plants and zones
2. **Real-time Calculations**: Live hydraulic and cost calculations
3. **Equipment Selection**: Interactive equipment catalog with filtering
4. **Weather Integration**: Real-time weather data display
5. **Technical Analysis**: Comprehensive analysis with charts and metrics

## Installation and Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
alembic upgrade head
```

### 3. Start the Backend

```bash
uvicorn app.main:app --reload
```

### 4. Start the Frontend

```bash
npm run dev
```

## Configuration

### Environment Variables

```env
# Weather API Configuration
WEATHER_API_KEY=your_openweathermap_api_key
WEATHER_BASE_URL=https://api.openweathermap.org/data/2.5

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/garden_planner

# Redis Configuration (for caching)
REDIS_URL=redis://localhost:6379
```

### Hydraulic Calculation Parameters

```python
# Physical constants (configurable)
GRAVITY = 9.81  # m/s²
WATER_DENSITY = 998.2  # kg/m³ at 20°C
WATER_VISCOSITY = 1.002e-3  # Pa·s at 20°C

# Pipe material properties
PIPE_PROPERTIES = {
    "pvc": {"roughness_mm": 0.0015, "cost_per_meter": 2.5},
    "pe": {"roughness_mm": 0.007, "cost_per_meter": 3.2},
    "pex": {"roughness_mm": 0.007, "cost_per_meter": 4.8},
    "copper": {"roughness_mm": 0.0015, "cost_per_meter": 12.0},
}
```

## Testing

### Run Backend Tests

```bash
pytest app/tests/test_irrigation.py -v
```

### Run Frontend Tests

```bash
npm test
```

### Test Coverage

```bash
pytest --cov=app/services --cov-report=html
```

## Performance Optimization

### Caching Strategy

- **Redis Caching**: Weather data and calculation results
- **Client-side Caching**: WebWorker caching for heavy calculations
- **Database Indexing**: Optimized queries with proper indexing

### Scalability Features

- **Async Processing**: Non-blocking calculations for large systems
- **Batch Processing**: Efficient handling of multiple zones
- **Memory Optimization**: Efficient data structures and algorithms

## Security Considerations

### API Security

- **Authentication**: JWT-based authentication for all endpoints
- **Authorization**: Role-based access control for irrigation projects
- **Input Validation**: Comprehensive Pydantic validation
- **Rate Limiting**: API rate limiting to prevent abuse

### Data Protection

- **Encryption**: Sensitive data encrypted at rest
- **Audit Logging**: Complete audit trail for all operations
- **Data Validation**: Strict input validation and sanitization

## Monitoring and Logging

### Application Monitoring

```python
import logging

logger = logging.getLogger(__name__)

# Log hydraulic calculations
logger.info(f"Hydraulic calculation completed: {result}")

# Log clustering results
logger.info(f"Clustering completed: {len(zones)} zones created")

# Log cost estimations
logger.info(f"Cost estimation: ${total_cost:.2f}")
```

### Performance Metrics

- **Calculation Time**: Track hydraulic calculation performance
- **Memory Usage**: Monitor memory consumption for large systems
- **API Response Time**: Track endpoint response times
- **Error Rates**: Monitor calculation error rates

## Troubleshooting

### Common Issues

1. **Hydraulic Calculation Errors**
   - Check pipe diameter constraints
   - Verify flow rate limits
   - Ensure pressure requirements are met

2. **Clustering Failures**
   - Verify plant data format
   - Check minimum plants per zone
   - Ensure sufficient data points

3. **Weather API Issues**
   - Verify API key configuration
   - Check network connectivity
   - Validate location coordinates

### Debug Mode

```python
# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed hydraulic calculations
engine.debug_mode = True
```

## Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 for Python, ESLint for TypeScript
2. **Testing**: Write comprehensive tests for all new features
3. **Documentation**: Update documentation for all changes
4. **Performance**: Ensure new features don't impact performance

### Adding New Equipment

```python
# Add to equipment database
new_equipment = {
    "name": "Custom Drip Emitter",
    "type": "drip",
    "flow_rate_lph": 6.0,
    "coverage_radius_m": 0.5,
    "cost_per_unit": 0.8,
    "manufacturer": "Custom",
    "model": "CDE-6"
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests via GitHub issues
- **Discussions**: Use GitHub discussions for general questions

## Roadmap

### Planned Features

- **3D Visualization**: Advanced 3D pipe network visualization
- **Mobile App**: Native mobile application for field use
- **AI Integration**: Machine learning for optimal scheduling
- **IoT Integration**: Real-time sensor data integration
- **Advanced Analytics**: Predictive analytics for water usage

### Performance Improvements

- **GPU Acceleration**: CUDA-based hydraulic calculations
- **Distributed Computing**: Multi-node calculation distribution
- **Real-time Updates**: WebSocket-based real-time updates
- **Offline Support**: Offline calculation capabilities 