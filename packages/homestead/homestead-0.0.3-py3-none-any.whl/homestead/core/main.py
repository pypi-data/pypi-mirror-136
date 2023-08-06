from pathlib import Path
from typing import Any, Callable, Coroutine, Dict, List, Optional, Sequence, Type, Union

from fastapi import FastAPI
from fastapi.datastructures import Default
from fastapi.params import Depends
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute

from homestead.utils.filesystem import get_file_path
from homestead.core.routes import bootstrap as bootstrap_routes


class Homestead(FastAPI):
    """
    A simple wrapper around FastAPI.
    Use this instead of FastAPI if you want to use the Homestead methods.
    """

    app_root_path: Path
    modules_path: Path

    def __init__(self,
                 *,
                 debug: bool = False,
                 routes: Optional[List[BaseRoute]] = None,
                 title: str = "FastAPI",
                 description: str = "",
                 version: str = "0.1.0",
                 openapi_url: Optional[str] = "/openapi.json",
                 openapi_tags: Optional[List[Dict[str, Any]]] = None,
                 servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
                 dependencies: Optional[Sequence[Depends]] = None,
                 default_response_class: Type[Response] = Default(JSONResponse),
                 docs_url: Optional[str] = "/docs",
                 redoc_url: Optional[str] = "/redoc",
                 swagger_ui_oauth2_redirect_url: Optional[str] = "/docs/oauth2-redirect",
                 swagger_ui_init_oauth: Optional[Dict[str, Any]] = None,
                 middleware: Optional[Sequence[Middleware]] = None,
                 exception_handlers: Optional[
                     Dict[
                         Union[int, Type[Exception]],
                         Callable[[Request, Any], Coroutine[Any, Any, Response]],
                     ]
                 ] = None,
                 on_startup: Optional[Sequence[Callable[[], Any]]] = None,
                 on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
                 terms_of_service: Optional[str] = None,
                 contact: Optional[Dict[str, Union[str, Any]]] = None,
                 license_info: Optional[Dict[str, Union[str, Any]]] = None,
                 openapi_prefix: str = "",
                 root_path: str = "",
                 root_path_in_servers: bool = True,
                 responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
                 callbacks: Optional[List[BaseRoute]] = None,
                 deprecated: Optional[bool] = None,
                 include_in_schema: bool = True,
                 **extra: Any
                 ):
        super().__init__(
            debug=debug,
            routes=routes,
            title=title,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_tags=openapi_tags,
            servers=servers,
            dependencies=dependencies,
            default_response_class=default_response_class,
            docs_url=docs_url,
            redoc_url=redoc_url,
            swagger_ui_oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
            swagger_ui_init_oauth=swagger_ui_init_oauth,
            middleware=middleware,
            exception_handlers=exception_handlers,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            terms_of_service=terms_of_service,
            contact=contact,
            license_info=license_info,
            openapi_prefix=openapi_prefix,
            root_path=root_path,
            root_path_in_servers=root_path_in_servers,
            responses=responses,
            callbacks=callbacks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            **extra
        )

        self.bootstrap()

    def bootstrap(self):
        """Bootstrap the app."""
        self.app_root_path = get_file_path("")
        self.modules_path = self.app_root_path.joinpath("app/modules")

        # Register routes
        bootstrap_routes.register_routes(self)

    def get(self, *args, **kwargs):
        """Raise not implemented error. Force to use the Homestead routers."""
        raise NotImplementedError("Use the Homestead routers instead.")

    def post(self, *args, **kwargs):
        """Raise not implemented error. Force to use the Homestead routers."""
        raise NotImplementedError("Use the Homestead routers instead.")

    def put(self, *args, **kwargs):
        """Raise not implemented error. Force to use the Homestead routers."""
        raise NotImplementedError("Use the Homestead routers instead.")

    def patch(self, *args, **kwargs):
        """Raise not implemented error. Force to use the Homestead routers."""
        raise NotImplementedError("Use the Homestead routers instead.")

    def delete(self, *args, **kwargs):
        """Raise not implemented error. Force to use the Homestead routers."""
        raise NotImplementedError("Use the Homestead routers instead.")
