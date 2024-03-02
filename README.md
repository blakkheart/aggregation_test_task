
# 🤖 Telegram Bot Aggregation salary 🤖

## Описание

Проект выполнен в качестве тестового задания для компании RLT (ООО Надежные Лояльные Технологии).

Алгоритм агрегации статистических данных о зарплатах сотрудников компании по временным промежуткам.

Алгоритм принимает на вход:
1.  Дату и время старта агрегации в ISO формате.
2.  Дату и время окончания агрегации в ISO формате.
3.  Тип агрегации. Типы агрегации могут быть следующие: hour, day, month. То есть группировка всех данных за час, день, месяц.

## Стэк технологий

- [aiogram](https://docs.aiogram.dev/en/latest/) — фреймворк для телеграм бота.
- [MongoDB](https://www.mongodb.com/) — база данных приложения.
- [asyncio](https://docs.python.org/3/library/asyncio.html) + [Motor](https://motor.readthedocs.io/en/stable/) — для асинхронной работы кода.
- [Docker](https://www.docker.com/) — контейнеризация приложения.

## Установка

1. Склонируйте репозиторий:
```bash
git clone https://github.com/blakkheart/aggregation_test_task.git
```
2. Перейдите в директорию проекта:
```bash
cd aggregation_test_task
```
3. Установите и активируйте виртуальное окружение:
   - Windows
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
   - Linux/macOS
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Обновите [pip](https://pip.pypa.io/en/stable/):
   - Windows
   ```bash
   (venv) python -m pip install --upgrade pip
   ```
   - Linux/macOS
   ```bash
   (venv) python3 -m pip install --upgrade pip
   ```
5. Установите зависимости из файла requirements.txt:
   ```bash
   (venv) pip install -r backend/requirements.txt
   ```
Создайте и заполните файл `.env` по примеру с файлом `.env.example`, который находится в корневой директории.



## Использование  

1. Введите команду для запуска докер-контейнера:
	```bash
	docker compose up
	```
Запустится БД, загрузятся данные из дампа и бот начнет работу.
Вы можете посылать данные боту в формате :
```json
{
"dt_from":"2022-09-01T00:00:00",
"dt_upto":"2022-12-31T23:59:00",
"group_type":"month"
}
```

И получать агрегированные данные за указанный промежуток и с указанной группировкой в формате: 
```json
{
"dataset": [5906586, 5515874, 5889803, 6092634],
"labels": ["2022-09-01T00:00:00", "2022-10-01T00:00:00", "2022-11-01T00:00:00", "2022-12-01T00:00:00"]
}
```

### Дополнительно
При запуске контейнера БД сама наполняет себя данными из дампа, сохраненного в директории `sampleDB`.
