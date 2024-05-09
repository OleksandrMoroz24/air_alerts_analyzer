from air_alerts_analyzer import settings
from pyrogram import Client
from datetime import datetime, timedelta
import requests
from asgiref.sync import async_to_sync


def analyze_report_with_openai(analytics):
    openai_api_key = settings.OPENAI_KEY
    headers = {"Authorization": f"Bearer {openai_api_key}"}

    messages = [
        {
            "role": "system",
            "content": "Ви досвідчений аналітик даних, який спеціалізується на аналізі трендів "
                       "та виявленні закономірностей у певних регіонах. "
                       "Ваше завдання - проаналізувати зібрані дані про щотижневу частоту повітряних тривог"
                       " внаслідок агресії росії у певному регіоні України. Виявивши тенденцію,"
                       " вам необхідно заглибитися в дані, зосередившись на кількості тривог у кожен день тижня"
                       " та погодинно за весь часовий період. Потім на основі цього аналізу слід надати загальний"
                       " і стислий опис можливих тривог за вказаний час,"
                       " враховуючи як день тижня, так і годину доби."
                       " Наприклад, проаналізувавши дані про частоту тривог за кілька тижнів, ви можете виявити,"
                       " що більшість тривог трапляється в будні дні рано вранці, що вказує на потенційну закономірність."
                       " Ця інформація може мати вирішальне значення для розуміння і, можливо, прогнозування"
                       " повітряних тривог у певному регіоні. Розразуй вирогідність тривоги відповідно"
                       " заданого часу та регіону на основі статистичних даних"
                       " у результаті завжди надавай максимально стислу та гарно оформлену відповідь",
        },
        {"role": "user", "content": [{"type": "text", "text": analytics}]},
    ]
    data = {"model": "gpt-4-turbo", "messages": messages, "max_tokens": 2000}

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=data
    )
    if response.status_code == 200:
        response_data = response.json()
        return (
            response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return "Не вдалося проаналізувати звіт."


@async_to_sync
async def fetch_telegram_messages():
    api_id = settings.TG_API_ID
    api_hash = settings.TG_API_HASH
    phone_number = settings.TG_PHONE
    channel_username = "kpszsu"

    messages = []
    app = Client(
        "my_account", api_id=api_id, api_hash=api_hash, phone_number=phone_number
    )

    async with app:

        async for message in app.get_chat_history(
            channel_username, limit=10
        ):
            messages.append(
                {
                    "date": message.date,
                    "text": message.text,
                }
            )

    return messages


def check_active_alerts(region_id):
    # URL API
    url = f"https://api.ukrainealarm.com/api/v3/alerts/{region_id}"
    headers = {"Authorization": settings.ALERTS_API}
    try:
        # Відправка GET запиту до API

        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Перевірка на помилки HTTP
        data = response.json()  # Конвертація відповіді в JSON

        # Перевірка на наявність активних тривог
        has_active_alerts = any(
            "activeAlerts" in item and item["activeAlerts"] for item in data
        )

        return has_active_alerts
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False
