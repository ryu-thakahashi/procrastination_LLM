# 先延ばし防止レポート生成AI

先延ばしにしているタスクを入力すると、その原因を分析し、具体的な対策レポートを生成するWebアプリです。
バックエンドはFastAPI、AIはGemini 2.5 Flashを使用しています。

## 機能

- タスク名と説明を入力すると、3ステップでレポートを自動生成
  1. **タスク分析**: 先延ばしの原因（期待感・タスク価値・フィードバック時間）を分析
  2. **対策立案**: 原因に対応した具体的な解決策を生成
  3. **レポート出力**: Markdownレポートをリアルタイムストリーミングで表示
- 生成されたレポートは `output/YYYYMMDD-HHMMSS/` に自動保存

## ディレクトリ構成

```
app/
├── main.py                  # FastAPIエントリーポイント
├── services/
│   └── procrastination.py   # Gemini API呼び出し・レポート生成ロジック
├── static/
│   ├── index.html           # フロントエンドUI（Tailwind CSS）
│   └── app-icon.svg
├── output/                  # 生成レポートの保存先（自動作成）
│   └── YYYYMMDD-HHMMSS/
│       ├── 01_task_analysis.md
│       ├── 02_task_strategy.md
│       └── 03_report.md
└── .env                     # 環境変数（GOOGLE_API_KEY）
```

プロンプトファイルは親ディレクトリの `prompts/` に配置されています。

```
prompts/
├── analyze_task.md          # タスク分析プロンプト
├── generate_task_strategy.md
├── generate_report.md
└── is_single_task.md
```

## セットアップ

### 前提条件

- Python 3.12+
- [Poetry](https://python-poetry.org/) がインストール済み
- Google AI Studio で取得した Gemini API キー

### インストール

リポジトリのルートで依存関係をインストールします。

```bash
poetry install
```

### 環境変数の設定

`app/.env` に Google API キーを設定します。

```
GOOGLE_API_KEY=your_api_key_here
```

## 起動方法

リポジトリのルートで以下を実行します。

```bash
poetry run uvicorn app.main:app --reload
```

ブラウザで `http://localhost:8000` を開くとUIが表示されます。

## モック起動（API不使用）

Gemini APIを呼び出さずに動作確認したい場合は、`USE_MOCK=true` を指定します。
`output/` 内の最新レポートが返されます。

```bash
USE_MOCK=true poetry run uvicorn app.main:app --reload
```

## API

### `POST /api/report`

レポートを生成するエンドポイント。Server-Sent Events (SSE) でストリーミング応答します。

**リクエスト**

```json
{
  "task_name": "就活のES作成",
  "task_desc": "サイバーエージェントに提出するESの作成を先延ばししてしまう。"
}
```

**レスポンス（SSEイベント）**

| `step`        | 内容                         |
|---------------|------------------------------|
| `analyzing`   | タスク分析中                 |
| `strategizing`| 先延ばし対策の立案中         |
| `reporting`   | レポート生成中               |
| `done`        | 完了。`report` フィールドにMarkdown形式のレポートが入る |
