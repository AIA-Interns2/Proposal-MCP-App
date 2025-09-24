from .prompt_func import *
from .docx_func import *
from .projectinfo import load_project_info

def extract_project_info(document_text):
  extract_basic_info(document_text)
  extract_plan(document_text)
  extract_scope(document_text)
  extract_contract_structure(document_text)
  extract_key_deliverables(document_text)
  extract_assumptions(document_text)
  extract_timeline(document_text)
  extract_budget(document_text)
  extract_delivery_team(document_text)
  extract_past_projects(document_text)

def create_word_doc(filename="project_proposal.docx"):
    doc = Document()
    project_data = load_project_info() 

    create_header_table(doc, logo_path=os.path.join(IMAGES_DIR, "Logo.png"), company_name="AI Advancements", company_name_font='Calibri Bold')
        
    # Initialize the info_data dictionary with default values
    basic_info = project_data.get("BASIC_INFO", {})
    info_data = {
        "PROJECT TITLE": basic_info.get("PROJECT TITLE", ""),
        "COMPANY NAME": basic_info.get("COMPANY NAME", ""),
        "CLIENT": basic_info.get("CLIENT", ""),
        "PROJECT MANAGER": basic_info.get("PROJECT MANAGER", ""),
        "AUTHOR": basic_info.get("AUTHOR", ""),
        "START DATE": basic_info.get("START DATE", ""),
        "END DATE": basic_info.get("END DATE", ""),
        "PROJECT DESCRIPTION": basic_info.get("PROJECT DESCRIPTION", "")
    }
    add_title(doc, basic_info.get("PROJECT TITLE", ""), size=48)

    create_info_table(doc, info_data)
    add_subheading(doc, '\nClient Approval and Sign-Off', size=11)
    add_body_text(doc, 'Name:\nDate:\nSignature:')
    add_subheading(doc, '\nContractor Approval and Sign-Off', size=11)
    add_body_text(doc, 'Name:\nDate:\nSignature:')
    
    # New page - Contents
    add_page_break(doc)
    add_heading(doc, 'Contents', size=20)
    
    # Table of contents
    toc_text = 'Change Logs\n1.0 Scope\n2.0 Contract Structure\n3.0 Key Deliverables\n4.0 Plan\n5.0 Assumptions\n6.0 Timeline\n7.0 Budget\n8.0 Delivery Team\n9.0 Past Projects'
    p = add_body_text(doc, toc_text, font_name='Calibri Bold')
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    
    # New page - Main content
    add_page_break(doc)
    
    # Change logs section
    add_heading(doc, 'Change Logs')
    author = basic_info.get("AUTHOR", "Not specified")
    create_change_log_table(doc, author)
    doc.add_paragraph("")

    # Main content sections
    add_heading(doc, '1.0 Scope')
    scope_text = project_data.get("SCOPE", "Scope information not found")
    add_body_text(doc, scope_text)
    
    add_heading(doc, '2.0 Contract Structure')
    contract_text = project_data.get("CONTRACT_STRUCTURE", "Contract structure information not found")
    add_body_text(doc, contract_text)
    
    add_heading(doc, '3.0 Key Deliverables')
    deliverables = project_data.get("KEY_DELIVERABLES", ["Key deliverables information not found"])
    add_bullet_points_from_list(doc, deliverables)
    
    add_heading(doc, '4.0 Plan')
    plan_text = project_data.get("PLAN", "Plan information not found")
    add_body_text(doc, plan_text)
    
    add_heading(doc, '5.0 Assumptions')
    assumptions = project_data.get("ASSUMPTIONS", ["Assumptions not found"])
    add_bullet_points_from_list(doc, assumptions)
    
    add_heading(doc, '6.0 Timeline')
    timeline_data = project_data.get("TIMELINE", {"TOTAL_DURATION": "Not specified", "MILESTONES": []})
    create_timeline_table(doc, timeline_data)
    
    add_heading(doc, '7.0 Budget')
    budget_data = project_data.get("BUDGET", {"TOTAL_COST": "Not specified", "ADDITIONAL_COST": []})
    create_budget_table(doc, budget_data, timeline_data.get("TOTAL_DURATION", "1"))
    
    add_heading(doc, '\n8.0 Delivery Team')
    team_data = project_data.get("DELIVERY_TEAM", {"TEAM_MEMBERS": []})
    add_delivery_team_details(doc, team_data)
    
    add_heading(doc, '9.0 Past Projects')
    past_projects = project_data.get("PAST_PROJECTS", {"PAST_PROJECTS": []})
    add_past_projects_section(doc, past_projects)

    doc.save(filename)
    print(f"Document '{filename}' created successfully!")
