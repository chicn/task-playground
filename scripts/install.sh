#!/usr/bin/env bash
# 指定したプロジェクトの .claude/skills/ に、このリポジトリのスキルをシンボリックリンクで入れる。
#
# 使い方:
#   scripts/install.sh <プロジェクトのパス>
#   scripts/install.sh --uninstall <プロジェクトのパス>
#
# リンク先は「このスクリプトがあるチェックアウト」の skills/。
# 確認中はワークツリーから、マージ後は main のチェックアウトから実行し直すと、向き先が切り替わる。
set -euo pipefail

usage() {
  echo "使い方: $0 [--uninstall] <プロジェクトのパス>" >&2
  exit 2
}

uninstall=0
if [ "${1:-}" = "--uninstall" ]; then
  uninstall=1
  shift
fi
[ $# -eq 1 ] || usage

project="$(cd "$1" 2>/dev/null && pwd)" || { echo "エラー: $1 が見つかりません" >&2; exit 1; }
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="$here/skills"
dest="$project/.claude/skills"

if [ "$project" = "$here" ]; then
  echo "エラー: task-playground 自身には入れません" >&2
  exit 1
fi

# 入れるスキル = skills/ 直下で SKILL.md を持つディレクトリ
skills=()
for d in "$src"/*/; do
  [ -f "${d}SKILL.md" ] && skills+=("$(basename "$d")")
done
[ ${#skills[@]} -gt 0 ] || { echo "エラー: $src にスキルがありません" >&2; exit 1; }

if [ "$uninstall" -eq 1 ]; then
  for name in "${skills[@]}"; do
    link="$dest/$name"
    if [ -L "$link" ]; then
      rm "$link"
      echo "削除: $link"
    fi
  done
  exit 0
fi

mkdir -p "$dest"
for name in "${skills[@]}"; do
  link="$dest/$name"
  if [ -e "$link" ] && [ ! -L "$link" ]; then
    echo "エラー: $link は既にあり、リンクではありません。上書きしません" >&2
    exit 1
  fi
  ln -sfn "$src/$name" "$link"
  echo "リンク: $link -> $src/$name"
done

# プロジェクトが git リポジトリなら、リンクを差分に出さない（この Mac 専用の絶対パスのため）
if git -C "$project" rev-parse --git-dir >/dev/null 2>&1; then
  exclude="$(git -C "$project" rev-parse --path-format=absolute --git-path info/exclude)"
  mkdir -p "$(dirname "$exclude")"
  touch "$exclude"
  for name in "${skills[@]}"; do
    line="/.claude/skills/$name"
    if ! grep -qxF "$line" "$exclude"; then
      echo "$line" >> "$exclude"
      echo "除外: ${line} (${exclude})"
    fi
  done
fi
