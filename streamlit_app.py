import ezdxf
import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai

# Configure Google Generative AI with your API key
genai.configure(api_key="YOUR_API_KEY")

def analyze_and_display_dxf(doc, msp, file_name):
    """Analyze and visualize the DXF file."""
    # Display Layers
    st.write(f"### Layers in {file_name}")
    for layer in doc.layers:
        st.write(f"- {layer.dxf.name}")

    # Count and Display Entities
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
    plt.legend(["Line", "Circle"], loc="upper right")
    st.pyplot(fig)

    # AI Analysis
    st.subheader(f"AI-Powered Insights for {file_name}")
    analysis_prompt = (
        f"This CAD design contains {len(doc.layers)} layers and the following entities: "
        f"{', '.join([f'{entity}: {count}' for entity, count in entity_counts.items()])}. "
        f"Analyze the design and suggest improvements, optimizations, and potential issues to address."
    )

    try:
        response = genai.chat(
            prompt=analysis_prompt,
            max_output_tokens=500,
        )
        if response and "candidates" in response:
            st.write(response["candidates"][0]["content"])
        else:
            st.warning("No AI suggestions generated. Try again later.")
    except Exception as e:
        st.error(f"Error during AI analysis: {e}")

# Main Streamlit app
def main():
    st.title("DXF File Analysis Tool")
    uploaded_file = st.file_uploader("Upload a DXF File", type=["dxf"])

    if uploaded_file:
        try:
            # Read DXF file
            doc = ezdxf.readfile(uploaded_file)
            msp = doc.modelspace()
            file_name = uploaded_file.name

            # Analyze and display the DXF
            analyze_and_display_dxf(doc, msp, file_name)

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
