import streamlit as st
import ezdxf
import matplotlib.pyplot as plt
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
        # Correct API call using generate_text()
        response = genai.generate_text(
            model="gemini-2",  # You can adjust the model name here
            prompt=analysis_prompt,
            max_output_tokens=500,
        )

        if response and response.candidates:
            st.write(response.candidates[0].output)
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
                # Debugging: List all files in ZIP
                file_names = zip_ref.namelist()
                st.write("Files in ZIP:", file_names)
                
                for name in file_names:
                    if name.endswith(".dxf"):
                        extracted_files.append(name)
                        with zip_ref.open(name) as extracted_file:
                            doc = ezdxf.readfile(BytesIO(extracted_file.read()))
                            msp = doc.modelspace()
                            analyze_and_display_dxf(doc, msp, name)

            if not extracted_files:
                st.warning("No DXF files found in the ZIP archive.")
    except zipfile.BadZipFile:
        st.error(f"Error: The ZIP file is not a valid ZIP archive.")
    except FileNotFoundError:
        st.error(f"Error: A file within the ZIP archive could not be found.")
    except Exception as e:
        st.error(f"Error extracting ZIP file: {e}")

# Main App Logic
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name

        if file_name.endswith(".dxf"):
            try:
                # Process DXF File
                doc = ezdxf.readfile(BytesIO(uploaded_file.read()))
                msp = doc.modelspace()
                analyze_and_display_dxf(doc, msp, file_name)
            except Exception as e:
                st.error(f"Error processing {file_name}: {e}")
        elif file_name.endswith(".svg"):
            # Process SVG File
            process_svg(uploaded_file)
        elif file_name.endswith(".zip"):
            # Process ZIP File
            process_zip(uploaded_file)
        else:
            st.warning(f"Unsupported file format: {file_name}")
else:
    st.info("Please upload at least one file to begin.")
