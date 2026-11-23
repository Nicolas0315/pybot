#!/bin/bash
# Long-running watcher on home-mac-main. Every 120s: fetch fork tags round-*, score any new one on dev+heldout.
# Also keeps bot-vs-bot chat running in a sibling process (see run_all.sh). Stops when ~/research/pybot-play/STOP exists.
ROOT=$HOME/research/pybot-play; REPO=$ROOT/pybot; LOGS=$ROOT/logs; mkdir -p $LOGS $ROOT/wt
export PATH=$HOME/.local/share/mise/shims:/opt/homebrew/bin:$PATH
while [ ! -f $ROOT/STOP ]; do
  git -C $REPO fetch -q --tags origin 2>>$LOGS/watch.err
  for t in $(git -C $REPO tag -l 'round-*' | sort); do
    [ -f $LOGS/score_$t.done ] && continue
    rm -rf $ROOT/wt/$t; git -C $REPO worktree prune; git -C $REPO worktree add -q -f $ROOT/wt/$t $t 2>>$LOGS/watch.err || continue
    for s in dev heldout; do
      uv run --no-project python $REPO/play/score.py --bot $ROOT/wt/$t --set $REPO/play/$s.json --out $LOGS/$t.$s.json > $LOGS/$t.$s.summary.json 2>>$LOGS/watch.err
    done
    git -C $REPO rev-parse $t > $LOGS/score_$t.done
    echo "$(date '+%F %T') scored $t" >> $LOGS/watch.log
    git -C $REPO worktree remove --force $ROOT/wt/$t
  done
  sleep 120
done
echo "$(date '+%F %T') STOP seen, exiting" >> $LOGS/watch.log
