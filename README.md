# task-playground

議事録と Journal から TODO を作り、AI に任せられるものは AI が実行して結果を共有するスキルを開発するリポジトリ。

## 流れ

```
議事録を作る（/gijiroku, /plaud-gijiroku）─┐
                                          ├─ todo-capture ─ Notion Tasks に登録 ─ ai-task-run ─ ShareDoc ─ Notion と Slack に報告
Morning Manifesto を書く ──────────────────┘
```

1. `todo-capture`: 議事録の `## Next Action`、Journal の「今日やり切ること」、または貼り付けたメモから TODO を取り出す。タスク名は分類込み35文字までに短くし、完了条件（Done）を本文に書く。AI に任せるかを提案し、確認してから Notion の Tasks に登録する
2. `ai-task-run`: `AI` フラグ付きのタスクを、調査と下書きの範囲で AI が実行する。成果物を ShareDoc に上げ、Notion の `Result URL` に記録し、Slack の自分宛 DM で知らせる

## 入れ方

使うプロジェクトにだけ、シンボリックリンクで入れる。

```sh
scripts/install.sh ~/Projects/ai-lab/meeting-notes
scripts/install.sh /Users/chihiro/Projects/private-cc/Succsess-Habits
```

外すときは `--uninstall` を付ける。リンク先は、スクリプトを実行したチェックアウトの `skills/` になる。詳しい運用は `CLAUDE.md` を見る。

### Notion Task Database

https://app.notion.com/p/ivoryinc/Projects-Tasks-38e40cedeb2783a7ae1f81d940cbd0bb
