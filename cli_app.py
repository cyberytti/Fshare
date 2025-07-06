import os
import time
import atexit
import zipfile
import tempfile
from pathlib import Path
from typing import List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm
from rich.rule import Rule
from backend.main import run_server



# --- Typer App and Rich Console Initialization ---
app = typer.Typer(
    name="fshare",
    help="""
    🚀 A modern CLI to instantly share files and directories from your terminal.
    
    Powered by Flask, Pinggy.io, and Rich.
    """,
    add_completion=False,
)
console = Console()

# --- ASCII Art Banner ---
# Generated with an ASCII art generator for a modern, blocky look.
ASCII_ART = r"""
     ______     __                  
   / ____/____/ /_  ____ _________ 
  / /_  / ___/ __ \/ __ `/ ___/ _ \
 / __/ (__  ) / / / /_/ / /  /  __/
/_/   /____/_/ /_/\__,_/_/   \___/ 
                                   
"""

# --- Helper Function for Zipping ---
def create_temporary_zip(paths: List[Path]) -> Path:
    """
    Creates a temporary zip file from a list of files and directories,
    showing a progress bar. Registers the file for cleanup on exit.
    """
    try:
        # Create a temporary file that we manage ourselves
        temp_file = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        temp_file.close()  # Close it so zipfile can open it
        temp_zip_path = Path(temp_file.name)

        # Register the cleanup function to delete the temp file on script exit
        atexit.register(os.remove, temp_zip_path)

        console.print(f"[cyan]Compressing {len(paths)} items into a temporary archive...[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            zip_task = progress.add_task("[green]Zipping...", total=len(paths))

            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for path in paths:
                    if path.is_file():
                        zipf.write(path, path.name)
                    elif path.is_dir():
                        # Recursively add all files in the directory
                        for file_in_dir in path.rglob('*'):
                            arcname = file_in_dir.relative_to(path.parent)
                            zipf.write(file_in_dir, arcname)
                    
                    progress.update(zip_task, advance=1, description=f"[green]Adding [bold]{path.name}[/bold]")
        
        console.print(f"[bold green]✔[/bold green] Archive created at: [dim]{temp_zip_path}[/dim]")
        return temp_zip_path

    except Exception as e:
        console.print(f"[bold red]Error during zipping:[/bold red] {e}")
        raise typer.Exit(code=1)


# --- Main CLI Command ---
@app.command()
def share(
    paths: List[Path] = typer.Argument(
        ...,  # '...' makes the argument required
        help="One or more paths to the files or directories you want to share.",
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        resolve_path=True, # Converts to absolute path
    ),
):
    """
    Starts a server to share one or more files/directories over the internet.
    """
    # --- Display New, Modern Welcome Banner ---
    console.print(ASCII_ART, style="bold magenta", justify="center")
    console.print(
        Panel(
            "[bold]Instant File & Directory Sharing from Your Terminal[/]",
            title="[cyan]v1.0[/]",
            subtitle="[dim]Press CTRL+C to exit[/dim]",
            style="cyan"
        )
    )
    console.print(Rule(style="dim cyan"))
    console.print() # Add a blank line for spacing

    file_to_serve: Path
    is_temp_zip = False

    # --- Logic to handle single/multiple files/directories ---
    if len(paths) == 1 and paths[0].is_file():
        file_to_serve = paths[0]
        console.print(f"Preparing to share single file: [bold yellow]{file_to_serve.name}[/bold yellow]")
    else:
        if len(paths) > 1:
            msg = f"You are about to share {len(paths)} items."
        else: # Single directory
            msg = f"You are about to share the directory [bold yellow]{paths[0].name}[/bold yellow]."
        
        console.print(f"{msg} They will be compressed into a single zip file.")
        
        if not Confirm.ask("[bold]Do you want to continue?[/bold]", default=True):
            console.print("[yellow]Aborted by user.[/yellow]")
            raise typer.Exit()
            
        file_to_serve = create_temporary_zip(paths)
        is_temp_zip = True

    console.print("\n[bold green]Ready to start the server![/bold green]")
    console.print(f"  [b]File to be served:[/b] [cyan]{file_to_serve.name}[/cyan]")
    if is_temp_zip:
        size_mb = file_to_serve.stat().st_size / (1024 * 1024)
        console.print(f"  [b]Archive Size:[/b] [cyan]{size_mb:.2f} MB[/cyan]")

    # Add a small delay for effect and readability
    time.sleep(1)

    # --- Start the backend server ---
    try:
        run_server(str(file_to_serve))
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()