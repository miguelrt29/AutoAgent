"""Test script that exercises all tools in a single agent run."""

from agent import Agent


def main():
    agent = Agent()

    message = (
        "Do these tasks in order:\n"
        "1. Search the web for 'FastAPI best practices 2024'\n"
        "2. Write the search results to a file called research.txt\n"
        "3. Read the file research.txt and confirm its content\n"
        "4. Call the API GET https://httpbin.org/get and show the response\n"
        "5. Run the command: echo 'Agent test complete'"
    )

    for event in agent.run(message):
        if event["type"] == "tool_call":
            print(f"[TOOL] {event['tool']}: {event['input']}")
        elif event["type"] == "text":
            print(f"[RESPONSE] {event['content']}")


if __name__ == "__main__":
    main()
