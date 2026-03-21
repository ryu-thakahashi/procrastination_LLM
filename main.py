import asyncio
import json
import os
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from services.procrastination import analyze_task, generate_report, generate_task_strategy

USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="先延ばし防止レポート生成AI")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task_name: str
    task_desc: str


@app.get("/", response_class=HTMLResponse)
async def root():
    with open(STATIC_DIR / "index.html", encoding="utf-8") as f:
        return f.read()


def load_latest_report() -> str:
    dirs = sorted(OUTPUT_DIR.glob("*/"), reverse=True)
    for d in dirs:
        report_file = d / "03_report.md"
        if not report_file.exists():
            return "# レポートが見つかりませんでした\n`output/` に `03_report.md` がありません。"

        return report_file.read_text(encoding="utf-8").strip()


@app.post("/api/report")
async def create_report(request: TaskRequest):
    async def event_stream():
        if USE_MOCK:
            for step, msg in [
                ("analyzing", "タスクを分析しています..."),
                ("strategizing", "先延ばし対策を考えています..."),
                ("reporting", "レポートを作成しています..."),
            ]:
                yield f"data: {json.dumps({'step': step, 'message': msg}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.4)
            report = load_latest_report()
        else:
            save_dir = OUTPUT_DIR / time.strftime("%Y%m%d-%H%M%S")

            msg = json.dumps({"step": "analyzing", "message": "タスクを分析しています..."}, ensure_ascii=False)
            yield f"data: {msg}\n\n"
            await asyncio.sleep(0)

            task_analysis = await asyncio.to_thread(analyze_task, request.task_name, request.task_desc, save_dir)

            msg = json.dumps({"step": "strategizing", "message": "先延ばし対策を考えています..."}, ensure_ascii=False)
            yield f"data: {msg}\n\n"
            await asyncio.sleep(0)

            task_strategy = await asyncio.to_thread(generate_task_strategy, task_analysis, save_dir)

            msg = json.dumps({"step": "reporting", "message": "レポートを作成しています..."}, ensure_ascii=False)
            yield f"data: {msg}\n\n"
            await asyncio.sleep(0)

            report = await asyncio.to_thread(generate_report, task_strategy, save_dir)

        yield f"data: {json.dumps({'step': 'done', 'report': report}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
