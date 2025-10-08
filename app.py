from typing import Any
import os
import datetime
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
import uvicorn
from AIA_ProposalAgent.prompt_func import *
from AIA_ProposalAgent.projectinfo import load_project_info, clear_project_info
from AIA_ProposalAgent.main import extract_project_info, create_word_doc
from blob import upload_blob, download_blob

def generate_proposal(user_input: str) -> str:
    """Generate proposal and return download URL"""
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

# Create MCP server instance
mcp_server = Server("proposal-agent")

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
    """Handle tool calls from MCP clients"""
    if name != "get_generated_proposal":
        raise ValueError(f"Unknown tool: {name}")
    
    if "user_input" not in arguments:
        raise ValueError("Missing required argument 'user_input'")
    
    # Call the proposal generation function
    result = generate_proposal(arguments["user_input"])
    
    return [types.TextContent(type="text", text=result)]

@mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_generated_proposal",
            description="Generate a project proposal from Monday CRM data and upload to Azure Blob Storage",
            inputSchema={
                "type": "object",
                "required": ["user_input"],
                "properties": {
                    "user_input": {
                        "type": "string",
                        "description": "Raw JSON data from Monday CRM containing project information",
                    }
                },
            },
        )
    ]

# Create SSE transport
sse = SseServerTransport("/messages/")

async def handle_sse(request: Request):
    """Handle SSE connections"""
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp_server.run(streams[0], streams[1], mcp_server.create_initialization_options())
    return Response()

async def health_check(request: Request):
    """Health check endpoint"""
    return Response(content='{"status": "ok"}', media_type="application/json")

async def root(request: Request):
    """Root endpoint"""
    return Response(content='{"message": "Proposal Agent Server Started"}', media_type="application/json")

# Create Starlette app
app = Starlette(
    debug=False,
    routes=[
        Route("/", endpoint=root, methods=["GET"]),
        Route("/health", endpoint=health_check, methods=["GET"]),
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)