import typer

from .commands import module_commands
from .commands import project
app = typer.Typer()

app.add_typer(module_commands.app, name="module")
app.add_typer(project.app, name="project")

if __name__ == "__main__":
    app()