from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport
import uvicorn
import os
import datetime

app = FastAPI(title="Proposal MCP Server API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import your MCP instance
try:
    from AIA_ProposalAgent.prompt_func import *
    from AIA_ProposalAgent.projectinfo import load_project_info, clear_project_info
    from AIA_ProposalAgent.main import extract_project_info, create_word_doc
    from blob import upload_blob, download_blob
    from fastmcp import FastMCP
    
    # Initialize FastMCP server
    mcp = FastMCP("Proposal Agent")
    
    @mcp.tool()
    def get_generated_proposal(user_input: str) -> str:
        doc_path = None
        try:
            cleaned_input = user_input.strip()
            
            if cleaned_input:
                clear_project_info()
                extract_project_info(cleaned_input)
                load_project_info()
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                doc_path = f"project_proposal_{timestamp}.docx"
                blob_name = f"proposal_{timestamp}.docx"
                
                create_word_doc(filename=doc_path)
                
                if not os.path.exists(doc_path):
                    return f"Word document was not created at {doc_path}"
                
                file_size = os.path.getsize(doc_path)
                print(f"Word doc created: {doc_path} ({file_size} bytes)")
                
                blob_url = upload_blob(doc_path, blob_name)
                
                if blob_url:
                    return f"Proposal generated successfully! Download here: {blob_url}"
                else:
                    return "Proposal created but Azure upload failed. Check logs above."
                    
            return "No input provided."
            
        except Exception as e:
            return f"Error generating proposal: {type(e).__name__}: {str(e)}"
        finally:
            if doc_path and os.path.exists(doc_path):
                try:
                    os.remove(doc_path)
                    print(f"Cleaned up local file: {doc_path}")
                except Exception as cleanup_error:
                    print(f"Failed to cleanup {doc_path}: {cleanup_error}")
    
except ImportError as e:
    mcp = None
    print(f"Warning: Could not import proposal modules: {e}")

@app.get("/")
async def root():
    return {
        "message": "Proposal MCP Server is running",
        "status": "healthy",
        "tools": ["get_generated_proposal"]
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "proposal-mcp-server"}

@app.get("/mcp/manifest.json")
async def manifest():
    return {
        "name": "proposal-mcp-server",
        "description": "Generates project proposals from Monday CRM data and uploads to Azure",
        "version": "1.0.0",
        "tools": [
            {"name": "get_generated_proposal", "description": "Generate a project proposal from Monday CRM data and upload to Azure Blob Storage"}
        ],
        "auth": {"type": "none"},
        "endpoints": {
            "sse": "https://proposalmcpapp-gagafgceehcxgxer.australiaeast-01.azurewebsites.net/mcp/sse"
        }
    }

# Only set up MCP SSE if the mcp module loaded successfully
if mcp is not None:
    sse_transport = SseServerTransport("/mcp/messages/")
    
    @app.get("/mcp/sse")
    async def handle_mcp_sse(request: Request):
        """Handle SSE connections for MCP communication"""
        try:
            async with sse_transport.connect_sse(request.scope, request.receive, request._send) as streams:
                await mcp._mcp_server.run(
                    streams[0], streams[1], mcp._mcp_server.create_initialization_options()
                )
            return Response()
        except Exception as e:
            print(f"SSE handler error: {e}")
            return Response(status_code=500)
    
    try:
        app.mount("/mcp/messages/", sse_transport.handle_post_message)
    except Exception as e:
        print(f"Failed to mount message handler: {e}")
else:
    @app.get("/mcp/sse")
    async def handle_mcp_sse_fallback():
        return {"error": "MCP module not available"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")