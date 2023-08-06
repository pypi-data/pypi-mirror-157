from sbcommons.logging import lambda_logger
import requests

logger = lambda_logger.get_logger(__name__)


def send_message(webhook_url: str, title: str, msg: str) -> bool:
    data = {
        "Text": msg,
        "TextFormat": "markdown",
        "Title": title
    }

    try:
        response = requests.post(webhook_url, json=data)
        if not response.status_code == 200:
            logger.info(
                f'Tried to post {msg} on teams webhook failed, status code: {response.status_code}'
            )
            return False
    except BaseException as e:
        logger.error(f'Exception when posting to teams, exception args: {e.args}')
        return False

    return True
