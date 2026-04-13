# Knowledge_Interface.py

from utils import os, st
from UI_model_select import render_create_DB_select
from config import VECTOR_DB_DIR

from RAG_Embedding import load_metadata, delete_files_from_db, create_new_vector_db, delete_vector_db, rebuild_vector_db

# Initialize user's last action state (used to trigger UI updates)
if "last_action" not in st.session_state:
    st.session_state.last_action = None  # Can be add/delete/create/delete_db

# Set page to wide layout and create left/right columns
st.set_page_config(layout="wide")
col_left, col_right = st.columns([1, 1])

# ===== Left: Create new database =====
with col_left:
    st.header("📂 Create Knowledge Base")

    # Model selection (e.g., select image processing model gemma3:27b, etc.)
    render_create_DB_select()

    # Upload files to create a new database
    uploaded_files = st.file_uploader(
        "**Upload PDF, Word, PPT, Media, Text or Image files**",
        type=["pdf", "ppt", "pptx", "docx", "txt", "png", "jpg", "jpeg", "mp3", "mp4"],
        accept_multiple_files=True,
        key="new_db_files"
    )

    # Database naming input field
    db_name = st.text_input("**Name the database (English or numbers)**", key="new_db_name")
    build_btn = st.button("🚧 Build Vector Database", key="build_new_db")

    # Create new database and process vectorization
    if build_btn:
        if not db_name:
            st.warning("Please enter a database name.")
        elif not uploaded_files:
            st.warning("Please upload files first.")
        else:
            try:
                with st.spinner("Creating vector database..."):
                    chunk_size = st.session_state.model_settings["chunk_size"]
                    chunk_overlap = st.session_state.model_settings["chunk_overlap"]
                    count = create_new_vector_db(db_name, uploaded_files, st.session_state.model_settings["img_model"], first_time=True, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                st.success(f"✅ Database '{db_name}' created successfully with {count} chunks.")
                st.session_state.last_action = "create"
                st.stop()
            except FileExistsError:
                st.error(f"❗ Database '{db_name}' already exists, please choose a different name.")


# ===== Right: Manage Knowledge Base =====
with col_right:
    st.header("📂 Manage Knowledge Base")
    chunk_size = st.session_state.model_settings["chunk_size"]
    chunk_overlap = st.session_state.model_settings["chunk_overlap"]
    
    # Get list of existing database folders
    db_list = sorted([d for d in os.listdir(VECTOR_DB_DIR) if os.path.isdir(os.path.join(VECTOR_DB_DIR, d))])
    selected_db = None

    # Database selection section
    with st.expander("📚 **Existing Database List**", expanded=True):
        if db_list:
            selected_db = st.selectbox("**Select a database to view details and manage**", [""] + db_list)
        else:
            st.write("No databases have been created yet.")
    
    # If the user selected a database, show its details and management options
    if selected_db:
        meta = load_metadata(selected_db)  # Read metadata.json
        st.markdown(f"### Database: `{selected_db}`")
        st.write("Last edited:", meta.get("last_edit", "Unknown"))
        st.write("Chunk size:", meta.get("chunk_size", 0))

        files = meta.get("files", [])
        st.write("Included files:")
        

        if files:
            # Create a dict to store checkbox status
            selected_to_delete = {}
            for idx, f_name in enumerate(files, start=1):
                col1, col2 = st.columns([0.1, 0.9])
                col1.markdown(f"{idx}.")
                selected_to_delete[f_name] = col2.checkbox(
                    label=f_name,
                    key=f"checkbox_{f_name}"
                )

            # Batch delete button
            if st.button("❌ Delete Selected Files"):
                files_to_delete = [f for f, checked in selected_to_delete.items() if checked]
                count = delete_files_from_db(selected_db, files_to_delete, chunk_overlap)
                st.success(f"✅ Database '{selected_db}' updated successfully, {count} chunks remaining.")     
        else:
            st.write("(No files currently)")

    # ===== Delete entire database function =====
        with st.expander("🗑️ Delete Entire Database", expanded=False):
            confirmed = st.checkbox("⚠️ Confirm deletion of this database. This operation cannot be undone!", key="confirm_delete_db")
            if st.button("Delete Database", key="delete_db_btn"):
                if not confirmed:
                    st.warning("Please check the confirmation box first.")
                else:
                    success = delete_vector_db(selected_db)
                    if success:
                        st.success(f"✅ Database `{selected_db}` has been successfully deleted!")
                        st.session_state.last_action = "delete_db"
                        st.stop()
                    else:
                        st.error("❌ Failed to delete database, please try again later.")
    
        # ===== Add files to existing database function =====
        st.markdown("### ➕ Add Files to This Database")
        uploaded_files = st.file_uploader(
            "**Select Files**",
            type=["pdf", "ppt", "pptx", "docx", "txt", "png", "jpg", "jpeg", "mp3", "mp4"],
            accept_multiple_files=True,
            key="add_files"
        )

        # Rebuild vector database with added files
        if st.button("🚀 Add and Rebuild Vector Database", key="upload_new_files"):
            if not uploaded_files:
                st.warning("Please upload files first.")
            else:
                with st.spinner("Rebuilding vector database..."):
                    count = rebuild_vector_db(selected_db, chunk_overlap, uploaded_files)
                st.success(f"✅ Build complete, {count} chunks in total.")
                st.session_state.last_action = "add"
                st.stop()