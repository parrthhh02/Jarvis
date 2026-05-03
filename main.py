"""
Lilu AI Assistant — Main Entry Point
Terminal-based interface for Lilu.
"""

import sys
import logging
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

import config
from core.orchestrator import Orchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO if "--debug" in sys.argv else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("lilu.log"), logging.StreamHandler(sys.stdout)]
)
# Suppress noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)

console = Console()

def print_welcome():
    """Display startup banner."""
    console.clear()
    console.print(Panel(
        "[bold cyan]Lilu[/] — Personal AI Assistant\n"
        f"[dim]Provider:[/] {config.get_active_provider()} | [dim]Voice:[/] {'ON' if config.VOICE_ENABLED else 'OFF'}",
        title="System Online",
        border_style="cyan",
        expand=False
    ))

def main():
    # Pre-flight checks
    warnings = config.validate_config()
    for w in warnings:
        console.print(f"[yellow]Warning:[/] {w}")
    
    if config.get_active_provider() == "none":
        console.print("[bold red]Fatal:[/] No LLM configured. Please set OPENAI_API_KEY or GROQ_API_KEY in .env")
        sys.exit(1)

    print_welcome()
    
    # Initialize Lilu
    with console.status("[dim]Initializing core systems...[/]"):
        try:
            lilu = Orchestrator()
            
            tts = None
            if config.VOICE_ENABLED:
                from voice.tts import EdgeTTS
                tts = EdgeTTS()
                
        except Exception as e:
            console.print(f"[bold red]Initialization failed:[/] {e}")
            sys.exit(1)

    # Main Chat Loop
    console.print("[dim]Type 'exit', 'quit', or press Ctrl+C to stop.[/]\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold cyan]You[/]")
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in ("exit", "quit"):
                console.print("[dim]Lilu shutting down...[/]")
                break
                
            with console.status("[cyan]Lilu is thinking...[/]"):
                response = lilu.process_input(user_input)
                
            console.print("\n[bold magenta]Lilu[/]")
            console.print(Markdown(response))
            console.print()
            
            if tts:
                # Speak in the background (or block if desired)
                tts.speak(response)
                
        except KeyboardInterrupt:
            console.print("\n[dim]Lilu shutting down...[/]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/] {e}")
            logging.error(f"Main loop error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
