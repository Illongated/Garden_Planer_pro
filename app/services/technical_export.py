import json
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
import io
import base64

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, blue, red, green, gray, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from .irrigation_planner import IrrigationPlanner
from ..schemas.irrigation import (
    IrrigationZone, IrrigationPipe, IrrigationEquipment, 
    HydraulicCalculationResult, CostEstimationResult
)


class TechnicalExportService:
    """Service for generating professional technical plan exports."""
    
    def __init__(self):
        self.irrigation_planner = IrrigationPlanner()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for technical documents."""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkblue
        )
        
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.black
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def generate_pdf_technical_report(
        self,
        garden_id: str,
        system_design: Dict[str, Any],
        project_name: str = "Irrigation System Design",
        include_drawings: bool = True
    ) -> bytes:
        """
        Generate a comprehensive PDF technical report for an irrigation system.
        
        Args:
            garden_id: Garden identifier
            system_design: Complete system design data
            project_name: Name of the project
            include_drawings: Whether to include technical drawings
            
        Returns:
            PDF document as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # Title page
        story.extend(self._create_title_page(project_name, garden_id))
        story.append(PageBreak())
        
        # Table of contents
        story.extend(self._create_table_of_contents())
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(system_design))
        story.append(PageBreak())
        
        # System overview
        story.extend(self._create_system_overview(system_design))
        story.append(PageBreak())
        
        # Hydraulic calculations
        story.extend(self._create_hydraulic_section(system_design))
        story.append(PageBreak())
        
        # Equipment specifications
        story.extend(self._create_equipment_section(system_design))
        story.append(PageBreak())
        
        # Cost analysis
        story.extend(self._create_cost_section(system_design))
        story.append(PageBreak())
        
        # Installation guidelines
        story.extend(self._create_installation_guidelines(system_design))
        story.append(PageBreak())
        
        # Maintenance schedule
        story.extend(self._create_maintenance_schedule(system_design))
        story.append(PageBreak())
        
        # Technical drawings (if requested)
        if include_drawings:
            story.extend(self._create_technical_drawings(system_design))
            story.append(PageBreak())
        
        # Appendices
        story.extend(self._create_appendices(system_design))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_title_page(self, project_name: str, garden_id: str) -> List:
        """Create the title page."""
        elements = []
        
        # Title
        title_text = f"<b>{project_name}</b>"
        elements.append(Paragraph(title_text, self.title_style))
        elements.append(Spacer(1, 20))
        
        # Subtitle
        subtitle_text = "Technical Design Report"
        elements.append(Paragraph(subtitle_text, self.subtitle_style))
        elements.append(Spacer(1, 30))
        
        # Project details
        details_data = [
            ["Project:", project_name],
            ["Garden ID:", garden_id],
            ["Date:", datetime.now().strftime("%B %d, %Y")],
            ["Report Type:", "Technical Design"],
            ["Status:", "Design Complete"]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(details_table)
        elements.append(Spacer(1, 30))
        
        # Disclaimer
        disclaimer_text = """
        <i>This technical report contains detailed specifications for the irrigation system design. 
        All calculations are based on standard engineering practices and should be reviewed by a 
        qualified professional before implementation.</i>
        """
        elements.append(Paragraph(disclaimer_text, self.normal_style))
        
        return elements
    
    def _create_table_of_contents(self) -> List:
        """Create table of contents."""
        elements = []
        
        elements.append(Paragraph("Table of Contents", self.title_style))
        elements.append(Spacer(1, 20))
        
        toc_items = [
            "1. Executive Summary",
            "2. System Overview",
            "3. Hydraulic Calculations",
            "4. Equipment Specifications",
            "5. Cost Analysis",
            "6. Installation Guidelines",
            "7. Maintenance Schedule",
            "8. Technical Drawings",
            "9. Appendices"
        ]
        
        for item in toc_items:
            elements.append(Paragraph(f"• {item}", self.normal_style))
            elements.append(Spacer(1, 3))
        
        return elements
    
    def _create_executive_summary(self, system_design: Dict[str, Any]) -> List:
        """Create executive summary section."""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.title_style))
        elements.append(Spacer(1, 12))
        
        # Key metrics
        zones = system_design.get("zones", [])
        hydraulic_result = system_design.get("hydraulic_calculations", {})
        cost_result = system_design.get("cost_estimation", {})
        
        summary_data = [
            ["Metric", "Value", "Status"],
            ["Total Zones", str(len(zones)), "✓"],
            ["Total Flow Rate", f"{hydraulic_result.get('total_flow_lph', 0):.1f} LPH", "✓"],
            ["System Pressure", f"{hydraulic_result.get('final_pressure_bar', 0):.2f} bar", "✓"],
            ["Total Cost", f"${cost_result.get('total_cost', 0):.2f}", "✓"],
            ["System Viable", "Yes" if hydraulic_result.get('is_system_viable', False) else "No", "⚠"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 12))
        
        # Summary text
        summary_text = f"""
        This irrigation system design consists of {len(zones)} zones with a total flow rate of 
        {hydraulic_result.get('total_flow_lph', 0):.1f} liters per hour. The system operates at 
        {hydraulic_result.get('final_pressure_bar', 0):.2f} bar with an estimated total cost of 
        ${cost_result.get('total_cost', 0):.2f}. The design includes comprehensive hydraulic calculations, 
        equipment specifications, and installation guidelines.
        """
        elements.append(Paragraph(summary_text, self.normal_style))
        
        return elements
    
    def _create_system_overview(self, system_design: Dict[str, Any]) -> List:
        """Create system overview section."""
        elements = []
        
        elements.append(Paragraph("System Overview", self.title_style))
        elements.append(Spacer(1, 12))
        
        zones = system_design.get("zones", [])
        
        # Zone overview table
        zone_headers = ["Zone", "Area (m²)", "Flow (LPH)", "Pressure (bar)", "Status"]
        zone_data = [zone_headers]
        
        for i, zone in enumerate(zones, 1):
            zone_data.append([
                f"Zone {i}",
                f"{zone.get('total_area_m2', 0):.1f}",
                f"{zone.get('required_flow_lph', 0):.1f}",
                f"{zone.get('operating_pressure_bar', 0):.2f}",
                zone.get('status', 'Unknown')
            ])
        
        zone_table = Table(zone_data, colWidths=[1*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        zone_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(zone_table)
        elements.append(Spacer(1, 12))
        
        # System characteristics
        elements.append(Paragraph("System Characteristics", self.subtitle_style))
        elements.append(Spacer(1, 6))
        
        characteristics = [
            f"• Total irrigation zones: {len(zones)}",
            f"• Total system area: {sum(zone.get('total_area_m2', 0) for zone in zones):.1f} m²",
            f"• Clustering efficiency: {system_design.get('clustering_efficiency', 0):.2f}",
            f"• System viability: {'Yes' if system_design.get('is_system_viable', False) else 'No'}"
        ]
        
        for char in characteristics:
            elements.append(Paragraph(char, self.normal_style))
        
        return elements
    
    def _create_hydraulic_section(self, system_design: Dict[str, Any]) -> List:
        """Create hydraulic calculations section."""
        elements = []
        
        elements.append(Paragraph("Hydraulic Calculations", self.title_style))
        elements.append(Spacer(1, 12))
        
        hydraulic_result = system_design.get("hydraulic_calculations", {})
        
        # Hydraulic summary table
        hydraulic_data = [
            ["Parameter", "Value", "Unit"],
            ["Total Flow Rate", f"{hydraulic_result.get('total_flow_lph', 0):.1f}", "LPH"],
            ["Total Pressure Loss", f"{hydraulic_result.get('total_pressure_loss_bar', 0):.3f}", "bar"],
            ["Final Pressure", f"{hydraulic_result.get('final_pressure_bar', 0):.2f}", "bar"],
            ["Flow Velocity", f"{hydraulic_result.get('velocity_ms', 0):.2f}", "m/s"],
            ["Reynolds Number", f"{hydraulic_result.get('reynolds_number', 0):.0f}", ""],
            ["Friction Factor", f"{hydraulic_result.get('friction_factor', 0):.4f}", ""]
        ]
        
        hydraulic_table = Table(hydraulic_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        hydraulic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(hydraulic_table)
        elements.append(Spacer(1, 12))
        
        # Warnings
        warnings = hydraulic_result.get('warnings', [])
        if warnings:
            elements.append(Paragraph("Hydraulic Warnings", self.subtitle_style))
            elements.append(Spacer(1, 6))
            
            for warning in warnings:
                warning_text = f"⚠ {warning}"
                elements.append(Paragraph(warning_text, self.normal_style))
        
        return elements
    
    def _create_equipment_section(self, system_design: Dict[str, Any]) -> List:
        """Create equipment specifications section."""
        elements = []
        
        elements.append(Paragraph("Equipment Specifications", self.title_style))
        elements.append(Spacer(1, 12))
        
        equipment_selections = system_design.get("equipment_selections", [])
        
        for i, equipment_result in enumerate(equipment_selections, 1):
            equipment = equipment_result.get("recommended_equipment", {})
            
            elements.append(Paragraph(f"Zone {i} Equipment", self.subtitle_style))
            elements.append(Spacer(1, 6))
            
            equipment_data = [
                ["Parameter", "Value"],
                ["Equipment Type", equipment.get("equipment_type", "Unknown")],
                ["Manufacturer", equipment.get("manufacturer", "Unknown")],
                ["Model", equipment.get("model", "Unknown")],
                ["Flow Rate", f"{equipment.get('flow_rate_lph', 0):.1f} LPH"],
                ["Pressure Range", f"{equipment.get('pressure_range_min', 0):.1f} - {equipment.get('pressure_range_max', 0):.1f} bar"],
                ["Coverage Radius", f"{equipment.get('coverage_radius_m', 0):.2f} m"],
                ["Spacing", f"{equipment.get('spacing_m', 0):.2f} m"],
                ["Cost per Unit", f"${equipment.get('cost_per_unit', 0):.2f}"],
                ["Quantity Needed", str(equipment_result.get("quantity_needed", 0))],
                ["Total Cost", f"${equipment_result.get('total_cost', 0):.2f}"],
                ["Coverage Efficiency", f"{equipment_result.get('coverage_efficiency', 0):.1%}"]
            ]
            
            equipment_table = Table(equipment_data, colWidths=[2.5*inch, 3.5*inch])
            equipment_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(equipment_table)
            elements.append(Spacer(1, 12))
            
            # Justification
            justification = equipment_result.get("justification", "")
            if justification:
                elements.append(Paragraph(f"<b>Selection Justification:</b> {justification}", self.normal_style))
                elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_cost_section(self, system_design: Dict[str, Any]) -> List:
        """Create cost analysis section."""
        elements = []
        
        elements.append(Paragraph("Cost Analysis", self.title_style))
        elements.append(Spacer(1, 12))
        
        cost_result = system_design.get("cost_estimation", {})
        
        # Cost breakdown table
        cost_data = [
            ["Component", "Cost ($)", "Percentage"],
            ["Equipment", f"{cost_result.get('equipment_cost', 0):.2f}", f"{cost_result.get('equipment_percentage', 0):.1f}%"],
            ["Pipes", f"{cost_result.get('pipe_cost', 0):.2f}", f"{cost_result.get('pipe_percentage', 0):.1f}%"],
            ["Fittings", f"{cost_result.get('fittings_cost', 0):.2f}", f"{cost_result.get('fittings_percentage', 0):.1f}%"],
            ["Installation", f"{cost_result.get('installation_cost', 0):.2f}", f"{cost_result.get('installation_percentage', 0):.1f}%"],
            ["Contingency", f"{cost_result.get('contingency_cost', 0):.2f}", f"{cost_result.get('contingency_percentage', 0):.1f}%"],
            ["<b>TOTAL</b>", f"<b>{cost_result.get('total_cost', 0):.2f}</b>", "<b>100%</b>"]
        ]
        
        cost_table = Table(cost_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
        ]))
        
        elements.append(cost_table)
        elements.append(Spacer(1, 12))
        
        # Cost per area
        zones = system_design.get("zones", [])
        total_area = sum(zone.get('total_area_m2', 0) for zone in zones)
        total_cost = cost_result.get('total_cost', 0)
        
        if total_area > 0:
            cost_per_area = total_cost / total_area
            elements.append(Paragraph(f"Cost per square meter: ${cost_per_area:.2f}/m²", self.normal_style))
        
        return elements
    
    def _create_installation_guidelines(self, system_design: Dict[str, Any]) -> List:
        """Create installation guidelines section."""
        elements = []
        
        elements.append(Paragraph("Installation Guidelines", self.title_style))
        elements.append(Spacer(1, 12))
        
        # General guidelines
        elements.append(Paragraph("General Installation Guidelines", self.subtitle_style))
        elements.append(Spacer(1, 6))
        
        guidelines = [
            "1. Ensure proper water source pressure and flow rate",
            "2. Install pressure regulators if necessary",
            "3. Use appropriate pipe materials for the application",
            "4. Follow manufacturer specifications for equipment installation",
            "5. Test system thoroughly before final commissioning",
            "6. Document all connections and valve positions",
            "7. Provide adequate drainage and backflow prevention",
            "8. Consider seasonal maintenance access"
        ]
        
        for guideline in guidelines:
            elements.append(Paragraph(guideline, self.normal_style))
        
        elements.append(Spacer(1, 12))
        
        # Safety considerations
        elements.append(Paragraph("Safety Considerations", self.subtitle_style))
        elements.append(Spacer(1, 6))
        
        safety_items = [
            "• Ensure electrical safety for any automated components",
            "• Follow local building codes and regulations",
            "• Use appropriate personal protective equipment",
            "• Test system under controlled conditions",
            "• Provide emergency shutdown procedures"
        ]
        
        for item in safety_items:
            elements.append(Paragraph(item, self.normal_style))
        
        return elements
    
    def _create_maintenance_schedule(self, system_design: Dict[str, Any]) -> List:
        """Create maintenance schedule section."""
        elements = []
        
        elements.append(Paragraph("Maintenance Schedule", self.title_style))
        elements.append(Spacer(1, 12))
        
        # Maintenance tasks
        maintenance_data = [
            ["Frequency", "Task", "Description"],
            ["Weekly", "Visual Inspection", "Check for leaks, damage, and proper operation"],
            ["Monthly", "Filter Cleaning", "Clean or replace filters as needed"],
            ["Seasonal", "System Flush", "Flush system to remove debris"],
            ["Annually", "Pressure Test", "Test system pressure and flow rates"],
            ["Annually", "Equipment Check", "Inspect and service all equipment"],
            ["As Needed", "Repairs", "Address any issues immediately"]
        ]
        
        maintenance_table = Table(maintenance_data, colWidths=[1.5*inch, 2*inch, 3.5*inch])
        maintenance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(maintenance_table)
        
        return elements
    
    def _create_technical_drawings(self, system_design: Dict[str, Any]) -> List:
        """Create technical drawings section."""
        elements = []
        
        elements.append(Paragraph("Technical Drawings", self.title_style))
        elements.append(Spacer(1, 12))
        
        # Note about drawings
        note_text = """
        <i>Technical drawings would be generated here based on the system design. 
        This would include zone layouts, pipe routing diagrams, and equipment placement plans. 
        In a full implementation, these would be generated programmatically from the design data.</i>
        """
        elements.append(Paragraph(note_text, self.normal_style))
        
        return elements
    
    def _create_appendices(self, system_design: Dict[str, Any]) -> List:
        """Create appendices section."""
        elements = []
        
        elements.append(Paragraph("Appendices", self.title_style))
        elements.append(Spacer(1, 12))
        
        # Appendix A: Design Data
        elements.append(Paragraph("Appendix A: Complete Design Data", self.subtitle_style))
        elements.append(Spacer(1, 6))
        
        # Convert system design to JSON for display
        design_json = json.dumps(system_design, indent=2, default=str)
        
        # Split into manageable chunks
        chunk_size = 80
        chunks = [design_json[i:i+chunk_size] for i in range(0, len(design_json), chunk_size)]
        
        for chunk in chunks[:10]:  # Limit to first 10 chunks to avoid huge PDFs
            elements.append(Paragraph(f"<code>{chunk}</code>", self.normal_style))
        
        if len(chunks) > 10:
            elements.append(Paragraph(f"... (showing first {len(chunks[:10])} of {len(chunks)} chunks)", self.normal_style))
        
        return elements
    
    def generate_svg_technical_drawing(
        self,
        system_design: Dict[str, Any],
        width: int = 800,
        height: int = 600
    ) -> str:
        """
        Generate an SVG technical drawing of the irrigation system.
        
        Args:
            system_design: Complete system design data
            width: SVG width in pixels
            height: SVG height in pixels
            
        Returns:
            SVG content as string
        """
        zones = system_design.get("zones", [])
        pipes = system_design.get("pipe_network", [])
        
        # SVG header
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .zone {{ fill: #e6f3ff; stroke: #0066cc; stroke-width: 2; }}
            .pipe {{ stroke: #333333; stroke-width: 3; fill: none; }}
            .equipment {{ fill: #ff6666; stroke: #cc0000; stroke-width: 1; }}
            .text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #333333; }}
            .title {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #333333; }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="#ffffff"/>
    
    <!-- Title -->
    <text x="{width/2}" y="30" text-anchor="middle" class="title">Irrigation System Layout</text>
    
    <!-- Legend -->
    <rect x="20" y="50" width="15" height="15" class="zone"/>
    <text x="45" y="62" class="text">Zone</text>
    
    <line x1="20" y1="80" x2="35" y2="80" class="pipe"/>
    <text x="45" y="85" class="text">Pipe</text>
    
    <circle cx="27.5" cy="105" r="7.5" class="equipment"/>
    <text x="45" y="110" class="text">Equipment</text>
'''
        
        # Calculate scaling factors
        max_x = max((zone.get('cluster_center_x', 0) for zone in zones), default=100)
        max_y = max((zone.get('cluster_center_y', 0) for zone in zones), default=100)
        
        scale_x = (width - 100) / max(max_x, 1)
        scale_y = (height - 150) / max(max_y, 1)
        scale = min(scale_x, scale_y)
        
        # Draw zones
        for i, zone in enumerate(zones):
            center_x = zone.get('cluster_center_x', 0) * scale + 50
            center_y = zone.get('cluster_center_y', 0) * scale + 100
            radius = math.sqrt(zone.get('total_area_m2', 0) / math.pi) * scale
            
            svg_content += f'''
    <!-- Zone {i+1} -->
    <circle cx="{center_x}" cy="{center_y}" r="{radius}" class="zone"/>
    <text x="{center_x}" y="{center_y + radius + 15}" text-anchor="middle" class="text">Zone {i+1}</text>
    <text x="{center_x}" y="{center_y + radius + 30}" text-anchor="middle" class="text">{zone.get('total_area_m2', 0):.1f} m²</text>'''
        
        # Draw pipes (simplified representation)
        if pipes:
            for i, pipe in enumerate(pipes):
                start_x = pipe.get('start_x', 0) * scale + 50
                start_y = pipe.get('start_y', 0) * scale + 100
                end_x = pipe.get('end_x', 0) * scale + 50
                end_y = pipe.get('end_y', 0) * scale + 100
                
                svg_content += f'''
    <!-- Pipe {i+1} -->
    <line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" class="pipe"/>'''
        
        # Add system information
        hydraulic_result = system_design.get("hydraulic_calculations", {})
        cost_result = system_design.get("cost_estimation", {})
        
        info_y = height - 80
        svg_content += f'''
    
    <!-- System Information -->
    <text x="20" y="{info_y}" class="text">Total Flow: {hydraulic_result.get('total_flow_lph', 0):.1f} LPH</text>
    <text x="20" y="{info_y + 15}" class="text">System Pressure: {hydraulic_result.get('final_pressure_bar', 0):.2f} bar</text>
    <text x="20" y="{info_y + 30}" class="text">Total Cost: ${cost_result.get('total_cost', 0):.2f}</text>
    <text x="20" y="{info_y + 45}" class="text">Zones: {len(zones)}</text>
'''
        
        svg_content += '</svg>'
        
        return svg_content
    
    def generate_svg_pipe_network(
        self,
        system_design: Dict[str, Any],
        width: int = 800,
        height: int = 600
    ) -> str:
        """
        Generate a detailed SVG of the pipe network.
        
        Args:
            system_design: Complete system design data
            width: SVG width in pixels
            height: SVG height in pixels
            
        Returns:
            SVG content as string
        """
        pipes = system_design.get("pipe_network", [])
        zones = system_design.get("zones", [])
        
        # SVG header
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <style>
            .main-pipe {{ stroke: #0066cc; stroke-width: 4; fill: none; }}
            .secondary-pipe {{ stroke: #3399ff; stroke-width: 2; fill: none; }}
            .zone {{ fill: #e6f3ff; stroke: #0066cc; stroke-width: 1; opacity: 0.5; }}
            .valve {{ fill: #ff6666; stroke: #cc0000; stroke-width: 1; }}
            .text {{ font-family: Arial, sans-serif; font-size: 10px; fill: #333333; }}
            .title {{ font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #333333; }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="{width}" height="{height}" fill="#ffffff"/>
    
    <!-- Title -->
    <text x="{width/2}" y="25" text-anchor="middle" class="title">Pipe Network Diagram</text>
'''
        
        # Calculate scaling
        max_x = max((pipe.get('end_x', 0) for pipe in pipes), default=100)
        max_y = max((pipe.get('end_y', 0) for pipe in pipes), default=100)
        
        scale_x = (width - 100) / max(max_x, 1)
        scale_y = (height - 100) / max(max_y, 1)
        scale = min(scale_x, scale_y)
        
        # Draw zones as background
        for i, zone in enumerate(zones):
            center_x = zone.get('cluster_center_x', 0) * scale + 50
            center_y = zone.get('cluster_center_y', 0) * scale + 80
            radius = math.sqrt(zone.get('total_area_m2', 0) / math.pi) * scale
            
            svg_content += f'''
    <!-- Zone {i+1} Background -->
    <circle cx="{center_x}" cy="{center_y}" r="{radius}" class="zone"/>'''
        
        # Draw pipes
        for i, pipe in enumerate(pipes):
            start_x = pipe.get('start_x', 0) * scale + 50
            start_y = pipe.get('start_y', 0) * scale + 80
            end_x = pipe.get('end_x', 0) * scale + 50
            end_y = pipe.get('end_y', 0) * scale + 80
            
            # Determine pipe class based on diameter or flow
            pipe_class = "main-pipe" if pipe.get('diameter_m', 0) > 0.02 else "secondary-pipe"
            
            svg_content += f'''
    <!-- Pipe {i+1} -->
    <line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" class="{pipe_class}"/>
    <text x="{(start_x + end_x)/2}" y="{(start_y + end_y)/2 - 5}" text-anchor="middle" class="text">Ø{pipe.get('diameter_m', 0)*1000:.0f}mm</text>'''
        
        # Add flow direction arrows
        for pipe in pipes:
            start_x = pipe.get('start_x', 0) * scale + 50
            start_y = pipe.get('start_y', 0) * scale + 80
            end_x = pipe.get('end_x', 0) * scale + 50
            end_y = pipe.get('end_y', 0) * scale + 80
            
            # Calculate arrow
            dx = end_x - start_x
            dy = end_y - start_y
            length = math.sqrt(dx*dx + dy*dy)
            
            if length > 0:
                # Normalize
                dx /= length
                dy /= length
                
                # Arrow head
                arrow_x = end_x - dx * 15
                arrow_y = end_y - dy * 15
                
                # Perpendicular vector for arrow wings
                perp_x = -dy
                perp_y = dx
                
                # Arrow head points
                wing1_x = arrow_x - dx * 10 + perp_x * 5
                wing1_y = arrow_y - dy * 10 + perp_y * 5
                wing2_x = arrow_x - dx * 10 - perp_x * 5
                wing2_y = arrow_y - dy * 10 - perp_y * 5
                
                svg_content += f'''
    <!-- Flow Direction -->
    <polygon points="{arrow_x},{arrow_y} {wing1_x},{wing1_y} {wing2_x},{wing2_y}" fill="#0066cc"/>'''
        
        # Add legend
        legend_y = height - 60
        svg_content += f'''
    
    <!-- Legend -->
    <line x1="20" y1="{legend_y}" x2="40" y2="{legend_y}" class="main-pipe"/>
    <text x="50" y="{legend_y + 4}" class="text">Main Pipe</text>
    
    <line x1="20" y1="{legend_y + 20}" x2="40" y2="{legend_y + 20}" class="secondary-pipe"/>
    <text x="50" y="{legend_y + 24}" class="text">Secondary Pipe</text>
    
    <circle cx="30" cy="{legend_y + 40}" r="5" class="zone"/>
    <text x="50" y="{legend_y + 44}" class="text">Zone</text>
'''
        
        svg_content += '</svg>'
        
        return svg_content 