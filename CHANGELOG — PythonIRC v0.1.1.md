**CHANGELOG — PythonIRC v0.1**

---

**v0.1.1**

**1. Complete redesign of the project architecture**

The project was manually redesigned and refactored to align with a production-ready architecture.

Previously:

```
app/
  auth.py
  chat.py
  database.py
  main.py
client/
  cli.py
```

Now:

```
app/
  core/
    config.py
  db/
    database.py
  models/
    models.py
  routers/
    auth.py
    chat.py
  services/
    auth.py
    chat.py
  schemas/
    auth.py
  main.py
client/
  cli.py
```

**2. Interface Color Scheme**

A client color scheme has been added—green for UI elements and tooltips, red for errors and system messages.

**3. Unique RGB colors for usernames**

Each user receives a unique username color based on a hash of their username. The hash is truncated to 24 bits and divided into three 8-bit parts—each part becomes one of the RGB components (0–255). This ensures that the same username always produces the same color within a session. The color is generated on the client side at each launch—there is no server-side color storage, and colors are recalculated when the client is restarted.

**4. Fixed display of long messages**

Fixed a bug where long messages left artifacts in the terminal—the terminal width is now taken into account, and the appropriate number of lines is cleared.

**5. GhostChat logo**

Added an ASCII logo when the client starts.


**CHANGELOG — PythonIRCv0.1.1**

---

**v0.1.1**

**1. Полная переработка архитектуры проекта**

Вручную была произведена полная переработка и дробление проекта под продакшен архитектуру.

Было:

```
app/
  auth.py
  chat.py
  database.py
  main.py
client/
  cli.py
```

Стало:

```
app/
  core/
    config.py
  db/
    database.py
  models/
    models.py
  routers/
    auth.py
    chat.py
  services/
    auth.py
    chat.py
  schemas/
    auth.py
  main.py
client/
  cli.py
```

**2. Цветовая схема интерфейса**

Добавлена цветовая схема клиента — зелёный для UI элементов и подсказок, красный для ошибок и системных сообщений.

**3. Уникальные RGB цвета ников**

Каждый пользователь получает уникальный цвет ника на основе хеша своего username. Хеш обрезается до 24 бит и делится на три части по 8 бит — каждая часть становится одним из компонентов RGB (0-255). Это гарантирует что один и тот же username всегда даёт один и тот же цвет в рамках сессии. Цвет генерируется на стороне клиента при каждом запуске — серверного хранения цветов нет, при перезапуске клиента цвета пересчитываются заново.

**4. Исправление отображения длинных сообщений**

Исправлен баг когда длинные сообщения оставляли артефакты в терминале — теперь учитывается ширина терминала и очищается нужное количество строк.

**5. Логотип GhostChat**

Добавлен ASCII логотип при запуске клиента.
