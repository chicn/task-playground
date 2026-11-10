---
name: todo-capture
description: 議事録の Next Action、または Journal の「今日やり切ること」から TODO を取り出し、AI に任せられるかの提案を付けて確認を取り、Notion の Tasks に登録する。議事録を作り終えた直後、または Morning Manifesto を書き終えた直後に使う。「TODOにして」「タスク登録して」「議事録からタスクを作って」と言われたときも使う。
---

# todo-capture

議事録または Journal から TODO を取り出し、Notion の Tasks に登録する。AI に任せられるタスクが1件でもあれば、最後に `ai-task-run` に進む。

## 入力

- 議事録: Notion の Meetings ページの URL。`/gijiroku` や `/plaud-gijiroku` が表示した URL を使う
- Journal: 日付（省略時は今日）。ファイルは `/Users/chihiro/Projects/private-cc/Succsess-Habits/morning-manifesto/journal_YYYY-MM-DD.md`

どちらか分からない場合だけ、ユーザーに聞く。

## 固定情報

| 項目 | 値 |
|---|---|
| Tasks | `collection://fa540ced-eb27-82c7-949c-876f41424223` |
| Projects | `collection://98340ced-eb27-8333-9895-073e3e27dbb3` |

Tasks のプロパティ: `Task name`（title）、`Status`、`Due`（date）、`Priority`、`Project`（Projects への relation）、`AI`（checkbox）、`AI state`（待機 / 実行中 / レビュー待ち / 要対応）、`Source`（Meeting / Journal）、`Source URL`（url）、`Result URL`（url）。

## 手順

### 1. 候補を取り出す

- 議事録: ページを `notion-fetch` で読み、`## Next Action` の未チェック項目（`- [ ]`）を取る。`[調査]` `[連絡]` の接頭辞はタスク名に残す。チェック済みの項目は対象外
- Journal: ファイルを読み、見出し `### 4. ◎ 今日「やり切る」ことは?` の下の箇条書きを取る。書式は日によって揺れるので、次のように読む
  - 親の項目（プロジェクト名や大きな括り）は `Project` の候補にする。子の項目をタスクにする。子が無い項目はそれ自体をタスクにする
  - `90min`、`30min` などの所要時間はタスク名から外し、本文に書く
  - タスクのさらに下にある補足の行（例: 「後ちょっとで決められそう、というものを作る」）はタスクにせず、そのタスクの本文に原文のまま書く
  - チェックボックスが付いた項目で `[x]` のものは対象外
  - 書かれた文言は変えない。要約も言い換えもしない

Journal ファイルには書き込まない。読むだけにする。このリポジトリでは、Claude がジャーナルの内容を書くことが禁止されている。

### 2. AI に任せるかを提案する

各候補に「AI」か「自分」を付ける。

- AI 向き: 調査、情報収集、比較、分析、資料・文面・議事録の下書き
- 自分向き: 判断、対人の調整、会議への出席、`[連絡]` の送信そのもの

`[連絡]` は、送信は自分向きだが、文面の下書きだけなら AI 向きとして扱える。その場合はタスク名を変えず、本文に「文面の下書きまで」と書く。迷うものは「自分」にする。

### 3. 確認を取る

次の表を見せて、修正や除外を受け付ける。確認が取れるまで Notion には書かない。

| # | タスク名 | AI / 自分 | Project | Due |
|---|---|---|---|---|

Project は次のように決める。

- Projects を `notion-query-data-sources` で引き、`Project name` が一致する行があるときだけ結ぶ
- 一致する行が無いときは空にする。Projects に行を新しく作らない
- 議事録の `Project`（select）がクライアント名なら、Projects の同名の行を探す

Due は、Journal 由来なら当日。議事録由来は、期限が書かれているときだけ入れる。

### 4. Notion に登録する

重複を避けるため、先に既存のタスクを調べる。

- 議事録: `Source URL` が同じで、`Task name` が同じものがあれば作らない
- Journal: `Source` が Journal で、`Due` が同じ日で、`Task name` が同じものがあれば作らない

作るときは `notion-create-pages` を使う。

- `data_source_id`: Tasks の ID
- `Task name`、`Status`（Not Started）、`Source`、`Source URL`（議事録のときだけ）、`date:Due:start`、`Project`
- AI タスクは `AI`=`__YES__`、`AI state`=`待機` を足す。自分向きのタスクは `AI` も `AI state` も入れない
- ページ本文に背景を書く。議事録なら該当する箇所の引用と議事録へのリンク、Journal なら所要時間と親の項目

作った件数、重複で飛ばした件数、AI タスクの件数を、各ページの URL とともに報告する。

### 5. AI タスクがあれば続ける

AI タスクが1件以上ある場合は、`ai-task-run` を、今登録したタスクを対象に実行する。ユーザーが「登録だけ」と言っている場合は進まない。

## 守ること

- Notion に書くのは、手順3の確認が取れた後だけ
- 既存のタスクの内容は書き換えない
- 秘密情報（パスワード、トークン、個人情報）はタスク名や本文に写さない
