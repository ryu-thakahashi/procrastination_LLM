import asyncio
import json
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from services.procrastination import (
    analyze_task,
    generate_report,
    generate_task_strategy,
    initialize_caches,
    suggest_causes,
    suggest_descriptions,
)

OUTPUT_DIR = Path(__file__).parent.parent / "output"
STATIC_DIR = Path(__file__).parent / "static"

ALLOWED_ORIGINS = [
    "https://procrastination-llm.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


class TaskRequest(BaseModel):
    """タスク名のみを含むリクエスト。"""

    task_name: str


class DescriptionRequest(BaseModel):
    """タスク名と先延ばし原因を含むリクエスト。"""

    task_name: str
    selected_cause: str


class ReportRequest(BaseModel):
    """レポート生成に必要なタスク情報を含むリクエスト。"""

    task_name: str
    task_desc: str
    description_key: str = ""
    selected_cause: str


def main() -> FastAPI:
    """FastAppアプリケーションを作成・セットアップして返す。

    Returns:
        セットアップ完了したFastAppインスタンス。
    """
    app = FastAPI(title="先延ばし防止レポート生成AI", lifespan=_lifespan)
    _setup_middleware(app)
    _setup_static_files(app)
    _setup_routes(app)
    return app


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """サーバーのライフサイクルを管理するコンテキスト。

    サーバー起動時にGeminiプロンプトキャッシュを初期化する。

    Args:
        app: FastAppインスタンス。
    """
    await asyncio.to_thread(initialize_caches)
    yield


def _setup_middleware(app: FastAPI) -> None:
    """CORSミドルウェアを設定する。

    Args:
        app: セットアップ対象のFastAppインスタンス。
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _setup_static_files(app: FastAPI) -> None:
    """静的ファイルのマウントを設定する。

    Args:
        app: セットアップ対象のFastAppインスタンス。
    """
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


async def _root() -> HTMLResponse:
    """トップページのHTMLを返す。

    Returns:
        index.htmlのコンテンツをHTMLResponseでラップしたもの。
    """
    with open(STATIC_DIR / "index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


async def _get_suggest_causes(request: TaskRequest) -> dict:
    """タスク情報をもとに先延ばし原因を5つ提案する。

    Args:
        request: タスク名を含むリクエスト。

    Returns:
        先延ばし原因のリスト。
    """
    causes_raw = await asyncio.to_thread(suggest_causes, request.task_name)
    return {"causes_raw": causes_raw}


async def _get_suggest_descriptions(request: DescriptionRequest) -> dict:
    """タスク名と原因をもとに、タスク説明候補を5つ提案する。

    Args:
        request: タスク名と原因を含むリクエスト。

    Returns:
        タスク説明候補のリスト。
    """
    descriptions_raw = await asyncio.to_thread(suggest_descriptions, request.task_name, request.selected_cause)
    return {"descriptions_raw": descriptions_raw}


async def _create_report(request: ReportRequest) -> StreamingResponse:
    """タスク情報をもとにレポートを生成し、Server-Sent Eventsで進捗と結果を返す。

    Args:
        request: タスク名とタスク説明を含むリクエスト。

    Returns:
        SSE形式のストリーミングレスポンス。
    """

    async def event_stream():
        """レポート生成の進捗をSSEで逐次配信するジェネレータ。"""
        save_dir = OUTPUT_DIR / time.strftime("%Y%m%d-%H%M%S")

        try:
            yield _format_sse_event("analyzing", "タスクを分析しています...")
            await asyncio.sleep(0)

            task_analysis = await asyncio.to_thread(
                analyze_task,
                request.task_name,
                request.task_desc,
                save_dir,
                request.selected_cause,
                request.description_key,
            )

            yield _format_sse_event("strategizing", "先延ばし対策を考えています...")
            await asyncio.sleep(0)

            task_strategy = await asyncio.to_thread(generate_task_strategy, task_analysis, save_dir)

            yield _format_sse_event("reporting", "レポートを作成しています...")
            await asyncio.sleep(0)

            report = await asyncio.to_thread(generate_report, task_strategy, save_dir)

            yield f"data: {json.dumps({'step': 'done', 'report': report}, ensure_ascii=False)}\n\n"
        except Exception as e:
            error_msg = f"処理中にエラーが発生しました: {type(e).__name__}"
            yield _format_sse_event("error", error_msg)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _setup_routes(app: FastAPI) -> None:
    """APIエンドポイントを設定する。

    Args:
        app: セットアップ対象のFastAppインスタンス。
    """
    app.add_api_route("/", _root, methods=["GET"])
    app.add_api_route("/api/suggest-causes", _get_suggest_causes, methods=["POST"])
    app.add_api_route("/api/suggest-descriptions", _get_suggest_descriptions, methods=["POST"])
    app.add_api_route("/api/report", _create_report, methods=["POST"])


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


if __name__ == "__main__":
    import uvicorn

    app = main()
    uvicorn.run(app, host="127.0.0.1", port=8000)
