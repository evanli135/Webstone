from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

from .config import ANTHROPIC_API_KEY, MODEL_NAME, TEMPERATURE
from .schemas import CodeOutput, TaskResult


def build_structured_llm(schema):
    """Wrap the LLM so it always returns a validated Pydantic model."""
    llm = ChatAnthropic(
        model=MODEL_NAME,
        api_key=ANTHROPIC_API_KEY,
        temperature=TEMPERATURE,
    )
    return llm.with_structured_output(schema, include_raw=False)


# --- Specialized callers ---

def generate_code(task: str) -> CodeOutput:
    """Ask the LLM to produce code; output is guaranteed to match CodeOutput schema."""
    llm = build_structured_llm(CodeOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a coding assistant. Return only structured output."),
        ("human", "{task}"),
    ])
    chain = prompt | llm
    result = chain.invoke({"task": task})
    assert isinstance(result, CodeOutput)  # guaranteed by with_structured_output
    return result


def summarize_task(task: str, raw_output: str) -> TaskResult:
    """Summarize a completed agent task into a validated TaskResult."""
    llm = build_structured_llm(TaskResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize the agent task result into structured output."),
        ("human", "Task: {task}\n\nRaw output:\n{output}"),
    ])
    chain = prompt | llm
    result = chain.invoke({"task": task, "output": raw_output})
    assert isinstance(result, TaskResult)
    return result
