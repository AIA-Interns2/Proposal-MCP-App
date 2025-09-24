from flask import Flask, render_template, request, send_file
from main import extract_project_info, create_word_doc
from projectinfo import clear_project_info, load_project_info, update_project_info
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    table_data = {}
    user_input = ""
    document_path = None
    
    if request.method == "POST":
        try:
            user_input = request.form["user_input"]
            
            # Extract information from text input
            if user_input.strip():
                clear_project_info()
                extract_project_info(user_input)
                table_data = load_project_info()
            
            # Handle manual inputs if provided
            basic_info = table_data.get("BASIC_INFO", {})
            if any([request.form.get(field) for field in ["company_name", "client", "project_manager", "author"]]):
                if request.form.get("company_name"):
                    basic_info["COMPANY NAME"] = request.form["company_name"]
                if request.form.get("client"):
                    basic_info["CLIENT"] = request.form["client"]
                if request.form.get("project_manager"):
                    basic_info["PROJECT MANAGER"] = request.form["project_manager"]
                if request.form.get("author"):
                    basic_info["AUTHOR"] = request.form["author"]
                update_project_info("BASIC_INFO", basic_info)
                table_data = load_project_info()

            document_path = "project_proposal.docx"
            create_word_doc(filename=document_path)
        
        except Exception as e:
            error_message = f"Error: {str(e)}"
            return render_template("index.html", error=error_message, user_input=user_input)
    
    return render_template("index.html", 
                           table_data=table_data, 
                           user_input=user_input, 
                           document_path=document_path)

@app.route("/download")
def download_document():
    document_path = "project_proposal.docx"
    if os.path.exists(document_path):
        return send_file(document_path, 
                         as_attachment=True, 
                         download_name='project_proposal.docx')
    return "Document not found", 404

if __name__ == "__main__":
    app.run(debug=True)
