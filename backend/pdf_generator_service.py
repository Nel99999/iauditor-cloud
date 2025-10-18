"""
PDF Report Generation Service for Inspections
Generates professional inspection reports with photos, charts, and tables
"""

from io import BytesIO
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, Image, PageBreak, KeepTogether, PageTemplate, Frame
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


class InspectionPDFGenerator:
    """Service for generating inspection report PDFs"""
    
    def __init__(self, page_size=letter):
        """Initialize the PDF generator"""
        self.page_size = page_size
        self.width, self.height = page_size
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Configure custom paragraph styles"""
        # Report title
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=15,
        ))
        
        # Finding text
        self.styles.add(ParagraphStyle(
            name='Finding',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#c0392b'),
            leftIndent=20,
        ))
        
    def generate_inspection_report(
        self,
        execution_data: dict,
        template_data: dict,
    ) -> BytesIO:
        """
        Generate inspection report PDF
        
        Args:
            execution_data: Inspection execution dict
            template_data: Inspection template dict
            
        Returns:
            BytesIO containing PDF data
        """
        buffer = BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_size,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch,
        )
        
        # Build content
        story = []
        
        # Header
        story.extend(self._create_header(execution_data, template_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Metadata table
        story.extend(self._create_metadata_table(execution_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Questions and answers
        story.extend(self._create_questions_section(execution_data, template_data))
        
        # Findings
        if execution_data.get('findings'):
            story.append(Spacer(1, 0.3*inch))
            story.extend(self._create_findings_section(execution_data))
        
        # Summary
        if execution_data.get('notes'):
            story.append(Spacer(1, 0.3*inch))
            story.extend(self._create_summary_section(execution_data))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    def _create_header(self, execution_data: dict, template_data: dict) -> List:
        """Create report header"""
        elements = []
        
        # Title
        title = Paragraph(
            f"Inspection Report<br/>{template_data.get('name', 'Inspection')}",
            self.styles['ReportTitle']
        )
        elements.append(title)
        
        # Status badge
        status = execution_data.get('status', 'completed').upper()
        passed = execution_data.get('passed')
        
        if passed is not None:
            status_text = "PASSED" if passed else "FAILED"
            status_color = colors.green if passed else colors.red
        else:
            status_text = status
            status_color = colors.grey
            
        status_para = Paragraph(
            f'<para alignment="center"><font color="{status_color}" size="16"><b>{status_text}</b></font></para>',
            self.styles['Normal']
        )
        elements.append(status_para)
        
        return elements
        
    def _create_metadata_table(self, execution_data: dict) -> List:
        """Create metadata table"""
        elements = []
        
        # Prepare data
        data = [
            ['Inspector:', execution_data.get('inspector_name', 'N/A')],
            ['Date:', execution_data.get('started_at', '')[:10]],
            ['Status:', execution_data.get('status', 'N/A')],
        ]
        
        if execution_data.get('score') is not None:
            data.append(['Score:', f"{execution_data['score']}%"])
            
        if execution_data.get('duration_minutes'):
            data.append(['Duration:', f"{execution_data['duration_minutes']} minutes"])
            
        if execution_data.get('location'):
            loc = execution_data['location']
            data.append(['Location:', f"Lat: {loc.get('lat', 'N/A')}, Lng: {loc.get('lng', 'N/A')}"])
        
        # Create table
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(table)
        return elements
        
    def _create_questions_section(self, execution_data: dict, template_data: dict) -> List:
        """Create questions and answers section"""
        elements = []
        
        heading = Paragraph('Inspection Details', self.styles['SectionHeading'])
        elements.append(heading)
        
        questions = template_data.get('questions', [])
        answers_dict = {a['question_id']: a for a in execution_data.get('answers', [])}
        
        # Create table data
        table_data = [['#', 'Question', 'Answer', 'Notes']]
        
        for idx, question in enumerate(questions, 1):
            answer = answers_dict.get(question['id'], {})
            
            # Format answer
            answer_value = answer.get('answer', 'N/A')
            if isinstance(answer_value, bool):
                answer_value = 'Yes' if answer_value else 'No'
            
            # Notes
            notes = answer.get('notes', '-') or '-'
            
            table_data.append([
                str(idx),
                Paragraph(question.get('question_text', ''), self.styles['Normal']),
                Paragraph(str(answer_value), self.styles['Normal']),
                Paragraph(notes[:50], self.styles['Normal'])
            ])
        
        # Create table
        table = Table(
            table_data,
            colWidths=[0.5*inch, 3*inch, 1.5*inch, 1.5*inch]
        )
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            # General
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        
        elements.append(table)
        return elements
        
    def _create_findings_section(self, execution_data: dict) -> List:
        """Create findings section"""
        elements = []
        
        heading = Paragraph('Findings & Issues', self.styles['SectionHeading'])
        elements.append(heading)
        
        findings = execution_data.get('findings', [])
        
        for idx, finding in enumerate(findings, 1):
            finding_para = Paragraph(
                f'{idx}. {finding}',
                self.styles['Finding']
            )
            elements.append(finding_para)
            elements.append(Spacer(1, 0.05*inch))
        
        return elements
        
    def _create_summary_section(self, execution_data: dict) -> List:
        """Create summary notes section"""
        elements = []
        
        heading = Paragraph('Summary Notes', self.styles['SectionHeading'])
        elements.append(heading)
        
        notes = Paragraph(
            execution_data.get('notes', ''),
            self.styles['Normal']
        )
        elements.append(notes)
        
        return elements
