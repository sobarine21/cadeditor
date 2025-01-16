import streamlit as st
import ezdxf
import matplotlib.pyplot as plt
from io import BytesIO
import os
from pathlib import Path
import google.generativeai as genai

# Configure Gemini AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Title
st.title("AI-Powered CAD Design Analyzer")
st.subheader("Upload, analyze, and receive AI-driven insights to improve your CAD designs.")

# File Upload Section
st.subheader("Upload CAD Files")
uploaded_files = st.file_uploader(
    "Upload CAD design(s) (.dxf format supported)", 
    type=["dxf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.write("### Uploaded Files")
    for file in uploaded_files:
        st.write(f"- {file.name} ({round(file.size / 1024, 2)} KB)")
    
    # Process Each File
    for file in uploaded_files:
        st.write(f"### Analyzing File: {file.name}")
        try:
            # Read the DXF File
            doc = ezdxf.readfile(file)
            msp = doc.modelspace()

            # Extract Layers and Entities
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

            ax.set_title("CAD File Visualization")
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

            # Adjustment Suggestions
            st.subheader("Apply Adjustments (Optional)")
            scale_factor = st.number_input("Scale Factor (e.g., 1.0 for no scaling)", value=1.0, step=0.1)
            rotation_angle = st.number_input("Rotation Angle (degrees)", value=0.0, step=1.0)
            dx = st.number_input("Translate X (units)", value=0.0, step=0.1)
            dy = st.number_input("Translate Y (units)", value=0.0, step=0.1)

            if st.button(f"Apply Adjustments to {file.name}"):
                try:
                    # Apply transformations
                    if scale_factor != 1.0:
                        for entity in msp:
                            if entity.is_supported_dxf_type():
                                entity.scale(scale_factor)
                    if rotation_angle != 0.0:
                        for entity in msp:
                            if entity.is_supported_dxf_type():
                                entity.rotate(rotation_angle)
                    if dx != 0.0 or dy != 0.0:
                        for entity in msp:
                            if entity.is_supported_dxf_type():
                                entity.translate(dx, dy)

                    # Save Adjusted File
                    output_file = f"adjusted_{file.name}"
                    doc.saveas(output_file)
                    st.success(f"Adjustments applied successfully. File saved as {output_file}.")

                    # Provide Download Option
                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="Download Adjusted File",
                            data=f,
                            file_name=output_file,
                            mime="application/dxf"
                        )
                except Exception as e:
                    st.error(f"Error during adjustments: {e}")

        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")
else:
    st.info("Upload one or more CAD files to begin.")

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
