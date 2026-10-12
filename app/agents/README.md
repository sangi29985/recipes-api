# Context Manager Agent System

A multi-agent system built with LlamaIndex and PyGitHub for gathering comprehensive context from GitHub pull requests.

## Overview

This system implements a ReActAgent that can analyze GitHub pull requests by:
- Fetching PR details (author, title, body, state, etc.)
- Retrieving commit information and changed files
- Reading file contents from the repository

## Installation

### Prerequisites

- Python 3.8+
- GitHub Personal Access Token with appropriate permissions
- OpenAI API Key

### Install Dependencies

```bash
pip install llama-index-core llama-index-llms-openai PyGithub python-dotenv
```

## Configuration

The system requires the following environment variables in your `.env` file:

```env
# GitHub Configuration
GITHUB_TOKEN=your-github-personal-access-token

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1
```

### GitHub Token Setup

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token (classic or fine-grained)
3. For fine-grained tokens, grant the following permissions:
   - Pull requests: Read access
   - Contents: Read access
   - Metadata: Read access

## Usage

### Basic Usage

```python
import asyncio
from app.agents.context_agent import main

# Run the agent for a specific PR
asyncio.run(main(pr_number=1))
```

### As a Module

```python
from app.agents.context_agent import context_agent

# Use the agent directly
response = await context_agent.astream_chat("Gather context for PR #1")

async for event in response.async_response_gen():
    print(event, end="", flush=True)
```

### Running the Script

```bash
# From the project root
python app/agents/context_agent.py
```

By default, it will analyze PR #1. You can modify the `PR_NUMBER` variable in the `__main__` section.

## Architecture

### Components

1. **Tool Functions**: Python functions that interact with the GitHub API
   - `get_pr_details(pr_number)`: Fetches PR metadata
   - `get_pr_commit_details(head_sha)`: Gets commit file changes
   - `get_file_contents(file_path, ref)`: Retrieves file contents

2. **LlamaIndex Tools**: Function tools created from the Python functions
   - Automatically converts function signatures and docstrings
   - Makes functions available to the agent

3. **ReActAgent**: The main agent that orchestrates tool usage
   - Uses reasoning and action loops
   - Decides which tools to call and in what order
   - Synthesizes information into a comprehensive response

4. **OpenAI LLM**: The language model powering the agent
   - Configurable model (default: gpt-4)
   - Handles reasoning and decision-making

### Agent System Prompt

The agent is configured with a specific system prompt that guides it to:
- Gather PR details first
- Fetch commit information to identify changed files
- Retrieve file contents when relevant

### Event Streaming

The system uses async event streaming to provide real-time feedback:
- Events are streamed as the agent works
- Each thought, action, and observation is visible
- Final response is available after streaming completes

## Example Output

```
================================================================================
Starting Context Agent for PR #1
================================================================================

Agent is working...

Thought: I need to gather the PR details first
Action: get_pr_details
Action Input: {"pr_number": 1}
Observation: {"author": "username", "title": "Add new feature", ...}

Thought: Now I need to get the changed files
Action: get_pr_commit_details
Action Input: {"head_sha": "abc123..."}
Observation: [{"filename": "app/models.py", "status": "modified", ...}]

...

================================================================================
Context gathering complete!
================================================================================
```

## Error Handling

The system includes comprehensive error handling:
- GitHub API errors are caught and reported
- Missing environment variables are detected before execution
- Binary files are handled gracefully
- Network issues are surfaced with clear messages

## Repository Configuration

The agent is currently configured to work with:
- Repository: `sangi29985/recipes-api`
- GitHub API: Standard REST API v3

To change the repository, modify the constants in `context_agent.py`:
```python
GITHUB_REPO_OWNER = "your-username"
GITHUB_REPO_NAME = "your-repo"
```

## Advanced Usage

### Custom Queries

You can ask the agent custom questions:

```python
response = await context_agent.astream_chat(
    "Get the PR details and show me what changed in the models.py file"
)
```

### Adding More Tools

To extend the agent with additional capabilities:

1. Define a new function with proper type hints and docstring
2. Convert it to a tool: `new_tool = FunctionTool.from_defaults(fn=your_function)`
3. Add it to the agent's tools list

### Custom LLM Configuration

You can use different OpenAI models or configurations:

```python
llm = OpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)
```

## Troubleshooting

### "Failed to fetch PR details"
- Check that your GitHub token has the necessary permissions
- Verify the PR number exists in the repository
- Ensure the repository owner and name are correct

### "Missing required environment variables"
- Verify all required variables are set in your `.env` file
- Make sure the `.env` file is in the project root
- Check that python-dotenv is installed

### "API rate limit exceeded"
- GitHub API has rate limits (5000/hour for authenticated requests)
- Wait for the rate limit to reset
- Use a different token if available

## Future Enhancements

Potential additions to the system:
- Multiple specialized agents (reviewer, tester, documenter)
- Workflow orchestration between agents
- Caching of GitHub data
- Support for other git providers (GitLab, Bitbucket)
- Integration with CI/CD systems

## References

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [PyGitHub Documentation](https://pygithub.readthedocs.io/)
- [GitHub REST API](https://docs.github.com/en/rest)
- [ReAct Pattern Paper](https://arxiv.org/abs/2210.03629)
