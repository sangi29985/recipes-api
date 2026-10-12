"""
Main entry point for the Multi-Agent PR Review System.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from github import Auth, Github
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import FunctionAgent
from llama_index.core.agent.workflow import AgentOutput, ToolCallResult, ToolCall, AgentWorkflow
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import RichPromptTemplate
from typing import Dict, List, Optional, Any

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
repo_url = "https://github.com/sangi29985/recipes-api.git"

# Parse repo info from URL
repo_name = repo_url.split('/')[-1].replace('.git', '')
username = repo_url.split('/')[-2]
full_repo_name = f"{username}/{repo_name}"

# Initialize GitHub client  
auth = Auth.Token(GITHUB_TOKEN)
github_client = Github(auth=auth)
repo = github_client.get_repo(full_repo_name)


# Tool Functions for GitHub API
def get_pr_details(pr_number: int) -> str:
    """
    Fetch details about a pull request given the PR number.
    
    Use this tool to get information about a pull request including the author,
    title, body, diff URL, state, and commit SHAs.
    
    Args:
        pr_number: The number of the pull request to retrieve.
        
    Returns:
        A string containing PR details in a readable format.
    """
    try:
        pull_request = repo.get_pull(pr_number)
        
        # Get commit SHAs
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
            "commit_SHAs": commit_SHAs
        }
        
        return str(pr_details)
        
    except Exception as e:
        return f"Error: Failed to fetch PR details: {type(e).__name__}: {str(e)}"


def get_pr_commit_details(head_sha: str) -> str:
    """
    Fetch changed files from a commit given the commit SHA.
    
    Use this tool to get the list of files that changed in a specific commit,
    including additions, deletions, and the patch/diff for each file.
    
    Args:
        head_sha: The SHA of the commit to retrieve details for.
        
    Returns:
        A string representation of the list of changed files with their details.
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
        
        # Return just the list of changed files, not wrapped in a dictionary
        return str(changed_files)
        
    except Exception as e:
        return f"Error: Failed to fetch commit details: {type(e).__name__}: {str(e)}"


def get_file_contents(file_path: str, ref: Optional[str] = None) -> str:
    """
    Fetch the contents of a file from the repository.
    
    Use this tool to retrieve the contents of any file in the repository.
    
    Args:
        file_path: The path to the file in the repository.
        ref: Optional branch, tag, or commit SHA. Defaults to the default branch.
        
    Returns:
        The file contents as a string.
    """
    try:
        if ref:
            file_content = repo.get_contents(file_path, ref=ref)
        else:
            file_content = repo.get_contents(file_path)
        
        if isinstance(file_content, list):
            return f"Error: {file_path} is a directory, not a file"
        
        content = file_content.decoded_content.decode('utf-8')
        return content
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error fetching file: {type(e).__name__}: {str(e)}\n{error_details}"


# State Management Functions
def add_context_to_state(gathered_contexts: str = "") -> str:
    """
    Mark that context has been gathered. Call this after retrieving PR details and changed files.
    
    Use this tool to indicate that you have finished gathering context from GitHub.
    You should call this after successfully retrieving PR details and changed files.
    
    Args:
        gathered_contexts: Summary of what context was gathered (optional).
        
    Returns:
        A confirmation message that context was recorded.
    """
    if gathered_contexts:
        return f"Context successfully recorded: {gathered_contexts[:100]}..."
    return "Context gathering marked as complete."


def add_comment_to_state(draft_comment: str = "") -> str:
    """
    Mark that a draft comment has been created. Call this after writing a review comment.
    
    Use this tool to indicate that you have finished drafting the review comment.
    
    Args:
        draft_comment: The draft review comment text (optional).
        
    Returns:
        A confirmation message that the draft was recorded.
    """
    if draft_comment:
        return f"Draft comment successfully recorded: {draft_comment[:100]}..."
    return "Draft comment marked as complete."


def add_final_review_to_state(final_review: str = "") -> str:
    """
    Mark that final review has been approved. Call this before posting to GitHub.
    
    Use this tool to indicate that the review has been approved and is ready to post.
    
    Args:
        final_review: The final review comment text (optional).
        
    Returns:
        A confirmation message that the final review was recorded.
    """
    if final_review:
        return f"Final review successfully recorded: {final_review[:100]}..."
    return "Final review marked as complete."


def post_review_to_github(pr_number: int, comment: str) -> str:
    """
    Post a review comment to a GitHub pull request.
    
    Use this tool to post the final reviewed comment to the specified PR on GitHub.
    
    Args:
        pr_number: The number of the pull request to post the review to.
        comment: The review comment text to post (markdown format).
        
    Returns:
        A confirmation message about the posting status.
    """
    try:
        if not comment or len(comment.strip()) < 150:
            return (
                "Cannot post yet: the review comment is missing or too short. "
                "Hand off to CommentorAgent so it can gather context and write a "
                "200-300 word review first."
            )
        pull_request = repo.get_pull(pr_number)
        # Submit a visible PR review. event=COMMENT is required so the review
        # is not left pending (pending reviews are hidden from get_reviews()).
        review = pull_request.create_review(body=comment, event="COMMENT")
        return f"Successfully posted review to PR #{pr_number}. Review ID: {review.id}"
    except Exception as e:
        return f"Error posting review to GitHub: {type(e).__name__}: {str(e)}"


# Convert functions to LlamaIndex tools
get_pr_details_tool = FunctionTool.from_defaults(fn=get_pr_details)
get_pr_commit_details_tool = FunctionTool.from_defaults(fn=get_pr_commit_details)
get_file_contents_tool = FunctionTool.from_defaults(fn=get_file_contents)
add_context_to_state_tool = FunctionTool.from_defaults(fn=add_context_to_state)
add_comment_to_state_tool = FunctionTool.from_defaults(fn=add_comment_to_state)
add_final_review_to_state_tool = FunctionTool.from_defaults(fn=add_final_review_to_state)
post_review_to_github_tool = FunctionTool.from_defaults(fn=post_review_to_github)


# Initialize LLM via LiteLLM (Moonshot Kimi models)
llm = OpenAI(
    model=os.getenv("OPENAI_MODEL", "kimi-k2.7-code-highspeed"),
    api_key=os.getenv("MOONSHOT_API_KEY") or os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("OPENAI_BASE_URL", "https://litellm.aks-hs-prod.int.hyperskill.org/")
)


# Create ContextAgent using FunctionAgent
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
        add_context_to_state_tool
    ],
    can_handoff_to=["CommentorAgent"]
)


# Create CommentorAgent using FunctionAgent
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

Your review should directly address the author in a friendly tone like:
"Thanks for fixing this. I think all places where we call quote should be fixed. Can you roll this fix out everywhere?"

Do NOT wait for approval. Hand off to ReviewAndPostingAgent as soon as you finish the review.""",
    tools=[add_comment_to_state_tool],
    can_handoff_to=["ContextAgent", "ReviewAndPostingAgent"]
)


# Create ReviewAndPostingAgent using FunctionAgent
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
    can_handoff_to=["CommentorAgent"]
)


# Create AgentWorkflow to orchestrate the agents
workflow_agent = AgentWorkflow(
    agents=[context_agent, commentor_agent, review_and_posting_agent],
    root_agent=review_and_posting_agent.name,
    initial_state={
        "gathered_contexts": "",
        "review_comment": "",
        "final_review": ""
    },
)


async def main():
    query = input().strip()
    prompt = RichPromptTemplate(query)

    handler = workflow_agent.run(prompt.format())

    current_agent = None
    async for event in handler.stream_events():
        if hasattr(event, "current_agent_name") and event.current_agent_name != current_agent:
            current_agent = event.current_agent_name
            print(f"Current agent: {current_agent}")
        elif isinstance(event, AgentOutput):
            if event.response.content:
                print("\\n\\nFinal response:", event.response.content)
            if event.tool_calls:
                print("Selected tools: ", [call.tool_name for call in event.tool_calls])
        elif isinstance(event, ToolCallResult):
            print(f"Output from tool: {event.tool_output}")
        elif isinstance(event, ToolCall):
            print(f"Calling selected tool: {event.tool_name}, with arguments: {event.tool_kwargs}")


if __name__ == "__main__":
    asyncio.run(main())
    github_client.close()
