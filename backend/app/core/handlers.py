from .exceptions import (
     BaseLodgeOpsError

)
from fastapi.responses import JSONResponse
from fastapi import Request



async def lodge_ops_error_handler(request: Request , exc: BaseLodgeOpsError):

    return JSONResponse(
        status_code=exc.status_code,
        content= {
            'error': exc.__class__.__name__,
            'detail': exc.detail,
            'meta': exc.meta
        }

    )

lodge_ops_handlers = {
    BaseLodgeOpsError: lodge_ops_error_handler

}
