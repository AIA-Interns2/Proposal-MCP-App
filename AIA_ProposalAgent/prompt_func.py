import os
import json
from .projectinfo import update_project_info, get_example_proposals, PROJECT_INFO_PATH
from .ai_service import *

def get_structured_response(prompt, user_input=None, structured=True):
    # load current project state from projectinfo.json
    try:
      with open(PROJECT_INFO_PATH, 'r') as f:
          current_state = json.load(f)
          prompt += f"\n\nCurrent Project State:\n{json.dumps(current_state, indent=2)}"
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    messages = []
    if user_input:
      prompt += f"\n\nInput text:\n{user_input}"
    
    examples = get_example_proposals()
    prompt += f'''\n\nExample Proposals:\nHere are a series of example proposals that I have written in the past for different clients. 
    The content does not relate here in any way only the structure and tone of voice matters. 
    Use these example proposals as a reference point of how to structure all sections of the proposal you are to write.{examples}'''
    messages.append({"role": "system", "content": prompt})

    try:
        if structured:
            return chat_structured(messages)
        else:
            return chat(messages)
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

def extract_basic_info(document_text):
    system_prompt = """
    Extract basic project information from the input text and format it as a JSON object with the following structure:
    
    {
      "PROJECT TITLE": "string",
      "COMPANY NAME": "string",
      "CLIENT": "string", 
      "PROJECT MANAGER": "string",
      "AUTHOR": "string",
      "START DATE": "string",
      "END DATE": "string",
      "PROJECT DESCRIPTION": "string"
    }
    
    Important extraction guidelines:
    - title should not be lengthy, just a few words
    - For any field where information is not available in the input text, use "Not specified".
    - The author and project manager is either Samuel Cunningham or Sean Oldenburger.
    - The project description should be a one sentence summary of the project.
    - Use Australian English spelling and grammar.
    """
    result = get_structured_response(document_text, system_prompt)
    update_project_info("BASIC_INFO", result)
    return result

def extract_scope(document_text):
    system_prompt = """
    Extract the project scope information from the input text and format it as a JSON object with the following structure:
    
    {
      "SCOPE": "string"
    }
    
    Important extraction guidelines:
    - Do not infer data, only use what is given in the text
    - If relevant information is found, structure it in short paragraphs outlining the following:
       - Paragraph 1: what this project is creating, using what AI models and how
       - Paragraph 2: AI Advancement's role in the project
    - Use similar sentence structure and total length to the sample.
    - If no scope information is found, return "Not specified" by itself.
    - Use Australian English spelling and grammar.

    EXAMPLE OUTPUTS:
    [This will be a beta project of the Knowledge Hub chatbot. 
    The chatbot will be available through a standalone website, developed and hosted by AI Advancements. 
    The chatbot will be able to answer questions and retrieve specific information when asked by the user. The chatbot should always reference the document from which the answer was found. 
    The beta will NOT include authentication or analytics.]

    [This project aims to support Curtin University's Tier 1 research group, CFIGS, in showcasing its academic outputs to the public and industry by developing a semi-automated pipeline for the discovery, summarisation, and publication of research content. 
    The system will: 
    Securely scrape CFIGS-related research papers from Curtin’s internal research repositories (which is protected behind Curtin login). 
    Utilise AI to summarise key details of each publication and create a news article based on the paper in your tone of voice. 
    Simple interface/script to easily run the system. Support human-in-the-loop workflows (Graydon’s role) to review, edit, and approve content. ]
    
    Use these examples to guide your json object, ensuring it contains similar sentence structure, tone, and length.
    """   
    result = get_structured_response(document_text, system_prompt)
    update_project_info("SCOPE", result.get("SCOPE", "Not specified"))
    return result

def extract_contract_structure(document_text):
    system_prompt = """
    Extract the contract structure information from the input text and format it as a JSON object with the following structure:
    
    {
      "CONTRACT_STRUCTURE": "string"
    }
    
    Important extraction guidelines:
    - Do not infer data, only use what is given in the text
    - If relevant info is found, structure it in short paragraphs outlining the following:
       - Paragraph 1: The contract type. Is it a fixed fee cost?
       - Paragraph 2: When to pay, and how invoicing will work
       - Paragraph 3: What happens to the intellectual property and when handover happens after both parties agree the deliverables are met
    - Use similar sentence structure to the sample.
    - If no contract structure information is found, return "Not specified" by itself.
    - Use Australian English spelling and grammar.

    EXAMPLE OUTPUTS:
    [The contract type of this project is a fixed fee cost. There is a fixed cost for the entire proposal which has been broken down into 2 phases as seen in Section 6. 
    The payment of this project is to be paid per completion of each phase. AIA will invoice the amount when both parties can agree the deliverables have been met. Invoices are due within 14 days of being issued. 
    Handover of code will be done upon AIA receiving payment of all milestones and both parties agree all deliverables of the project are met. 
    Curtin’s IP maintains their IP, including all data, documentation and processes. Likewise, IP created by AI Advancements stays with AI Advancements. 
    AI Advancements core team is responsible and in charge of all work completed and will ensure everything completed is up to their standards. AI Advancements retains the right to subcontract or hire for parts of the project if required.  ]
    
    [The contract type of this project is a fixed fee cost.  
    The payment of this project is to be paid per completion of the project. AIA will invoice the amount when both parties can agree the key deliverables outlined in Section 3.0 have been met. 
    Handover of code will be done upon AIA receiving full payment. 
    Capital Legal will retain all intellectual property associated with this project, including any code, data or other resources generated. ]
    
    Use these examples to guide your json object, ensuring it contains similar sentence structure, tone, and length.
    """
    result = get_structured_response(document_text, system_prompt)
    update_project_info("CONTRACT_STRUCTURE", result.get("CONTRACT_STRUCTURE", "Not specified"))
    return result

def extract_plan(document_text):
    system_prompt = """
    Generate a plan for the project using the provided meeting notes, information and all other data provided. Output only the plan as plain text, not using any formatting.

    Your task is to generate the PLAN section for a proposal document prepared by an AI consulting company.

    Guidelines:
    - Only output the project plan — do not include timeline, budget, deliverables, or any extra commentary.
    - Use plain text, no markdown or formatting. Do not include a title.
    - Structure the plan into clearly titled sections (e.g., Frontend, Backend, Hosting, AI Integration, etc.) if relevant.
    - Within each section, use lists, bullet points, sub bullet points, tables, etc. to describe what the team will do.
    - Ensure to be detailed and specific about the tasks, technologies, and approaches that will be used as provided in the input text. However do not write paragraphs or long sentences, keep things short and easy to read.
    - Keep language simple and focused on outcomes.
    - Do not invent or infer information that isn’t in the input — only use what’s explicitly provided.
    - Keep it easy for non-technical stakeholders to understand and read.
    - Use Australian English spelling and grammar.
    - Only look at the plan section of the example proposals provided, ignore all other sections.
    - Do not include sections that are already covered in other parts of the proposal (e.g., scope, assumptions, etc.)
    """
    result = get_structured_response(document_text, system_prompt, False)
    update_project_info("PLAN", result)
    return result

def extract_key_deliverables(document_text):
    system_prompt = """
    Extract the key deliverables information from the input text and format it as a JSON object with the following structure:
    
    {
      "KEY_DELIVERABLES": ["string"]
    }
    
    Important extraction guidelines:
    - A key deliverable is a tangible output that AI Advancements is committing to deliver to the client.
    - Only include final outputs that would be handed over to the client, presented in a report, or considered a completed product (e.g., MVP application, feasibility report, training session).
    - Write each deliverable as a short, clear sentence or phrase.
    - There should be around 3-5 key deliverables, depending on the project size you can make more or less.
    - If no key deliverables are mentioned in the text, return: { "KEY_DELIVERABLES": ["Not specified"] }
    - Use Australian English spelling and grammar.
    """
    result = get_structured_response(document_text, system_prompt)
    update_project_info("KEY_DELIVERABLES", result.get("KEY_DELIVERABLES", ["Not specified"]))
    return result

def extract_assumptions(document_text):
    system_prompt = """
    Extract the assumptions information from the input text and format it as a JSON object with the following structure:
    
    {
      "ASSUMPTIONS": ["string"]
    }

    Guidelines:
    - An assumption is a condition believed to be true for the project to succeed, but which is not confirmed or controlled by the project team. These are typically external dependencies, client responsibilities, or preconditions the team cannot guarantee.
    - Only include unverified conditions that impact project feasibility, planning, or delivery.
    - Examples include:
      - Client will provide API keys, data, or system access.
      - Hosting environment is set up and accessible.
      - Project stakeholders will be available for scheduled meetings.
      - Client will supply pre-translated templates for system use.
    - Each assumption must be a short, clear sentence.
    - Must be something the team is relying on, but does not own or control.
    - Use Australian English spelling and grammar.
    """
    result = get_structured_response(document_text, system_prompt)
    update_project_info("ASSUMPTIONS", result.get("ASSUMPTIONS", ["Not specified"]))
    return result

def extract_timeline(document_text):
    system_prompt = """
     Extract the timeline information from the input text and format it as a JSON object with the following structure:
    
    {
      "MILESTONES": [
        {
          "DESCRIPTION": "string",
          "ESTIMATED_TIME": "string"
        },
      "TOTAL_DURATION": "string",
      ]
    }
    
    Important extraction guidelines:
    - Extract 2–5 major milestones or tasks based directly on the input text. Each must be a distinct phase or deliverable the team is responsible for.
    - Use short milestone descriptions (max 6 words) using the project’s actual language (do not reword unless unclear).
    - ESTIMATED_TIME must be a whole number string representing the duration in **working days**. Do not include “days” or decimals.
    - Use explicit durations if provided.
    - If durations are not provided, assign realistic defaults based on task type:
      - Simple or one-time tasks: 1–2 days
      - Design/development stages: 3-5 days
      - Testing, deployment, or reviews: 2–3 days
    - For long-term projects (multi-phase), base durations on context but keep them proportional.
    - Return the total duration as a string — sum of all ESTIMATED_TIME values.
    - Use Australian English spelling and grammar.
    """
    result = get_structured_response(document_text, system_prompt)
    update_project_info("TIMELINE", result or {"TOTAL_DURATION": "Not specified", "MILESTONES": []})
    return result

def extract_budget(document_text):
    system_prompt = """
    Extract the budget information from the input text and format it as a JSON object with the following structure:
    
    {
      "TOTAL_COST": "string",
      "ADDITIONAL_COST": [
        {
          "CATEGORY": "string",
          "TIME": "",
          "DAY_RATE": "",
          "COST": "string"
        }
      ]
    }
    
    Important extraction guidelines:
    - Extract the total cost of the project if mentioned.
    - If any additional costs are explicitly mentioned, extract it with a category and cost. Time and day rate will be empty strings.
    - If no additional costs are found, return an empty array.
    """
    result = get_structured_response(document_text, system_prompt)
    update_project_info("BUDGET", result or {"TOTAL_COST": "Not specified", "ADDITIONAL_COST": []})
    return result

def extract_delivery_team(document_text):
    system_prompt = """
    Extract the delivery team information from the input text and format it as a JSON object with the following structure:
    
    {
      "TEAM_MEMBERS": [
        {
          "NAME": "string",
        }
      ]
    }
    
    Important extraction guidelines:
    - Specifically look for these team members by name, if one of these names is seen output it in the JSON object:
      * Sam Cunningham / Samuel Cunningham
      * Sean Oldenburger
      * Lindsey Hershman
    - Look for full names or first names (Sam/Samuel, Sean).
    - If no team members are found, use Samuel Cunningham and Sean Oldenburger as default team members.
    """
    result = get_structured_response(document_text, system_prompt)
    update_project_info("DELIVERY_TEAM", result or {"TEAM_MEMBERS": ["Samuel Cunningham", "Sean Oldenburger"]})
    return result

def extract_past_projects(document_text):
    try:
        json_path = os.path.join(os.path.dirname(__file__), "data", "pastprojects.json")
        with open(json_path, 'r') as file:
            project_data = json.load(file)
            available_projects = project_data["PROJECTS"]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading pastprojects.json: {str(e)}")
        available_projects = {}

    system_prompt = f"""
    Extract similar past projects from the input text and format it as a JSON object with the following structure:
    
    {{
      "PAST_PROJECTS": [
        {{
          "PROJECT_NAME": "string"
        }}
      ]
    }}
    
    Important extraction guidelines:
    - Look for 3-5 previous projects that are most similar or relate to the current project based on the project description.
    - Choose from these available projects only: {', '.join(available_projects.keys())}
    - Consider similarities in project type, technology used, or client sector.
    - If no similar projects are found, return empty array.
    """
    result = get_structured_response(document_text, system_prompt)
    update_project_info("PAST_PROJECTS", result or {"PAST_PROJECTS": []})
    return result