from environs import Env
from telegram import LabeledPrice

env = Env()
env.read_env()


def start_without_shipping(bot, update, price):
    chat_id = update.callback_query.message.chat.id
    title = 'Payment_{0}'.format(chat_id)
    description = 'We\'re waiting for your payment'

    payload = 'Custom payload'
    provider_token = env.str('TRANZZO_PAYMENT')
    start_parameter = 'Payment_{0}'.format(chat_id)
    currency = 'RUB'
    prices = [LabeledPrice('Test payment', price * 100)]
    bot.sendInvoice(chat_id, title, description, payload,
                    provider_token, start_parameter, currency, prices)


def precheckout_callback(bot, update):
    query = update.pre_checkout_query

    if query.invoice_payload != 'Custom payload':
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
                                      error_message='Something went wrongs')
    else:
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


def successful_payment_callback(bot, update):
    update.message.reply_text('Please, send location or address')
