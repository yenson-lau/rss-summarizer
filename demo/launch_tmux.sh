TMUX="RSSDemo"
if [ "$1" = 'kill' ] || [ "$1" = 'reset' ]; then
  tmux kill-session -t $TMUX
fi
if [ ! "$1" = 'kill' ]; then
  if ! tmux a -t $TMUX; then
    tmux new-session \; \
      rename-session $TMUX \; \
      send-keys 'vim demo/example_texts_1.json' Enter C-l \; \
      split-window -h \; \
      send-keys C-l \; \
      send-keys 'curl -X POST -H "Content-Type: application/json" -d @demo/example_texts_1.json https://volatile-steel.herokuapp.com/texts' \; \
      select-pane -t 0 \; \
      rename-window texts1 \; \
      \; \
      new-window \; \
      send-keys 'vim demo/example_texts_2.json' Enter C-l \; \
      split-window -h \; \
      send-keys C-l \; \
      send-keys 'curl -X POST -H "Content-Type: application/json" -d @demo/example_texts_2.json https://volatile-steel.herokuapp.com/texts' \; \
      select-pane -t 0 \; \
      rename-window texts2 \; \
      \; \
      new-window \; \
      send-keys 'vim demo/example_rss.json' Enter C-l \; \
      split-window -h \; \
      send-keys C-l \; \
      send-keys 'curl -X POST -H "Content-Type: application/json" -d @demo/example_rss.json https://volatile-steel.herokuapp.com/rss' \; \
      select-pane -t 0 \; \
      rename-window rss \; \
      \; \
      select-window -t 0 \; \
      \;
  fi
fi
