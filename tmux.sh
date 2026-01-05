#!/bin/bash

session_name="menu"
directory="$HOME/Sync/healthy-menu"

# Убиваем старую сессию, если есть
tmux kill-session -t "$session_name" 2>/dev/null

cd $directory/backend
source venv/bin/activate

# Создаём сессию с первым окном сразу
tmux new-session -d -s "$session_name" -n "lzg"
tmux send-keys -t "$session_name":lzg "lzg" C-m
tmux rename-window lzg🧩 

# Остальные окна
tmux new-window -t "$session_name" -n "new"
tmux send-keys -t "$session_name":back "cd $directory/backend" C-m
tmux send-keys -t "$session_name":back "hx" C-m
tmux rename-window back⚙️ 

tmux new-window -t "$session_name" -n "front"
tmux send-keys -t "$session_name":front "cd $directory/frontend" C-m
tmux send-keys -t "$session_name":front "hx" C-m
tmux rename-window front🎨

tmux new-window -t "$session_name" -n "db"
tmux send-keys -t "$session_name":db "cd $directory/backend" C-m
tmux send-keys -t "$session_name":db "vim" C-m
tmux rename-window db🗄️

tmux new-window -t "$session_name" -n "k8s"
tmux send-keys -t "$session_name":k8s "cd $directory/k8s" C-m
tmux send-keys -t "$session_name":k8s "hx" C-m
tmux rename-window lzg🧭

tmux new-window -t "$session_name" -n "k9s"
tmux send-keys -t "$session_name":k8s "k9s" C-m

tmux new-window -t "$session_name" -n "lzd"
tmux send-keys -t "$session_name":lzd "lzd" C-m
tmux rename-window lzg🐳

# Выбираем первое окно и подключаемся
tmux select-window -t "$session_name":lzg
tmux attach-session -t "$session_name"
