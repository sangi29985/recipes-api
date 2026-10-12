# Context Manager Agent System - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Context Manager Agent System                        │
│                    (LlamaIndex + PyGitHub + OpenAI)                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           User Interaction Layer                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │  context_agent   │  │   examples.py    │  │  Custom Scripts  │    │
│  │      .py         │  │  (6 examples)    │  │   (User Code)    │    │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘    │
│           │                     │                      │               │
│           └──────────────┬──────┴──────────────────────┘               │
│                          │                                             │
└──────────────────────────┼─────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ReActAgent (LlamaIndex)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  System Prompt:                                                         │
│  "You are the context gathering agent. When gathering context,          │
│   you MUST gather: PR details, changed files, and requested files."     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                    ReAct Loop (Reasoning)                     │     │
│  │                                                                │     │
│  │  1. Thought: What information do I need?                      │     │
│  │  2. Action: Select appropriate tool                           │     │
│  │  3. Action Input: Provide parameters                          │     │
│  │  4. Observation: Process tool results                         │     │
│  │  5. Repeat until goal achieved                                │     │
│  │  6. Final Answer: Synthesize and respond                      │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                                                         │
└──────────────────────────┬──────────────────┬───────────────────────────┘
                           │                  │
                           ▼                  ▼
           ┌───────────────────────┐  ┌──────────────────┐
           │    OpenAI LLM         │  │  Event Streaming  │
           │    (GPT-4)            │  │  (Async)          │
           ├───────────────────────┤  ├──────────────────┤
           │ - Reasoning           │  │ - Real-time      │
           │ - Planning            │  │   feedback       │
           │ - Tool selection      │  │ - Token-by-token │
           │ - Response synthesis  │  │ - Progress vis.  │
           └───────────────────────┘  └──────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Tool Layer (LlamaIndex)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐    │
│  │                  │  │                  │  │                  │    │
│  │  get_pr_details  │  │ get_pr_commit_   │  │ get_file_        │    │
│  │     _tool        │  │  details_tool    │  │  contents_tool   │    │
│  │                  │  │                  │  │                  │    │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤    │
│  │ Input:           │  │ Input:           │  │ Input:           │    │
│  │ - pr_number      │  │ - head_sha       │  │ - file_path      │    │
│  │                  │  │                  │  │ - ref (optional) │    │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤    │
│  │ Returns:         │  │ Returns:         │  │ Returns:         │    │
│  │ - author         │  │ - filename       │  │ - path           │    │
│  │ - title          │  │ - status         │  │ - content        │    │
│  │ - body           │  │ - additions      │  │ - encoding       │    │
│  │ - diff_url       │  │ - deletions      │  │ - sha            │    │
│  │ - state          │  │ - changes        │  │ - size           │    │
│  │ - head_sha       │  │ - patch          │  │                  │    │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘    │
│           │                     │                      │               │
└───────────┼─────────────────────┼──────────────────────┼───────────────┘
            │                     │                      │
            └─────────────┬───────┴──────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     GitHub API Layer (PyGitHub)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────────────────────────────────────────────┐        │
│  │              PyGitHub Client                               │        │
│  │                                                             │        │
│  │  Repository: sangi29985/recipes-api                        │        │
│  │  Authentication: GitHub Personal Access Token              │        │
│  │  Rate Limit: 5000 requests/hour                            │        │
│  └────────────────────────────────────────────────────────────┘        │
│                          │                                              │
│                          ▼                                              │
│  ┌────────────────────────────────────────────────────────────┐        │
│  │                   GitHub REST API v3                       │        │
│  │                                                             │        │
│  │  • GET /repos/{owner}/{repo}/pulls/{number}                │        │
│  │  • GET /repos/{owner}/{repo}/commits/{sha}                 │        │
│  │  • GET /repos/{owner}/{repo}/contents/{path}               │        │
│  └────────────────────────────────────────────────────────────┘        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      GitHub Repository                                  │
│                   sangi29985/recipes-api                                │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
User Query
    │
    │  "Gather context for PR #1"
    │
    ▼
┌──────────────────────┐
│   ReActAgent         │
│   (Entry Point)      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Thought Phase      │  "I need to get PR details first"
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Action Phase       │  Tool: get_pr_details
│                      │  Input: {"pr_number": 1}
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   GitHub API Call    │  GET /repos/.../pulls/1
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Observation        │  Result: {author, title, body, ...}
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Thought Phase      │  "Now I need the changed files"
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Action Phase       │  Tool: get_pr_commit_details
│                      │  Input: {"head_sha": "abc123..."}
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   GitHub API Call    │  GET /repos/.../commits/abc123...
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Observation        │  Result: [{filename, status, ...}]
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Thought Phase      │  "I have enough information"
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Final Answer       │  Comprehensive response with all context
└──────┬───────────────┘
       │
       ▼
    User
```

## Component Interaction Matrix

```
┌──────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│                  │  User    │  Agent   │   LLM    │  Tools   │  GitHub  │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ User             │    -     │  Query   │    -     │    -     │    -     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ ReActAgent       │ Response │    -     │ Prompts  │  Calls   │    -     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ OpenAI LLM       │    -     │ Reasons  │    -     │ Selects  │    -     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Tools            │    -     │ Results  │    -     │    -     │   API    │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ GitHub API       │    -     │    -     │    -     │   Data   │    -     │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         .env File                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GITHUB_TOKEN          ──────────────┐                          │
│  OPENAI_API_KEY        ─────────┐    │                          │
│  OPENAI_MODEL          ────┐    │    │                          │
│  OPENAI_BASE_URL       ──┐ │    │    │                          │
│                          │ │    │    │                          │
└──────────────────────────┼─┼────┼────┼──────────────────────────┘
                           │ │    │    │
                           │ │    │    │
         ┌─────────────────┘ │    │    │
         │         ┌─────────┘    │    │
         │         │              │    │
         ▼         ▼              ▼    ▼
    ┌────────┐ ┌──────┐     ┌────────────┐
    │ OpenAI │ │ LLM  │     │   GitHub   │
    │  SDK   │ │Config│     │   Client   │
    └────┬───┘ └───┬──┘     └─────┬──────┘
         │         │              │
         └────┬────┘              │
              │                   │
              ▼                   ▼
         ┌─────────┐        ┌──────────┐
         │ OpenAI  │        │  PyGitHub│
         │   LLM   │        │  Tools   │
         └────┬────┘        └─────┬────┘
              │                   │
              └────────┬──────────┘
                       │
                       ▼
                ┌──────────────┐
                │  ReActAgent  │
                └──────────────┘
```

## Error Handling Flow

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Try: Execute Agent              │
│                                         │
│  ┌────────────────────────────────┐    │
│  │  Try: Call Tool                │    │
│  │                                 │    │
│  │  ┌──────────────────────────┐  │    │
│  │  │  Try: GitHub API Call    │  │    │
│  │  └──────────────────────────┘  │    │
│  │           │                     │    │
│  │           ▼                     │    │
│  │  Except GithubException:        │    │
│  │  └─> Return error dict          │    │
│  └────────────────────────────────┘    │
│           │                             │
│           ▼                             │
│  Observe error in agent context         │
│  Agent can handle or report             │
│                                         │
└─────────────────────────────────────────┘
         │
         ▼
Except Exception:
└─> Print error and raise
         │
         ▼
┌─────────────────┐
│  User sees      │
│  clear error    │
│  message        │
└─────────────────┘
```

## File Organization

```
recipes-api/
│
├── .env                           # Environment configuration
│   ├── GITHUB_TOKEN               # ✅ Configured
│   ├── OPENAI_API_KEY             # ⚠️  Needs user input
│   ├── OPENAI_MODEL               # ✅ Configured
│   └── OPENAI_BASE_URL            # ✅ Configured
│
└── app/
    └── agents/                    # Agent system directory
        │
        ├── __init__.py            # Package initialization
        │
        ├── context_agent.py       # 🔧 Main implementation
        │   ├── Tool Functions     #    - get_pr_details()
        │   ├── LlamaIndex Tools   #    - get_pr_commit_details()
        │   ├── LLM Configuration  #    - get_file_contents()
        │   ├── Agent Creation     #    - ReActAgent setup
        │   └── Main Function      #    - Async streaming
        │
        ├── examples.py            # 📚 Usage examples
        │   ├── Example 1          #    - Basic analysis
        │   ├── Example 2          #    - Focused file analysis
        │   ├── Example 3          #    - Change summary
        │   ├── Example 4          #    - Direct tool usage
        │   ├── Example 5          #    - Multi-turn conversation
        │   └── Example 6          #    - Error handling
        │
        ├── verify_setup.py        # ✅ Setup verification
        │   ├── Package Check      #    - Dependency validation
        │   ├── Env Var Check      #    - Configuration check
        │   └── Import Test        #    - Module loading test
        │
        ├── requirements.txt       # 📦 Dependencies
        │   ├── llama-index-core
        │   ├── llama-index-llms-openai
        │   ├── PyGithub
        │   ├── python-dotenv
        │   └── openai
        │
        ├── README.md              # 📖 Full documentation
        ├── QUICKSTART.md          # 🚀 Quick start guide
        ├── SUMMARY.md             # 📊 Implementation summary
        └── ARCHITECTURE.md        # 🏗️  This file
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐ │
│  │  User Scripts  │  │  Examples      │  │  Agents      │ │
│  └────────────────┘  └────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                   Framework Layer                           │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │              LlamaIndex (v0.14+)                   │    │
│  │  • ReActAgent                                       │    │
│  │  • FunctionTool                                     │    │
│  │  • Event Streaming                                  │    │
│  │  • OpenAI Integration                               │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                   Integration Layer                         │
│                                                             │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │    PyGitHub      │              │   OpenAI SDK     │    │
│  │    (v2.0+)       │              │   (v1.0+)        │    │
│  └──────────────────┘              └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                              │
│                                                             │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │  GitHub REST API │              │   OpenAI API     │    │
│  │      (v3)        │              │    (GPT-4)       │    │
│  └──────────────────┘              └──────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                    Runtime Layer                            │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │            Python 3.8+ (async/await)               │    │
│  │  • asyncio                                          │    │
│  │  • aiohttp                                          │    │
│  │  • Type hints                                       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
└─────────────────────────────────────────────────────────────┘

1. Token Storage
   ┌───────────────┐
   │   .env file   │  • Git-ignored
   │               │  • Local filesystem only
   │  • GITHUB_    │  • Never committed
   │    TOKEN      │  • Masked in logs
   │  • OPENAI_    │
   │    API_KEY    │
   └───────────────┘

2. GitHub Authentication
   ┌───────────────┐
   │   PyGitHub    │  • Token-based auth
   │               │  • HTTPS only
   │  • Read-only  │  • Rate limited
   │    permissions│  • Scoped access
   └───────────────┘

3. OpenAI Communication
   ┌───────────────┐
   │  OpenAI API   │  • API key auth
   │               │  • HTTPS only
   │  • Encrypted  │  • Token counting
   │    transport  │  • Usage limits
   └───────────────┘

4. Code Execution
   ┌───────────────┐
   │   Local VM    │  • No remote exec
   │               │  • Sandboxed tools
   │  • Read-only  │  • Error handling
   │    GitHub ops │  • Input validation
   └───────────────┘
```

## Performance Characteristics

```
Operation                 Latency       Rate Limit    Notes
─────────────────────────────────────────────────────────────
get_pr_details()          ~200ms        5000/hour     1 API call
get_pr_commit_details()   ~300ms        5000/hour     1 API call
get_file_contents()       ~250ms        5000/hour     1 API call per file
Agent reasoning           ~1-2s         -             OpenAI API call
Full PR analysis          ~5-10s        -             Multiple tools
Multi-turn conversation   ~5-20s        -             Multiple reasoning steps
```

## Scalability Considerations

```
┌─────────────────────────────────────────────────────────────┐
│                  Current Implementation                     │
├─────────────────────────────────────────────────────────────┤
│  • Single repository                                        │
│  • Sequential tool execution                                │
│  • No caching                                               │
│  • Single agent instance                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Potential Enhancements                     │
├─────────────────────────────────────────────────────────────┤
│  • Multi-repository support                                 │
│  • Parallel tool execution                                  │
│  • GitHub data caching                                      │
│  • Multiple specialized agents                              │
│  • Workflow orchestration                                   │
│  • Result persistence                                       │
└─────────────────────────────────────────────────────────────┘
```

---

**This architecture diagram provides a comprehensive visual overview of the Context Manager Agent System, showing how all components interact and data flows through the system.**
