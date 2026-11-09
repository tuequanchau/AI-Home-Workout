 giao-dien-ui-1
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from interface.home import get_home_html
from interface.workout import get_workout_html
from interface.summary import get_summary_html

app = FastAPI(title="Smurf Fitness", description="Trợ lý tập luyện AI")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(get_home_html())


@app.get("/workout", response_class=HTMLResponse)
def workout() -> HTMLResponse:
    return HTMLResponse(get_workout_html())


@app.get("/summary", response_class=HTMLResponse)
def summary() -> HTMLResponse:
    return HTMLResponse(get_summary_html())

def main():
    print("================================")
    print("   AI HOME WORKOUT ASSISTANT")
    print("================================")
    print("Project is running successfully!")


if __name__ == "__main__":
    main()
 main
