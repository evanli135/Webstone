from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage



from .config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_ITERATIONS, TEMPERATURE
from .tools import ALL_TOOLS



SYSTEM_PROMPT = """You are an expert coding agent. You can read, write, and execute code to help users with programming tasks.

You have access to the following tools:
- read_file: Read file contents
- write_file: Write or create files
- list_files: List directory contents
- run_shell: Execute shell commands
- Python_REPL: Execute Python code directly

Always reason step-by-step. When writing code, verify it works by running it. If something fails, diagnose and fix it."""

class CodingAgentInput(BaseModel):
    model_config = ConfigDict(strict=True)

    query: str = Field(description="Coding task to complete")
    max_results: int = Field(default=5, gt=0, le=20, description="Max results to return")


def build_agent() -> AgentExecutor:
    llm = ChatAnthropic(
        model=MODEL_NAME,
        api_key=ANTHROPIC_API_KEY,
        temperature=TEMPERATURE,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)

    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        max_iterations=MAX_ITERATIONS,
        verbose=True,
        handle_parsing_errors=True,
    )


class CodingAgent:
    def __init__(self):
        self.executor = build_agent()
        self.chat_history: list = []

    def run(self, user_input: str) -> str:
        result = self.executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history,
        })
        output = result["output"]
        self.chat_history.append(HumanMessage(content=user_input))
        self.chat_history.append(AIMessage(content=output))
        return output

    def reset(self):
        self.chat_history = []
