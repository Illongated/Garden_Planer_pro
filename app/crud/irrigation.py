from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.irrigation import (
    IrrigationZone, IrrigationEquipment, IrrigationSchedule, 
    WeatherData, IrrigationProject, EquipmentType, ZoneStatus, ScheduleType
)
from schemas.irrigation import (
    IrrigationZoneCreate, IrrigationZoneUpdate,
    IrrigationEquipmentCreate, IrrigationEquipmentUpdate,
    IrrigationScheduleCreate, IrrigationScheduleUpdate,
    WeatherDataCreate, IrrigationProjectCreate, IrrigationProjectUpdate
)


class IrrigationZoneCRUD:
    """CRUD operations for irrigation zones."""
    
    def create_zone(self, db: Session, *, zone_in: IrrigationZoneCreate) -> IrrigationZone:
        """Create a new irrigation zone."""
        zone_data = zone_in.model_dump()
        db_zone = IrrigationZone(**zone_data)
        db.add(db_zone)
        db.commit()
        db.refresh(db_zone)
        return db_zone
    
    def get_zone(self, db: Session, *, zone_id: UUID) -> Optional[IrrigationZone]:
        """Get a specific irrigation zone by ID."""
        return db.query(IrrigationZone).filter(IrrigationZone.id == zone_id).first()
    
    def get_zones(
        self, 
        db: Session, 
        *, 
        garden_id: Optional[UUID] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[IrrigationZone]:
        """Get irrigation zones with optional filtering."""
        query = db.query(IrrigationZone)
        
        if garden_id:
            query = query.filter(IrrigationZone.garden_id == garden_id)
        
        return query.offset(skip).limit(limit).all()
    
    def update_zone(
        self, 
        db: Session, 
        *, 
        zone_id: UUID, 
        zone_in: IrrigationZoneUpdate
    ) -> Optional[IrrigationZone]:
        """Update an irrigation zone."""
        db_zone = self.get_zone(db=db, zone_id=zone_id)
        if not db_zone:
            return None
        
        update_data = zone_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_zone, field, value)
        
        db.commit()
        db.refresh(db_zone)
        return db_zone
    
    def delete_zone(self, db: Session, *, zone_id: UUID) -> bool:
        """Delete an irrigation zone."""
        db_zone = self.get_zone(db=db, zone_id=zone_id)
        if not db_zone:
            return False
        
        db.delete(db_zone)
        db.commit()
        return True


class IrrigationEquipmentCRUD:
    """CRUD operations for irrigation equipment."""
    
    def create_equipment(
        self, 
        db: Session, 
        *, 
        equipment_in: IrrigationEquipmentCreate
    ) -> IrrigationEquipment:
        """Create new irrigation equipment."""
        equipment_data = equipment_in.model_dump()
        db_equipment = IrrigationEquipment(**equipment_data)
        db.add(db_equipment)
        db.commit()
        db.refresh(db_equipment)
        return db_equipment
    
    def get_equipment_by_id(
        self, 
        db: Session, 
        *, 
        equipment_id: UUID
    ) -> Optional[IrrigationEquipment]:
        """Get specific irrigation equipment by ID."""
        return db.query(IrrigationEquipment).filter(
            IrrigationEquipment.id == equipment_id
        ).first()
    
    def get_equipment(
        self, 
        db: Session, 
        *, 
        equipment_type: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[IrrigationEquipment]:
        """Get irrigation equipment with optional filtering."""
        query = db.query(IrrigationEquipment)
        
        if equipment_type:
            query = query.filter(IrrigationEquipment.equipment_type == equipment_type)
        
        return query.offset(skip).limit(limit).all()
    
    def update_equipment(
        self, 
        db: Session, 
        *, 
        equipment_id: UUID, 
        equipment_in: IrrigationEquipmentUpdate
    ) -> Optional[IrrigationEquipment]:
        """Update irrigation equipment."""
        db_equipment = self.get_equipment_by_id(db=db, equipment_id=equipment_id)
        if not db_equipment:
            return None
        
        update_data = equipment_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_equipment, field, value)
        
        db.commit()
        db.refresh(db_equipment)
        return db_equipment
    
    def delete_equipment(self, db: Session, *, equipment_id: UUID) -> bool:
        """Delete irrigation equipment."""
        db_equipment = self.get_equipment_by_id(db=db, equipment_id=equipment_id)
        if not db_equipment:
            return False
        
        db.delete(db_equipment)
        db.commit()
        return True


class IrrigationScheduleCRUD:
    """CRUD operations for irrigation schedules."""
    
    def create_schedule(
        self, 
        db: Session, 
        *, 
        schedule_in: IrrigationScheduleCreate
    ) -> IrrigationSchedule:
        """Create new irrigation schedule."""
        schedule_data = schedule_in.model_dump()
        db_schedule = IrrigationSchedule(**schedule_data)
        db.add(db_schedule)
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    
    def get_schedule_by_id(
        self, 
        db: Session, 
        *, 
        schedule_id: UUID
    ) -> Optional[IrrigationSchedule]:
        """Get specific irrigation schedule by ID."""
        return db.query(IrrigationSchedule).filter(
            IrrigationSchedule.id == schedule_id
        ).first()
    
    def get_schedules(
        self, 
        db: Session, 
        *, 
        zone_id: Optional[UUID] = None,
        schedule_type: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[IrrigationSchedule]:
        """Get irrigation schedules with optional filtering."""
        query = db.query(IrrigationSchedule)
        
        if zone_id:
            query = query.filter(IrrigationSchedule.zone_id == zone_id)
        
        if schedule_type:
            query = query.filter(IrrigationSchedule.schedule_type == schedule_type)
        
        return query.offset(skip).limit(limit).all()
    
    def update_schedule(
        self, 
        db: Session, 
        *, 
        schedule_id: UUID, 
        schedule_in: IrrigationScheduleUpdate
    ) -> Optional[IrrigationSchedule]:
        """Update irrigation schedule."""
        db_schedule = self.get_schedule_by_id(db=db, schedule_id=schedule_id)
        if not db_schedule:
            return None
        
        update_data = schedule_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_schedule, field, value)
        
        db.commit()
        db.refresh(db_schedule)
        return db_schedule
    
    def delete_schedule(self, db: Session, *, schedule_id: UUID) -> bool:
        """Delete irrigation schedule."""
        db_schedule = self.get_schedule_by_id(db=db, schedule_id=schedule_id)
        if not db_schedule:
            return False
        
        db.delete(db_schedule)
        db.commit()
        return True


class WeatherDataCRUD:
    """CRUD operations for weather data."""
    
    def create_weather_data(
        self, 
        db: Session, 
        *, 
        weather_in: WeatherDataCreate
    ) -> WeatherData:
        """Create new weather data entry."""
        weather_data = weather_in.model_dump()
        db_weather = WeatherData(**weather_data)
        db.add(db_weather)
        db.commit()
        db.refresh(db_weather)
        return db_weather
    
    def get_weather_data(
        self, 
        db: Session, 
        *, 
        garden_id: Optional[UUID] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[WeatherData]:
        """Get weather data with optional filtering."""
        query = db.query(WeatherData)
        
        if garden_id:
            query = query.filter(WeatherData.garden_id == garden_id)
        
        if start_date:
            query = query.filter(WeatherData.date >= start_date)
        
        if end_date:
            query = query.filter(WeatherData.date <= end_date)
        
        return query.order_by(WeatherData.date.desc()).offset(skip).limit(limit).all()
    
    def get_latest_weather_data(
        self, 
        db: Session, 
        *, 
        garden_id: UUID
    ) -> Optional[WeatherData]:
        """Get the latest weather data for a garden."""
        return db.query(WeatherData).filter(
            WeatherData.garden_id == garden_id
        ).order_by(WeatherData.date.desc()).first()


class IrrigationProjectCRUD:
    """CRUD operations for irrigation projects."""
    
    def create_project(
        self, 
        db: Session, 
        *, 
        project_in: IrrigationProjectCreate
    ) -> IrrigationProject:
        """Create new irrigation project."""
        project_data = project_in.model_dump()
        db_project = IrrigationProject(**project_data)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    def get_project_by_id(
        self, 
        db: Session, 
        *, 
        project_id: UUID
    ) -> Optional[IrrigationProject]:
        """Get specific irrigation project by ID."""
        return db.query(IrrigationProject).filter(
            IrrigationProject.id == project_id
        ).first()
    
    def get_projects(
        self, 
        db: Session, 
        *, 
        garden_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[IrrigationProject]:
        """Get irrigation projects with optional filtering."""
        query = db.query(IrrigationProject)
        
        if garden_id:
            query = query.filter(IrrigationProject.garden_id == garden_id)
        
        if is_active is not None:
            query = query.filter(IrrigationProject.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def update_project(
        self, 
        db: Session, 
        *, 
        project_id: UUID, 
        project_in: IrrigationProjectUpdate
    ) -> Optional[IrrigationProject]:
        """Update irrigation project."""
        db_project = self.get_project_by_id(db=db, project_id=project_id)
        if not db_project:
            return None
        
        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    
    def delete_project(self, db: Session, *, project_id: UUID) -> bool:
        """Delete irrigation project."""
        db_project = self.get_project_by_id(db=db, project_id=project_id)
        if not db_project:
            return False
        
        db.delete(db_project)
        db.commit()
        return True


# Initialize CRUD instances
irrigation_zone_crud = IrrigationZoneCRUD()
irrigation_equipment_crud = IrrigationEquipmentCRUD()
irrigation_schedule_crud = IrrigationScheduleCRUD()
weather_data_crud = WeatherDataCRUD()
irrigation_project_crud = IrrigationProjectCRUD() 