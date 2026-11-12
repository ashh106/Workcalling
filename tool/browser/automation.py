import asyncio
import os
from dotenv import load_dotenv

from browser_use import Agent, Browser
from browser_use.llm import ChatGoogle

# Load environment variables
load_dotenv()

def run_browser_automation(task: str) -> str:
    """
    Run browser automation using browser-use agent to perform the task in headed mode.

    Args:
        task: The task description for the browser agent to execute

    Returns:
        The final result returned by the agent.
    """
    async def _run():
        # Initialize the LLM using the native browser_use wrapper
        llm = ChatGoogle(model="gemini-3-flash-preview")

        # Configure the browser to be visible
        browser = Browser(
            headless=False,
        )

        # Create the agent with the specified task
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
        )

        # Run the agent and return the final result
        try:
            result = await agent.run()
            return result.final_result()
        finally:
            if hasattr(browser, 'close'):
                await browser.close()

    def _run_sync():
        return asyncio.run(_run())

    try:
        # Check if we are already in an event loop
        try:
            asyncio.get_running_loop()
            # If we are, run in a separate thread to avoid "asyncio.run() cannot be called from a running event loop"
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(_run_sync)
                return future.result()
        except RuntimeError:
            # No running event loop, we can use asyncio.run directly
            return asyncio.run(_run())
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error executing browser task: {str(e)}"
