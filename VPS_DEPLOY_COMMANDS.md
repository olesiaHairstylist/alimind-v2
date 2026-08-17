# VPS_DEPLOY_COMMANDS.md

Стандартные команды для обновления AliMind V2 на VPS.

---

## 1. Подключение

```bash
ssh root@SERVER_IP
```

---

## 2. Переход в проект

```bash
cd /home/botuser/bot
```

---

## 3. Проверить текущую версию

```bash
git log --oneline -1
```

Проверить изменения:

```bash
git status
```

---

## 4. Получить новый код

```bash
git pull origin main
```

---

## 5. Перезапустить сервис

```bash
sudo systemctl restart alimind-bot
```

---

## 6. Проверить статус

```bash
systemctl status alimind-bot --no-pager
```

Ожидается:

```
Active: active (running)
```

---

## 7. Просмотр последних логов

```bash
journalctl -u alimind-bot -n 50 --no-pager
```

---

## 8. Онлайн-логи

```bash
journalctl -u alimind-bot -f
```

Выход:

```
Ctrl + C
```

---

## 9. Запуск отдельного модуля

Активировать окружение:

```bash
cd /home/botuser/bot
source .venv/bin/activate
```

Запуск:

```bash
python -m app.modules.city_events.sources.electricity_source
```

или напрямую:

```bash
/home/botuser/bot/.venv/bin/python \
    -m app.modules.city_events.sources.electricity_source
```

---

## 10. Проверить Python

```bash
ls -l /home/botuser/bot/.venv/bin/python
```

---

## 11. Основной путь проекта

```
/home/botuser/bot
```

Не использовать старые пути вида:

```
/root/ALIMIND_V2
```

---

## Последовательность деплоя

```text
git push
        ↓
ssh VPS
        ↓
cd /home/botuser/bot
        ↓
git pull
        ↓
sudo systemctl restart alimind-bot
        ↓
systemctl status alimind-bot
        ↓
journalctl -u alimind-bot -f
```