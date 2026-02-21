#!/bin/bash

session_name="menu"
directory="$HOME/Sync/healthy-menu"

# Убиваем старую сессию, если есть
tmux kill-session -t "$session_name" 2>/dev/null

cd $directory/backend
#source venv/bin/activate

# Создаём сессию с первым окном сразу
tmux new-session -d -s "$session_name" -n "lzg"
tmux send-keys -t "$session_name":lzg "lzg" C-m
tmux rename-window lzg🧩 

# Остальные окна
tmux new-window -t "$session_name" -n "new"
tmux send-keys -t "$session_name":new "cd $directory/backend" C-m
tmux send-keys -t "$session_name":new "hx" C-m
tmux rename-window back⚙️ 

tmux new-window -t "$session_name" -n "new"
tmux send-keys -t "$session_name":new "cd $directory/frontend" C-m
tmux send-keys -t "$session_name":new "hx" C-m
tmux rename-window front🎨

tmux new-window -t "$session_name" -n "new"
tmux send-keys -t "$session_name":new "cd $directory/backend" C-m
tmux send-keys -t "$session_name":new "vim" C-m
tmux rename-window db🗄️

tmux new-window -t "$session_name" -n "new"
tmux send-keys -t "$session_name":new "cd $directory/k8s" C-m
tmux send-keys -t "$session_name":new "hx" C-m
tmux rename-window k8s☸️

tmux new-window -t "$session_name" -n "new"
tmux send-keys -t "$session_name":new "k9s" C-m
tmux rename-window k9s🐶

tmux new-window -t "$session_name" -n "new"
tmux send-keys -t "$session_name":new "helm" C-m
tmux rename-window helm⚓️ 

tmux new-window -t "$session_name" -n "new"
tmux send-keys -t "$session_name":new "lzd" C-m
tmux rename-window lzd🐳

tmux new-window -t "$session_name" -n "new"
tmux send-keys -t "$session_name":new "kaskade consumer -b kafka:9092 -t new_orders" C-m
tmux rename-window kafka☕️


# Выбираем первое окно и подключаемся
tmux select-window -t "$session_name":lzg🧩
tmux attach-session -t "$session_name"


