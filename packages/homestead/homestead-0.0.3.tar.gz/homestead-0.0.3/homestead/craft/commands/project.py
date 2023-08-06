from cookiecutter.main import cookiecutter
import typer

app = typer.Typer()


@app.command()
def init():
    cookiecutter(
        'https://github.com/HomesteadFramework/cookiecutter.git',
    )


if __name__ == "__main__":
    app()
