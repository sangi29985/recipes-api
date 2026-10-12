# Getting Started Checklist

Use this checklist to get your Context Manager Agent System up and running!

---

## ✅ Installation & Setup

- [ ] **Install Python packages**
  ```bash
  pip install llama-index-core llama-index-llms-openai PyGithub python-dotenv
  ```
  Or use: `pip install -r app/agents/requirements.txt`

- [ ] **Get GitHub Token**
  - Go to: https://github.com/settings/tokens
  - Create new token with `repo` scope
  - Copy token

- [ ] **Get OpenAI API Key**
  - Go to: https://platform.openai.com/api-keys
  - Create new secret key
  - Copy key

- [ ] **Configure .env file**
  - Open `.env` in project root
  - Replace `your-openai-api-key-here` with your actual key
  - Save file
  - ✅ GITHUB_TOKEN should already be configured

- [ ] **Verify setup**
  ```bash
  python3 app/agents/verify_setup.py
  ```
  All checks should pass! ✅

---

## 🚀 First Run

- [ ] **Run the basic agent**
  ```bash
  python3 app/agents/context_agent.py
  ```
  - Should analyze PR #1
  - Watch the agent work in real-time
  - See the final comprehensive response

- [ ] **Try the examples**
  ```bash
  python3 app/agents/examples.py
  ```
  - Runs all 6 examples
  - Shows different usage patterns
  - Demonstrates capabilities

- [ ] **Run a specific example**
  ```bash
  python3 app/agents/examples.py 1 1
  ```
  - First number: example number (1-6)
  - Second number: PR number

---

## 📖 Learn the System

- [ ] **Read QUICKSTART.md**
  - 5-minute guide
  - All essential information
  - Common troubleshooting

- [ ] **Skim README.md**
  - Comprehensive documentation
  - Architecture overview
  - Advanced usage patterns

- [ ] **Review examples.py code**
  - See how to use the agent
  - Learn different query patterns
  - Understand async/await usage

---

## 🔧 Customize (Optional)

- [ ] **Change target repository**
  - Edit `context_agent.py`
  - Modify `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME`
  - Ensure your GitHub token has access

- [ ] **Customize agent behavior**
  - Edit the `system_prompt` in `context_agent.py`
  - Tell the agent what to focus on
  - Guide its reasoning process

- [ ] **Try different OpenAI models**
  - Edit `OPENAI_MODEL` in `.env`
  - Options: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
  - GPT-4 recommended for best results

- [ ] **Add new tools**
  - Create new function in `context_agent.py`
  - Add proper docstring (LLM reads this!)
  - Wrap with `FunctionTool.from_defaults()`
  - Add to agent's tools list

---

## 🎯 Use Cases to Try

- [ ] **Analyze a specific PR**
  ```python
  await context_agent.astream_chat("Analyze PR #5 and summarize changes")
  ```

- [ ] **Focus on specific files**
  ```python
  await context_agent.astream_chat(
      "Get PR #3 and show me what changed in models.py"
  )
  ```

- [ ] **Multi-turn investigation**
  ```python
  # First question
  await context_agent.astream_chat("What files changed in PR #2?")
  # Follow-up
  await context_agent.astream_chat("Show me the first file's contents")
  ```

- [ ] **Direct tool usage**
  ```python
  from app.agents.context_agent import get_pr_details
  details = get_pr_details(1)
  print(details)
  ```

---

## 🐛 Troubleshooting

If something doesn't work:

- [ ] **Run verification script**
  ```bash
  python3 app/agents/verify_setup.py
  ```
  - Shows exactly what's wrong
  - Checks packages, env vars, imports

- [ ] **Check .env file**
  - File exists in project root?
  - OPENAI_API_KEY is your actual key?
  - GITHUB_TOKEN is present?

- [ ] **Verify PR exists**
  - Visit: https://github.com/sangi29985/recipes-api/pulls/[NUMBER]
  - Does the PR exist?
  - Is the repository correct?

- [ ] **Check network access**
  - Can you reach api.github.com?
  - Can you reach api.openai.com?
  - Any firewall/proxy issues?

---

## 📚 Documentation Reference

Quick links to documentation:

| Need | Read This | Time |
|------|-----------|------|
| Quick setup | [QUICKSTART.md](QUICKSTART.md) | 5 min |
| Full guide | [README.md](README.md) | 20 min |
| System design | [ARCHITECTURE.md](ARCHITECTURE.md) | 15 min |
| Usage examples | [examples.py](examples.py) | 10 min |
| Everything | [INDEX.md](INDEX.md) | 5 min |

---

## ✨ Success Criteria

You're ready when:

- ✅ All verification checks pass
- ✅ Basic agent runs successfully
- ✅ You understand the examples
- ✅ You can analyze different PRs
- ✅ You know how to customize behavior

---

## 🎉 You're Done!

Once you've completed this checklist, you have a fully functional multi-agent system!

**What you can do now:**
- Analyze any PR in your repository
- Ask natural language questions about code changes
- Build custom workflows and automation
- Extend with new tools and capabilities
- Create specialized agents for different tasks

**Next level:**
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the design
- Study how the ReAct pattern works
- Add tools for code quality checks
- Build a reviewer agent
- Create multi-agent workflows

---

**Need help?** Check [INDEX.md](INDEX.md) for navigation or [README.md](README.md) for troubleshooting.

**Questions?** All answers are in the documentation files we created!

---

*Created: October 6, 2026*  
*System Status: ✅ Ready for Production*
