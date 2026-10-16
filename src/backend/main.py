from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

from api.users import router as user_router

app = FastAPI(
    title="Resonance",
    description="Scalable audio catalog and RBAC management built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)


api_router = APIRouter(prefix="/api")


api_router.include_router(user_router, prefix="/users", tags=["Users"])

app.include_router(api_router)


@app.get("/health", include_in_schema=False)
def health():
    return JSONResponse(content={"status:": "ok"})
