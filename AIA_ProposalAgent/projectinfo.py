import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PROJECT_INFO_PATH = os.path.join(DATA_DIR, "projectinfo.json")
EXAMPLE_PROPOSALS_PATH = os.path.join(DATA_DIR, "exampleproposals.json")

def load_project_info():
    # Load projectinfo.json from the data directory
    try:
        with open(PROJECT_INFO_PATH, 'r') as f:
            project_data = json.load(f)
            return project_data
    except Exception as e:
        print(f"Error loading project data: {e}")
        return {}
    
def update_project_info(key, value):
    # Update projectinfo.json with new data
    try:
        project_data = load_project_info()
        project_data[key] = value
        with open(PROJECT_INFO_PATH, 'w') as f:
            json.dump(project_data, f, indent=2)
    except Exception as e:
        print(f"Error updating projectinfo.json: {str(e)}")

def clear_project_info():
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Clear projectinfo.json at startup
    empty_project_info = {
        "BASIC_INFO": {},
        "PLAN": "Not specified",
        "SCOPE": "Not specified",
        "CONTRACT_STRUCTURE": "Not specified",
        "KEY_DELIVERABLES": ["Not specified"],
        "ASSUMPTIONS": ["Not specified"],
        "TIMELINE": {
            "TOTAL_DURATION": "Not specified",
            "MILESTONES": []
        },
        "BUDGET": {
            "TOTAL_COST": "Not specified",
            "ADDITIONAL_COST": []
        },
        "DELIVERY_TEAM": {
            "TEAM_MEMBERS": []
        },
        "PAST_PROJECTS": {
            "PAST_PROJECTS": []
        }
    }
    
    try:
        with open(PROJECT_INFO_PATH, 'w') as f:
            json.dump(empty_project_info, f, indent=2)
        print("Cleared projectinfo.json")
    except Exception as e:
        print(f"Error clearing projectinfo.json: {str(e)}")

def get_example_proposals():
    # Load and format example proposals from JSON file
    try:
        with open(EXAMPLE_PROPOSALS_PATH, 'r') as f:
            proposals_data = json.load(f)
            proposals = []
            for project_name, project_data in proposals_data["PROJECTS"].items():
                if "PROPOSAL" in project_data:
                    proposals.append(f"Example {project_name}:\n{project_data['PROPOSAL']}")
            
            if proposals:
                return "\n\n".join(proposals)
            return ""
    except Exception as e:
        print(f"Error loading example proposals: {e}")
        return ""