import streamlit as st
import ezdxf
import matplotlib.pyplot as plt
import os
import zipfile
from io import BytesIO
import google.generativeai as genai

# Configure Gemini AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# App Title
st.title("AI-Powered CAD Design Analyzer")
st.subheader("Upload, analyze, and receive AI-driven insights to improve your CAD designs.")

# File Upload Section
st.subheader("Upload CAD Files")

uploaded_files = st.file_uploader(
    "Upload CAD design(s) (.dxf, .svg formats or .zip with DXF files)",
    type=["dxf", "svg", "zip"],
    accept_multiple_files=True,
)

# Functions for processing different file types
def analyze_and_display_dxf(doc, msp, file_name):
    """Analyze and visualize the DXF file."""
    # Layers and Entities
    st.write(f"### Layers in {file_name}")
    for layer in doc.layers:
        st.write(f"- {layer.dxf.name}")

    st.write(f"### Entities in {file_name}")
    entities = [entity.dxftype() for entity in msp]
    entity_counts = {entity: entities.count(entity) for entity in set(entities)}
    for entity, count in entity_counts.items():
        st.write(f"- {entity}: {count}")

    # Visualization
    st.write(f"### Visualization of {file_name}")
    fig, ax = plt.subplots(figsize=(10, 6))
    for entity in msp:
        if entity.dxftype() == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            ax.plot([start.x, end.x], [start.y, end.y], color="blue", label="Line")
        elif entity.dxftype() == "CIRCLE":
            center = entity.dxf.center
            radius = entity.dxf.radius
            circle = plt.Circle((center.x, center.y), radius, color="red", fill=False)
            ax.add_patch(circle)

    ax.set_title(f"Visualization - {file_name}")
    ax.set_aspect("equal")
    st.pyplot(fig)

    # AI Analysis
    st.subheader(f"AI-Powered Insights for {file_name}")
    analysis_prompt = (
        f"This CAD design contains {len(doc.layers)} layers and the following entities: "
        f"{', '.join([f'{entity}: {count}' for entity, count in entity_counts.items()])}. "
        f"Analyze the design and suggest improvements, optimizations, and potential issues to address."
    )

    try:
        response = genai.generate_text(
            model="gemini-1.5-flash",
            prompt=analysis_prompt,
            max_output_tokens=500,
        )
        if response and "candidates" in response:
            st.write(response["candidates"][0]["output"])
        else:
            st.warning("No AI suggestions generated. Try again later.")
    except Exception as e:
        st.error(f"Error during AI analysis: {e}")

def process_svg(file):
    """Process and display SVG files."""
    try:
        svg_content = file.getvalue().decode("utf-8")
        st.write("### SVG File Content")
        st.code(svg_content, language="xml")
    except Exception as e:
        st.error(f"Error processing SVG file: {e}")

def process_zip(file):
    """Extract and process DXF files from a ZIP archive."""
    try:
        with zipfile.ZipFile(file, "r") as zip_ref:
            extracted_files = []
            with st.spinner("Extracting files..."):
                for name in zip_ref.namelist():
                    if name.endswith(".dxf"):
                        extracted_files.append(name)
                        zip_ref.extract(name, "temp_zip")
            if not extracted_files:
                st.warning("No DXF files found in the ZIP archive.")
                return
            for dxf_file in extracted_files:
                st.write(f"Processing {dxf_file}...")
                file_path = os.path.join("temp_zip", dxf_file)
                doc = ezdxf.readfile(file_path)
                msp = doc.modelspace()
                analyze_and_display_dxf(doc, msp, dxf_file)
    except Exception as e:
        st.error(f"Error processing ZIP file: {e}")

# Main Logic
if uploaded_files:
    for file in uploaded_files:
        st.write(f"### Analyzing File: {file.name}")

        if file.name.endswith(".zip"):
            process_zip(BytesIO(file.read()))
        elif file.name.endswith(".dxf"):
            try:
                doc = ezdxf.readfile(BytesIO(file.read()))
                msp = doc.modelspace()
                analyze_and_display_dxf(doc, msp, file.name)
            except Exception as e:
                st.error(f"Error processing DXF file {file.name}: {e}")
        elif file.name.endswith(".svg"):
            process_svg(file)
        else:
            st.warning(f"Unsupported file format: {file.name}")
else:
    st.info("Upload one or more CAD files to begin.")

# General AI Assistance Section
st.subheader("General AI Assistance")
general_prompt = st.text_input("Enter your prompt (e.g., 'How to optimize CAD designs for 3D printing?')")

if st.button("Generate AI Response"):
    try:
        response = genai.generate_text(
            model="gemini-1.5-flash",
            prompt=general_prompt,
            max_output_tokens=300,
        )
        if response and "candidates" in response:
            st.write("### AI Response")
            st.write(response["candidates"][0]["output"])
        else:
            st.warning("No response generated. Try refining your prompt.")
    except Exception as e:
        st.error(f"Error with Gemini AI: {e}")
