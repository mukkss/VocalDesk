import asyncio

# Import the main customer service agent
from customer_service_agent import customer_service_agent
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from utils import (
    add_user_query_to_history,
    call_agent_async,
)

load_dotenv()

# ===== PART 1: Initialize In-Memory Session Service =====
# Using in-memory storage for this example (non-persistent)
session_service = InMemorySessionService()


# ===== PART 2: Define Initial State =====
# This will be used when creating a new session
initial_state = {
    "user_name": "Mukkss",
    "purchased_courses": [],
    "interaction_history": [],
}


async def main_async():
    # Setup constants
    APP_NAME = "Customer Support"
    USER_ID = "mukkss"

    # ===== PART 3: Session Creation =====
    # Create a new session with initial state
    new_session = session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    SESSION_ID = new_session.id
    print(f"Created new session: {SESSION_ID}")

    # ===== PART 4: Agent Runner Setup =====
    # Create a runner with the main customer service agent
    runner = Runner(
        agent=customer_service_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    # ===== PART 5: Interactive Conversation Loop =====
    print("\nWelcome to Customer Service Chat!")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Ending conversation. Goodbye!")
            break

        # Show state before interaction
        current_session = session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
        selected_before = current_session.state.get("selected_course_id", None)
        print(f"\n🔍 SELECTED COURSE BEFORE: {selected_before}")

        # Add to history
        add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, user_input
        )

        # Call agent
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)

        # Show state after interaction
        updated_session = session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
        selected_after = updated_session.state.get("selected_course_id", None)
        print(f"✅ SELECTED COURSE AFTER: {selected_after}")

    # ===== PART 6: State Examination =====
    # Show final session state
    final_session = session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("\nFinal Session State:")
    for key, value in final_session.state.items():
        print(f"{key}: {value}")


def main():
    """Entry point for the application."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()