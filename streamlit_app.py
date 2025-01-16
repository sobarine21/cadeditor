import streamlit as st
import ezdxf
from pathlib import Path
import matplotlib.pyplot as plt
from io import BytesIO
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to display CAD file content
def preview_cad(file):
    try:
        doc = ezdxf.readfile(file)
        msp = doc.modelspace()
        
        layers = doc.layers
        entities = [entity.dxftype() for entity in msp]
        
        # Display summary of layers and entities
        st.write("### Layers in File:")
        for layer in layers:
            st.write(f"- {layer.dxf.name}")
        
        st.write("### Entities in File:")
        entity_counts = {entity: entities.count(entity) for entity in set(entities)}
        for entity, count in entity_counts.items():
            st.write(f"- {entity}: {count}")
        
        return doc, msp
    except Exception as e:
        st.error(f"Error reading CAD file: {e}")
        return None, None

# Function to visualize CAD entities
def visualize_cad(msp):
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

    ax.set_title("CAD File Visualization")
    ax.set_aspect("equal")
    plt.legend(loc="upper right")
    st.pyplot(fig)

# Function to process the CAD file
def process_cad(msp, scale_factor=1.0, rotation_angle=0, translation=(0, 0)):
    try:
        log = []
        
        # Apply transformations
        if scale_factor != 1.0:
            log.append(f"Scaled entities by factor {scale_factor}")
            for entity in msp:
                if entity.is_supported_dxf_type():
                    entity.scale(scale_factor)
        
        if rotation_angle != 0:
            log.append(f"Rotated entities by {rotation_angle} degrees")
            for entity in msp:
                if entity.is_supported_dxf_type():
                    entity.rotate(rotation_angle)
        
        if translation != (0, 0):
            dx, dy = translation
            log.append(f"Translated entities by ({dx}, {dy})")
            for entity in msp:
                if entity.is_supported_dxf_type():
                    entity.translate(dx, dy)
        
        return log
    except Exception as e:
        st.error(f"Error processing CAD file: {e}")
        return []

# Streamlit App UI
st.title("Advanced CAD Design Adjuster with AI Assistance")
st.write("Upload, preview, adjust, and download your CAD designs with AI-powered assistance.")

# CAD File Upload Section
st.subheader("Upload and Preview Your CAD File(s)")

uploaded_files = st.file_uploader("Upload CAD design(s) (.dxf format)", type=["dxf"], accept_multiple_files=True)

if uploaded_files:
    st.write("Uploaded Files:")
    for uploaded_file in uploaded_files:
        st.write(f"- {uploaded_file.name}")
        
    # Select a file to preview and process
    selected_file = st.selectbox("Select a file to preview and process:", uploaded_files)
    
    if selected_file:
        doc, msp = preview_cad(selected_file)
        if doc and msp:
            # Visualization
            st.subheader("CAD File Visualization")
            visualize_cad(msp)
            
            # Adjustments Section
            st.subheader("Adjust Your CAD Design")
            scale_factor = st.number_input("Scale Factor (e.g., 1.0 for no scaling)", value=1.0, step=0.1)
            rotation_angle = st.number_input("Rotation Angle (degrees)", value=0.0, step=1.0)
            dx = st.number_input("Translate X (units)", value=0.0, step=0.1)
            dy = st.number_input("Translate Y (units)", value=0.0, step=0.1)
            
            if st.button("Apply Adjustments"):
                with st.spinner("Applying adjustments..."):
                    log = process_cad(msp, scale_factor, rotation_angle, (dx, dy))
                    if log:
                        output_file = f"processed_{selected_file.name}"
                        doc.saveas(output_file)
                        st.success(f"Adjustments applied successfully! File saved as {output_file}")
                        
                        # Download options
                        with open(output_file, "rb") as f:
                            st.download_button(
                                label="Download Processed File",
                                data=f,
                                file_name=Path(output_file).name,
                                mime="application/dxf"
                            )
                        
                        # Download log
                        log_data = "\n".join(log)
                        log_file = BytesIO(log_data.encode())
                        st.download_button(
                            label="Download Adjustment Log",
                            data=log_file,
                            file_name="adjustment_log.txt",
                            mime="text/plain"
                        )

# Gemini AI Integration Section
st.subheader("AI Assistance for CAD Design")
st.write("Use Gemini AI to get suggestions or best practices for your CAD design.")

prompt = st.text_input("Enter your prompt (e.g., 'How to optimize my CAD design?')")

if st.button("Generate AI Response"):
    try:
        # Generate response from Gemini AI
        response = genai.generate_text(prompt=prompt)
        if response and "candidates" in response:
            st.write("AI Response:")
            st.write(response["candidates"][0]["output"])
        else:
            st.warning("No response generated. Try refining your prompt.")
    except Exception as e:
        st.error(f"Error with Gemini AI: {e}")
