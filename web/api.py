import uvicorn
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from fastapi import FastAPI

app = FastAPI()

app.mount("/web/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return RedirectResponse(url="/web/static/index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
