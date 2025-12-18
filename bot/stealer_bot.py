from telebot import TeleBot


class FileStealer:

    def __init__(self, token: str, chat_id: str):
        self.chat_id = chat_id
        self.bot = TeleBot(token)

    def get_messages(self):
        print('Пытаюсь получить сообщения')
        updates = self.bot.get_updates()
        for update in updates:
            if update.message:
                print(f'Сообщение: {update.message.text}')
