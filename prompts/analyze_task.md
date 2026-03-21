## タスク分析の実施

与えられたタスクの情報をもとに、タスク分析を実施してください。

## 制約

- `preventing_factors` の各値（task_expectations / task_value / feedback_time）は **20字以内** で記述すること。

## タスク情報

{{
    "title": "{task_name}",
    "description": "{task_desc}",
}}

## 例1

### 入力

{{
    "title": "論文執筆",
    "description": "Social Networks に出す論文の執筆を先延ばしにしてしまう。",
}}

### 出力

{{
    "title": "論文執筆",
    "description": "Social Networks に出す論文の執筆を先延ばしにしてしまう。",
    "minimum_goal": "Social Networks に出す論文の初稿を保存する",
    "milestone": [
        "outline の作成"
        "introduction の執筆",
        "methods の執筆",
        "データ分析",
        "results の執筆",
        "discussion の執筆",
        "原稿の確認・修正",
        "初稿完成",
    ],
    "preventing_factors": {{
        "task_expectations": "初稿を完成させられるきがしない",
        "task_value": "初稿が完成できなかったときの損失を過大推定",
        "feedback_time": "初稿完成までに時間がかかりすぎる",
    }}
}}

## 例2

### 入力

{{
    "title": "就活のES作成",
    "description": "サイバーエージェントに提出するESの作成を先延ばししてしまう。"
}}

### 出力

{{
    "title": "就活のES作成",
    "description": "サイバーエージェントに提出するESの作成を先延ばししてしまう。",
    "minimum_goal": "サイバーエージェントのESを1社分、項目を埋めた状態で保存する",
    "milestone": [
        "企業研究（求める人物像の言語化）",
        "自己分析とエピソードの棚卸し",
        "各設問に対するプロット（骨組み）作成",
        "ガクチカ（学生時代に力を入れたこと）の執筆",
        "志望動機の執筆",
        "結論のインパクトと論理構成の確認",
        "文字数調整と誤字脱字チェック（生成AI）",
        "提出ボタンを押す"
    ],
    "preventing_factors": {{
        "task_expectations": "自分の経歴でサイバーエージェントに通用する気がしない",
        "task_value": "完璧な内容でないと落ちてしまうという過度なプレッシャー",
        "feedback_time": "書き上げても選考結果が出るまで時間がかかり、達成感が得にくい",
    }}
}}
