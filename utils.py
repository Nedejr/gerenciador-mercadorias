import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_pdf(dataframe):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 40, "Exported Table")
    
    x_offset = 30
    y_offset = height - 60
    line_height = 20
    
    # Draw column headers
    for i, column in enumerate(dataframe.columns):
        c.drawString(x_offset + i * 100, y_offset, column)
    
    # Draw rows
    for index, row in dataframe.iterrows():
        y_offset -= line_height
        for i, value in enumerate(row):
            c.drawString(x_offset + i * 100, y_offset, str(value))
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer