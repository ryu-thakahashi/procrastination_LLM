import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from services.procrastination import analyze_task, generate_report, generate_task_strategy, initialize_caches, suggest_causes

USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """サーバー起動時にGeminiプロンプトキャッシュを初期化する。"""
    if not USE_MOCK:
        await asyncio.to_thread(initialize_caches)
    yield


app = FastAPI(title="先延ばし防止レポート生成AI", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://procrastination-llm.onrender.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task_name: str
    task_desc: str


class ReportRequest(BaseModel):
    task_name: str
    task_desc: str
    selected_cause: str


@app.get("/", response_class=HTMLResponse)
async def root():
    """トップページのHTMLを返す。"""
    with open(STATIC_DIR / "index.html", encoding="utf-8") as f:
        return f.read()


@app.post("/api/suggest-causes")
async def get_suggest_causes(request: TaskRequest):
    """タスク情報をもとに先延ばし原因を5つ提案する。

    Args:
        request: タスク名とタスク説明を含むリクエスト。

    Returns:
        先延ばし原因のリスト。
    """
    if USE_MOCK:
        import json as _json
        mock_causes = {
            "タスクの解像度": "論文を書き終えるまでに必要なタスクを正確に把握できていない",
            "感情的なハードル": "完成した時に受けるフィードバックが怖い",
            "報酬優先": "他にもっと楽しいタスクがあるので、手を付けようと思わない",
            "対人要因": "指導教員や共著者等との連絡が面倒",
            "コンディション": "疲れ等によって、体のコンディションが整っていない",
            "タスク粒度が粗い": "やらなきゃいけないタスクはわかっているが、そのタスクを完了させるまでが長い",
        }
        return {"causes_raw": _json.dumps({"causes": mock_causes}, ensure_ascii=False)}
    causes_raw = await asyncio.to_thread(suggest_causes, request.task_name, request.task_desc)
    return {"causes_raw": causes_raw}


@app.post("/api/report")
async def create_report(request: ReportRequest):
    """タスク情報をもとにレポートを生成し、Server-Sent Eventsで進捗と結果を返す。

    Args:
        request: タスク名とタスク説明を含むリクエスト。
    """

    async def event_stream():
        """レポート生成の進捗をSSEで逐次配信するジェネレータ。"""
        if USE_MOCK:
            for step, message in [
                ("analyzing", "タスクを分析しています..."),
                ("strategizing", "先延ばし対策を考えています..."),
                ("reporting", "レポートを作成しています..."),
            ]:
                yield _format_sse_event(step, message)
                await asyncio.sleep(0.4)
            report = _load_latest_report()
        else:
            save_dir = OUTPUT_DIR / time.strftime("%Y%m%d-%H%M%S")

            yield _format_sse_event("analyzing", "タスクを分析しています...")
            await asyncio.sleep(0)

            task_analysis = await asyncio.to_thread(
                analyze_task, request.task_name, request.task_desc, save_dir, request.selected_cause
            )

            yield _format_sse_event("strategizing", "先延ばし対策を考えています...")
            await asyncio.sleep(0)

            task_strategy = await asyncio.to_thread(generate_task_strategy, task_analysis, save_dir)

            yield _format_sse_event("reporting", "レポートを作成しています...")
            await asyncio.sleep(0)

            report = await asyncio.to_thread(generate_report, task_strategy, save_dir)

        yield f"data: {json.dumps({'step': 'done', 'report': report}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _format_sse_event(step: str, message: str) -> str:
    """Server-Sent Events形式のデータ文字列を生成する。

    インライン化するとjson.dumpsとf文字列の結合で120字を超えるため関数化している。

    Args:
        step: 現在の処理ステップ名。
        message: ユーザーに表示するメッセージ。

    Returns:
        SSE形式のデータ文字列。
    """
    payload = {"step": step, "message": message}
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _load_latest_report() -> str:
    """最新のレポートファイルを読み込んで返す。

    Returns:
        最新レポートのテキスト。存在しない場合はエラーメッセージ。
    """
    dirs = sorted(OUTPUT_DIR.glob("*/"), reverse=True)
    for d in dirs:
        report_file = d / "03_report.md"
        if report_file.exists():
            text = report_file.read_text(encoding="utf-8").strip()
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return text.strip()
    return "# レポートが見つかりませんでした\n`output/` に `03_report.md` がありません。"
