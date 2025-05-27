from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.curr.services import lifespan
from app.users import routers as user_rout, model
from app.users.security import get_current_user
from app.curr.routers import router as curr_router

app = FastAPI(lifespan=lifespan)
app.include_router(user_rout.router)
app.include_router(curr_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request, user: model.User | None = Depends(get_current_user)):
    return templates.TemplateResponse("main_page.html", {
        "request": request,
        "user" : user,
    })
