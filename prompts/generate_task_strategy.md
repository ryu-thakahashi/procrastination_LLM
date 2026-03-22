## タスクの先延ばし対策案の作成

与えられたタスク情報にもとづき、タスクを先延ばしにしてしまう要因に対する対策を実施してください。

## タスク情報

{task_info}

## 例1

### 入力

{{
    "title": "論文執筆",
    "description": "Social Networks に出す論文の執筆を先延ばしにしてしまう。",
    "minimum_goal": "Social Networks に出す論文の初稿を完成させる",
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
        "task_values": "初稿が完成できなかったときの損失を過大推定",
        "feedback_time": "初稿完成までに時間がかかりすぎる",
    }}
}}

### 出力

{{
    "task_expectations": {{
        "factor": "初稿を完成させられるきがしない",
        "present": "何をすればいいか分からない",
        "empathy": "やってみてもできる気がしない",
        "solution": "正確な見積書を作成する",
        "goal_state": "完成させられそう",
        "counterplan": {{
            "break_tasks": {{
                "contents": "原稿の完成までに必要なタスク (15min/1task) を作成する",
                "who_can_do_it" : "AI",
            }},
"estimate_tasks": {{
                "contents": "タスクの所要時間を見積もる",
                "who_can_do_it" : "AI",
            }},
"estimate_tasks": {{
                "contents": "タスクの難易度 (難/普通/易) を見積もる",
                "who_can_do_it" : "AI",
            }},
"create_estimatation": {{
                "contents": "タスクの見積書を作成する",
                "who_can_do_it" : "AI",
            }}
}},
}},
"task_values": {{
        "factor": "初稿が完成できなかったときの損失を過大推定",
        "present": "原稿が完成できなかったとき、すべてが失われる気がする",
        "empathy": "損失が大き過ぎると、やる気も起きない",
        "solution": "損失を正確に見積もる",
        "goal_state": "損失はそれほど大きくないな",
        "counterplan": {{
            "counterplan_rule": [
                "worst_results, wrong_results, wrong_response, worst_response を key, 内容を value (str) の形で整理する。"
            ],
            "worst_results": "原稿の執筆を断念する",
            "worst_response": "指導教員に怒られ、評価が下がる",
            "wrong_results": "未熟な原稿が出来上がる",
            "wrong_response": "指導教員から数多くの指摘がくるが、怒られない",
        }},
}},
"feedback_time": {{
        "factor": "フィードバックまでの時間が長い",
        "present": "完成までに時間がかかりすぎて、達成感が得られない",
        "empathy": "進めているのに、達成感が得られないのは辛い",
        "solution": "マイルストーンを設定する",
        "goal_state": "進めるたびに達成感が得られる",
        "counterplan": {{
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
            "intermediate_feedback": "タスクの成果を生成AIに投げ、ポジティブなフィードバックをもらう"
        }},
}}
}}

## 例2

### 入力

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
        "task_values": "完璧な内容でないと落ちてしまうという過度なプレッシャー",
        "feedback_time": "書き上げても選考結果が出るまで時間がかかり、達成感が得にくい",
    }}
}}

### 出力

{{
    "task_expectations": {{
        "factor": "自分の経歴でサイバーエージェントに通用する気がしない",
        "present": "「自分の経歴では通用しないのではないか」という不安を感じている",
        "empathy": "自信が持てないと、どうしても筆が重くなる",
        "solution": "企業とのマッチングを正確に把握する",
        "goal_state": "自分の経験と企業の求める要素がマッチしていることを理解し、自信を持ってESを書ける",
        "counterplan": {{
            "extract_requirements": {{
                "contents": "企業が求める要素を3つ調べる",
                "who_can_do_it": "AI"
            }},
"search_experience": {{
                "contents": "要素に紐づく過去の経験を1つずつ書く",
                "who_can_do_it": "User"
            }},
"redefine_value": {{
                "contents": "「企業が求める要素」と「自分の経験」がマッチしていることを再定義する",
                "who_can_do_it": "User"
            }},
"check_compatibility": {{
                "contents": "再定義した内容をもとに「企業が自分を採用することのメリット」を書く",
                "who_can_do_it": "AI"
            }}
}}
}},
"task_values": {{
            "factor": "完璧な内容でないと落ちてしまうという過度なプレッシャー",
            "present": "完璧な内容でないと落ちると思い込んでいる",
            "empathy": "ハードルを上げすぎると、失敗を恐れてやる気も起きなくなる",
            "solution": "減点方式から加点方式への思考転換",
            "goal_state": "自分の成長を確認しながら、ESをブラッシュアップできる",
            "counterplan": {{
                "counterplan_rule": [
                    "worst_results, wrong_results, wrong_response, worst_response を key, 内容を value (str) の形で整理する。"
                ],
                "worst_results": "締め切りに間に合わず、提出すらできない（0点）",
                "worst_response": "内定が出ない",
                "wrong_results": "60点の出来だが、まずは提出する（選考対象に入る）",
                "wrong_response": "通過するかは不明だが、すくなくとも次の選考に活用できる"
            }}
}},
"task_feedbacks": {{
            "factor": "書き上げても選考結果が出るまで時間がかかり、達成感が得にくい",
            "present": "ESの枠を埋めきるまでが遠く感じられる",
            "empathy": "進めているのに、達成感が得られないのは辛い",
            "solution": "プロセス自体を報酬化する",
            "goal_state": "進めるたびに達成感が得られる",
            "counterplan": {{
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
                "self_reward": "1項目書き終えるごとに好きな飲み物を飲む",
                "intermediate_feedback": "書き上げたセクションを生成AIに投げ、ポジティブなフィードバックをもらう"
            }}
}}
}}
