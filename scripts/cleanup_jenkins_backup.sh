#!/bin/bash
#
# Скрипт очистки backup Jenkins для переноса в новый контейнер
# Удаляет временные файлы, кэши, плагины и историю сборок
# Сохраняет конфигурацию, credentials и структуру jobs
#

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Логирование
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка аргументов
if [ -z "$1" ]; then
    echo "Использование: $0 <путь_к_jenkins_home> [опции]"
    echo ""
    echo "Опции:"
    echo "  --keep-builds     Сохранить историю сборок (по умолчанию удаляется)"
    echo "  --dry-run         Показать что будет удалено без фактического удаления"
    echo "  --help            Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 /path/to/jenkins_home"
    echo "  $0 /path/to/jenkins_home --keep-builds"
    echo "  $0 /path/to/jenkins_home --dry-run"
    exit 1
fi

JENKINS_HOME="$1"
KEEP_BUILDS=false
DRY_RUN=false

# Парсинг аргументов
shift
while [ $# -gt 0 ]; do
    case "$1" in
        --keep-builds)
            KEEP_BUILDS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "Использование: $0 <путь_к_jenkins_home> [опции]"
            echo ""
            echo "Опции:"
            echo "  --keep-builds     Сохранить историю сборок"
            echo "  --dry-run         Показать что будет удалено без удаления"
            echo "  --help            Показать эту справку"
            exit 0
            ;;
        *)
            log_error "Неизвестная опция: $1"
            exit 1
            ;;
    esac
done

# Проверка существования директории
if [ ! -d "$JENKINS_HOME" ]; then
    log_error "Директория не существует: $JENKINS_HOME"
    exit 1
fi

# Проверка что это действительно Jenkins home (по config.xml)
if [ ! -f "$JENKINS_HOME/config.xml" ]; then
    log_error "Файл config.xml не найден. Это может не быть Jenkins home директорией."
    exit 1
fi

log_info "Очистка Jenkins backup: $JENKINS_HOME"
if [ "$DRY_RUN" = true ]; then
    log_warn "Режим dry-run - файлы не будут удалены"
fi
if [ "$KEEP_BUILDS" = true ]; then
    log_warn "История сборок будет сохранена"
fi

echo ""

# ============================================
# 0. СОХРАНЕНИЕ СПИСКА ПЛАГИНОВ (перед удалением)
# ============================================
log_info "=== Сохранение списка плагинов ==="
PLUGINS_FILE="$JENKINS_HOME/plugins.txt"

if [ -d "$JENKINS_HOME/plugins" ]; then
    # Получаем список плагинов из .jpi/.hpi файлов
    plugin_list=$(find "$JENKINS_HOME/plugins" -maxdepth 1 \( -name "*.jpi" -o -name "*.hpi" \) -printf "%f\n" 2>/dev/null | sed 's/\.\(jpi\|hpi\)$//' | sort)
    
    if [ -n "$plugin_list" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY-RUN] Сохранить плагины в: $PLUGINS_FILE"
            echo "  Плагины найдены:"
            echo "$plugin_list" | while read -r plugin; do
                echo "    - $plugin"
            done
        else
            echo "$plugin_list" > "$PLUGINS_FILE"
            plugin_count=$(echo "$plugin_list" | wc -l)
            log_info "Сохранено $plugin_count плагинов в: $PLUGINS_FILE"
        fi
    else
        log_warn "Плагины не найдены"
    fi
else
    log_warn "Директория plugins не найдена"
fi

echo ""

# Функция удаления
remove_item() {
    local item="$1"
    local description="$2"
    
    if [ -e "$item" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [DRY-RUN] Удалить $description: $item"
        else
            log_info "Удаление $description: $item"
            rm -rf "$item"
        fi
    fi
}

# ============================================
# 1. ПЛАГИНЫ (можно переустановить в новом контейнере)
# ============================================
log_info "=== Очистка плагинов ==="
remove_item "$JENKINS_HOME/plugins" "директория с плагинами"

# ============================================
# 2. КЭШИ
# ============================================
log_info "=== Очистка кэшей ==="
remove_item "$JENKINS_HOME/caches" "кэш Git и других инструментов"
remove_item "$JENKINS_HOME/.cache" "скрытый кэш"

# ============================================
# 3. ВРЕМЕННЫЕ ФАЙЛЫ И ЛОГИ
# ============================================
log_info "=== Очистка временных файлов и логов ==="
remove_item "$JENKINS_HOME/logs" "логи задач"
remove_item "$JENKINS_HOME/.java" "кэш Java"
remove_item "$JENKINS_HOME/.groovy" "кэш Groovy"
remove_item "$JENKINS_HOME/war" "распакованный WAR (восстанавливается контейнером)"
remove_item "$JENKINS_HOME/updates" "загруженные обновления плагинов"

# ============================================
# 4. FINGERPRINTS (отпечатки артефактов)
# ============================================
log_info "=== Очистка fingerprints ==="
remove_item "$JENKINS_HOME/fingerprints" "отпечатки файлов"

# ============================================
# 5. ИСТОРИЯ СБОРОК (опционально)
# ============================================
if [ "$KEEP_BUILDS" = false ]; then
    log_info "=== Очистка истории сборок ==="
    if [ -d "$JENKINS_HOME/jobs" ]; then
        for job_dir in "$JENKINS_HOME/jobs"/*/; do
            if [ -d "$job_dir" ]; then
                builds_dir="${job_dir}builds"
                if [ -d "$builds_dir" ]; then
                    remove_item "$builds_dir" "история сборок в $(basename "$job_dir")"
                    # Пересоздаем пустую директорию builds
                    if [ "$DRY_RUN" = false ]; then
                        mkdir -p "$builds_dir"
                    fi
                fi
                # Также чистим workspace
                workspace_dir="${job_dir}workspace"
                remove_item "$workspace_dir" "workspace в $(basename "$job_dir")"
            fi
        done
    fi
else
    log_warn "Пропуск очистки истории сборок (--keep-builds указан)"
fi

# ============================================
# 6. NODES (конфигурация нод может быть специфична для старого контейнера)
# ============================================
log_info "=== Очистка конфигурации нод ==="
# Сохраняем master конфигурацию, чистим только кэши нод
if [ -d "$JENKINS_HOME/nodes" ]; then
    for node_dir in "$JENKINS_HOME/nodes"/*/; do
        if [ -d "$node_dir" ]; then
            # Удаляем workspace и кэши нод
            remove_item "${node_dir}workspace" "workspace ноды $(basename "$node_dir")"
            remove_item "${node_dir}.cache" "кэш ноды $(basename "$node_dir")"
        fi
    done
fi

# ============================================
# 7. ВРЕМЕННЫЕ ФАЙЛЫ В КОРНЕ JENKINS_HOME
# ============================================
log_info "=== Очистка временных файлов в корне ==="
remove_item "$JENKINS_HOME/copy_reference_file.log" "лог copy_reference"
remove_item "$JENKINS_HOME/queue.xml" "текущая очередь задач"
remove_item "$JENKINS_HOME/queue.xml.bak" "резервная копия очереди"

# ============================================
# ИТОГИ
# ============================================
echo ""
log_info "=== Очистка завершена ==="
echo ""
echo "Сохраненные файлы и директории:"
echo "  ✓ config.xml и *.xml конфигурации"
echo "  ✓ credentials.xml (учетные данные)"
echo "  ✓ secrets/ (ключи шифрования)"
echo "  ✓ users/ (пользователи)"
echo "  ✓ jobs/*/config.xml (конфигурации задач)"
echo "  ✓ .groovy/, .config/ (скрипты инициализации)"
echo "  ✓ plugins.txt (список плагинов)"
echo ""

# Вывод команды для установки плагинов
if [ -f "$PLUGINS_FILE" ] && [ "$DRY_RUN" = false ]; then
    echo "Для установки плагинов в новом контейнере выполните:"
    echo ""
    echo "  # Копирование plugins.txt в контейнер и установка:"
    echo "  docker cp $PLUGINS_FILE <контейнер>:/tmp/plugins.txt"
    echo "  docker exec <контейнер> bash -c '"
    echo "    jenkins-plugin-cli --plugin-file /tmp/plugins.txt --war /usr/share/jenkins/jenkins.war'"
    echo ""
    echo "  # Или через Jenkins CLI (альтернативный способ):"
    echo "  java -jar jenkins-cli.jar -s http://localhost:8080 install-plugin < $PLUGINS_FILE"
    echo ""
    echo "Список плагинов для установки ($(wc -l < "$PLUGINS_FILE") шт.):"
    cat "$PLUGINS_FILE" | while read -r plugin; do
        echo "  - $plugin"
    done
    echo ""
elif [ "$DRY_RUN" = true ] && [ -d "$JENKINS_HOME/plugins" ]; then
    echo "Для установки плагинов в новом контейнере используйте:"
    echo ""
    echo "  docker cp plugins.txt <контейнер>:/tmp/plugins.txt"
    echo "  docker exec <контейнер> jenkins-plugin-cli --plugin-file /tmp/plugins.txt"
    echo ""
fi

echo "Для восстановления в новом контейнере:"
echo "  1. Скопируйте очищенную директорию в новый контейнер"
echo "  2. Установите плагины командой выше"
echo "  3. Перезапустите Jenkins"
echo ""

if [ "$DRY_RUN" = true ]; then
    log_warn "Это был dry-run. Для фактического удаления уберите флаг --dry-run"
fi
