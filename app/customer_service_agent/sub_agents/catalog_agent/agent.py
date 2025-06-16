import os 
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

COURSES = [
    {
        "course_id": "ai_marketing_platform",
        "name": "AI Marketing Platform",
        "price": "$149",
        "value": "Learn to build AI-powered marketing apps",
        "duration": "6 weeks"
    },
    {
        "course_id": "voice_ai_builder",
        "name": "Voice AI Builder",
        "price": "$199",
        "value": "Build voice interfaces and assistants",
        "duration": "4 weeks"
    },
    {
        "course_id": "genai_workshop",
        "name": "Generative AI Workshop",
        "price": "$99",
        "value": "Hands-on with image and text generation",
        "duration": "3 weeks"
    }
]



def list_courses(tool_context: ToolContext) -> dict:
    """Returns a list of all available courses."""
    return {"courses": COURSES}


def set_course_selection(tool_context: ToolContext, course_id: str) -> dict:
    """Sets the selected course ID in the shared agent state."""
    course_ids = [course["course_id"] for course in COURSES]
    if course_id not in course_ids:
        return {"status": "error", "message": f"Course ID '{course_id}' not found."}

    tool_context.state["selected_course_id"] = course_id
    return {"status": "success", "message": f"Course '{course_id}' selected."}


catalog_agent = Agent(
    name="catalog_agent",
    model="gemini-2.0-flash",
    description="Agent responsible for listing and managing course selection.",
    instruction="""
    You are the Catalog Agent. Your job is to help users browse and select available courses.
    
    - Use `list_courses` to show all available courses with details.
    - If the user mentions a specific course, confirm its availability and use `set_course_selection` to update state.
    - Be polite and informative. If a course isn’t found, say so clearly.

    Store the selected course ID in `state.selected_course_id` using the tool.
    """,
    tools=[list_courses, set_course_selection]
)
