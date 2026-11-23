#!/bin/bash
# start detached tmux sessions: pybot-watch (round scorer) and pybot-chat (bot-vs-bot loop)
ROOT=$HOME/research/pybot-play; REPO=$ROOT/pybot; export PATH=/opt/homebrew/bin:$HOME/.local/share/mise/shims:$PATH
rm -f $ROOT/STOP
tmux new-session -d -s pybot-watch "bash $REPO/play/watch.sh >> $ROOT/logs/watch.out 2>&1"
tmux new-session -d -s pybot-chat "cd $REPO && uv run --no-project python play/botchat.py --turns 30 --seeds 0-1 --loop --out $ROOT/logs/chats.jsonl >> $ROOT/logs/chat.out 2>&1"
