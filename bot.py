import os
import json
import logging
from telebot import TeleBot, types
from flask import Flask, render_template_string
from threading import Thread

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============ НАСТРОЙКИ ============
TOKEN = os.environ.get('BOT_TOKEN', 'ТВОЙ_ТОКЕН')  # Берем из настроек Render
CONFIG_FILE = "/data/chat_config.json"

# ============ СОЗДАЕМ БОТА ============
bot = TeleBot(TOKEN)

# ============ ВЕБ-СЕРВЕР ============
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 Telegram Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                max-width: 600px;
                margin: 0 auto;
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
            }
            .status {
                font-size: 1.5em;
                color: #4CAF50;
                font-weight: bold;
                margin: 20px 0;
            }
            .info {
                margin-top: 20px;
                font-size: 1.1em;
                line-height: 1.6;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Telegram Bot</h1>
            <div class="status">✅ БОТ АКТИВЕН И РАБОТАЕТ</div>
            <div class="info">
                <p>Хостинг: <strong>Render.com</strong></p>
                <p>Статус: <strong>24/7 онлайн</strong></p>
                <p>Бот принимает сообщения в Telegram</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return "OK", 200

# Запускаем Flask в отдельном потоке
def run_flask():
    app.run(host='0.0.0.0', port=10000)

# ============ РАБОТА С ДАННЫМИ ============
def save_chat_id(chat_id):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'chat_id': chat_id}, f)
        logging.info(f"Сохранен chat_id: {chat_id}")
        return True
    except Exception as e:
        logging.error(f"Ошибка сохранения: {e}")
        return False

def load_chat_id():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get('chat_id')
    except Exception as e:
        logging.error(f"Ошибка загрузки: {e}")
    return None

# ============ КОМАНДЫ БОТА ============
@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    """Обработчик команд /start и /help"""
    help_text = """
🤖 <b>Бот-предложка 24/7</b>

📍 <b>Хостинг:</b> Render.com
⚡ <b>Статус:</b> Активен

📋 <b>Команды:</b>
/set [ID] - Настроить чат для предложок
/chat - Проверить текущий чат
/status - Статус бота

🔧 <b>Как настроить:</b>
1. Добавь бота в группу как администратора
2. Узнай ID группы через @username_to_id_bot
3. Напиши: <code>/set -1001234567890</code>

📤 <b>Как использовать:</b>
Просто отправь любое сообщение боту в ЛС!
Оно будет переслано в настроенную группу.
"""
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

@bot.message_handler(commands=['set'])
def set_command(message):
    """Настройка чата"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(
                message.chat.id,
                "❌ <b>Укажи ID чата!</b>\n"
                "Пример: <code>/set -1001234567890</code>\n\n"
                "Как получить ID:\n"
                "1. Добавь @username_to_id_bot в группу\n"
                "2. Отправь команду /id\n"
                "3. Скопируй ID группы (начинается с -100)",
                parse_mode='HTML'
            )
            return
        
        chat_id = int(parts[1])
        if save_chat_id(chat_id):
            bot.send_message(
                message.chat.id,
                f"✅ <b>Чат успешно настроен!</b>\n"
                f"ID: <code>{chat_id}</code>\n\n"
                f"Теперь все сообщения будут приходить в этот чат.",
                parse_mode='HTML'
            )
        else:
            bot.send_message(message.chat.id, "❌ Ошибка сохранения!")
            
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ <b>ID должен быть числом!</b>\n"
            "Пример: <code>/set -1001234567890</code>",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {str(e)}")

@bot.message_handler(commands=['chat'])
def chat_command(message):
    """Проверка текущего чата"""
    chat_id = load_chat_id()
    if chat_id:
        bot.send_message(
            message.chat.id,
            f"📌 <b>Текущий чат:</b>\n"
            f"ID: <code>{chat_id}</code>",
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ <b>Чат не настроен!</b>\n"
            "Используй команду: <code>/set [ID_чата]</code>",
            parse_mode='HTML'
        )

@bot.message_handler(commands=['status'])
def status_command(message):
    """Статус бота"""
    try:
        me = bot.get_me()
        chat_id = load_chat_id()
        
        status_text = f"""
🤖 <b>Статус бота</b>

✅ <b>Работает на Render.com</b>
👤 <b>Бот:</b> @{me.username}
🆔 <b>ID бота:</b> {me.id}
🌐 <b>Веб-страница:</b> Работает
"""
        
        if chat_id:
            status_text += f"\n📌 <b>Чат настроен:</b> {chat_id}"
        else:
            status_text += "\n📌 <b>Чат не настроен</b>"
            
        bot.send_message(message.chat.id, status_text, parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка получения статуса: {e}")

# ============ ОБРАБОТКА СООБЩЕНИЙ ============
pending_messages = {}

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker'])
def handle_message(message):
    """Обработка всех сообщений от пользователей"""
    
    # Игнорируем команды и сообщения не из ЛС
    if message.chat.type != 'private':
        return
    
    if message.text and message.text.startswith('/'):
        return
    
    # Проверяем настроен ли чат
    target_chat_id = load_chat_id()
    if not target_chat_id:
        bot.send_message(
            message.chat.id,
            "❌ <b>Чат не настроен!</b>\n"
            "Сначала настрой чат командой:\n"
            "<code>/set [ID_чата]</code>\n\n"
            "ID можно получить через @username_to_id_bot",
            parse_mode='HTML'
        )
        return
    
    # Сохраняем сообщение
    pending_messages[message.message_id] = {
        'message': message,
        'user_id': message.from_user.id
    }
    
    # Создаем клавиатуру с кнопками
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_send = types.InlineKeyboardButton('✅ Отправить', callback_data=f'send_{message.message_id}')
    btn_cancel = types.InlineKeyboardButton('❌ Отменить', callback_data=f'cancel_{message.message_id}')
    markup.add(btn_send, btn_cancel)
    
    # Формируем текст предпросмотра
    preview = "📤 <b>Подтвердите отправку:</b>\n\n"
    
    if message.text:
        text_preview = message.text[:150]
        if len(message.text) > 150:
            text_preview += "..."
        preview += f"📝 {text_preview}"
    elif message.caption:
        caption_preview = message.caption[:150]
        if len(message.caption) > 150:
            caption_preview += "..."
        preview += f"📷 {caption_preview}"
    elif message.photo:
        preview += "📷 Фото"
    elif message.video:
        preview += "🎥 Видео"
    elif message.document:
        preview += "📄 Документ"
    elif message.audio:
        preview += "🎵 Аудио"
    elif message.voice:
        preview += "🎤 Голосовое сообщение"
    elif message.sticker:
        preview += "😀 Стикер"
    else:
        preview += "📎 Медиа-файл"
    
    preview += f"\n\n➡️ <b>Будет отправлено в чат:</b> {target_chat_id}"
    
    bot.send_message(message.chat.id, preview, parse_mode='HTML', reply_markup=markup)

# ============ ОБРАБОТКА КНОПОК ============
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработка нажатий кнопок"""
    
    # Убираем кнопки
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    except:
        pass
    
    # Разбираем callback_data
    data = call.data
    if '_' in data:
        action, msg_id_str = data.split('_', 1)
        try:
            msg_id = int(msg_id_str)
        except:
            msg_id = None
    else:
        action = data
        msg_id = None
    
    # Обработка отмены
    if action == 'cancel':
        bot.edit_message_text(
            "❌ <b>Отправка отменена</b>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML'
        )
        if msg_id in pending_messages:
            del pending_messages[msg_id]
        bot.answer_callback_query(call.id, "Отменено")
        return
    
    # Обработка отправки
    if action == 'send' and msg_id in pending_messages:
        bot.edit_message_text(
            "🔄 <b>Отправляю...</b>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode='HTML'
        )
        
        try:
            msg_data = pending_messages[msg_id]
            user_message = msg_data['message']
            target_chat_id = load_chat_id()
            
            # Формируем информацию об авторе
            user = user_message.from_user
            sender_info = user.first_name or ""
            if user.last_name:
                sender_info += f" {user.last_name}"
            if user.username:
                sender_info += f" (@{user.username})"
            
            caption = f"📨 <b>От:</b> {sender_info}\n\n"
            
            # Отправляем в зависимости от типа контента
            if user_message.text:
                bot.send_message(
                    target_chat_id,
                    f"{caption}{user_message.text}",
                    parse_mode='HTML'
                )
            elif user_message.photo:
                bot.send_photo(
                    target_chat_id,
                    user_message.photo[-1].file_id,
                    caption=caption + (user_message.caption or ""),
                    parse_mode='HTML'
                )
            elif user_message.video:
                bot.send_video(
                    target_chat_id,
                    user_message.video.file_id,
                    caption=caption + (user_message.caption or ""),
                    parse_mode='HTML'
                )
            elif user_message.document:
                bot.send_document(
                    target_chat_id,
                    user_message.document.file_id,
                    caption=caption + (user_message.caption or ""),
                    parse_mode='HTML'
                )
            elif user_message.audio:
                bot.send_audio(
                    target_chat_id,
                    user_message.audio.file_id,
                    caption=caption + (user_message.caption or ""),
                    parse_mode='HTML'
                )
            elif user_message.voice:
                bot.send_voice(
                    target_chat_id,
                    user_message.voice.file_id,
                    caption=caption,
                    parse_mode='HTML'
                )
            elif user_message.sticker:
                bot.send_sticker(target_chat_id, user_message.sticker.file_id)
            else:
                bot.send_message(
                    target_chat_id,
                    f"{caption}[Тип: {user_message.content_type}]",
                    parse_mode='HTML'
                )
            
            bot.edit_message_text(
                "✅ <b>Сообщение отправлено!</b>",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id, "Успешно отправлено!")
            
            # Удаляем из ожидания
            if msg_id in pending_messages:
                del pending_messages[msg_id]
            
        except Exception as e:
            error_msg = f"❌ <b>Ошибка отправки:</b>\n{str(e)[:100]}"
            if "bot was kicked" in str(e).lower():
                error_msg += "\n\n⚠️ <b>Бота удалили из чата!</b>"
            elif "not enough rights" in str(e).lower():
                error_msg += "\n\n⚠️ <b>У бота нет прав на отправку!</b>"
            
            bot.edit_message_text(
                error_msg,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode='HTML'
            )
            bot.answer_callback_query(call.id, "Ошибка!")
            logging.error(f"Ошибка отправки: {e}")
    
    else:
        bot.answer_callback_query(call.id, "Сообщение устарело")

# ============ ЗАПУСК ============
if __name__ == '__main__':
    # Запускаем веб-сервер в отдельном потоке
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print("=" * 50)
    print("🤖 Telegram Bot Starting on Render.com")
    print("=" * 50)
    
    # Создаем папку для данных если её нет
    os.makedirs('/data', exist_ok=True)
    
    # Проверяем токен
    if TOKEN == 'ТВОЙ_ТОКЕН':
        print("❌ ОШИБКА: Не забудь заменить токен в настройках Render!")
        print("Добавь переменную окружения BOT_TOKEN в Render Dashboard")
        exit(1)
    
    print("✅ Все проверки пройдены")
    print("🌐 Веб-сервер запущен на порту 10000")
    print("🤖 Запускаю Telegram бота...")
    print("=" * 50)
    
    # Бесконечный цикл бота
    try:
        bot.infinity_polling()
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        print(f"🔁 Перезапуск через 10 секунд...")
        import time
        time.sleep(10)
