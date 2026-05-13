from rich.console import Console

console = Console()
err_console = Console(stderr=True)


def info(message: str) -> None:
    console.print(f"[cyan]ℹ[/cyan]  {message}")


def success(message: str) -> None:
    console.print(f"[green]✓[/green]  {message}")


def warn(message: str) -> None:
    err_console.print(f"[yellow]⚠[/yellow]  {message}")


def error(message: str) -> None:
    err_console.print(f"[red]✗[/red]  {message}")
