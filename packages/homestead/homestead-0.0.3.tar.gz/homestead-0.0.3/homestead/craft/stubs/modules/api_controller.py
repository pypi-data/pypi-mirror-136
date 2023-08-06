from fastapi import Request
from homestead import APIRouter

router = APIRouter(
    prefix="/{{module_name}}",
)


@router.get('/')
async def get(request: Request):
    """A route that returns json data"""
    return {}
