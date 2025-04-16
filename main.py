from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from database import init_db
from routers import contacts, users

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles rate limit exceeded exceptions.

    Args:
        request (Request): The incoming HTTP request.
        exc (RateLimitExceeded): The exception raised when the rate limit is exceeded.

    Returns:
        JSONResponse: A response with a 429 status code and an error message.
    """
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )


@app.on_event("startup")
async def on_startup():
    """
    Initializes the database on application startup.
    """
    init_db()


# Routers
app.include_router(contacts.router)
app.include_router(users.router)
