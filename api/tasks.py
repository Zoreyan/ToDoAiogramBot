from celery import shared_task
import requests
import logging
from urllib.parse import quote
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_telegram_notification(self, telegram_id: int, text: str):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '7824168828:AAFLkEqZYP2OuJdNbWonnTuBErDra6xhip4')
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    
    payload = {
        'chat_id': telegram_id,
        'text': text,
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info(f"Уведомление отправлено. Chat ID: {telegram_id}. Ответ: {response.json()}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке уведомления: {str(e)}")
        try:
            self.retry(countdown=60 * 5)
        except self.MaxRetriesExceededError:
            logger.error(f"Не удалось отправить уведомление после 3 попыток. Chat ID: {telegram_id}")
        return False