# Coding Agent Example

A simple LangChain-based coding agent that predates the Webstone research runtime.
Kept here for reference — it is **not** part of the core `webstone` package.

## Run

```bash
# From the repo root
pip install langchain langchain-anthropic langchain-experimental python-dotenv
python -m examples.coding_agent.main
```

Requires `ANTHROPIC_API_KEY` in your `.env` file.
