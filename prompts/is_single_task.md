## original input

{{
"title": "{task_name}",
"description": "{task_desc}",
}}

## 例1

### 入力

{{
    "title": "就活のES作成",
    "description": "サイバーエージェントに提出するESの作成を先延ばししてしまう。"
}}

### 出力

{{
    "tasks": ["就活のES作成"],
    "task_is_single": true,
}}

## 例2

### 入力

{{
    "title": "研究助成の申請書・研究発表の資料作成",
    "description": "研究助成金の獲得に向けた申請書の執筆および、付随する説明資料の作成を先延ばしにしてしまう。"
}}

### 出力

{{
    "tasks": ["研究助成の申請書作成", "研究発表の資料作成"],
    "task_is_single": true,
}}
