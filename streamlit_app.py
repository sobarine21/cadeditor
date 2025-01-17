import streamlit as st
import ezdxf
import matplotlib.pyplot as plt
from io import BytesIO
import os
from pathlib import Path
import google.generativeai as genai
import numpy as np
import zipfile
from io import StringIO

# Configure Gemini AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Title
st.title("AI-Powered CAD Design Analyzer")
st.subheader("Upload, analyze, and receive AI-driven insights to improve your CAD designs.")

# File Upload Section
st.subheader("Upload CAD Files")

# Support for multiple file types: DXF, SVG, and ZIP containing DXF files
uploaded_files = st.file_uploader(
    "Upload CAD design(s) (.dxf, .svg formats or .zip with DXF files)", 
    type=["dxf", "svg", "zip"], 
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        st.write(f"### Analyzing File: {file.name}")
        
        try:
            # Handle different file formats (DXF, SVG, ZIP)
            if file.type == "application/zip":
                # Unzip the file and process DXF files within it
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    zip_ref.extractall("temp_zip")
                    # Process each DXF file inside the ZIP
                    for file_name in zip_ref.namelist():
                        if file_name.endswith(".dxf"):
                            st.write(f"Processing {file_name} inside the ZIP...")
                            dxf_file_path = os.path.join("temp_zip", file_name)
                            doc = ezdxf.readfile(dxf_file_path)
                            msp = doc.modelspace()
                            analyze_and_display_dxf(doc, msp, file_name)
            elif file.type == "image/svg+xml":
                # Process SVG file
                st.write("Processing SVG file...")
                process_svg(file)
            elif file.type == "application/dxf":
                # Process DXF file
                doc = ezdxf.readfile(file)
                msp = doc.modelspace()
                analyze_and_display_dxf(doc, msp, file.name)
        
        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")

else:
    st.info("Upload one or more CAD files to begin.")

def analyze_and_display_dxf(doc, msp, file_name):
    """Analyze and visualize the DXF file"""
    
    # Layers and Entities
    st.write("#### Layers in the File")
    for layer in doc.layers:
        st.write(f"- {layer.dxf.name}")

    st.write("#### Entities in the File")
    entities = [entity.dxftype() for entity in msp]
    entity_counts = {entity: entities.count(entity) for entity in set(entities)}
    for entity, count in entity_counts.items():
        st.write(f"- {entity}: {count}")

    # Visualization
    st.write("#### Visualization")
    fig, ax = plt.subplots(figsize=(10, 6))
    for entity in msp:
        if entity.dxftype() == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            ax.plot([start.x, end.x], [start.y, end.y], color='blue', label="Line")
        elif entity.dxftype() == "CIRCLE":
            center = entity.dxf.center
            radius = entity.dxf.radius
            circle = plt.Circle((center.x, center.y), radius, color='red', fill=False)
            ax.add_patch(circle)

    ax.set_title(f"CAD File Visualization - {file_name}")
    ax.set_aspect("equal")
    plt.legend(loc="upper right")
    st.pyplot(fig)

    # AI Analysis and Suggestions
    st.subheader("AI-Powered Insights")
    analysis_prompt = (
        f"This CAD design contains {len(doc.layers)} layers and the following entities: "
        f"{', '.join([f'{entity}: {count}' for entity, count in entity_counts.items()])}. "
        f"Analyze the design and suggest improvements, optimizations, and potential issues to address."
    )

    try:
        # Use Gemini AI to Analyze the Design
        response = genai.generate_content(
            model="gemini-1.5-flash",
            prompt=analysis_prompt,
            max_output_tokens=500
        )
        if response and response.candidates:
            st.write("### AI Suggestions")
            st.write(response.candidates[0]["output"])
        else:
            st.warning("No suggestions generated. Try again later.")
    except Exception as e:
        st.error(f"Error during AI analysis: {e}")

def process_svg(file):
    """Process and display SVG files"""
    # For simplicity, let's just display the raw SVG content for now.
    # You can extend this to render the SVG as an image or analyze its contents.
    try:
        svg_content = file.getvalue().decode("utf-8")
        st.write("### SVG File Content")
        st.code(svg_content, language='xml')
    except Exception as e:
        st.error(f"Error processing SVG file: {e}")

# General AI Prompt Section
st.subheader("General AI Assistance")
general_prompt = st.text_input("Enter your prompt (e.g., 'How to optimize CAD designs for 3D printing?')")

if st.button("Generate AI Response"):
    try:
        response = genai.generate_content(
            model="gemini-1.5-flash",
            prompt=general_prompt,
            max_output_tokens=300
        )
        if response and response.candidates:
            st.write("### AI Response")
            st.write(response.candidates[0]["output"])
        else:
            st.warning("No response generated. Try refining your prompt.")
    except Exception as e:
        st.error(f"Error with Gemini AI: {e}")

# Additional Features Implemented:
# 1. **ZIP File Support**: Upload and extract DXF files from ZIP archives.
# 2. **SVG File Support**: Display raw SVG content or process SVG files for further analysis.
# 3. **Batch Processing**: Allows for batch processing of multiple DXF and SVG files, including handling ZIP archives containing multiple DXF files.
# 4. **General AI Assistance**: Still includes the AI-powered suggestions for general prompts related to CAD design optimization and other topics.
# 5. **File-Specific Processing**: Each file type (DXF, SVG, ZIP) is processed accordingly with separate handlers for different file formats.
