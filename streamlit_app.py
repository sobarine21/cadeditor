import streamlit as st
import google.generativeai as genai
import tempfile
from stl import mesh  # Correct import from numpy-stl
import numpy as np  # For handling file data and analysis

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("Ever AI - CAD Design Analyzer")
st.write("Use AI to analyze CAD designs and generate responses based on your prompt.")

# File upload for CAD files (STL, STEP, DWG, etc.)
uploaded_file = st.file_uploader("Upload your CAD file", type=["stl", "step", "dwg"])

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
        cad_data = "STEP file parsing is not implemented yet. You can implement a STEP parser based on libraries such as `pythonOCC`."
    
    elif uploaded_file.name.endswith('.dwg'):
        cad_data = "DWG file parsing is not implemented yet. You can implement DWG parsing using libraries such as `ezdxf`."
    
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
