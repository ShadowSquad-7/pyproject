from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
import panel as pn

from app.users import routers as user_rout, model
from app.users.security import get_current_user
from app.parcers.runner import run_background_scripts
from app.plotly.dash import get_currency_dashboard

run_background_scripts()

dashboard=get_currency_dashboard()
pn.serve(
    dashboard,
    port=8050,
    address="0.0.0.0",
    show=False,  # Не открывать браузер автоматически
    allow_websocket_origin=["*"],  # Разрешить все источники
    title="Currency Dashboard"
)


app = FastAPI()
app.include_router(user_rout.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request, user: model.User | None = Depends(get_current_user)):
    return templates.TemplateResponse("main_page.html", {
        "request": request,
        "user" : user,
    })
