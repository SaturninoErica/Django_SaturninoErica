# Horse Tour

Изолированный Django REST API для стартапа с турами: конными, пешими,
мотоциклетными и другими. Основной проект репозитория не изменяется.

## Установка и запуск

```powershell
cd horse_tour
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Если Windows Application Control блокирует создание `.venv` или запуск
`pip.exe`, откройте новое окно PowerShell и используйте установленный Python
без виртуального окружения:

```powershell
cd horse_tour
python -m pip install --user -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Форма `python -m pip` запускает pip через Python и не вызывает `pip.exe`
напрямую. Если политика организации блокирует установку и таким способом,
обратитесь к администратору за разрешённым Python-окружением.

Для разработки документация Swagger UI доступна по адресу
`http://127.0.0.1:8000/api/docs/`; схема OpenAPI — `/api/schema/`.
Административная панель — `/admin/`.

## Связи и бизнес-правила

- `TouristProfile.user` — один к одному с Django-пользователем.
- `TourCategory.tours` и `Tour.categories` — многие ко многим.
- `Tour` связан с `Booking` и `Review` один ко многим.
- Один пользователь не может создать более одного бронирования на один
  `scheduled_at`, даже если это разные туры. Проверка выполняется API и
  ограничением уникальности в базе данных.
- Оставлять отзывы можно только о турах с завершенным бронированием.
  Один пользователь может оставить несколько отзывов.
- Оценка отзыва ограничена диапазоном от 1 до 5.

## API

- `POST /api/users/` — регистрация (username, email, password).
- `/api/profiles/`, `/api/categories/`, `/api/tours/`, `/api/bookings/`,
  `/api/reviews/` — стандартные операции списка, создания, просмотра,
  изменения и удаления.
- Для тура передавайте массив `categories` с ID существующих категорий.
- Для бронирования передавайте `user`, `tour`, `scheduled_at` и при
  необходимости `status` (`pending`, `confirmed`, `completed`, `cancelled`).
- Отзыв содержит `user`, `tour`, `rating` и `comment`.

API открыт для учебной/тестовой разработки и не включает авторизацию.
Перед публичным развертыванием настройте аутентификацию и разрешения.

## Тестирование

```powershell
python manage.py test
```

Набор проверяет POST/GET/PUT/PATCH/DELETE, регистрацию пользователя,
сохранение связей, запрет повторного бронирования на то же время и
создание нескольких отзывов только для завершенного тура.
