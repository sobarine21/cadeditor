import streamlit as st
import google.generativeai as genai
import os
from io import BytesIO
import tempfile
from stl import mesh  # For .stl file parsing
import numpy as np  # For handling file data and analysis
import ezdxf  # For .dwg file parsing
from OCC.Extend.DataExchange import read_step_file  # For .step file parsing
from OCC.Core.TopoDS import TopoDS_Shape

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("Ever AI - CAD Design Analyzer")
st.write("Use AI to analyze CAD designs and generate responses based on your prompt.")

# File upload for CAD files (STL, STEP, DWG, etc.)
uploaded_file = st.file_uploader("Upload your CAD file", type=["stl", "step", "dwg"])

def parse_step_file(file_path):
    try:
        shape = read_step_file(file_path)
        # Example processing (you can extract more details as needed)
        return f"STEP file parsed with {str(shape)} shape data."
    except Exception as e:
        return f"Error parsing STEP file: {e}"

def parse_dwg_file(file_path):
    try:
        doc = ezdxf.readfile(file_path)
        entities_count = len(doc.entities)  # Counting number of entities (you can extend this)
        return f"DWG file contains {entities_count} entities."
    except Exception as e:
        return f"Error parsing DWG file: {e}"

if uploaded_file is not None:
    # Temporarily save the uploaded file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_file.getvalue())
    temp_file_path = temp_file.name
    
    # Parse the CAD file based on the extension
    cad_data = ""
    
    if uploaded_file.name.endswith('.stl'):
        # Load and parse STL file
        try:
            cad_mesh = mesh.Mesh.from_file(temp_file_path)
            cad_data = f"STL file loaded with {len(cad_mesh.vectors)} triangular faces."
        except Exception as e:
            cad_data = f"Error parsing STL file: {e}"

    elif uploaded_file.name.endswith('.step'):
        cad_data = parse_step_file(temp_file_path)
    
    elif uploaded_file.name.endswith('.dwg'):
        cad_data = parse_dwg_file(temp_file_path)
    
    else:
        cad_data = "Unsupported CAD file format."

    # Show basic CAD data to the user
    st.write(f"File Details: {uploaded_file.name}")
    st.write(f"CAD Analysis: {cad_data}")

    # Prompt input field for specific analysis or queries
    prompt = st.text_input("Enter your prompt (e.g., Analysis, Design Suggestions, etc.):", "")
    
    # Button to generate AI response based on user prompt
    if st.button("Generate AI Response"):
        if prompt:
            try:
                # Load and configure the model (Gemini AI model)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Generate AI response based on user prompt and CAD data
                full_prompt = f"Analyze the following CAD data and answer based on this prompt: '{prompt}'. CAD Data: {cad_data}"
                response = model.generate_content(full_prompt)
                
                # Display AI response
                st.write("AI Response:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error generating response: {e}")
        else:
            st.error("Please enter a prompt to analyze the CAD design.")
else:
    st.info("Please upload a CAD file to begin analysis.")
