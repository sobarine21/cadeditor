import streamlit as st
import google.generativeai as genai
import tempfile
from stl import mesh
import numpy as np

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("Ever AI - CAD Design Analyzer")
st.write("Use AI to analyze CAD designs and generate responses based on your prompt.")

# File upload for CAD files (STL, STEP, DWG, etc.)
uploaded_file = st.file_uploader("Upload your CAD file", type=["stl", "step", "dwg"])

def calculate_surface_area(cad_mesh):
    """Calculate surface area by summing areas of each triangular face."""
    surface_area = 0.0
    for face in cad_mesh.vectors:
        # Calculate the area of the triangle using cross product
        v1 = face[1] - face[0]
        v2 = face[2] - face[0]
        cross_product = np.cross(v1, v2)
        area = np.linalg.norm(cross_product) / 2.0
        surface_area += area
    return surface_area

def calculate_volume(cad_mesh):
    """Calculate volume using the divergence theorem (also called the 'signed volume')."""
    volume = 0.0
    for face in cad_mesh.vectors:
        v0 = face[0]
        v1 = face[1]
        v2 = face[2]
        volume += np.dot(v0, np.cross(v1, v2)) / 6.0
    return abs(volume)

def analyze_mesh_quality(cad_mesh):
    """Analyze the mesh quality and return a basic assessment."""
    num_faces = len(cad_mesh.vectors)
    num_degenerate_faces = sum(np.isnan(face).any() for face in cad_mesh.vectors)
    return num_faces, num_degenerate_faces

def apply_simplification(cad_mesh):
    """Simplify the mesh by removing small, unnecessary faces or simplifying geometry."""
    simplified_faces = []
    for face in cad_mesh.vectors:
        # Example: Remove very small faces to reduce complexity (threshold: area < 0.001)
        v1 = face[1] - face[0]
        v2 = face[2] - face[0]
        cross_product = np.cross(v1, v2)
        area = np.linalg.norm(cross_product) / 2.0
        if area > 0.001:  # Only keep faces with significant area
            simplified_faces.append(face)
    # Create a new mesh with the simplified faces
    simplified_mesh = mesh.Mesh(np.array(simplified_faces))
    return simplified_mesh

def apply_thickening(cad_mesh, thickness_factor=1.2):
    """Thicken the geometry by expanding the vertices."""
    thickened_faces = []
    for face in cad_mesh.vectors:
        centroid = np.mean(face, axis=0)
        # Move the vertices away from the centroid
        thickened_face = [centroid + (vertex - centroid) * thickness_factor for vertex in face]
        thickened_faces.append(np.array(thickened_face))
    # Create a new mesh with the thickened faces
    thickened_mesh = mesh.Mesh(np.array(thickened_faces))
    return thickened_mesh

if uploaded_file is not None:
    # Temporarily save the uploaded file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_file.getvalue())
    temp_file_path = temp_file.name
    
    # Parse the CAD file based on the extension
    cad_data = ""
    additional_analysis = ""
    modified_mesh = None

    if uploaded_file.name.endswith('.stl'):
        # Load and parse STL file
        try:
            cad_mesh = mesh.Mesh.from_file(temp_file_path)
            if cad_mesh is None or len(cad_mesh.vectors) == 0:
                raise ValueError("The STL file is empty or invalid.")
            
            cad_data = f"STL file loaded with {len(cad_mesh.vectors)} triangular faces."

            # Additional analysis (e.g., mesh properties)
            surface_area = calculate_surface_area(cad_mesh)
            volume = calculate_volume(cad_mesh)
            num_faces, num_degenerate_faces = analyze_mesh_quality(cad_mesh)
            additional_analysis = f"Surface Area: {surface_area:.2f} square units\nVolume: {volume:.2f} cubic units\nFaces: {num_faces} faces\nDegenerate Faces: {num_degenerate_faces}"

            # Suggest improvements
            improvement_suggestions = "We suggest simplifying the mesh and thickening thin areas to improve structural integrity."

            # Apply improvements if selected
            st.write(improvement_suggestions)
            apply_simplification_checkbox = st.checkbox("Simplify the Mesh")
            apply_thickening_checkbox = st.checkbox("Thicken Thin Areas")

            if apply_simplification_checkbox:
                modified_mesh = apply_simplification(cad_mesh)
                st.write("Mesh simplification applied.")
            
            if apply_thickening_checkbox:
                modified_mesh = apply_thickening(cad_mesh)
                st.write("Geometry thickening applied.")

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

    # Provide download option for the revised file
    if modified_mesh is not None:
        # Ensure temporary file is written properly
        output_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".stl").name
        modified_mesh.save(output_file_path)
        st.write(f"Revised mesh has been created. You can download the modified STL file [here](file://{output_file_path}).")

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
