import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from google import genai

load_dotenv(find_dotenv())

GEMINI_API = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"
_GEMINI_CLIENT = genai.Client(api_key=GEMINI_API)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def analyze_task(task_name: str, task_desc: str, save_dir: Path | None = None) -> str:
    """タスクを分析してAIの応答を返す。

    Args:
        task_name: タスク名。
        task_desc: タスクの説明。
        save_dir: 結果の保存先ディレクトリ。Noneの場合は保存しない。

    Returns:
        タスク分析結果のテキスト。
    """
    prompt = (
        (PROMPTS_DIR / "analyze_task.md").read_text(encoding="utf-8").format(task_name=task_name, task_desc=task_desc)
    )
    response = _get_gemini_response(prompt)
    _save_if_needed(response, save_dir, "01_task_analysis.md")
    return response


def _get_gemini_response(contents: str) -> str:
    """Gemini APIにリクエストを送り、レスポンスを返す。

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


def generate_task_strategy(task_info: str, save_dir: Path | None = None) -> str:
    """タスク情報をもとに先延ばし対策を生成する。

    Args:
        task_info: タスク分析結果のテキスト。
        save_dir: 結果の保存先ディレクトリ。Noneの場合は保存しない。

    Returns:
        先延ばし対策のテキスト。
    """
    prompt = (PROMPTS_DIR / "generate_task_strategy.md").read_text(encoding="utf-8").format(task_info=task_info)
    response = _get_gemini_response(prompt)
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
    prompt = (PROMPTS_DIR / "generate_report.md").read_text(encoding="utf-8").format(task_strategy=task_strategy)
    response = _get_gemini_response(prompt)
    _save_if_needed(response, save_dir, "03_report.md")
    return response
