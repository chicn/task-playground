# task-playground

議事録と Journal から TODO を作り、AI に任せられるものは AI が実行して結果を共有するための**スキルを開発するリポジトリ**。ここで作ったスキルを、使うプロジェクトにだけシンボリックリンクで入れて使う。このリポジトリ自体では議事録も Journal も実行しない。

## 構成

- `skills/todo-capture/SKILL.md`: 議事録の Next Action、または Journal の「今日やり切ること」から TODO を取り出し、AI に任せるかの提案を付けて確認し、Notion の Tasks に登録する
- `skills/ai-task-run/SKILL.md`: `AI` フラグ付きの待機中タスクを実行し、ShareDoc で共有して Notion と Slack に報告する
- `scripts/install.sh <プロジェクトのパス>`: 指定したプロジェクトの `.claude/skills/` にリンクする。`--uninstall` で外す
- `skills/SKILL.md`: 空のプレースホルダー（スキルとしては入らない）

## 入れ先

| プロジェクト | 用途 | 連携の書き場所 |
|---|---|---|
| `~/Projects/ai-lab/meeting-notes` | 議事録（`/gijiroku`、`/plaud-gijiroku`）を作った後に TODO を登録する | そのプロジェクトの `CLAUDE.md` |
| `/Users/chihiro/Projects/private-cc/Succsess-Habits` | Morning Manifesto の後に TODO を登録する | `morning-manifesto/SKILL.md` の「完了後」 |

`~/.claude/`（グローバル）には入れない。`~/.claude/commands/gijiroku.md` などグローバルのファイルは書き換えない。

## 運用

- **main がそのまま本番になる**: リンク先は main のチェックアウトなので、main に入れた時点で入れ先の全プロジェクトに反映される。開発はブランチかワークツリーで行い、試してから main に入れる
- 確認中は、ワークツリーの `scripts/install.sh` を実行するとリンクがワークツリーを向く。マージ後に main のチェックアウトで実行し直すと、main を向く
- スキルは場所に依存させない。どのプロジェクトから呼んでも動くよう、Notion の ID はスキル内に書く

## Notion

Projects & Tasks: https://app.notion.com/p/38e40cedeb2783a7ae1f81d940cbd0bb

| DB | data source |
|---|---|
| Tasks | `collection://fa540ced-eb27-82c7-949c-876f41424223` |
| Projects | `collection://98340ced-eb27-8333-9895-073e3e27dbb3` |
| Meetings（議事録の置き場。参照のみ） | `collection://28eb4478-7cd2-43e6-929f-170e1b243216` |

Tasks に追加したプロパティ:

| プロパティ | 型 | 意味 |
|---|---|---|
| `AI` | checkbox | AI に任せるタスクか |
| `AI state` | select | 待機 / 実行中 / レビュー待ち / 要対応。`Status` を Done にするのは人 |
| `Source` | select | Meeting / Journal |
| `Source URL` | url | 議事録ページの URL（Journal のときは空） |
| `Result URL` | url | AI の成果物（ShareDoc）の URL |

## AI に任せてよい範囲

- してよい: Web 調査、Notion・Drive・ローカルファイルの読み取り、文章や文面の下書き
- しない: メール送信、他人への Slack 投稿、カレンダー変更、push、削除。`[連絡]` は文面の下書きまで
- 情報が足りない、判断が要る、根拠が見つからないときは、推測せず `AI state`=`要対応` にして質問する

成果物は `~/.local/share/task-playground/outputs/YYYY-MM-DD/` に置く（リポジトリの外）。ShareDoc の共有範囲は組織の全メンバーで、本人限定にはできない。

## 注意

- Succsess-Habits の Journal は読むだけにする。Claude がジャーナルの内容を書くことは、同リポジトリで禁止されている。同リポジトリでは、コミットも明示の指示があるときだけ行う
- URL の直後には半角スペースを置く（`~/.claude/CLAUDE.md` の規則）
