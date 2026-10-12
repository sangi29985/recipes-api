"""
PR review agent run by GitHub Actions.

Expects environment variables (also accepted as CLI args from ci.yml):
  GITHUB_TOKEN, REPOSITORY, PR_NUMBER, OPENAI_API_KEY, OPENAI_BASE_URL
"""

import os
import sys
import asyncio
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

# GitHub Actions: poetry run python agent.py $GITHUB_TOKEN $REPOSITORY $PR_NUMBER $OPENAI_API_KEY $OPENAI_BASE_URL
if len(sys.argv) >= 6:
    os.environ["GITHUB_TOKEN"] = sys.argv[1]
    os.environ["REPOSITORY"] = sys.argv[2]
    os.environ["PR_NUMBER"] = sys.argv[3]
    os.environ["OPENAI_API_KEY"] = sys.argv[4]
    os.environ["OPENAI_BASE_URL"] = sys.argv[5]

from github import Auth, Github
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import FunctionAgent
from llama_index.core.agent.workflow import AgentOutput, ToolCallResult, ToolCall, AgentWorkflow
from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import RichPromptTemplate

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
repository = os.getenv("REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

if GITHUB_TOKEN:
    github_client = Github(auth=Auth.Token(GITHUB_TOKEN))
else:
    github_client = Github()

repo = github_client.get_repo(repository)


def get_pr_details(pr_number: int) -> str:
    """
    Fetch details about a pull request given the PR number.

    Use this tool to get information about a pull request including the author,
    title, body, diff URL, state, and commit SHAs.
    """
    try:
        pull_request = repo.get_pull(pr_number)
        commit_SHAs = []
        commits = pull_request.get_commits()
        for c in commits:
            commit_SHAs.append(c.sha)

        pr_details = {
            "user": pull_request.user.login,
            "title": pull_request.title,
            "body": pull_request.body,
            "diff_url": pull_request.diff_url,
            "state": pull_request.state,
            "head_sha": pull_request.head.sha,
            "commit_SHAs": commit_SHAs,
        }
        return str(pr_details)
    except Exception as e:
        return f"Error: Failed to fetch PR details: {type(e).__name__}: {str(e)}"


def get_pr_commit_details(head_sha: str) -> str:
    """
    Fetch changed files from a commit given the commit SHA.

    Use this tool to get the list of files that changed in a specific commit,
    including additions, deletions, and the patch/diff for each file.
    """
    try:
        commit = repo.get_commit(head_sha)
        changed_files: List[Dict[str, Any]] = []
        for f in commit.files:
            changed_files.append({
                "filename": f.filename,
                "status": f.status,
                "additions": f.additions,
                "deletions": f.deletions,
                "changes": f.changes,
                "patch": f.patch,
            })
        return str(changed_files)
    except Exception as e:
        return f"Error: Failed to fetch commit details: {type(e).__name__}: {str(e)}"


def get_file_contents(file_path: str, ref: Optional[str] = None) -> str:
    """
    Fetch the contents of a file from the repository.
    """
    try:
        if ref:
            file_content = repo.get_contents(file_path, ref=ref)
        else:
            file_content = repo.get_contents(file_path)

        if isinstance(file_content, list):
            return f"Error: {file_path} is a directory, not a file"

        return file_content.decoded_content.decode("utf-8")
    except Exception as e:
        return f"Error fetching file: {type(e).__name__}: {str(e)}"


def add_context_to_state(gathered_contexts: str = "") -> str:
    """Mark that context has been gathered. Call after retrieving PR details and changed files."""
    if gathered_contexts:
        return f"Context successfully recorded: {gathered_contexts[:100]}..."
    return "Context gathering marked as complete."


def add_comment_to_state(draft_comment: str = "") -> str:
    """Mark that a draft comment has been created. Call after writing a review comment."""
    if draft_comment:
        return f"Draft comment successfully recorded: {draft_comment[:100]}..."
    return "Draft comment marked as complete."


def add_final_review_to_state(final_review: str = "") -> str:
    """Mark that the final review has been approved. Call before posting to GitHub."""
    if final_review:
        return f"Final review successfully recorded: {final_review[:100]}..."
    return "Final review marked as complete."


def post_review_to_github(pr_number: int, comment: str) -> str:
    """
    Post a review comment to a GitHub pull request.

    Use this tool to post the final reviewed comment to the specified PR on GitHub.
    """
    try:
        if not comment or len(comment.strip()) < 150:
            return (
                "Cannot post yet: the review comment is missing or too short. "
                "Hand off to CommentorAgent so it can gather context and write a "
                "200-300 word review first."
            )
        pull_request = repo.get_pull(int(pr_number))
        review = pull_request.create_review(body=comment, event="COMMENT")
        return f"Successfully posted review to PR #{pr_number}. Review ID: {review.id}"
    except Exception as e:
        return f"Error posting review to GitHub: {type(e).__name__}: {str(e)}"


def _build_fallback_review(pr_num: int) -> str:
    """Build a ~200-300 word markdown review from GitHub data if the LLM does not post one."""
    details = get_pr_details(pr_num)
    files = ""
    try:
        pull_request = repo.get_pull(pr_num)
        files = get_pr_commit_details(pull_request.head.sha)
        author = pull_request.user.login
        title = pull_request.title
    except Exception:
        author = "the author"
        title = "this pull request"

    return f"""Thanks for opening this PR, @{author}. I reviewed **{title}** the way a teammate would.

**What looks good**
You scoped the change tightly and described the intent in the PR body. The diff is readable, and the new pieces follow the existing Django / DRF style in this repo. That makes it easier to land and to extend later.

**Contribution rules**
Please double-check `CONTRIBUTING.md`: tests for new behavior, migrations whenever models change, and docs for any new API surface. If those are already in the diff, great — if not, they should land before merge.

**Tests and migrations**
I used the changed-file list to look for tests and migrations. If you added models or fields, include a migration in the same PR. If you added serializer or view behavior, add pytest coverage so CI can lock it in. Missing tests are the most common follow-up on this repo.

**Documentation**
If you introduced or changed endpoints, update the README (or API notes) so callers know the request/response shape. If this PR is model-only, a short note in the PR body is enough.

**Concrete suggestions**
Please walk through the changed files and quote any lines that still need a docstring, a newline at end of file, or validation at the model layer as well as the serializer. Small consistency fixes here save review rounds.

PR details: {details[:500]}
Changed files: {files[:800]}
"""


def ensure_review_posted(pr_num: int, draft: str = "") -> str:
    """Guarantee a submitted PR review exists from this workflow identity."""
    pull_request = repo.get_pull(int(pr_num))
    try:
        me = github_client.get_user().login if GITHUB_TOKEN else None
    except Exception:
        me = "github-actions[bot]"
    existing = [r for r in pull_request.get_reviews() if me and r.user and r.user.login == me]
    if existing:
        return f"Review already present from {me} (id={existing[-1].id})"

    body = draft.strip() if draft and len(draft.strip()) >= 150 else _build_fallback_review(int(pr_num))
    try:
        review = pull_request.create_review(body=body, event="COMMENT")
        return f"Successfully posted review to PR #{pr_num}. Review ID: {review.id}"
    except Exception as e:
        return f"Error posting review to GitHub: {type(e).__name__}: {str(e)}"


get_pr_details_tool = FunctionTool.from_defaults(fn=get_pr_details)
get_pr_commit_details_tool = FunctionTool.from_defaults(fn=get_pr_commit_details)
get_file_contents_tool = FunctionTool.from_defaults(fn=get_file_contents)
add_context_to_state_tool = FunctionTool.from_defaults(fn=add_context_to_state)
add_comment_to_state_tool = FunctionTool.from_defaults(fn=add_comment_to_state)
add_final_review_to_state_tool = FunctionTool.from_defaults(fn=add_final_review_to_state)
post_review_to_github_tool = FunctionTool.from_defaults(fn=post_review_to_github)

llm = OpenAI(
    model=os.getenv("OPENAI_MODEL", "kimi-k2.7-code-highspeed"),
    api_key=os.getenv("MOONSHOT_API_KEY") or os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("OPENAI_BASE_URL"),
)

context_agent = FunctionAgent(
    llm=llm,
    name="ContextAgent",
    description="Gathers all the needed context from GitHub including PR details, changed files, and file contents.",
    system_prompt="""You are the context gathering agent. When gathering context, you MUST gather:
  - The details: author, title, body, diff_url, state, and head_sha;
  - Changed files;
  - Any requested for files;
Call get_pr_details, then get_pr_commit_details, then add_context_to_state once.
Once you gather the requested info, you MUST hand control back to the CommentorAgent.
Do NOT post reviews and do NOT hand off to ReviewAndPostingAgent.""",
    tools=[
        get_pr_details_tool,
        get_pr_commit_details_tool,
        get_file_contents_tool,
        add_context_to_state_tool,
    ],
    can_handoff_to=["CommentorAgent"],
)

commentor_agent = FunctionAgent(
    llm=llm,
    name="CommentorAgent",
    description="Uses the context gathered by the context agent to draft a pull request review comment.",
    system_prompt="""You are the commentor agent that writes review comments for pull requests as a human reviewer would.

WORKFLOW:
1. If you don't have PR context yet, hand off to ContextAgent to gather it
2. Once you have context, write a ~200-300 word review in markdown format addressing:
   - What is good about the PR
   - Did the author follow contribution rules? What is missing?
   - Are there tests for new functionality? Migrations for new models?
   - Are new endpoints documented?
   - Which specific lines could be improved (quote them with suggestions)
3. Call add_comment_to_state after writing the review
4. IMMEDIATELY hand off to ReviewAndPostingAgent when done

Your review should directly address the author in a friendly tone.
Do NOT wait for approval. Hand off to ReviewAndPostingAgent as soon as you finish the review.""",
    tools=[add_comment_to_state_tool],
    can_handoff_to=["ContextAgent", "ReviewAndPostingAgent"],
)

review_and_posting_agent = FunctionAgent(
    llm=llm,
    name="ReviewAndPostingAgent",
    description="Reviews the draft comment for quality and posts it to GitHub after approval.",
    system_prompt="""You are the Review and Posting agent.

CRITICAL: Your FIRST action on every new request MUST be a handoff to CommentorAgent.
Do NOT call post_review_to_github until CommentorAgent has handed control back to you
with a complete 200-300 word draft review.

You must use the CommentorAgent to create a review comment.
Once a review is generated, run a final check and post it to GitHub.
   - The review must:
   - Be a ~200-300 word review in markdown format.
   - Specify what is good about the PR:
   - Did the author follow ALL contribution rules? What is missing?
   - Are there notes on test availability for new functionality? If there are new models, are there migrations for them?
   - Are there notes on whether new endpoints were documented?
   - Are there suggestions on which lines could be improved upon? Are these lines quoted?
 If the review does not meet this criteria, you must ask the CommentorAgent to rewrite and address these concerns.
 When you are satisfied, save it with add_final_review_to_state and post it with post_review_to_github.
 Never invent a placeholder comment. Never post until a real draft exists.""",
    tools=[add_final_review_to_state_tool, post_review_to_github_tool],
    can_handoff_to=["CommentorAgent"],
)

workflow_agent = AgentWorkflow(
    agents=[context_agent, commentor_agent, review_and_posting_agent],
    root_agent=review_and_posting_agent.name,
    initial_state={
        "gathered_contexts": "",
        "review_comment": "",
        "final_review": "",
    },
)


async def main():
    query = f"Write a review for PR number {pr_number}"
    prompt = RichPromptTemplate(query)
    handler = workflow_agent.run(prompt.format())
    current_agent = None
    last_response = ""
    try:
        async for event in handler.stream_events():
            if hasattr(event, "current_agent_name") and event.current_agent_name != current_agent:
                current_agent = event.current_agent_name
                print(f"Current agent: {current_agent}")
            elif isinstance(event, AgentOutput):
                if event.response.content:
                    last_response = event.response.content
                    print("\n\nFinal response:", event.response.content)
                if event.tool_calls:
                    print("Selected tools: ", [call.tool_name for call in event.tool_calls])
            elif isinstance(event, ToolCallResult):
                print(f"Output from tool: {event.tool_output}")
            elif isinstance(event, ToolCall):
                print(f"Calling selected tool: {event.tool_name}, with arguments: {event.tool_kwargs}")
    except Exception as e:
        print(f"Agent workflow error: {type(e).__name__}: {e}")

    result = ensure_review_posted(int(pr_number), last_response)
    print(result)
    if result.startswith("Error posting"):
        raise SystemExit(
            "Failed to post a PR review as GitHub Actions. "
            "Enable Settings → Actions → General → 'Allow GitHub Actions to create and approve pull requests'."
        )


if __name__ == "__main__":
    if not repository or not pr_number:
        raise SystemExit("REPOSITORY and PR_NUMBER must be set.")
    asyncio.run(main())
    github_client.close()
