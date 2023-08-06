from fastapi import Request
from homestead import WebRouter
import fastapi_jinja

router = WebRouter(
    prefix="/{{module_name}}",
)


@router.get('/')
@fastapi_jinja.template('index.html')
async def get(request: Request):
    """A route that returns html data"""
    return {}

