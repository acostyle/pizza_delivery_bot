import logging
import redis
from environs import Env

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler


from app.bots.cart import generate_cart
from app.bots.keyboard import create_menu_markup
from app.bots.geocoder import fetch_coordinates
from app.api.authentication import get_access_token
from app.api.customer import create_customer
from app.api.product import get_product_by_id, get_product_photo_by_id, get_all_products
from app.api.cart import delete_product_from_cart, get_or_create_cart, add_product_to_cart


env = Env()
env.read_env()

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = env.str('TELEGRAM_BOT_TOKEN')
REDIS_PASSWORD = env.str('REDIS_PASSWORD')
REDIS_HOST = env.str('REDIS_HOST')
REDIS_PORT = env.int('REDIS_PORT')
YA_API_KEY = env.str('YA_API_KEY')

_database = None


def start(bot, update):
    logger.info('User started bot')
    access_token = get_access_token(_database)
    get_or_create_cart(access_token, update.message.chat_id)
    reply_markup = create_menu_markup(access_token)
    update.message.reply_text(
        reply_markup=reply_markup,
        text='Welcome! Please, choose a pizza:',
    )
    return 'HANDLE_MENU'


def handle_menu(bot, update):
    access_token = get_access_token(_database)
    query = update.callback_query
    
    if query.data == 'cart':
        generate_cart(_database, bot, update)
        return 'HANDLE_CART'
    elif 'page' in query.data:
        page = query.data.split(',')[1]
        reply_markup = create_menu_markup(access_token, int(page))

        bot.edit_message_text(
            text='Welcome! Please, choose a pizza:',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            reply_markup=reply_markup,
        )
    elif query.data == 'menu':
        reply_markup = create_menu_markup(access_token)
        bot.send_message(
            reply_markup=reply_markup,
            chat_id=query.message.chat_id,
            text='Welcome! Please, choose a pizza:',
        )
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )

        return 'HANDLE_MENU'

    keyboard = [
        [
            InlineKeyboardButton(
                'Add to cart',
                callback_data='add, {0}'.format(query.data)
            ),
        ],
        [InlineKeyboardButton('Cart 🛒', callback_data='cart')],
        [InlineKeyboardButton('Menu', callback_data='menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query_data = query.data.split(', ')
    if len(query_data) > 1:
        product_id = query_data[1]
    else:
        product_id = query.data
    product = get_product_by_id(access_token, product_id)
    product_photo_id = product['relationships']['main_image']['data']['id']
    product_photo = get_product_photo_by_id(access_token, product_photo_id)
    product_name = product['name']
    product_description = product['description']
    product_price = product['price'][0]['amount']

    bot.send_photo(
        chat_id=query.message.chat_id,
        photo=product_photo,
        reply_markup=reply_markup,
        caption='{0}\n\n{1} руб.\n{2}'.format(
            product_name,
            product_price,
            product_description,
        ),
    )

    bot.delete_message(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
    )

    return 'HANDLE_DESCRIPTION'


def handle_description(bot, update):
    access_token = get_access_token(_database)
    query = update.callback_query

    if query.data == 'menu':
        reply_markup = create_menu_markup(access_token)
        bot.send_message(
            reply_markup=reply_markup,
            chat_id=query.message.chat_id,
            text='Welcome! Please, choose a pizza:',
        )
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )

        return 'HANDLE_MENU'
    elif query.data == 'cart':
        generate_cart(_database, bot, update)
        return 'HANDLE_CART'

    product_id = query.data.split(', ')[1]

    add_product_to_cart(
        access_token,
        query.message.chat_id,
        product_id,
        1,
    )

    return 'HANDLE_MENU'


def handle_cart(bot, update):
    access_token = get_access_token(_database)
    query = update.callback_query

    if query.data == 'menu':
        reply_markup = create_menu_markup(access_token)
        bot.send_message(
            reply_markup=reply_markup,
            chat_id=query.message.chat_id,
            text='Welcome! Please, choose a pizza:',
        )
        bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )

        return 'HANDLE_MENU'

    elif query.data == 'pay':
        bot.edit_message_text(
            text='Please, send your location',
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )

        return 'HANDLE_WAITING'
    
    delete_product_from_cart(
        access_token,
        query.message.chat_id,
        query.data,
    )
    generate_cart(_database, bot, update)

    return 'HANDLE_CART'


def handle_waiting(bot, update):
    if update.message.text:
        try:
            current_position = fetch_coordinates(
                YA_API_KEY,
                update.message.text,
            )
            print(f'Current pos: {current_position}')
        except ValueError:
            current_position = None
            bot.send_message(
                text='I can\'t recognize the address',
                chat_id=update.message.chat_id,
            )
    else:
        message = None
        if update.edited_message:
            message = update.edited_message
        else:
            message = update.message
        
        current_position = (
            message.location.longitude,
            message.location.latitude,
        )
    
    update.message.reply_text(
        text=current_position,
    )



def handle_users_reply(bot, update):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = _database.get(chat_id)

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'HANDLE_WAITING': handle_waiting,
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update)
        _database.set(chat_id, next_state)
    except Exception as err:
        logger.error(err)


def get_database_connection():
    global _database
    if _database is None:
        _database = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
    return _database


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
    )
    get_database_connection()
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_menu))
    updater.start_polling()


if __name__ == '__main__':
    main()