import pathlib
import shutil

import typer
import questionary

from homestead.utils.filesystem import get_file_path

app = typer.Typer()


@app.command()
def create(
        name: str = typer.Option(..., help="Name of the module"),
):
    """Create a new module"""
    module_name = name.lower()
    app_root_path = get_file_path("")
    modules_path = app_root_path.joinpath("app/modules")

    # create module di  rectory
    new_module_path = str(modules_path.joinpath(module_name))
    pathlib.Path(new_module_path).mkdir(parents=True)

    type_of_controller = questionary.select(
        "What kind of router do you want?",
        choices=["web", "api"],
    ).ask()

    # create required files
    craft_path = str(pathlib.Path(__file__).parent.parent)
    modules_stubs_path = f"{craft_path}/stubs/modules"

    # create controller
    controller_file_path = f"{new_module_path}/controller.py"

    # web controller
    if type_of_controller == "web":
        controller_stub_path = f"{modules_stubs_path}/web/web_controller.py"
        stub_file = open(controller_stub_path, "r")
        new_file = open(controller_file_path, "w")

        for line in stub_file:
            new_file.write(line.replace("{{module_name}}", module_name))

        # make the view for the root route
        view_file_path = f"{app_root_path}/app/views/{module_name}"
        print(view_file_path)
        pathlib.Path(view_file_path).mkdir(parents=True)
        view_stub_path = f"{craft_path}/stubs/views/stub_view.html"
        stub = open(view_stub_path, "r").read()
        view_file = open(f"{view_file_path}/index.html", "w")

        for line in stub:
            view_file.write(line.replace(" {{module_name_placeholder}}", module_name))

        view_file.close()

    # api controller
    elif type_of_controller == "api":
        controller_stub_path = f"{modules_stubs_path}/api/api_controller.py"
        stub_file = open(controller_stub_path, "r")
        new_file = open(controller_file_path, "w")

        for line in stub_file:
            new_file.write(line.replace("{{module_name}}", module_name))

        new_file.close()

    # create init models and schemas files
    open(f"{new_module_path}/__init__.py", "a").close()
    open(f"{new_module_path}/models.py", "a").close()
    open(f"{new_module_path}/schemas.py", "a").close()
    open(f"{new_module_path}/service.py", "a").close()


if __name__ == "__main__":
    app()
