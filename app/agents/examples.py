"""
Example usage patterns for the Context Manager Agent System.

This script demonstrates various ways to use the context agent
for different scenarios and use cases.
"""

import asyncio
import os
from dotenv import load_dotenv
from app.agents.context_agent import (
    context_agent,
    get_pr_details,
    get_pr_commit_details,
    get_file_contents
)


# Load environment variables
load_dotenv()


async def example_basic_pr_analysis(pr_number: int):
    """
    Example 1: Basic PR analysis
    
    Demonstrates the simplest use case - getting comprehensive
    context about a pull request.
    """
    print("\n" + "="*80)
    print(f"Example 1: Basic PR Analysis for PR #{pr_number}")
    print("="*80 + "\n")
    
    query = f"Gather complete context for pull request #{pr_number}"
    
    response_stream = await context_agent.astream_chat(query)
    
    async for event in response_stream.async_response_gen():
        print(event, end="", flush=True)
    
    print("\n\n✅ Basic analysis complete!\n")


async def example_focused_file_analysis(pr_number: int, file_name: str):
    """
    Example 2: Focused file analysis
    
    Demonstrates how to ask the agent to focus on specific files
    within a pull request.
    """
    print("\n" + "="*80)
    print(f"Example 2: Analyzing specific file '{file_name}' in PR #{pr_number}")
    print("="*80 + "\n")
    
    query = f"""For pull request #{pr_number}, I need to understand:
    1. What is the PR about?
    2. Was the file '{file_name}' changed?
    3. If yes, get the contents of that file and summarize the changes
    """
    
    response_stream = await context_agent.astream_chat(query)
    
    async for event in response_stream.async_response_gen():
        print(event, end="", flush=True)
    
    print("\n\n✅ Focused file analysis complete!\n")


async def example_change_summary(pr_number: int):
    """
    Example 3: Change summary
    
    Demonstrates asking the agent to provide a summary of all changes
    in a pull request.
    """
    print("\n" + "="*80)
    print(f"Example 3: Comprehensive Change Summary for PR #{pr_number}")
    print("="*80 + "\n")
    
    query = f"""For pull request #{pr_number}, provide a comprehensive summary:
    1. Who created the PR and what is it about?
    2. List all files that were changed
    3. For each file, show the statistics (additions, deletions)
    4. Identify the most significant changes
    """
    
    response_stream = await context_agent.astream_chat(query)
    
    async for event in response_stream.async_response_gen():
        print(event, end="", flush=True)
    
    print("\n\n✅ Change summary complete!\n")


async def example_direct_tool_usage():
    """
    Example 4: Direct tool usage
    
    Demonstrates using the tool functions directly without the agent,
    useful for programmatic access to specific data.
    """
    print("\n" + "="*80)
    print("Example 4: Direct Tool Usage (No Agent)")
    print("="*80 + "\n")
    
    pr_number = 1
    
    # Get PR details directly
    print(f"📋 Fetching PR #{pr_number} details...")
    pr_details = get_pr_details(pr_number)
    
    if "error" not in pr_details:
        print(f"   ✓ Title: {pr_details['title']}")
        print(f"   ✓ Author: {pr_details['author']}")
        print(f"   ✓ State: {pr_details['state']}")
        print(f"   ✓ HEAD SHA: {pr_details['head_sha']}\n")
        
        # Get commit details
        print(f"📝 Fetching commit details for {pr_details['head_sha'][:7]}...")
        commit_details = get_pr_commit_details(pr_details['head_sha'])
        
        if commit_details and "error" not in commit_details[0]:
            print(f"   ✓ Found {len(commit_details)} changed file(s):")
            for file_info in commit_details:
                print(f"      • {file_info['filename']} ({file_info['status']})")
                print(f"        +{file_info['additions']} -{file_info['deletions']}")
        
        print("\n✅ Direct tool usage complete!\n")
    else:
        print(f"❌ Error: {pr_details['error']}\n")


async def example_multi_turn_conversation(pr_number: int):
    """
    Example 5: Multi-turn conversation
    
    Demonstrates having a back-and-forth conversation with the agent,
    asking follow-up questions based on previous responses.
    """
    print("\n" + "="*80)
    print(f"Example 5: Multi-turn Conversation about PR #{pr_number}")
    print("="*80 + "\n")
    
    # First turn - get basic info
    print("🔵 Turn 1: Getting basic PR information...")
    print("-" * 80)
    response1 = await context_agent.astream_chat(
        f"What is pull request #{pr_number} about? Just give me the basics."
    )
    
    async for event in response1.async_response_gen():
        print(event, end="", flush=True)
    
    print("\n\n" + "-" * 80)
    
    # Second turn - dig deeper
    print("🔵 Turn 2: Finding out what files changed...")
    print("-" * 80)
    response2 = await context_agent.astream_chat(
        "What files were changed in this PR?"
    )
    
    async for event in response2.async_response_gen():
        print(event, end="", flush=True)
    
    print("\n\n" + "-" * 80)
    
    # Third turn - specific file
    print("🔵 Turn 3: Examining a specific file...")
    print("-" * 80)
    response3 = await context_agent.astream_chat(
        "Can you show me the current contents of the first file that was changed?"
    )
    
    async for event in response3.async_response_gen():
        print(event, end="", flush=True)
    
    print("\n\n✅ Multi-turn conversation complete!\n")


async def example_error_handling():
    """
    Example 6: Error handling
    
    Demonstrates how the system handles various error scenarios.
    """
    print("\n" + "="*80)
    print("Example 6: Error Handling Demonstration")
    print("="*80 + "\n")
    
    # Try to get a non-existent PR
    print("🔴 Test 1: Non-existent PR...")
    pr_details = get_pr_details(99999)
    if "error" in pr_details:
        print(f"   ✓ Error caught: {pr_details['error']}\n")
    
    # Try to get a non-existent file
    print("🔴 Test 2: Non-existent file...")
    file_content = get_file_contents("non_existent_file.py")
    if "error" in file_content:
        print(f"   ✓ Error caught: {file_content['error']}\n")
    
    # Try to get a directory instead of a file
    print("🔴 Test 3: Directory instead of file...")
    dir_content = get_file_contents("app")
    if "error" in dir_content:
        print(f"   ✓ Error caught: {dir_content['error']}\n")
    
    print("✅ Error handling demonstration complete!\n")


async def run_all_examples():
    """Run all examples in sequence."""
    print("\n" + "="*80)
    print("CONTEXT MANAGER AGENT - COMPREHENSIVE EXAMPLES")
    print("="*80)
    
    pr_number = 1  # Change this to test with a different PR
    
    # Check for required environment variables
    required_vars = ["GITHUB_TOKEN", "OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\n❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please ensure these are set in your .env file\n")
        return
    
    print("\n📚 Running examples with PR #" + str(pr_number))
    print("(You can modify PR_NUMBER in the script to test different PRs)\n")
    
    # Example 1: Basic analysis
    await example_basic_pr_analysis(pr_number)
    
    # Example 2: Focused file analysis
    await example_focused_file_analysis(pr_number, "models.py")
    
    # Example 3: Change summary
    await example_change_summary(pr_number)
    
    # Example 4: Direct tool usage (synchronous)
    await example_direct_tool_usage()
    
    # Example 5: Multi-turn conversation
    await example_multi_turn_conversation(pr_number)
    
    # Example 6: Error handling
    await example_error_handling()
    
    print("\n" + "="*80)
    print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("="*80 + "\n")


async def run_single_example(example_number: int, pr_number: int = 1):
    """
    Run a single example by number.
    
    Args:
        example_number: Which example to run (1-6)
        pr_number: PR number to analyze (default: 1)
    """
    examples = {
        1: lambda: example_basic_pr_analysis(pr_number),
        2: lambda: example_focused_file_analysis(pr_number, "models.py"),
        3: lambda: example_change_summary(pr_number),
        4: lambda: example_direct_tool_usage(),
        5: lambda: example_multi_turn_conversation(pr_number),
        6: lambda: example_error_handling(),
    }
    
    if example_number in examples:
        await examples[example_number]()
    else:
        print(f"❌ Error: Example {example_number} does not exist.")
        print(f"Available examples: 1-6")


if __name__ == "__main__":
    import sys
    
    # Allow running specific examples from command line
    # Usage: python examples.py [example_number] [pr_number]
    # Example: python examples.py 1 5
    
    if len(sys.argv) > 1:
        try:
            example_num = int(sys.argv[1])
            pr_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            asyncio.run(run_single_example(example_num, pr_num))
        except ValueError:
            print("❌ Error: Please provide valid numbers")
            print("Usage: python examples.py [example_number] [pr_number]")
    else:
        # Run all examples if no arguments provided
        asyncio.run(run_all_examples())
