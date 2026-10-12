# Context Manager Agent System - Complete Index

**Welcome to the Context Manager Agent System!** This index will help you navigate all the files and find exactly what you need.

---

## 🚀 Quick Start (Start Here!)

| File | Purpose | When to Use |
|------|---------|-------------|
| **[QUICKSTART.md](QUICKSTART.md)** | 5-minute setup guide | First time setup |
| **[verify_setup.py](verify_setup.py)** | Check your installation | After installation |
| **[context_agent.py](context_agent.py)** | Run basic example | Test the system |

**First time? Go here:** [QUICKSTART.md](QUICKSTART.md)

---

## 📖 Documentation

### For Users

| File | What's Inside | Best For |
|------|---------------|----------|
| **[README.md](README.md)** | Complete documentation with architecture, usage, troubleshooting | Understanding the full system |
| **[QUICKSTART.md](QUICKSTART.md)** | Step-by-step setup instructions | Getting started quickly |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Visual diagrams and system design | Understanding how it works |

### For Developers

| File | What's Inside | Best For |
|------|---------------|----------|
| **[SUMMARY.md](SUMMARY.md)** | Implementation details and completeness checklist | Project overview |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Component interactions and data flows | System design understanding |
| **[requirements.txt](requirements.txt)** | All dependencies with versions | Dependency management |

---

## 💻 Code Files

### Core Implementation

**[context_agent.py](context_agent.py)** - Main Agent System (250+ lines)

```python
# What's inside:
- Tool Functions:
  • get_pr_details(pr_number)          # Fetch PR metadata
  • get_pr_commit_details(head_sha)    # Get commit changes
  • get_file_contents(file_path, ref)  # Read repository files

- LlamaIndex Integration:
  • FunctionTool wrappers              # Convert functions to tools
  • OpenAI LLM configuration           # GPT-4 setup
  • ReActAgent creation                # Main agent setup
  
- Async Execution:
  • Event streaming                    # Real-time progress
  • Error handling                     # Graceful failures
  • Main entry point                   # Command-line interface
```

**When to edit:**
- Change repository (GITHUB_REPO_OWNER, GITHUB_REPO_NAME)
- Modify agent behavior (system_prompt)
- Add new tools (create function + wrap with FunctionTool)

### Examples and Testing

**[examples.py](examples.py)** - Usage Examples (370+ lines)

```python
# Six complete examples:

Example 1: Basic PR Analysis
  • Simple query to get all PR context

Example 2: Focused File Analysis
  • Target specific files in a PR

Example 3: Comprehensive Change Summary
  • Detailed analysis with statistics

Example 4: Direct Tool Usage
  • Use tools without the agent

Example 5: Multi-turn Conversation
  • Back-and-forth with the agent

Example 6: Error Handling
  • How errors are handled gracefully
```

**How to run:**
```bash
# All examples
python3 app/agents/examples.py

# Specific example with specific PR
python3 app/agents/examples.py 1 5  # Example 1, PR #5
```

**[verify_setup.py](verify_setup.py)** - Setup Verification (170+ lines)

```python
# Checks:
✅ Python version (>= 3.8)
✅ All required packages installed
✅ Environment variables configured
✅ Agent module can be imported
✅ Tools are available
```

**When to run:**
- After initial installation
- When something doesn't work
- After changing configuration
- Before deploying

---

## 📋 Configuration Files

**[requirements.txt](requirements.txt)** - Python Dependencies

```
llama-index-core>=0.14.0       # Agent framework
llama-index-llms-openai>=0.8.0 # OpenAI integration
PyGithub>=2.0.0                # GitHub API client
python-dotenv>=1.0.0           # Environment management
openai>=1.0.0                  # OpenAI SDK
```

**[../.env](../../.env)** - Environment Variables (in project root)

```env
GITHUB_TOKEN=...         # ✅ Already configured
OPENAI_API_KEY=...       # ⚠️  Needs your key
OPENAI_MODEL=gpt-4       # ✅ Configured
OPENAI_BASE_URL=...      # ✅ Configured
```

---

## 🎯 Common Tasks

### Task 1: Run Your First Analysis

1. Read: [QUICKSTART.md](QUICKSTART.md) (5 minutes)
2. Add your OpenAI key to `.env`
3. Run: `python3 app/agents/verify_setup.py`
4. Run: `python3 app/agents/context_agent.py`

### Task 2: Analyze a Specific PR

**Option A: Edit and Run**
```bash
# Edit context_agent.py, change PR_NUMBER = 1 to your PR number
python3 app/agents/context_agent.py
```

**Option B: Use Examples**
```bash
# Run example 1 with PR #5
python3 app/agents/examples.py 1 5
```

**Option C: Write Custom Code**
```python
from app.agents.context_agent import context_agent
import asyncio

async def my_analysis():
    response = await context_agent.astream_chat("Analyze PR #5")
    async for event in response.async_response_gen():
        print(event, end="", flush=True)

asyncio.run(my_analysis())
```

### Task 3: Add a New Tool

1. **Define function in context_agent.py:**
```python
def my_new_tool(param: str) -> dict:
    """
    Clear description of what this tool does.
    The LLM reads this to understand when to use it.
    
    Args:
        param: Description of parameter
        
    Returns:
        Dictionary with results
    """
    # Your implementation
    return {"result": "data"}
```

2. **Wrap it as a tool:**
```python
my_new_tool_wrapped = FunctionTool.from_defaults(fn=my_new_tool)
```

3. **Add to agent:**
```python
context_agent = ReActAgent.from_tools(
    tools=[
        get_pr_details_tool,
        get_pr_commit_details_tool,
        get_file_contents_tool,
        my_new_tool_wrapped,  # Add here
    ],
    llm=llm,
    verbose=True,
    system_prompt="..."
)
```

### Task 4: Change Target Repository

Edit `context_agent.py`:
```python
# Change these lines:
GITHUB_REPO_OWNER = "your-username"
GITHUB_REPO_NAME = "your-repo-name"
```

### Task 5: Customize Agent Behavior

Edit the `system_prompt` in `context_agent.py`:
```python
context_agent = ReActAgent.from_tools(
    tools=[...],
    llm=llm,
    system_prompt="""
    Your custom instructions here.
    Tell the agent what to focus on,
    how to behave, and what to prioritize.
    """
)
```

### Task 6: Use Different OpenAI Model

Edit `.env`:
```env
# Options: gpt-4, gpt-4-turbo, gpt-3.5-turbo
OPENAI_MODEL=gpt-3.5-turbo
```

Or in code:
```python
llm = OpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY")
)
```

---

## 🔍 Troubleshooting Guide

### Problem: "Missing required environment variables"

**Solution:**
1. Check `.env` file exists in project root
2. Ensure it contains `GITHUB_TOKEN` and `OPENAI_API_KEY`
3. Run: `python3 app/agents/verify_setup.py`

**Reference:** [QUICKSTART.md - Step 2](QUICKSTART.md#2-configure-environment-variables)

### Problem: "Failed to fetch PR details"

**Possible Causes:**
1. PR number doesn't exist
2. GitHub token lacks permissions
3. Repository name is wrong

**Solution:**
1. Verify PR exists: `https://github.com/sangi29985/recipes-api/pulls/1`
2. Check token: `https://github.com/settings/tokens`
3. Check repo config in `context_agent.py`

**Reference:** [README.md - Troubleshooting](README.md#troubleshooting)

### Problem: "Module not found" or Import Errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r app/agents/requirements.txt

# Verify installation
python3 app/agents/verify_setup.py
```

**Reference:** [QUICKSTART.md - Step 1](QUICKSTART.md#1-install-dependencies)

### Problem: Agent gives wrong or incomplete answers

**Possible Causes:**
1. System prompt not clear enough
2. Missing tools
3. Model is too weak (use GPT-4)

**Solution:**
1. Enhance system prompt with specific instructions
2. Add specialized tools for missing functionality
3. Ensure `OPENAI_MODEL=gpt-4` in `.env`

**Reference:** [README.md - Advanced Usage](README.md#advanced-usage)

---

## 📊 File Statistics

```
Total Lines: ~1,936

Breakdown:
- Python Code:     ~800 lines
- Documentation:   ~1,100 lines
- Configuration:   ~30 lines

Files Created:     8
Dependencies:      5 packages
```

---

## 🎓 Learning Path

### Beginner Path

1. ✅ Read [QUICKSTART.md](QUICKSTART.md)
2. ✅ Run [verify_setup.py](verify_setup.py)
3. ✅ Run [context_agent.py](context_agent.py)
4. ✅ Try [examples.py](examples.py) - all 6 examples

### Intermediate Path

5. ✅ Read [README.md](README.md) - full documentation
6. ✅ Study [context_agent.py](context_agent.py) code
7. ✅ Modify agent's system prompt
8. ✅ Analyze different PRs
9. ✅ Write custom queries

### Advanced Path

10. ✅ Read [ARCHITECTURE.md](ARCHITECTURE.md)
11. ✅ Add new tools
12. ✅ Create specialized agents
13. ✅ Integrate with CI/CD
14. ✅ Build multi-agent workflows

---

## 🔗 External Resources

### LlamaIndex
- [Official Documentation](https://docs.llamaindex.ai/)
- [ReAct Agent Guide](https://docs.llamaindex.ai/en/stable/examples/agent/react_agent/)
- [Function Tools](https://docs.llamaindex.ai/en/stable/module_guides/deploying/agents/tools/)

### PyGitHub
- [Documentation](https://pygithub.readthedocs.io/)
- [API Reference](https://pygithub.readthedocs.io/en/latest/github.html)

### GitHub REST API
- [Pull Requests API](https://docs.github.com/en/rest/pulls)
- [Commits API](https://docs.github.com/en/rest/commits)
- [Contents API](https://docs.github.com/en/rest/repos/contents)

### OpenAI
- [API Documentation](https://platform.openai.com/docs)
- [Model Pricing](https://openai.com/pricing)
- [API Keys](https://platform.openai.com/api-keys)

---

## 🎯 Next Steps

Based on your needs:

### For Testing
→ Go to [QUICKSTART.md](QUICKSTART.md)

### For Understanding
→ Go to [README.md](README.md)

### For Development
→ Go to [ARCHITECTURE.md](ARCHITECTURE.md)

### For Examples
→ Go to [examples.py](examples.py)

### For Debugging
→ Go to [verify_setup.py](verify_setup.py)

---

## 📞 Support

If you get stuck:

1. **Check Documentation**
   - Start with [QUICKSTART.md](QUICKSTART.md)
   - Read relevant section in [README.md](README.md)
   - Review [ARCHITECTURE.md](ARCHITECTURE.md) for design

2. **Run Diagnostics**
   ```bash
   python3 app/agents/verify_setup.py
   ```

3. **Test with Examples**
   ```bash
   python3 app/agents/examples.py
   ```

4. **Review Error Messages**
   - Most errors include helpful hints
   - Check the troubleshooting sections

---

**📚 Complete File List:**

```
app/agents/
├── __init__.py              # Package initialization
├── context_agent.py         # 🔧 Main implementation
├── examples.py              # 📚 Six usage examples
├── verify_setup.py          # ✅ Setup checker
├── requirements.txt         # 📦 Dependencies
├── README.md                # 📖 Full documentation
├── QUICKSTART.md            # 🚀 Quick start guide
├── SUMMARY.md               # 📊 Implementation summary
├── ARCHITECTURE.md          # 🏗️  System design
└── INDEX.md                 # 📑 This file
```

---

**Happy coding! 🎉**

*Last updated: October 6, 2026*
