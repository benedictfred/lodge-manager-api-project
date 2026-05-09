from .exceptions import (
    BaseAlreadyExistError,
    BaseNotFoundError,
    UnauthorizedAccessError,
    InvalidLeaseActionError,
    BaseMaxLimitReachedError

)
from fastapi.responses import JSONResponse
from fastapi import Request


async def not_found_exception_handler(request: Request, exc: BaseNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            'error': 'Not Found',
            'detail': exc.detail
        }
    )


async def already_exist_exception_handler(request: Request, exc: BaseAlreadyExistError):
    return JSONResponse(
        status_code=400,
        content={
            'error': 'Already exists',
            'detail': exc.detail
        }
    )


async def unauthorized_access_exception_handler(request: Request, exc: UnauthorizedAccessError):
    return JSONResponse(
        status_code=403,
        content={
            'error': 'Not authorized',
            'detail': exc.detail
        }
    )

async def invalid_lease_action_handler(request: Request, exc: InvalidLeaseActionError):
    return JSONResponse(
        status_code=400,
        content={
            'error': 'Invalid Lease Action',
            'detail': exc.detail
        }
    )

async def max_limit_reached_handler(request: Request, exc: BaseMaxLimitReachedError):
    return JSONResponse(
        status_code=400,
        content={
            'error': 'Limit Reached',
            'detail': exc.detail
        }
    )

lodge_ops_handlers = {
    BaseNotFoundError: not_found_exception_handler,
    BaseAlreadyExistError: already_exist_exception_handler,
    UnauthorizedAccessError: unauthorized_access_exception_handler,
    InvalidLeaseActionError: invalid_lease_action_handler,
    BaseMaxLimitReachedError: max_limit_reached_handler

}
