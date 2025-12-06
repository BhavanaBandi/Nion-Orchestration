# Nion Orchestration Engine - Enhanced Main Entry Point
# CLI interface using Typer with testio.md format support

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

import typer

from config import config, OUTPUT_DIR
from models.l1_models import Message, Sender
from orchestration.l1_orchestrator import L1Orchestrator
from orchestration.l2_coordinator import L2Coordinator
from rendering.map_renderer import render_orchestration_map
from storage.db import storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer(
    name="nion",
    help="Nion Orchestration Engine - L1→L2→L3 Task Orchestration"
)


async def run_orchestration(
    message_dict: dict,
    context: Optional[dict] = None
) -> str:
    """
    Run the full L1→L2→L3 orchestration pipeline.
    
    Args:
        message_dict: Message data in testio.md format
        context: Optional context for L1 planning
        
    Returns:
        The rendered orchestration map
    """
    message_id = message_dict.get("message_id", message_dict.get("id", "MSG-UNKNOWN"))
    logger.info(f"Starting orchestration for message: {message_id}")
    
    # L1: Plan tasks
    logger.info("L1: Planning tasks...")
    l1_orchestrator = L1Orchestrator(context=context)
    l1_result = await l1_orchestrator.plan_tasks_from_dict(message_dict)
    
    if not l1_result.success:
        logger.error(f"L1 planning failed: {l1_result.error}")
        return f"Error: L1 planning failed - {l1_result.error}"
    
    task_plan = l1_result.task_plan
    logger.info(f"L1: Generated {len(task_plan.tasks)} tasks")
    
    # Save task plan to storage
    storage.save_task_plan(task_plan)
    
    # Get message content for L3 extraction
    content = message_dict.get("content", message_dict.get("body", ""))
    
    # L2: Route and execute tasks
    logger.info("L2: Routing tasks to L3 agents...")
    l2_coordinator = L2Coordinator()
    routing_results = await l2_coordinator.route_all_tasks(task_plan, content)
    
    # Save extractions to storage
    for result in routing_results:
        if result.success and result.extraction_result:
            storage.save_extraction(
                task_id=result.task.task_id,
                extraction_type=result.l3_agent or result.domain,
                data=result.extraction_result.model_dump(mode='json')
            )
    
    # Render orchestration map
    logger.info("Rendering orchestration map...")
    map_text = render_orchestration_map(task_plan, routing_results)
    
    # Save to storage
    storage.save_orchestration_map(message_id, map_text)
    
    return map_text


def parse_message_file(input_file: Path) -> dict:
    """Parse message from JSON file, handling both old and testio formats."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Normalize to testio format
    if "message_id" not in data and "id" in data:
        data["message_id"] = data["id"]
    
    if "sender" not in data:
        data["sender"] = {"name": "Unknown", "role": None}
    elif isinstance(data["sender"], str):
        data["sender"] = {"name": data["sender"], "role": None}
    
    if "content" not in data and "body" in data:
        data["content"] = data["body"]
    
    if "source" not in data:
        data["source"] = "email"
    
    return data


@app.command()
def process(
    input_file: Path = typer.Option(
        ..., "--input", "-i",
        help="Path to input message JSON file"
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Path to output file (default: output/<message_id>_orchestration.txt)"
    ),
    context_file: Optional[Path] = typer.Option(
        None, "--context", "-c",
        help="Path to context JSON file"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Enable verbose logging"
    )
):
    """
    Process a message through the orchestration pipeline.
    
    Example:
        python main.py process --input samples/MSG-001.json
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load input message
    if not input_file.exists():
        typer.echo(f"Error: Input file not found: {input_file}", err=True)
        raise typer.Exit(1)
    
    try:
        message_dict = parse_message_file(input_file)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Invalid JSON in input file: {e}", err=True)
        raise typer.Exit(1)
    
    message_id = message_dict.get("message_id", input_file.stem)
    
    # Load context if provided
    context = None
    if context_file and context_file.exists():
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                context = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Could not parse context file: {context_file}")
    
    # Run orchestration
    typer.echo(f"Processing message: {message_id}")
    map_text = asyncio.run(run_orchestration(message_dict, context))
    
    # Determine output path
    if output_file is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_file = OUTPUT_DIR / f"{message_id}_orchestration.txt"
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(map_text)
    
    typer.echo(f"\nOrchestration complete!")
    typer.echo(f"Output saved to: {output_file}")
    typer.echo("\n" + map_text)


@app.command()
def demo():
    """Run a demo with MSG-001 sample data."""
    demo_message = {
        "message_id": "MSG-001",
        "source": "email",
        "sender": {
            "name": "Sarah Chen",
            "role": "Product Manager"
        },
        "content": "The customer demo went great! They loved it but asked if we could add real-time notifications and a dashboard export feature. They're willing to pay 20% more and need it in the same timeline. Can we make this work?",
        "project": "PRJ-ALPHA"
    }
    
    typer.echo("Running demo with MSG-001 sample message...")
    typer.echo("-" * 40)
    
    # Run orchestration
    map_text = asyncio.run(run_orchestration(demo_message))
    
    # Save output
    output_file = OUTPUT_DIR / "MSG-001_orchestration.txt"
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(map_text)
    
    typer.echo(map_text)
    typer.echo(f"\nOutput saved to: {output_file}")


@app.command()
def test_all():
    """Run all test cases from testio.md."""
    test_cases = [
        {
            "message_id": "MSG-101",
            "source": "slack",
            "sender": {"name": "John Doe", "role": "Engineering Manager"},
            "content": "What's the status of the authentication feature?",
            "project": "PRJ-BETA"
        },
        {
            "message_id": "MSG-102",
            "source": "email",
            "sender": {"name": "Sarah Chen", "role": "Product Manager"},
            "content": "Can we add SSO integration before the December release?",
            "project": "PRJ-ALPHA"
        },
        {
            "message_id": "MSG-103",
            "source": "email",
            "sender": {"name": "Mike Johnson", "role": "VP Engineering"},
            "content": "Should we prioritize security fixes or the new dashboard?",
            "project": "PRJ-GAMMA"
        },
        {
            "message_id": "MSG-104",
            "source": "meeting",
            "sender": {"name": "System", "role": "Meeting Bot"},
            "content": "Dev: I'm blocked on API integration, staging is down. QA: Found 3 critical bugs in payment flow. Designer: Mobile mockups ready by Thursday. Tech Lead: We might need to refactor the auth module.",
            "project": "PRJ-ALPHA"
        },
        {
            "message_id": "MSG-105",
            "source": "email",
            "sender": {"name": "Lisa Wong", "role": "Customer Success Manager"},
            "content": "The client is asking why feature X promised for Q3 is still not delivered. They're threatening to escalate to legal. What happened?",
            "project": "PRJ-DELTA"
        },
        {
            "message_id": "MSG-106",
            "source": "slack",
            "sender": {"name": "Random User", "role": "Unknown"},
            "content": "We need to speed things up",
            "project": None
        }
    ]
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    for tc in test_cases:
        typer.echo(f"\n{'='*60}")
        typer.echo(f"Processing {tc['message_id']}: {tc['content'][:50]}...")
        typer.echo("="*60)
        
        try:
            map_text = asyncio.run(run_orchestration(tc))
            
            output_file = OUTPUT_DIR / f"{tc['message_id']}_orchestration.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(map_text)
            
            typer.echo(f"✓ {tc['message_id']} completed → {output_file}")
        except Exception as e:
            typer.echo(f"✗ {tc['message_id']} failed: {e}", err=True)
    
    typer.echo(f"\n\nAll test cases completed. Check {OUTPUT_DIR} for results.")


@app.command()
def version():
    """Show version information."""
    typer.echo("Nion Orchestration Engine v0.2.0")
    typer.echo(f"LLM: Groq LLaMA 3 70B ({config.llm.model})")
    typer.echo("Stack: Python + SQLite + Groq API")


if __name__ == "__main__":
    app()
