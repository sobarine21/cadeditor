import streamlit as st
import ezdxf
import matplotlib.pyplot as plt
import os
import zipfile
from io import BytesIO
import google.generativeai as genai

# Configure Gemini AI with API key
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

# Analyze DXF Files
def analyze_and_display_dxf(doc, msp, file_name):
    """Analyze and visualize the DXF file."""
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
            ax.plot([start.x, end.x], [start.y, end.y], color="blue")
        elif entity.dxftype() == "CIRCLE":
            center = entity.dxf.center
            radius = entity.dxf.radius
            circle = plt.Circle((center.x, center.y), radius, color="red", fill=False)
            ax.add_patch(circle)

    ax.set_title(f"Visualization - {file_name}")
    ax.set_aspect("equal")
    plt.legend(["Lines", "Circles"], loc="upper right")
    st.pyplot(fig)

    # AI Analysis
    st.subheader(f"AI-Powered Insights for {file_name}")
    analysis_prompt = (
        f"This CAD design contains {len(doc.layers)} layers and the following entities: "
        f"{', '.join([f'{entity}: {count}' for entity, count in entity_counts.items()])}. "
        f"Analyze the design and suggest improvements, optimizations, and potential issues to address."
    )

    try:
        # Correct API call using generate() instead of generate_text
        response = genai.generate(
            model="gemini-2.0-flash-exp",  # You can adjust the model name here
            prompt=analysis_prompt,
            max_output_tokens=500,
        )

        if response and "candidates" in response:
            st.write(response["candidates"][0]["output"])
        else:
            st.warning("No AI suggestions generated. Try again later.")
    except Exception as e:
        st.error(f"Error during AI analysis: {e}")

# Process SVG Files
def process_svg(file):
    """Process and display SVG files."""
    try:
        svg_content = file.getvalue().decode("utf-8")
        st.write("### SVG File Content")
        st.code(svg_content, language="xml")
    except Exception as e:
        st.error(f"Error processing SVG file: {e}")

# Process ZIP Archives
def process_zip(file):
    """Extract and process DXF files from a ZIP archive."""
    try:
        with zipfile.ZipFile(file, "r") as zip_ref:
            extracted_files = []
            with st.spinner("Extracting files..."):
                for name in zip_ref.namelist():
