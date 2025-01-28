import streamlit as st
import google.generativeai as genai
from datetime import datetime
import base64

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.title("Ever AI - Text to CAD Design")
st.write("Use generative AI to create CAD designs from text descriptions.")

# Initialize session state for storing history and designs
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'designs' not in st.session_state:
    st.session_state['designs'] = []

# Function to create a download link for CAD design
def create_download_link(file_content, file_name):
    b64 = base64.b64encode(file_content.encode()).decode()
    href = f'<a href="data:file/cad;base64,{b64}" download="{file_name}">Download CAD Design</a>'
    return href

# Prompt input field
prompt = st.text_input("Enter your design description:", "A modern, minimalist chair")

# Button to generate response and CAD design
if st.button("Generate CAD Design"):
    try:
        # Load and configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate response from the model
        response = model.generate_content(prompt)
        
        # Display response in Streamlit
        st.write("Generated Description:")
        st.write(response.text)
        
        # Save prompt and response to history
        st.session_state['history'].append({"prompt": prompt, "response": response.text, "timestamp": str(datetime.now())})
        
        # Placeholder for generating CAD design (replace with actual CAD generation logic)
        cad_design = {
            "description": response.text,
            "design_data": "CAD design data placeholder",
            "timestamp": str(datetime.now())
        }
        st.session_state['designs'].append(cad_design)
        
        st.success("CAD Design Generated Successfully!")
        
    except Exception as e:
        st.error(f"Error: {e}")

# Display history of prompts and responses
st.write("History:")
for entry in st.session_state['history']:
    st.write(f"Prompt: {entry['prompt']}")
    st.write(f"Response: {entry['response']}")
    st.write(f"Timestamp: {entry['timestamp']}")
    st.write("---")

# Display generated CAD designs
st.write("Generated CAD Designs:")
for i, design in enumerate(st.session_state['designs']):
    st.write(f"Description: {design['description']}")
    st.write(f"Timestamp: {design['timestamp']}")
    st.write("CAD Design Data:", design['design_data'])
    # Create a download link for the CAD design
    download_link = create_download_link(design['design_data'], f"cad_design_{i}.cad")
    st.markdown(download_link, unsafe_allow_html=True)
    st.write("---")

# Placeholder for additional design and modeling features
st.write("Additional Features:")
st.write("1. Zoom and Pan functionality for CAD designs")
st.write("2. Basic editing tools to modify the designs")
st.write("3. Export designs in various formats (e.g., DWG, DXF)")
st.write("4. 3D viewing capabilities")
st.write("5. Design validation and error checks")
st.write("6. Collaborative editing and sharing")
st.write("7. Template library for common designs")
st.write("8. Import external CAD files")
st.write("9. AI-based design suggestions")
st.write("10. Measurement tools for distances, angles, and areas")
st.write("11. Annotations and notes on designs")
st.write("12. Layer management for design elements")
st.write("13. Version control for design iterations")
st.write("14. Notifications for design updates")
st.write("15. Real-time data synchronization")
