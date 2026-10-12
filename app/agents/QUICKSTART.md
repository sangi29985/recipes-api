# Quick Start Guide

Get up and running with the Context Manager Agent System in 5 minutes!

## 1. Install Dependencies

```bash
pip install llama-index-core llama-index-llms-openai PyGithub python-dotenv
```

Or use the requirements file:

```bash
pip install -r app/agents/requirements.txt
```

## 2. Configure Environment Variables

Edit the `.env` file in your project root and add:

```env
# GitHub Token (get from https://github.com/settings/tokens)
GITHUB_TOKEN=your_github_token_here

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Configure the model (default: gpt-4)
OPENAI_MODEL=gpt-4

# Optional: Configure API base URL (default: https://api.openai.com/v1)
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Getting a GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name (e.g., "Context Agent")
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click "Generate token"
6. Copy the token and paste it in your `.env` file

### Getting an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Give it a name
4. Copy the key and paste it in your `.env` file

## 3. Verify Your Setup

Run the verification script to check everything is configured correctly:

```bash
python3 app/agents/verify_setup.py
```

If all checks pass, you're ready to go! ✅

## 4. Run Your First Agent

### Option A: Run the basic example

```bash
python3 app/agents/context_agent.py
```

This will analyze PR #1 by default. To change the PR number, edit the file and modify the `PR_NUMBER` variable.

### Option B: Run all examples

```bash
python3 app/agents/examples.py
```

This will run through all 6 examples showing different use cases.

### Option C: Run a specific example

```bash
# Run example 1 with PR #1
python3 app/agents/examples.py 1 1

# Run example 3 with PR #5
python3 app/agents/examples.py 3 5
```

## 5. Use in Your Code

```python
import asyncio
from app.agents.context_agent import context_agent

async def analyze_pr(pr_number: int):
    query = f"Analyze pull request #{pr_number} and summarize the changes"
    
    response_stream = await context_agent.astream_chat(query)
    
    async for event in response_stream.async_response_gen():
        print(event, end="", flush=True)
    
    print("\n\nDone!")

# Run it
asyncio.run(analyze_pr(1))
```

## Troubleshooting

### "Missing required environment variables"

Make sure your `.env` file is in the project root directory and contains all required variables.

### "Failed to fetch PR details"

1. Check that the PR number exists in your repository
2. Verify your GitHub token has the correct permissions
3. Make sure the repository configuration in `context_agent.py` is correct:
   ```python
   GITHUB_REPO_OWNER = "sangi29985"
   GITHUB_REPO_NAME = "recipes-api"
   ```

### "Module not found" errors

Make sure you installed all dependencies:
```bash
pip install -r app/agents/requirements.txt
```

### "API rate limit exceeded"

GitHub has rate limits. Wait a bit and try again, or use a different token.

## What's Next?

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🔍 Explore [examples.py](examples.py) to see different usage patterns
- 🛠️ Modify the agent's system prompt in `context_agent.py` to customize behavior
- ➕ Add more tools to extend the agent's capabilities

## Need Help?

- Check the [README.md](README.md) for comprehensive documentation
- Review the [examples.py](examples.py) for usage patterns
- Run `python3 app/agents/verify_setup.py` to diagnose setup issues

---

**Happy coding! 🚀**
