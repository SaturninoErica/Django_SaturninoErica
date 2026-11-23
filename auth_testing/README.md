# Учетные записи с проверкой CAPTCHA

Самостоятельный Django-проект с регистрацией, входом по имени пользователя и
паролю, личным кабинетом и одноразовой математической CAPTCHA на странице
входа.

## Установка и запуск

```powershell
cd auth_testing
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Откройте `http://127.0.0.1:8000/register/` для регистрации. Личный кабинет
доступен по адресу `/account/`; войти можно по адресу `/login/`.

## Тесты и отчет Word

```powershell
python manage.py test
```

Команда Django запускает тесты регистрации, входа, CAPTCHA и личного кабинета,
а затем сохраняет сводку и результаты каждого теста в
`test-reports/test-results.docx`. Файл можно скачать из приложения по адресу
`/test-report/` после входа под учетной записью сотрудника Django (`is_staff`).
Доступ к отчету ограничен сотрудниками, так как он может содержать трассировки
ошибок.
