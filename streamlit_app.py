import streamlit as st
import google.generativeai as genai
import tempfile
from stl import mesh
import numpy as np
from math import pi

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("Ever AI - CAD Design Analyzer")
st.write("Use AI to analyze CAD designs and generate responses based on your prompt.")

# File upload for CAD files (STL, STEP, DWG, etc.)
uploaded_file = st.file_uploader("Upload your CAD file", type=["stl", "step", "dwg"])

def calculate_mesh_properties(cad_mesh):
    """Calculate and return basic mesh properties: volume and surface area"""
    volume = cad_mesh.get_mass_properties()[0]  # Volume of the mesh
    surface_area = cad_mesh.get_area()  # Surface area of the mesh
    return volume, surface_area

def analyze_mesh_quality(cad_mesh):
    """Analyze the mesh quality and return a basic assessment."""
    num_faces = len(cad_mesh.vectors)
    num_degenerate_faces = sum(np.isnan(face).any() for face in cad_mesh.vectors)
    return num_faces, num_degenerate_faces

if uploaded_file is not None:
    # Temporarily save the uploaded file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_file.getvalue())
    temp_file_path = temp_file.name
    
    # Parse the CAD file based on the extension
    cad_data = ""
    additional_analysis = ""

    if uploaded_file.name.endswith('.stl'):
        # Load and parse STL file
        try:
            cad_mesh = mesh.Mesh.from_file(temp_file_path)
            cad_data = f"STL file loaded with {len(cad_mesh.vectors)} triangular faces."

            # Additional analysis (e.g., mesh properties)
            volume, surface_area = calculate_mesh_properties(cad_mesh)
            num_faces, num_degenerate_faces = analyze_mesh_quality(cad_mesh)
            additional_analysis = f"Volume: {volume:.2f} cubic units\nSurface Area: {surface_area:.2f} square units\nFaces: {num_faces} faces\nDegenerate Faces: {num_degenerate_faces}"

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
    
    if additional_analysis:
        st.write("Advanced Analysis:")
        st.write(additional_analysis)

    # Prompt input field for specific analysis or queries
    prompt = st.text_input("Enter your prompt (e.g., Analysis, Design Suggestions, etc.):", "")
    
    # Button to generate AI response based on user prompt
    if st.button("Generate AI Response"):
        if prompt:
            try:
                # Load and configure the model (Gemini AI model)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Generate AI response based on user prompt and CAD data
                full_prompt = f"Analyze the following CAD data and answer based on this prompt: '{prompt}'. CAD Data: {cad_data} Additional Analysis: {additional_analysis}"
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
