#!/usr/bin/env python3
"""ワークログの書き忘れを防ぐ Claude Code の hook。

使い方（.claude/settings.json から呼ばれる）:
  worklog-check.py commit   PreToolUse(Bash): git commit の前に、今日の日付のワークログがあるか確かめる
  worklog-check.py stop     Stop: ワークログを書かずに作業が続いていたら、応答の終わりに一度確認する

どちらも、失敗したら何もせず通す。hook の不具合で作業を止めないため。
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

WORKLOG_DIR = "docs/worklog"

# stop: 前回ワークログを書いてから（または前回確認してから）ツールをこの回数使ったら確認する。
STOP_THRESHOLD = int(os.environ.get("WORKLOG_STOP_THRESHOLD", "10"))

# 作業として数えないツール。
IGNORED_TOOLS = {"AskUserQuestion", "TodoWrite", "ToolSearch", "Skill", "ExitPlanMode", "EnterPlanMode"}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

GIT_COMMIT = re.compile(r"\bgit\b(\s+-[cC]\s+\S+)*\s+commit\b")


def repo_root(cwd):
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except Exception:
        pass
    return Path(cwd)


def worklog_dir(data):
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    path = repo_root(cwd) / WORKLOG_DIR
    return path if path.is_dir() else None


def check_commit(data):
    if data.get("tool_name") != "Bash":
        return
    command = (data.get("tool_input") or {}).get("command") or ""
    if not GIT_COMMIT.search(command):
        return
    directory = worklog_dir(data)
    if directory is None:
        return
    today = datetime.now().strftime("%Y-%m-%d")
    if any(directory.glob(f"{today}-*.md")):
        return
    reason = (
        f"今日（{today}）の日付のワークログが {WORKLOG_DIR}/ にありません。"
        "CLAUDE.md の Worklog 節に従ってこの作業のワークログを書き、同じコミットに含めてから、もう一度コミットしてください。"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def count_tools(transcript_path):
    """(ツールを使った総数, 最後にワークログへ書いた時点の総数) を返す。"""
    total = 0
    last_write = 0
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") != "assistant" or entry.get("isSidechain"):
                continue
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name = block.get("name") or ""
                if name in IGNORED_TOOLS:
                    continue
                total += 1
                path = str((block.get("input") or {}).get("file_path") or "")
                if name in WRITE_TOOLS and f"/{WORKLOG_DIR}/" in path:
                    last_write = total
    return total, last_write


def check_stop(data):
    if data.get("stop_hook_active"):
        return
    transcript = data.get("transcript_path")
    if not transcript or not os.path.isfile(transcript):
        return
    if worklog_dir(data) is None:
        return

    total, last_write = count_tools(transcript)

    state_dir = Path(tempfile.gettempdir()) / "claude-worklog-hook"
    state_file = state_dir / f"{data.get('session_id') or 'unknown'}.json"
    last_asked = 0
    try:
        last_asked = int(json.loads(state_file.read_text()).get("asked_at", 0))
    except Exception:
        pass

    if total - max(last_write, last_asked) < STOP_THRESHOLD:
        return

    state_dir.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps({"asked_at": total}))
    reason = (
        "ワークログの確認です。前回ワークログを書いてから作業が続いています。"
        f"依頼された作業（コードを変更しない調査や検討も含む）が一区切りついていれば、CLAUDE.md の Worklog 節に従って {WORKLOG_DIR}/ に記録してください。"
        "まだ途中の場合と、記録するほどの作業をしていない場合は、何も書かずにそのまま応答を終えてください。この確認についてユーザーに説明する必要はありません。"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        data = json.load(sys.stdin)
        if mode == "commit":
            check_commit(data)
        elif mode == "stop":
            check_stop(data)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
