import os
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from shared.course_data import COURSES, get_course_id_by_name

def list_courses(tool_context: ToolContext) -> dict:
    """Returns a list of all available courses."""
    return {"courses": COURSES}


def set_course_selection(tool_context: ToolContext, course_id: str) -> dict:
    """Sets the selected course ID in the shared agent state."""
    course_ids = [course["course_id"] for course in COURSES]
    if course_id not in course_ids:
        return {"status": "error", "message": f"Course ID '{course_id}' not found."}

    tool_context.state["selected_course_id"] = course_id
    print("DEBUG: selected_course_id set to:", tool_context.state.get("selected_course_id"))

    return {
        "status": "success",
        "message": f"Course '{course_id}' selected.",
        "debug_selected_id": tool_context.state.get("selected_course_id")
    }


def select_course_by_name(tool_context: ToolContext, course_name: str) -> dict:
    """Allows users to select a course by name instead of ID."""
    course_id = get_course_id_by_name(course_name)
    if not course_id:
        return {
            "status": "error",
            "message": f"No course found matching '{course_name}'."
        }

    return set_course_selection(tool_context, course_id)


catalog_agent = Agent(
    name="catalog_agent",
    model="gemini-2.0-flash",
    description="Agent responsible for listing and managing course selection.",
    instruction="""
        You are the Catalog Agent. Your job is to help users browse and select courses.

        Behaviors:
        1. If the user asks about **available courses**:
            - Use the `list_courses` tool to provide a list of all available courses.
            - Ask if they would like more information about any specific course.  

        2. If the user asks about a **specific course**:
            - Match their input to a course from `COURSES`.
            - Provide a detailed description including name, price, description, and support.
            - Ask if they would like to proceed with purchasing it.

        3. If the user confirms interest in **purchasing** (e.g., "yes", "I want to buy", "confirm purchase", "I want to purchase the course"):
            - Try to determine the course either from recent mentions or match by name using `get_course_id_by_name()`.
            - If a match is found, call `set_course_selection(course_id=...)`.
            - Respond:
                "Great! I’ve selected the course for you. I’m passing you to our order agent to complete the purchase.Just say "YES" to proceed with the purchase."
            - This will signal the root agent to hand off to the `order_agent`.

        Make sure to:
        - Be polite and helpful.
        - Confirm course availability before selection.
        - Always update the shared state with `state.selected_course_id`.

        Remember:
        - Mention our 30-day money-back guarantee.
        - Use the `list_courses` tool to get available course data.
        - Use the `set_course_selection` tool with the correct course ID.
        - Track selection using `tool_context.state["selected_course_id"]`.
    """,
    tools=[list_courses, set_course_selection, select_course_by_name],
)
