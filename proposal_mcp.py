from typing import Any
import os
import datetime
from mcp.server.fastmcp import FastMCP
from AIA_ProposalAgent.prompt_func import *
from AIA_ProposalAgent.projectinfo import load_project_info, clear_project_info
from AIA_ProposalAgent.main import extract_project_info, create_word_doc
from blob import upload_blob, download_blob

# Initialize FastMCP server
mcp = FastMCP("Proposal Agent")

@mcp.tool()
def get_generated_proposal(user_input: str) -> str:
    doc_path = None
    try:
        # Clean the input
        cleaned_input = user_input.strip()
        
        if cleaned_input:  
            clear_project_info()
            extract_project_info(cleaned_input)
            load_project_info()
            
            # Use timestamp to make unique filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            doc_path = f"project_proposal_{timestamp}.docx"
            blob_name = f"proposal_{timestamp}.docx"
            
            create_word_doc(filename=doc_path)
            
            # Check if file was created
            if not os.path.exists(doc_path):
                return f"Word document was not created at {doc_path}"
            
            file_size = os.path.getsize(doc_path)
            print(f"Word doc created: {doc_path} ({file_size} bytes)")
            
            # Upload to blob storage with unique name
            blob_url = upload_blob(doc_path, blob_name)
            
            if blob_url:
                return f"Proposal generated successfully! Download here: {blob_url}"
            else:
                return "Proposal created but Azure upload failed. Check logs above."
                
        return "No input provided."
        
    except Exception as e:
        return f"Error generating proposal: {type(e).__name__}: {str(e)}"
    finally:
        # Clean up the local file after upload
        if doc_path and os.path.exists(doc_path):
            try:
                os.remove(doc_path)
                print(f"Cleaned up local file: {doc_path}")
            except Exception as cleanup_error:
                print(f"Failed to cleanup {doc_path}: {cleanup_error}")

if __name__ == "__main__":
    mcp.run(transport="stdio")