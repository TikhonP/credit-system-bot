# import sys
#
# sys.dont_write_bytecode = True


import os

import sentry_sdk

sentry_sdk.init(
    dsn="https://2fb6ef76c9234fc2a0b77ef06b6fda68@o1075119.ingest.sentry.io/6716649",

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
from django.db.models import Sum

django.setup()

# Import your models for use in your script
from db.models import User, MoneyRequest
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler, Updater

TOKEN = os.environ.get('MUSIC_QUEUE_TELEGRAM_TOKEN')
ADMIN_ID = 304915293


def start_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user, created = User.get_user_and_created(update, context)
    if user.user_id == ADMIN_ID:
        user.is_admin = True
        user.save()
        update.message.reply_text("Вы админ!")

    if created:
        text = "Приветствуем вас в кредитном банке Тихона, для того чтобы начать работу " \
               "введите команду /money <сумма в рублях> <описание>\n" \
               "*Например*: /money 1000 Зарплата\n\n" \
               "Для того чтобы узнать больше введите команду /help"
    else:
        text = "И снова здрасьте!"

    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


def duty_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    user = User.get_user(update, context)
    moneyRequests = user.moneyrequest_set.filter(is_done=False)

    if moneyRequests.count() == 0:
        update.message.reply_text('У вас нет долгов!')
        return

    text = "*Ваши долги:*\n\n"
    for moneyRequest in moneyRequests:
        text += f"*{moneyRequest.price}* - {moneyRequest.description}\n"

    text += "\nВсего: *{}*".format(moneyRequests.aggregate(Sum('price'))['price__sum'])
    update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(
        "/money <сумма в рублях> <описание> - запросить деньги\n"
        "/duty - узнать свои долги\n"
    )


def money_command(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update, context)
    str_array = update.message.text.split()

    try:
        price = str_array[1]
        description = ' '.join(str_array[2:])
    except IndexError:
        update.message.reply_text('Неверный формат ввода!')
        return

    if not price.isdigit():
        update.message.reply_text('Неверный формат ввода!')
        return

    money = int(price)
    money_request = MoneyRequest.objects.create(
        price=money,
        description=description,
        user=user
    )

    context.bot.send_message(chat_id=ADMIN_ID, text=f"Пользователь {user.first_name} {user.last_name} создал запрос "
                                                    f"на {money_request.price} рублей. ({money_request.description})")

    update.message.reply_text(f"Запрос на получение {money_request.price} - {money_request.description} создан")


def get_duties_for_admin(update: Update, context: CallbackContext):
    user = User.get_user(update, context)
    if user.is_admin:
        text = "*Долги:*\n\n"
        for user in User.objects.filter(is_admin=False):
            moneyRequests = user.moneyrequest_set.filter(is_done=False)

            if moneyRequests.count() == 0:
                continue

            text += f"*{user.first_name} {user.last_name}*:\n"
            for moneyRequest in moneyRequests:
                text += f"*{moneyRequest.price}* - {moneyRequest.description}\n"
            text += "\nВсего: *{}*\n\n".format(moneyRequests.aggregate(Sum('price'))['price__sum'])

        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text('Вы не админ!')


def main() -> None:
    """Start the bot."""

    global DATA

    if TOKEN is None:
        logger.error("None token exported")
        exit()

    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('money', money_command))
    dispatcher.add_handler(CommandHandler('duty', duty_command))
    dispatcher.add_handler(CommandHandler('duties', get_duties_for_admin))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
