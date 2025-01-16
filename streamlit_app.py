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
st.title("Advanced CAD Design Adjuster with AI")
st.subheader("Upload, analyze, adjust, and optimize your CAD designs with the power of AI.")

# File Upload Section
st.subheader("Upload CAD Files")
uploaded_files = st.file_uploader(
    "Upload CAD design(s) (.dxf, .dwg, .svg formats supported)", 
    type=["dxf", "dwg", "svg"], 
    accept_multiple_files=True
)

if uploaded_files:
    # Display File Metadata
    st.write("### Uploaded Files")
    file_metadata = []
    for file in uploaded_files:
        file_metadata.append({"File Name": file.name, "Size (KB)": round(file.size / 1024, 2), "Type": Path(file.name).suffix})
    
    st.dataframe(file_metadata)

    # Process Each File
    for file in uploaded_files:
        st.write(f"### Preview: {file.name}")
        file_ext = Path(file.name).suffix

        # Handle DXF Files
        if file_ext == ".dxf":
            try:
                doc = ezdxf.readfile(file)
                msp = doc.modelspace()

                # Preview Layers and Entities
                st.write("#### Layers in the File")
                for layer in doc.layers:
                    st.write(f"- {layer.dxf.name}")

                st.write("#### Entities in the File")
                entities = [entity.dxftype() for entity in msp]
                entity_counts = {entity: entities.count(entity) for entity in set(entities)}
                for entity, count in entity_counts.items():
                    st.write(f"- {entity}: {count}")

                # Visualize Basic Entities
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
                st.subheader("AI-Powered Suggestions")
                prompt = f"Analyze the CAD design with {len(doc.layers)} layers and entities like {list(entity_counts.keys())}. Suggest improvements or issues."
                try:
                    response = genai.generate_text(prompt=prompt)
                    if response and "candidates" in response:
                        st.write("#### AI Suggestions")
                        st.write(response["candidates"][0]["output"])
                    else:
                        st.warning("No suggestions generated. Try refining the prompt.")
                except Exception as e:
                    st.error(f"Error with Gemini AI: {e}")

                # Adjustments Section
                st.subheader("Adjust Your CAD Design")
                scale_factor = st.number_input("Scale Factor (e.g., 1.0 for no scaling)", value=1.0, step=0.1)
                rotation_angle = st.number_input("Rotation Angle (degrees)", value=0.0, step=1.0)
                dx = st.number_input("Translate X (units)", value=0.0, step=0.1)
                dy = st.number_input("Translate Y (units)", value=0.0, step=0.1)

                if st.button(f"Apply Adjustments to {file.name}"):
                    try:
                        # Apply transformations
                        log = []
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

                        if (dx, dy) != (0.0, 0.0):
                            log.append(f"Translated entities by ({dx}, {dy})")
                            for entity in msp:
                                if entity.is_supported_dxf_type():
                                    entity.translate(dx, dy)

                        # Save the Adjusted File
                        output_file = f"processed_{file.name}"
                        doc.saveas(output_file)
                        st.success(f"Adjustments applied successfully! File saved as {output_file}")

                        # Download Options
                        with open(output_file, "rb") as f:
                            st.download_button(
                                label="Download Adjusted File",
                                data=f,
                                file_name=Path(output_file).name,
                                mime="application/dxf"
                            )

                        # Log Download
                        log_data = "\n".join(log)
                        log_file = BytesIO(log_data.encode())
                        st.download_button(
                            label="Download Adjustment Log",
                            data=log_file,
                            file_name=f"log_{file.name}.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Error applying adjustments: {e}")

            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")
        else:
            st.warning(f"File format {file_ext} not supported for visualization. Supported formats: .dxf")

else:
    st.info("Upload one or more CAD files to begin.")

# Gemini AI General Analysis Section
st.subheader("AI Assistance for CAD Design")
st.write("Use AI to get suggestions or best practices for your CAD design.")

general_prompt = st.text_input("Enter your prompt (e.g., 'How to optimize my CAD designs?')")

if st.button("Generate AI Response"):
    try:
        response = genai.generate_text(prompt=general_prompt)
        if response and "candidates" in response:
            st.write("#### AI Response")
            st.write(response["candidates"][0]["output"])
        else:
            st.warning("No response generated. Try refining your prompt.")
    except Exception as e:
        st.error(f"Error with Gemini AI: {e}")
