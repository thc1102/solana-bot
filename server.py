import asyncio
from contextlib import asynccontextmanager

import uvicorn
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from fastapi import FastAPI

from main import run
from settings.config import AppConfig
from web.api import router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    asyncio.create_task(run())
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return RedirectResponse(url="/static/index.html")


if __name__ == '__main__':
    # 注册路由
    app.include_router(router)
    # 注册静态资源
    app.mount("/static", StaticFiles(directory="web/static"), name="static")
    uvicorn.run(app, host="127.0.0.1", port=AppConfig.WEB_PORT, log_level="error")
