"""
Context Manager Agent System using LlamaIndex and PyGitHub.

This module implements a ReActAgent that gathers context from GitHub pull requests,
including PR details, commit information, and file contents.
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

from github import Github, GithubException, Auth
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from llama_index.core.agent.workflow import AgentOutput, ToolCallResult
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.prompts import RichPromptTemplate


# Load environment variables
load_dotenv()

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_OWNER = "sangi29985"
GITHUB_REPO_NAME = "recipes-api"

# Initialize GitHub client
auth = Auth.Token(GITHUB_TOKEN)
github_client = Github(auth=auth)
repo = github_client.get_repo(f"{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}")


# Tool Functions
def get_pr_details(pr_number: int) -> Dict[str, Any]:
    """
    Fetch details of a GitHub pull request.
    
    This function retrieves comprehensive information about a pull request including
    the author, title, description, diff URL, current state, and the HEAD commit SHA.
    
    Args:
        pr_number: The number of the pull request to fetch details for.
        
    Returns:
        A dictionary containing:
            - author: The username of the PR author
            - title: The PR title
            - body: The PR description/body text
            - diff_url: URL to view the PR diff
            - state: Current state of the PR (open/closed)
            - head_sha: The SHA of the HEAD commit
            
    Raises:
        GithubException: If the PR is not found or there's an API error.
    """
    try:
        pr = repo.get_pull(pr_number)
        
        return {
            "author": pr.user.login,
            "title": pr.title,
            "body": pr.body or "",
            "diff_url": pr.diff_url,
            "state": pr.state,
            "head_sha": pr.head.sha
        }
    except GithubException as e:
        return {"error": f"Failed to fetch PR details: {str(e)}"}


def get_pr_commit_details(head_sha: str) -> List[Dict[str, Any]]:
    """
    Fetch detailed information about all files changed in a commit.
    
    This function retrieves the complete list of files modified in a commit,
    including statistics about additions, deletions, and the actual code changes.
    
    Args:
        head_sha: The SHA hash of the commit to analyze.
        
    Returns:
        A list of dictionaries, each containing:
            - filename: Path to the changed file
            - status: Type of change (added/modified/removed/renamed)
            - additions: Number of lines added
            - deletions: Number of lines deleted
            - changes: Total number of line changes
            - patch: The actual diff/patch content (if available)
            
    Raises:
        GithubException: If the commit is not found or there's an API error.
    """
    try:
        commit = repo.get_commit(head_sha)
        files = commit.files
        
        file_details = []
        for file in files:
            file_details.append({
                "filename": file.filename,
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": getattr(file, 'patch', None)
            })
        
        return file_details
    except GithubException as e:
        return [{"error": f"Failed to fetch commit details: {str(e)}"}]


def get_file_contents(file_path: str, ref: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch the contents of a specific file from the repository.
    
    This function retrieves the content of any file in the repository,
    optionally from a specific branch, commit, or tag.
    
    Args:
        file_path: The path to the file within the repository.
        ref: Optional reference (branch name, commit SHA, or tag) to fetch from.
             If not provided, defaults to the repository's default branch.
             
    Returns:
        A dictionary containing:
            - path: The file path
            - content: The decoded file content as a string
            - encoding: The encoding used for the file
            - sha: The SHA hash of the file
            - size: File size in bytes
            
    Raises:
        GithubException: If the file is not found or there's an API error.
    """
    try:
        if ref:
            file_content = repo.get_contents(file_path, ref=ref)
        else:
            file_content = repo.get_contents(file_path)
        
        # Handle the case where get_contents returns a list (for directories)
        if isinstance(file_content, list):
            return {"error": f"{file_path} is a directory, not a file"}
        
        return {
            "path": file_content.path,
            "content": file_content.decoded_content.decode('utf-8'),
            "encoding": file_content.encoding,
            "sha": file_content.sha,
            "size": file_content.size
        }
    except GithubException as e:
        return {"error": f"Failed to fetch file contents: {str(e)}"}
    except UnicodeDecodeError:
        return {"error": f"File {file_path} appears to be binary and cannot be decoded as text"}


# Convert functions to LlamaIndex tools
get_pr_details_tool = FunctionTool.from_defaults(fn=get_pr_details)
get_pr_commit_details_tool = FunctionTool.from_defaults(fn=get_pr_commit_details)
get_file_contents_tool = FunctionTool.from_defaults(fn=get_file_contents)


# Initialize OpenAI LLM
llm = OpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4"),
    api_key=os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("OPENAI_BASE_URL")
)


# Create ContextAgent using ReActAgent
context_agent = ReActAgent(
    name="ContextAgent",
    description="Context gathering agent for GitHub pull requests",
    system_prompt="""You are the context gathering agent. When gathering context, you MUST gather:
- The details: author, title, body, diff_url, state, and head_sha
- Changed files
- Any requested files

Always provide comprehensive context by using the available tools to fetch all necessary information.
Start by getting the PR details, then fetch commit details to see what files changed, and finally
retrieve the contents of relevant files when needed.""",
    tools=[
        get_pr_details_tool,
        get_pr_commit_details_tool,
        get_file_contents_tool
    ],
    llm=llm,
    verbose=True
)


async def main():
    """
    Main entry point for the Context Agent system.
    
    This function runs the agent with event streaming to show the agent's thought process,
    tool calls, and final response in real-time.
    """
    while True:
        try:
            query = input().strip()
            if not query:
                continue
                
            prompt = RichPromptTemplate(query)
            handler = context_agent.run(prompt.format())
            current_agent = None
            
            async for event in handler.stream_events():
                if hasattr(event, "current_agent_name") and event.current_agent_name != current_agent:
                    current_agent = event.current_agent_name
                    print(f"Current agent: {current_agent}")
                elif isinstance(event, AgentOutput):
                    if event.response.content:
                        print(event.response.content)
                elif isinstance(event, ToolCallResult):
                    print(f"Output from tool: {event.tool_output}")
                    
        except EOFError:
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            continue


if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["GITHUB_TOKEN", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please ensure these are set in your .env file")
        exit(1)
    
    # Run the async main function
    asyncio.run(main())
    github_client.close()
