import streamlit as st
import os
from dotenv import load_dotenv

# MUST BE AT THE TOP
load_dotenv()

# Core engine is now direct_flow.py for stabilized free-tier execution.

st.set_page_config(page_title="Aura-Dev AI", page_icon="🌍")

st.title("🛡️ Aura-Dev: Multimodal Agentic Framework")
st.caption("Inclusive Global Software Development | SDG 9: Industry, Innovation, & Infrastructure")

# Sidebar for Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    model_choice = st.selectbox(
        "Select AI Provider & Model",
        [
            "openrouter/qwen/qwen3.5-35b-a3b",
            "gemini/gemini-3-flash-preview",
            "gemini/gemini-3.1-pro-preview",
            "gemini/gemini-2.0-flash",
            "gemini/gemini-flash-latest",
            "gemini/gemini-pro-latest",
            "openai/gpt-4o",
            "openai/gpt-4o-mini"
        ],
        index=1,
        help="Gemini 3 Flash Preview & 3.1 Pro Preview are now available as primary engines."
    )
    st.info("💎 **High Resilience**: If your choice hits a quota limit, the system will **automatically rotate** through available models to finish your project.")
    st.warning("⚠️ 7-Agent Core Dominion: Robust Error Recovery Active.")

if not os.path.exists("generated_project"):
    os.makedirs("generated_project")

uploaded_file = st.file_uploader("Upload a System Sketch or UI Diagram", type=['png', 'jpg', 'jpeg'])
voice_requirements = st.text_area("Voice/Functional Requirements (What should this app DO?)", 
                                 placeholder="e.g., A low-bandwidth farm tracking app that works offline...")
user_desc = st.text_input("Project Objective (Short name/goal)")

if st.button("🚀 Run Aura-Dev (7-Agent Core Mode)"):
    if uploaded_file and user_desc:
        temp_image_path = "temp_sketch.png"
        with open(temp_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        from crew_flow import run_aura_crew
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.status("Aura-Dev: Orchestrating 7-Agent Core Intelligence (CrewAI)...", expanded=True) as status:
            # Use specific model name for direct SDK
            vision_model_id = model_choice.split("/")[-1]
            
            for update in run_aura_crew(temp_image_path, user_desc, voice_requirements, model_choice):
                if "error" in update:
                    st.error(update["error"])
                    break
                
                status_text.text(update["status"])
                progress_bar.progress(update["progress"])
                
                if "vision" in update:
                    st.session_state.vision = update["vision"]
                    st.write("✅ Vision Agent finished.")

                if "blueprint" in update:
                    st.session_state.blueprint = update["blueprint"]
                    st.write("✅ Architect Agent finished.")
                
                if "files" in update:
                    st.write(f"✅ Lead Developer created {len(update['files'])} files.")
                
                if "debug" in update:
                    st.session_state.debug_report = update["debug"]
                    st.write("✅ Debug Agent finished.")

                if "optimization" in update:
                    st.session_state.opt_report = update["optimization"]
                    st.write("✅ Optimization Agent finished.")

                if "audit" in update:
                    st.session_state.audit = update["audit"]
                    st.session_state.cog_report = update.get("cog_report", "No cognitive audit available.")
                    st.session_state.result = update["final_result"]
                    st.write("✅ Sustainability Agent finished.")
                    st.success("7-Agent Workflow Completed!")
                    status.update(label="Workflow Complete!", state="complete")
    else:
        st.error("Please provide both a sketch and a description.")

# Display Results if available
if "result" in st.session_state:
    result = st.session_state.result
    vision = st.session_state.get("vision", "No vision context available.")
    blueprint = st.session_state.get("blueprint", "No blueprint available.")
    audit = st.session_state.get("audit", "Audit report pending...")
    cog = st.session_state.get("cog_report", "No cognitive audit available.")
    debug = st.session_state.get("debug_report", "No debug issues detected.")
    opt = st.session_state.get("opt_report", "No optimization suggestions.")
    
    st.divider()
    
    col1, col2 = st.columns([8, 2])
    with col1:
        st.subheader("🚀 Transformation Results")
    with col2:
        if st.button("🗑️ Clear Results"):
            for key in ["result", "vision", "blueprint", "audit", "debug_report", "opt_report", "cog_report"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Output Visualization
    tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "👁️ Vision Context",
        "🏗️ Architecture & Blueprint", 
        "💻 Code Implementation", 
        "🛠️ Self-Healing Debug", 
        "🚀 Optimization Report",
        "🧠 DX & Cognitive Audit",
        "🌿 Sustainability Audit"
    ])
    
    with tab0:
        st.markdown(vision)

    with tab1:
        st.markdown(blueprint)
    
    with tab2:
        st.info("Files are located in the `generated_project` directory.")
        
        # Show list of generated files
        if os.path.exists("generated_project"):
            files = []
            for root, _, filenames in os.walk("generated_project"):
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(root, filename), "generated_project")
                    files.append(rel_path)
            
            if files:
                st.write("#### 📂 Generated Files:")
                for f in files:
                    with st.expander(f"📄 {f}"):
                        filepath = os.path.join("generated_project", f)
                        try:
                            with open(filepath, "r", encoding="utf-8") as file:
                                st.code(file.read())
                        except:
                            st.warning(f"Could not read {f}. It might be a binary file.")
            else:
                st.info("No files were detected in the output directory.")

    with tab3:
        st.subheader("🛠️ Autonomous Debugging & Self-Healing Report")
        st.markdown(debug)
    
    with tab4:
        st.subheader("🚀 Performance Optimization Report")
        st.markdown(opt)

    with tab5:
        st.subheader("🧠 Cognitive Load & Developer Experience Audit")
        st.markdown(cog)
    
    with tab6:
        st.subheader("🌿 Green-AI Sustainability Audit")
        st.markdown(audit)
else:
    if not (uploaded_file and user_desc):
        st.info("📝 **Ultimate Mode Active**: Upload a sketch, name your project, and click the Build button above.")
