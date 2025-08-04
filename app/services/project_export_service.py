import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
import tempfile
import zipfile
from io import BytesIO

from models.project import Project, ProjectVersion, ProjectComment, ProjectActivity
from schemas.project import ProjectExport, ProjectImport, ProjectCreate
from crud.project import project_crud

class ProjectExportService:
    """Service for exporting and importing projects in various formats."""
    
    def __init__(self):
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
    
    def export_project(self, db: Session, project_id: uuid.UUID) -> ProjectExport:
        """Export a project with all its data."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
        
        # Get all versions
        versions = db.query(ProjectVersion).filter(
            ProjectVersion.project_id == project_id
        ).order_by(ProjectVersion.version_number).all()
        
        # Get all comments
        comments = db.query(ProjectComment).filter(
            ProjectComment.project_id == project_id
        ).order_by(ProjectComment.created_at).all()
        
        # Get all activities
        activities = db.query(ProjectActivity).filter(
            ProjectActivity.project_id == project_id
        ).order_by(ProjectActivity.created_at).all()
        
        return ProjectExport(
            project=project,
            versions=versions,
            comments=comments,
            activities=activities,
            export_metadata={
                "exported_at": datetime.utcnow().isoformat(),
                "export_version": "1.0",
                "total_versions": len(versions),
                "total_comments": len(comments),
                "total_activities": len(activities)
            }
        )
    
    def export_to_json(self, db: Session, project_id: uuid.UUID) -> str:
        """Export project to JSON file."""
        export_data = self.export_project(db, project_id)
        
        # Convert to JSON-serializable format
        json_data = {
            "project": {
                "id": str(export_data.project.id),
                "name": export_data.project.name,
                "description": export_data.project.description,
                "location": export_data.project.location,
                "climate_zone": export_data.project.climate_zone,
                "soil_type": export_data.project.soil_type,
                "garden_size": export_data.project.garden_size,
                "layout_data": export_data.project.layout_data,
                "plant_data": export_data.project.plant_data,
                "irrigation_data": export_data.project.irrigation_data,
                "status": export_data.project.status.value,
                "is_public": export_data.project.is_public,
                "allow_comments": export_data.project.allow_comments,
                "allow_forking": export_data.project.allow_forking,
                "created_at": export_data.project.created_at.isoformat(),
                "updated_at": export_data.project.updated_at.isoformat()
            },
            "versions": [
                {
                    "id": str(version.id),
                    "version_number": version.version_number,
                    "name": version.name,
                    "description": version.description,
                    "layout_data": version.layout_data,
                    "plant_data": version.plant_data,
                    "irrigation_data": version.irrigation_data,
                    "is_tagged": version.is_tagged,
                    "tag_name": version.tag_name,
                    "created_at": version.created_at.isoformat()
                }
                for version in export_data.versions
            ],
            "comments": [
                {
                    "id": str(comment.id),
                    "content": comment.content,
                    "position_x": comment.position_x,
                    "position_y": comment.position_y,
                    "element_id": comment.element_id,
                    "parent_comment_id": str(comment.parent_comment_id) if comment.parent_comment_id else None,
                    "is_resolved": comment.is_resolved,
                    "created_at": comment.created_at.isoformat(),
                    "updated_at": comment.updated_at.isoformat()
                }
                for comment in export_data.comments
            ],
            "activities": [
                {
                    "id": str(activity.id),
                    "activity_type": activity.activity_type,
                    "description": activity.description,
                    "metadata": activity.metadata,
                    "created_at": activity.created_at.isoformat()
                }
                for activity in export_data.activities
            ],
            "export_metadata": export_data.export_metadata
        }
        
        # Create file
        filename = f"project_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = self.export_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def export_to_pdf(self, db: Session, project_id: uuid.UUID) -> str:
        """Export project to PDF file."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
        except ImportError:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
        
        # Create PDF file
        filename = f"project_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = self.export_dir / filename
        
        doc = SimpleDocTemplate(str(file_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(f"Project: {project.name}", title_style))
        story.append(Spacer(1, 20))
        
        # Project details
        story.append(Paragraph("Project Details", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        details_data = [
            ["Name", project.name],
            ["Description", project.description or "No description"],
            ["Location", project.location or "Not specified"],
            ["Climate Zone", project.climate_zone or "Not specified"],
            ["Soil Type", project.soil_type or "Not specified"],
            ["Garden Size", f"{project.garden_size} m²" if project.garden_size else "Not specified"],
            ["Status", project.status.value.title()],
            ["Public", "Yes" if project.is_public else "No"],
            ["Created", project.created_at.strftime("%Y-%m-%d %H:%M")],
            ["Last Updated", project.updated_at.strftime("%Y-%m-%d %H:%M")]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(details_table)
        story.append(Spacer(1, 20))
        
        # Layout data summary
        if project.layout_data:
            story.append(Paragraph("Layout Summary", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            layout_summary = f"Layout contains {len(project.layout_data)} elements"
            story.append(Paragraph(layout_summary, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Plant data summary
        if project.plant_data:
            story.append(Paragraph("Plant Summary", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            plant_count = len(project.plant_data.get('plants', []))
            story.append(Paragraph(f"Total plants: {plant_count}", styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Versions summary
        versions = db.query(ProjectVersion).filter(
            ProjectVersion.project_id == project_id
        ).order_by(ProjectVersion.version_number.desc()).limit(5).all()
        
        if versions:
            story.append(Paragraph("Recent Versions", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            version_data = [["Version", "Name", "Created"]]
            for version in versions:
                version_data.append([
                    str(version.version_number),
                    version.name,
                    version.created_at.strftime("%Y-%m-%d %H:%M")
                ])
            
            version_table = Table(version_data, colWidths=[1*inch, 3*inch, 2*inch])
            version_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(version_table)
            story.append(Spacer(1, 20))
        
        # Comments summary
        comments = db.query(ProjectComment).filter(
            ProjectComment.project_id == project_id
        ).order_by(ProjectComment.created_at.desc()).limit(5).all()
        
        if comments:
            story.append(Paragraph("Recent Comments", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            for comment in comments:
                comment_text = f"<b>{comment.created_at.strftime('%Y-%m-%d %H:%M')}</b>: {comment.content}"
                story.append(Paragraph(comment_text, styles['Normal']))
                story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        return str(file_path)
    
    def export_to_png(self, db: Session, project_id: uuid.UUID) -> str:
        """Export project layout as PNG image."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
        except ImportError:
            raise ImportError("Pillow is required for PNG export. Install with: pip install Pillow")
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
        
        # Create a simple layout visualization
        # In a real implementation, you'd render the actual garden layout
        img_width, img_height = 800, 600
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw title
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        title = f"Project: {project.name}"
        draw.text((20, 20), title, fill='black', font=font)
        
        # Draw project info
        info_font = ImageFont.load_default()
        y_pos = 80
        info_lines = [
            f"Location: {project.location or 'Not specified'}",
            f"Climate Zone: {project.climate_zone or 'Not specified'}",
            f"Garden Size: {project.garden_size} m²" if project.garden_size else "Garden Size: Not specified",
            f"Status: {project.status.value.title()}",
            f"Created: {project.created_at.strftime('%Y-%m-%d')}"
        ]
        
        for line in info_lines:
            draw.text((20, y_pos), line, fill='black', font=info_font)
            y_pos += 25
        
        # Draw a simple layout representation
        if project.layout_data:
            draw.text((20, 200), "Layout Data Available", fill='green', font=info_font)
        else:
            draw.text((20, 200), "No Layout Data", fill='red', font=info_font)
        
        # Save image
        filename = f"project_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = self.export_dir / filename
        
        img.save(str(file_path))
        return str(file_path)
    
    def export_to_zip(self, db: Session, project_id: uuid.UUID) -> str:
        """Export project as ZIP file containing all formats."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
        
        # Create temporary directory for files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Export to different formats
            json_path = self.export_to_json(db, project_id)
            pdf_path = self.export_to_pdf(db, project_id)
            png_path = self.export_to_png(db, project_id)
            
            # Create ZIP file
            zip_filename = f"project_{project_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = self.export_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add files to ZIP
                zipf.write(json_path, "project.json")
                zipf.write(pdf_path, "project.pdf")
                zipf.write(png_path, "project.png")
                
                # Add metadata
                metadata = {
                    "project_id": str(project_id),
                    "project_name": project.name,
                    "exported_at": datetime.utcnow().isoformat(),
                    "formats": ["json", "pdf", "png"]
                }
                
                metadata_path = temp_path / "metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                zipf.write(str(metadata_path), "metadata.json")
            
            # Clean up individual files
            os.remove(json_path)
            os.remove(pdf_path)
            os.remove(png_path)
            
            return str(zip_path)
    
    def import_project(self, db: Session, project_import: ProjectImport, owner_id: uuid.UUID) -> Project:
        """Import a project from JSON data."""
        # Create project from import data
        project_data = {
            "name": project_import.name,
            "description": project_import.description,
            "layout_data": project_import.layout_data,
            "plant_data": project_import.plant_data,
            "irrigation_data": project_import.irrigation_data,
            "is_public": False,  # Imported projects are private by default
            "allow_comments": True,
            "allow_forking": True
        }
        
        # Create the project
        project_create = ProjectCreate(**project_data)
        project = project_crud.create_project(
            db=db, project_in=project_create, owner_id=owner_id
        )
        
        # Add import metadata as activity
        from models.project import ProjectActivity
        activity = ProjectActivity(
            project_id=project.id,
            user_id=owner_id,
            activity_type="project_imported",
            description=f"Project imported from external source",
            metadata={
                "import_metadata": project_import.import_metadata,
                "original_name": project_import.name
            }
        )
        db.add(activity)
        db.commit()
        
        return project
    
    def import_from_json_file(self, db: Session, file_path: str, owner_id: uuid.UUID) -> Project:
        """Import a project from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract project data
        project_data = data.get("project", {})
        
        # Create import object
        project_import = ProjectImport(
            name=project_data.get("name", "Imported Project"),
            description=project_data.get("description"),
            layout_data=project_data.get("layout_data"),
            plant_data=project_data.get("plant_data"),
            irrigation_data=project_data.get("irrigation_data"),
            import_metadata={
                "source_file": file_path,
                "imported_at": datetime.utcnow().isoformat(),
                "original_project_id": project_data.get("id")
            }
        )
        
        return self.import_project(db, project_import, owner_id)

# Create service instance
project_export_service = ProjectExportService() 