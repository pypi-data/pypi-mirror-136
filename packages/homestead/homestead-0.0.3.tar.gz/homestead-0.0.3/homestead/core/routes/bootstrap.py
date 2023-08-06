import importlib


def register_routes(app):
    """Automatically register all routes in the application."""
    modules_path = app.modules_path
    exlcude_paths = ['__pycache__']
    for module_path in modules_path.iterdir():
        if module_path.is_dir() and module_path.name not in exlcude_paths:
            mod = importlib.import_module(f"app.modules.{module_path.name}.controller")
            app.include_router(mod.router)
