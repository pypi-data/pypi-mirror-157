import requests

class BotGram():
    def __init__(self, token):
        global bot_token
        bot_token = token

    def message(self, chat_id, text):
        r = requests.get(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={str(chat_id)}&text={str(text)}')
        return r.json()

    def photo(self, chat_id, photo_url, caption=''):
        if caption == '':
            r = requests.get(f'https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id={str(chat_id)}&photo={str(photo_url)}')
        else:
            r = requests.get(
                f'https://api.telegram.org/bot{bot_token}/sendPhoto?chat_id={str(chat_id)}&photo={str(photo_url)}&caption={str(caption)}')
        return r.json()

    def sticker(self, chat_id, sticker):
        r = requests.get(f'https://api.telegram.org/bot{bot_token}/sendSticker?chat_id={str(chat_id)}&sticker={str(sticker)}')
        return r.json()