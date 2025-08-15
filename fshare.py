import os
import time
import atexit
import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box
from backend.main import run_server

# --- Typer App and Rich Console Initialization ---
app = typer.Typer(
    name="fshare",
    help="""
    🚀 [bold cyan]Fshare - Instant File Sharing from Terminal[/bold cyan]
    
    [dim]Share files and directories instantly over the internet with a single command.[/dim]
    
    [yellow]✨ Features:[/yellow]
    • [green]No file size limits[/green] - Share files of any size
    • [green]Global access[/green] - Accessible from anywhere via secure tunnels  
    • [green]Auto-compression[/green] - Multiple files/directories are automatically zipped
    • [green]Privacy-focused[/green] - Files are served directly from your machine
    • [green]Temporary links[/green] - Links expire when you stop the server
    
    [yellow]🔧 Examples:[/yellow]
    • [dim]fshare document.pdf[/dim]                    [blue]# Share a single file[/blue]
    • [dim]fshare photo.jpg song.mp3[/dim]             [blue]# Share multiple files (auto-zipped)[/blue]
    • [dim]fshare my_project/[/dim]                     [blue]# Share entire directory (auto-zipped)[/blue]
    • [dim]fshare --help[/dim]                          [blue]# Show this help message[/blue]
    
    [red]⚠️  Press CTRL+C to stop sharing and terminate the server[/red]
    """,
    add_completion=False,
    rich_markup_mode="rich"
)
console = Console()

# --- Enhanced ASCII Art Banner with Color ---
ASCII_ART = r"""
[bold magenta]     ______     __                  
   / ____/____/ /_  ____ _________ 
  / /_  / ___/ __\/ __ `/ ___/ _ \
 / __/ (__  ) / / / /_/ / /  /  __/
/_/   /____/_/ /_/\__,_/_/   \___/ [/bold magenta]
                                   
[bold cyan]    Instant File Sharing • v1.0[/bold cyan]
"""

# --- Helper Functions ---
def display_welcome_banner():
    """Display the enhanced welcome banner with better styling."""
    console.print()
    console.print(Align.center(ASCII_ART))
    console.print()
    
    # Create a beautiful info panel
    info_panel = Panel(
        "[bold white]Share files instantly from your terminal to anywhere in the world[/bold white]\n"
        "[dim]Powered by Flask & Pinggy.io tunnels • No uploads required[/dim]",
        title="[cyan]🌐 Global File Sharing[/cyan]",
        subtitle="[dim]Press CTRL+C anytime to stop[/dim]",
        style="cyan",
        box=box.ROUNDED
    )
    console.print(Align.center(info_panel))
    console.print()

def display_file_info(paths: List[Path], file_to_serve: Path, is_temp_zip: bool):
    """Display detailed information about the files being shared."""
    
    # Create a table for file information
    table = Table(
        title="[bold cyan]📁 Files to Share[/bold cyan]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("Item", style="yellow", no_wrap=True)
    table.add_column("Type", style="blue")
    table.add_column("Size", style="green", justify="right")
    
    if is_temp_zip:
        # Show original items that will be zipped
        total_size = 0
        for path in paths:
            if path.is_file():
                size_bytes = path.stat().st_size
                size_str = format_file_size(size_bytes)
                table.add_row(path.name, "📄 File", size_str)
                total_size += size_bytes
            elif path.is_dir():
                # Calculate directory size
                dir_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                size_str = format_file_size(dir_size)
                table.add_row(path.name, "📁 Directory", size_str)
                total_size += dir_size
        
        # Add separator and zip info
        table.add_section()
        zip_size = file_to_serve.stat().st_size
        table.add_row(
            f"[bold]{file_to_serve.name}[/bold]", 
            "📦 Archive (Final)", 
            f"[bold green]{format_file_size(zip_size)}[/bold green]"
        )
        
        # Show compression ratio
        if total_size > 0:
            ratio = (1 - zip_size / total_size) * 100
            compression_text = f"[dim](Compressed by {ratio:.1f}%)[/dim]" if ratio > 0 else "[dim](No compression)[/dim]"
            console.print(f"\n{compression_text}")
    else:
        # Single file
        size_bytes = file_to_serve.stat().st_size
        size_str = format_file_size(size_bytes)
        table.add_row(file_to_serve.name, "📄 File", size_str)
    
    console.print(table)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

def create_temporary_zip(paths: List[Path]) -> Path:
    """
    Creates a temporary zip file from a list of files and directories,
    showing an enhanced progress bar. Registers the file for cleanup on exit.
    """
    try:
        # Create a temporary file that we manage ourselves
        temp_file = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
        temp_file.close()  # Close it so zipfile can open it
        temp_zip_path = Path(temp_file.name)
        
        # Register the cleanup function to delete the temp file on script exit
        atexit.register(os.remove, temp_zip_path)
        
        # Enhanced compression message
        console.print()
        console.print(Panel(
            f"[yellow]🗜️  Creating archive from {len(paths)} item(s)...[/yellow]",
            style="yellow",
            box=box.ROUNDED
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style="cyan", complete_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            zip_task = progress.add_task("[cyan]Preparing archive...", total=len(paths))
            
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for path in paths:
                    if path.is_file():
                        zipf.write(path, path.name)
                        progress.update(zip_task, advance=1, description=f"[cyan]✓ Added file: [bold]{path.name}[/bold]")
                    elif path.is_dir():
                        # Count files first for better progress tracking
                        files_in_dir = list(path.rglob('*'))
                        for file_in_dir in files_in_dir:
                            if file_in_dir.is_file():
                                arcname = file_in_dir.relative_to(path.parent)
                                zipf.write(file_in_dir, arcname)
                        progress.update(zip_task, advance=1, description=f"[cyan]✓ Added directory: [bold]{path.name}[/bold]")
        
        console.print(f"[bold green]✅ Archive ready:[/bold green] [dim]{temp_zip_path.name}[/dim]")
        return temp_zip_path
    except Exception as e:
        console.print(f"[bold red]❌ Error during compression:[/bold red] {e}")
        raise typer.Exit(code=1)

def show_server_ready_message():
    """Display the server ready message with instructions."""
    console.print()
    console.print(Panel(
        "[bold green]🚀 Server is starting up![/bold green]\n\n"
        "[white]What happens next:[/white]\n"
        "[dim]1.[/dim] Local server starts on your machine\n"
        "[dim]2.[/dim] Secure tunnel creates public URL\n"
        "[dim]3.[/dim] Share the URL with anyone, anywhere\n\n"
        "[yellow]⚠️  Keep this terminal open while sharing[/yellow]\n"
        "[red]Press CTRL+C to stop sharing[/red]",
        title="[green]🌐 Ready to Share[/green]",
        style="green",
        box=box.ROUNDED
    ))

# --- Enhanced Main CLI Command ---
@app.command()
def share(
    paths: List[Path] = typer.Argument(
        ...,  # Required argument
        help="📁 One or more paths to files or directories you want to share.",
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        resolve_path=True
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="🔍 Show detailed information during the process"
    )
):
    """
    🚀 Share files and directories instantly over the internet.
    
    This command starts a local server and creates a secure tunnel to make your files
    accessible from anywhere in the world. Perfect for quickly sharing files without
    uploading them to cloud services.
    
    [yellow]Examples:[/yellow]
    • fshare share document.pdf
    • fshare share photo.jpg video.mp4 
    • fshare share my_folder/
    • fshare share file1.txt file2.txt
    """
    
    # Display enhanced welcome banner
    display_welcome_banner()
    
    file_to_serve: Path
    is_temp_zip = False
    
    # Enhanced logic for handling files/directories
    if len(paths) == 1 and paths[0].is_file():
        # Single file case
        file_to_serve = paths[0]
        console.print(f"[bold yellow]📄 Sharing single file:[/bold yellow] [cyan]{file_to_serve.name}[/cyan]")
    else:
        # Multiple files or directories - need to zip
        if len(paths) > 1:
            msg = f"[bold yellow]📦 Sharing {len(paths)} items[/bold yellow] (will be compressed into one archive)"
        else:
            msg = f"[bold yellow]📁 Sharing directory:[/bold yellow] [cyan]{paths[0].name}[/cyan] (will be compressed)"
        
        console.print(msg)
        
        # Enhanced confirmation prompt
        console.print()
        if not Confirm.ask(
            "[bold]Continue with compression?[/bold]", 
            default=True,
            show_default=True
        ):
            console.print("[yellow]📤 Operation cancelled by user.[/yellow]")
            raise typer.Exit()
        
        file_to_serve = create_temporary_zip(paths)
        is_temp_zip = True
    
    # Display file information table
    console.print()
    display_file_info(paths, file_to_serve, is_temp_zip)
    
    # Show server ready message
    show_server_ready_message()
    
    # Add small delay for better UX
    if verbose:
        console.print("[dim]Initializing server components...[/dim]")
    time.sleep(1.5)
    
    # Start the backend server
    try:
        run_server(str(file_to_serve))
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Sharing stopped by user. Thanks for using Fshare![/yellow]")
        raise typer.Exit()
    except Exception as e:
        console.print(f"\n[bold red]❌ An unexpected error occurred:[/bold red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1)

@app.command()
def version():
    """📋 Show version information and credits."""
    version_info = Table(
        title="[bold cyan]Fshare Version Info[/bold cyan]",
        box=box.ROUNDED,
        show_header=False
    )
    version_info.add_column("Field", style="yellow", no_wrap=True)
    version_info.add_column("Value", style="green")
    
    version_info.add_row("Version", "[bold]v1.0[/bold]")
    version_info.add_row("Built with", "Python, Flask, Typer, Rich")
    version_info.add_row("Tunneling", "Pinggy.io")
    version_info.add_row("License", "MIT License")
    version_info.add_row("Repository", "github.com/cyberytti/Fshare")
    
    console.print()
    console.print(version_info)
    console.print()

if __name__ == "__main__":
    app()
