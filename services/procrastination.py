import json
import os
import re
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from google import genai

load_dotenv(find_dotenv())
GEMINI_API = os.getenv("GOOGLE_API_KEY")
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def get_gemini_response(contents: str) -> str:
    client = genai.Client(api_key=GEMINI_API)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
    )
    return response.text


def formatting_as_json(response_text: str):
    removed = re.sub("```json|```", "", response_text)
    return json.loads(removed)


def _save(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def analyze_task(task_name: str, task_desc: str, save_dir: Path | None = None) -> str:
    with open(PROMPTS_DIR / "analyze_task.md", "r", encoding="utf-8") as f:
        prompt = f.read().format(task_name=task_name, task_desc=task_desc)
    response = get_gemini_response(contents=prompt)
    if save_dir:
        _save(response, save_dir / "01_task_analysis.md")
    return response


def generate_task_strategy(task_info: str, save_dir: Path | None = None) -> str:
    with open(PROMPTS_DIR / "generate_task_strategy.md", "r", encoding="utf-8") as f:
        prompt = f.read().format(task_info=task_info)
    response = get_gemini_response(contents=prompt)
    if save_dir:
        _save(response, save_dir / "02_task_strategy.md")
    return response


def generate_report(task_strategy: str, save_dir: Path | None = None) -> str:
    with open(PROMPTS_DIR / "generate_report.md", "r", encoding="utf-8") as f:
        prompt = f.read().format(task_strategy=task_strategy)
    response = get_gemini_response(contents=prompt)
    if save_dir:
        _save(response, save_dir / "03_report.md")
    return response
