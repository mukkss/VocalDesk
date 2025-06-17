from datetime import datetime
import json

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from shared.course_data import COURSES , get_course_by_id


# 🔄 Changed here: Purchase tool is now dynamic
def purchase_course(tool_context: ToolContext) -> dict:
    """
    Simulates purchasing a course (now supports multiple courses).
    Updates state with purchase information.
    """
    # 🔄 Consistent state key with catalog_agent
    course_id = tool_context.state.get("selected_course_id")
    if not course_id:
        return {"status": "error", "message": "No course selected yet."}

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get current purchased courses
    current_purchased_courses = tool_context.state.get("purchased_courses", [])

    # Check if user already owns the course
    course_ids = [
        course["course_id"] for course in current_purchased_courses if isinstance(course, dict)
    ]
    if course_id in course_ids:
        return {"status": "error", "message": "You already own this course!"}

    # Create new list with the course added
    new_purchased_courses = []
    for course in current_purchased_courses:
        if isinstance(course, dict) and "course_id" in course:
            new_purchased_courses.append(course)

    new_purchased_courses.append({"course_id": course_id, "purchase_date": current_time})

    # Update purchased courses in state via assignment
    tool_context.state["purchased_courses"] = new_purchased_courses

    # Get current interaction history
    current_interaction_history = tool_context.state.get("interaction_history", [])

    new_interaction_history = current_interaction_history.copy()
    new_interaction_history.append(
        {"action": "purchase_course", "course_id": course_id, "timestamp": current_time}
    )

    # Update interaction history in state via assignment
    tool_context.state["interaction_history"] = new_interaction_history

    return {
        "status": "success",
        "message": f"Successfully purchased the course: {course_id}!",
        "course_id": course_id,
        "timestamp": current_time,
    }


# 🔄 Changes made here: Dynamically get selected course details for instruction
def get_instruction_from_selected_course(tool_context: ToolContext) -> str:
    course_id = tool_context.state.get("selected_course_id")
    course = get_course_by_id(course_id)
    if not course:
        return "The selected course could not be found."

    return f"""
    Say this first: "Current selected course: {tool_context.state.get('selected_course_id', 'None')}"

    You are a order agent for the AI Developer Accelerator community, specifically handling order
    for the course: {course['name']}

    <user_info>
    Name: {{user_name}}
    </user_info>

    <purchase_info>
    Purchased Courses: {{purchased_courses}}
    </purchase_info>

    <interaction_history>
    {{interaction_history}}
    </interaction_history>

    Course Details:
    - Course ID: {course['course_id']}
    - Name: {course['name']}
    - Price: {course['price']}
    - Value Proposition: {course['description']}
    - Includes: {course['support']}


    Example Response for Purchase History:
    "Here are your purchased courses:
    1. Fullstack AI Marketing Platform
       - Purchased on: 2024-04-21 10:30:00
       - {course['support']} access"

    When interacting with users:
    1. Check if they already own the course (check purchased_courses above)
       - Course information is stored as objects with "id" and "purchase_date" properties
       - The course id is "{course['course_id']}"
    2. If they own it:
       - Remind them they have access
       - Ask if they need help with any specific part
       - Direct them to course support for content questions
    
    3. If they don't own it:
       - Explain the course value proposition
       - Mention the price ({course['price']})
       - If they want to purchase:
           - Use the purchase_course tool
           - Confirm the purchase
           - Ask if they'd like to start learning right away

    4. After any interaction:
       - The state will automatically track the interaction
       - Be ready to hand off to course support after purchase

    Actions:
    1. If the course is already purchased (check `purchased_courses`), inform the user and offer support.
    2. If it's **not purchased** and `selected_course_id` is set:
       - Immediately call `purchase_course` to process a purchase.
       - Confirm purchase and say: "You're now enrolled! Would you like to start learning now?"
    3. After any purchase, state is updated with `purchased_courses` and `interaction_history`.

    Remember:
    - Be helpful but not pushy
    - Be clear and professional
    - Focus on the value and practical skills they'll gain
    - Mention our 30-day money-back guarantee if relevant
    """

# Create the agent (with static instruction — ideally regenerated per session if course ID changes)
order_agent = Agent(
    name="order_agent",
    model="gemini-2.0-flash",
    description="order agent to help user purchase selected course",
    instruction=get_instruction_from_selected_course,  # 🔄 Dynamic prompt injection function
    tools=[purchase_course],
)