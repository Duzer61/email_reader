# Проект "email_reader". Написан в качестве тестового задания.
### [Описание задания](https://docs.google.com/document/d/1pNA2sj0PPNYH7CzSxJCop8pNhbq8BoSkes2HfLidt58/edit?usp=sharing)
__________________________
### Краткая инструкция по запуску в dev режиме:
Для запуска проекта на локальной машине должны работать PostgreSQL и Redis.
- скачать проект на локальную машину `git clone git@github.com:Duzer61/email_reader.git`
- перейти в директорию с проектом `/email_reader/`
- создать виртуальное окружение командой `python3 -m venv venv` (команда для Linux). Для Windows `python -m venv venv`. В проекте применялся python3.12
- активировать виртуальное окружение  `source venv/bin/activate` (для Windows `source venv/Scripts/activate`)
- в зависимости от операционной системы переименовать файл `requirements_linux.txt` или `requirements_windows.txt` в `requirements.txt` 
- установить зависимости. При активированном виртуальном окружении выполнить команду: `pip install -r requirements.txt`
- переименовать файл `.env.example` в `.env` и внести при необходимости свои данные
- перейти в директорию `/email_reader/` в которой находится файл `manage.py`
- сделать миграции: `python3 manage.py makemigrations` и применить их `python3 manage.py migrate`
- создать суперпользователя `python3 manage.py createsuperuser`
- запустить проект в dev режиме `python3 manage.py runserver`
_____________

### Работа с проектом
- Предусмотрена работа с почтовыми сервисами `yandex.ru, gmail.com, mail.ru` по протоколу IMAP
- Сначала необходимо через админку внести данные почтовых аккаунтов (email и пароль приложения). **Обратите внимание:** нужен именно пароль приложения, а не стандартный пароль от аккаунта. О паролях приложения для Яндекса [справку можно получить тут](https://yandex.ru/support/id/authorization/app-passwords.html)
- админка доступна по адресу http://127.0.0.1:8000/admin/  В разделе `Accounts` можно внести email и пароль приложения.
- После того как аккаунты добавлены, можно пользоваться приложением. Основная страница доступна по адресу: http://127.0.0.1:8000/reader/
- Вверху страницы в раскрывающемся списке можно выбрать аккаунт из ранее внесенных и нажать на кнопку `Начать загрузку`
- Если в эл.письме есть вложения, то они сохраняются с уникальными именами в директорию `/email_reader/attachments/`
____________
## Технологии в проекте:
 - Python 3.12
 - Django 4.2.11
 - Channels 4.0.0
 - Channels-redis 4.1.0
 - Daphne 4.1.0
 - PostgreSQL
 - Redis
 - Django-cryptography 1.1
_______
  ##  Автор
Данил Кочетов - [GitHub](https://github.com/Duzer61)