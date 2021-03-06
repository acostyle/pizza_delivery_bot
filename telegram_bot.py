import json
from textwrap import dedent

import logging
import redis
from environs import Env

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, PreCheckoutQueryHandler

from app.bots.cart import generate_cart
from app.bots.keyboard import create_menu_markup, create_delivery_menu
from app.bots.geocoder import fetch_coordinates, get_closest_entry
from app.bots.payment import start_without_shipping, precheckout_callback, successful_payment_callback
from app.api.authentication import get_access_token
from app.api.customer import create_customer_address
from app.api.flow import get_entries, get_entry
from app.api.product import get_product_by_id, get_product_photo_by_id
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


def start(bot, update, job_queue):
    logger.info('User started bot')
    access_token = get_access_token(_database)
    get_or_create_cart(access_token, update.message.chat_id)
    reply_markup = create_menu_markup(access_token)
    update.message.reply_text(
        reply_markup=reply_markup,
        text='Welcome! Please, choose a pizza:',
    )
    return 'HANDLE_MENU'


def handle_menu(bot, update, job_queue):
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
        [InlineKeyboardButton('Cart ????', callback_data='cart')],
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
        caption='{0}\n\n{1} ??????.\n{2}'.format(
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


def handle_description(bot, update, job_queue):
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


def handle_cart(bot, update, job_queue):
    access_token = get_access_token(_database)
    query = update.callback_query
    payment, price = query.data.split(', ')
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

    elif payment == 'payment':
        start_without_shipping(bot, update, int(price))

        return 'HANDLE_WAITING'
    
    delete_product_from_cart(
        access_token,
        query.message.chat_id,
        query.data,
    )
    generate_cart(_database, bot, update)

    return 'HANDLE_CART'


def handle_waiting(bot, update, job_queue):
    access_token = get_access_token(_database)

    if location := update.message.location:
        current_position = (location.latitude, location.longitude)
    elif not (current_position := fetch_coordinates(
        YA_API_KEY,
        update.message.text,
    )):
            bot.send_message(
                text='I can\'t recognize the address',
                chat_id=update.message.chat_id,
            )

            return 'HANDLE_WAITING'

    flow_slug = 'pizzeria'

    create_customer_address(access_token, current_position, str(update.message.chat_id))

    flow_pizzerias = get_entries(access_token, flow_slug)
    closest_pizzeria = get_closest_entry(current_position, flow_pizzerias)
    pizzeria = get_entry(access_token, flow_slug, closest_pizzeria['id'])

    delivery_man_id = pizzeria['delivery_man_id']
    distance_between_pizzeria_and_customer = round(
        closest_pizzeria['distance'],
        1,
    )

    if closest_pizzeria['distance'] < 0.5:
        reply = dedent('''\n
        ???????????????????? ???????? ????????????????, ?????????? {0} ????. ???? ??????.
        ???? ?????????? ???? ?????????????????? ??????????????????, ???????? ???????????? ?????????????? ???????? :)

        ?????? ??????????: {1}
        '''.format(
            distance_between_pizzeria_and_customer,
            pizzeria['address'],
        )
    )
        reply_markup = create_delivery_menu(delivery_man_id, current_position)

    elif closest_pizzeria['distance'] < 5:
        reply = dedent('''\n
        ?????????????????? ???????????????? ??? {0}.

        ???? ?????? ?????????? ?????????????????? ???? ????????????????????. ???????????????? ??? 100 ????????????.
        ???????????????? ?????? ???????????????????
        '''.format(pizzeria['address'])
    )
        reply_markup = create_delivery_menu(delivery_man_id, current_position)
    
    elif closest_pizzeria['distance'] < 20:
        reply = dedent('''\n
        ?????????????????? ???????????????? ??? {0}.

        ???????????????? ?????????? 300 ????????????.
        ?????????????????? ???????????????? ?????? ???????? ?????????????????
        '''.format(pizzeria['address'])
    )
        reply_markup = create_delivery_menu(delivery_man_id, current_position)
    
    else:
        reply = dedent('''\n
        ?????????????????? ???????????????? ?? {0} ????. ???? ??????.
        ???????? ?????????????? ???? ?????????? ?????????????????? ?????????? ?????? ???????????? :??
        '''.format(distance_between_pizzeria_and_customer)
    )
        keyboard = [InlineKeyboardButton('Menu', callback_data='menu')]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(
            text=reply,
            chat_id=update.message.chat_id,
        )

        return 'HANDLE_MENU'
    
    if reply_markup:
        bot.send_message(
            text=reply,
            chat_id=update.message.chat_id,
            reply_markup=reply_markup,
        )
    
        return 'HANDLE_DELIVERY'


def handle_delivery(bot, update, job_queue):
    query = update.callback_query
    if query.data == 'pickup':
        bot.send_message(
            text='?????????????? ?????? ?????????? ????',
            chat_id=update.message.chat.id,
        )
    else:
        telegram_id, (lon, lat) = json.loads(query.data)
        reply = '?????????? ?????? ?????????????? {0} ?????????????? ????????????????'.format(
            telegram_id,
        )
        bot.send_message(
            text=reply,
            chat_id=telegram_id,
        )
        bot.send_location(
            chat_id=telegram_id,
            longitude=lon,
            latitude=lat,
        )

        job_queue.run_once(late_delivery_pizza, 60*60, context=query.message.chat.id)


def late_delivery_pizza(bot, job_queue):
    bot.send_message(
        chat_id=job_queue.context,
        text='?????????????????? ????????????????, ?????? ?????????? ?????????????????? ?????? ?????????????????? :)',
    )


def handle_users_reply(bot, update, job_queue):
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
        'HANDLE_DELIVERY': handle_delivery,
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(bot, update, job_queue)
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
    dispatcher.add_handler(CallbackQueryHandler(
        handle_users_reply,
        pass_job_queue=True,
    ))
    dispatcher.add_handler(MessageHandler(
        Filters.text | Filters.location,
        handle_users_reply,
        pass_job_queue=True,
    ))
    dispatcher.add_handler(CommandHandler(
        'start',
        handle_users_reply,
        pass_job_queue=True,
    ))
    dispatcher.add_handler(CallbackQueryHandler(handle_menu))
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dispatcher.add_handler(MessageHandler(
        Filters.successful_payment,
        successful_payment_callback,
    ))
    updater.start_polling()


if __name__ == '__main__':
    main()
