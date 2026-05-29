from agent.agent import CodingAgent


def main():
    agent = CodingAgent()
    print("Coding Agent ready. Type 'exit' to quit, 'reset' to clear history.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("Chat history cleared.\n")
            continue

        response = agent.run(user_input)
        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    main()
