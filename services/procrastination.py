import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
import google.genai as genai

load_dotenv(find_dotenv())

GEMINI_API = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"
_GEMINI_CLIENT = genai.Client(api_key=GEMINI_API)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

_SPLIT_MARKERS: dict[str, str] = {
    "suggest_causes": "## タスク情報",
    "analyze_task": "## タスク情報",
    "generate_task_strategy": "## タスク情報",
    "generate_report": "## 入力データ",
}

_CACHE_CHAR_THRESHOLD = 2000

_PROMPT_CACHES: dict[str, str | None] = {k: None for k in _SPLIT_MARKERS}


def _split_prompt(prompt_key: str) -> tuple[str, str]:
    """プロンプトファイルを静的部分と動的テンプレートに分割する。

    Args:
        prompt_key: プロンプトファイル名（拡張子なし）。

    Returns:
        (static_part, dynamic_template) のタプル。
    """
    text = (PROMPTS_DIR / f"{prompt_key}.md").read_text(encoding="utf-8")
    marker = _SPLIT_MARKERS[prompt_key]
    idx = text.find(marker)
    if idx == -1:
        return text, ""
    return text[:idx].rstrip(), text[idx:]


def initialize_caches() -> None:
    """全プロンプトの静的部分をGeminiにキャッシュする。サーバー起動時に呼び出す。"""
    print("[cache] google.genai ライブラリでのキャッシュ初期化をスキップ（フォールバックモード）")


def suggest_causes(task_name: str) -> str:
    """タスクの先延ばし原因をGeminiから取得し、生テキストで返す。

    Args:
        task_name: タスク名。

    Returns:
        Geminiのレスポンス文字列（JSONテキスト）。
    """
    _, tmpl = _split_prompt("suggest_causes")
    dynamic = tmpl.format(task_name=task_name)
    return _get_gemini_response_cached("suggest_causes", dynamic)


def analyze_task(task_name: str, task_desc: str, save_dir: Path | None = None, selected_cause: str = "") -> str:
    """タスクを分析してAIの応答を返す。

    Args:
        task_name: タスク名。
        task_desc: タスクの説明。
        save_dir: 結果の保存先ディレクトリ。Noneの場合は保存しない。
        selected_cause: ユーザーが選択した先延ばし原因。空文字の場合は無視する。

    Returns:
        タスク分析結果のテキスト。
    """
    _, tmpl = _split_prompt("analyze_task")
    dynamic = tmpl.format(task_name=task_name, task_desc=task_desc, selected_cause=selected_cause)
    response = _get_gemini_response_cached("analyze_task", dynamic)
    _save_if_needed(response, save_dir, "01_task_analysis.md")
    return response


def generate_task_strategy(task_info: str, save_dir: Path | None = None) -> str:
    """タスク情報をもとに先延ばし対策を生成する。

    Args:
        task_info: タスク分析結果のテキスト。
        save_dir: 結果の保存先ディレクトリ。Noneの場合は保存しない。

    Returns:
        先延ばし対策のテキスト。
    """
    _, tmpl = _split_prompt("generate_task_strategy")
    dynamic = tmpl.format(task_info=task_info)
    response = _get_gemini_response_cached("generate_task_strategy", dynamic)
    _save_if_needed(response, save_dir, "02_task_strategy.md")
    return response


def generate_report(task_strategy: str, save_dir: Path | None = None) -> str:
    """先延ばし対策をもとにレポートを生成する。

    Args:
        task_strategy: 先延ばし対策のテキスト。
        save_dir: 結果の保存先ディレクトリ。Noneの場合は保存しない。

    Returns:
        生成されたレポートのテキスト。
    """
    _, tmpl = _split_prompt("generate_report")
    dynamic = tmpl.format(task_strategy=task_strategy)
    response = _get_gemini_response_cached("generate_report", dynamic)
    _save_if_needed(response, save_dir, "03_report.md")
    return response


def _get_gemini_response(contents: str) -> str:
    """Gemini APIにリクエストを送り、レスポンスを返す（キャッシュなし）。

    Args:
        contents: Geminiに送るプロンプト文字列。

    Returns:
        Geminiのレスポンステキスト。
    """
    response = _GEMINI_CLIENT.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
    )
    return response.text


def _get_gemini_response_cached(prompt_key: str, dynamic_content: str) -> str:
    """キャッシュを利用してGeminiにリクエストする。キャッシュ未設定時はフォールバック。

    Args:
        prompt_key: プロンプトキー（_PROMPT_CACHES のキー）。
        dynamic_content: ユーザー固有の動的コンテンツ。

    Returns:
        Geminiのレスポンステキスト。
    """
    static_part, _ = _split_prompt(prompt_key)
    return _get_gemini_response(static_part + "\n\n" + dynamic_content)


def _save_if_needed(text: str, save_dir: Path | None, filename: str) -> None:
    """保存先が指定されている場合のみ、テキストをファイルに保存する。

    Args:
        text: 保存するテキスト。
        save_dir: 保存先ディレクトリ。Noneの場合は何もしない。
        filename: 保存するファイル名。
    """
    if save_dir is None:
        return
    save_path = save_dir / filename
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(text, encoding="utf-8")
