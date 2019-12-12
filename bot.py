import datetime
import asyncio
import uuid
import aiogram
from aiogram import Bot, Dispatcher, executor, exceptions
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
import scripts.messages as msg
import scripts.markup as mk
from scripts.config import TOKEN, ADMINS, DEVELOPER_ID
from scripts.db_manager import UsersDbManager, ActionsDbManager
import scripts.ServiceMarketApi as api
from scripts.text_parser import get_order_text, get_item_description, stats_text
from scripts.email_sender import send_photo

bot = Bot(TOKEN)
dp = Dispatcher(bot)
# UsersDbManager.clear()
loop = asyncio.get_event_loop()


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('show_by_model_'))
async def show_by_model(inline_query):
    data = inline_query.query[14:]
    data = data.split('|')
    tel_id = inline_query.from_user.id
    user = await UsersDbManager.get_user(tel_id, loop)

    try:
        model = data[0]
        sub_category_id = int(data[1])
    except Exception:
        if user.language == 'ru':
            text = msg.nothing_found_article_ru.format(data[0])
        elif user.language == 'uk':
            text = msg.nothing_found_article_ukr.format(data[0])
        else:
            text = msg.nothing_found_article_en.format(data[0])

        result_id = str(uuid.uuid4())
        message_content = InputTextMessageContent(text)
        result = InlineQueryResultArticle(
            id=result_id, title=text,
            thumb_url='https://img.icons8.com/dotty/2x/nothing-found.png',
            thumb_height=400, thumb_width=400,
            input_message_content=message_content
        )
        await bot.answer_inline_query(inline_query.id, results=[result], cache_time=1)
        return

    search_results = await api.search_by_model(model, user.language)

    products = []
    print(search_results)

    if type(search_results['data']['products']['products']) is dict:
        all_items = search_results['data']['products']['products'].values()
    else:
        all_items = search_results['data']['products']['products']

    for item in all_items:
        if item['category_id'] == int(sub_category_id):
            products.append(item)

    if inline_query.offset != '':
        offset = int(inline_query.offset)
    else:
        offset = 0

    if len(products) < offset + 20:
        next_offset = ''
        end = len(products)
    else:
        next_offset = offset + 20
        end = next_offset

    results = []
    for i in range(offset, end):
        product = products[i]

        try:
            url = product['url']
            stock = int(product['stock'])
            price = product['price']
            name = product['name']
            image_url = product['image']

            if stock > 20:
                if user.language == 'ru':
                    stock = 'более 20-ти'
                elif user.language == 'ukr':
                    stock = 'більше 20-ти'
                else:
                    stock = 'more than 20'

            result_id = str(uuid.uuid4())

            item_description = await get_item_description(product, user.language, loop)
            message_content = InputTextMessageContent(item_description, parse_mode='HTML')
        except KeyError:
            print('Key Error')
            continue

        if url is not None:
            keyboard = mk.go_to_site_keyboard(url, user.language)
        else:
            keyboard = None

        if user.language == 'ru':
            description = 'Цена: {0} грн    В наличии шт.: {1}'.format(price, stock)
        elif user.language == 'uk':
            description = 'Ціна: {0} грн    В наявності шт.: {1}'.format(price, stock)
        else:
            description = 'Cost: {0} uah    In stock: {1}'.format(price, stock)

        results.append(
            InlineQueryResultArticle(
            id=result_id, title=name, description=description,
            thumb_url=image_url,
            thumb_height=400, thumb_width=400,
            input_message_content=message_content,
            reply_markup=keyboard
        ))
    print(next_offset)

    try:
        await bot.answer_inline_query(inline_query.id, results=results, next_offset=str(next_offset), cache_time=1)
    except aiogram.utils.exceptions.NetworkError:
        print('Network error, file too large')


@dp.inline_handler(lambda inline_query: inline_query.query.startswith('show_by_article_'))
async def show_by_article(inline_query):
    article = inline_query.query[16:]
    tel_id = inline_query.from_user.id
    user = await UsersDbManager.get_user(tel_id, loop)
    products = await api.search_by_number(article, user.language)

    if len(products) == 0:
        if user.language == 'ru':
            text = msg.nothing_found_article_ru.format(article)
        elif user.language == 'uk':
            text = msg.nothing_found_article_ukr.format(article)
        else:
            text = msg.nothing_found_article_en.format(article)

        result_id = str(uuid.uuid4())
        message_content = InputTextMessageContent(text)
        result = InlineQueryResultArticle(
            id=result_id, title=text,
            thumb_url='https://img.icons8.com/dotty/2x/nothing-found.png',
            thumb_height=400, thumb_width=400,
            input_message_content=message_content
        )
        await bot.answer_inline_query(inline_query.id, results=[result], cache_time=1)
        return

    print('Offset ' + inline_query.offset)

    if inline_query.offset != '':
        offset = int(inline_query.offset)
    else:
        offset = 0

    if len(products) < offset + 20:
        next_offset = ''
        end = len(products)
    else:
        next_offset = offset + 20
        end = next_offset

    results = []
    for i in range(offset, end):
        product = products[i]

        try:
            url = product['url']
            stock = product['stock']
            price = product['price']
            name = product['name']
            image_url = product['image']

            if stock > 20:
                if user.language == 'ru':
                    stock = 'более 20-ти'
                elif user.language == 'ukr':
                    stock = 'більше 20-ти'
                else:
                    stock = 'more than 20'

            result_id = str(uuid.uuid4())

            item_description = await get_item_description(product, user.language, loop)
            message_content = InputTextMessageContent(item_description, parse_mode='HTML')
        except KeyError:
            print('Key Error')
            continue

        if url is not None:
            keyboard = mk.go_to_site_keyboard(url, user.language)
        else:
            keyboard = None

        if user.language == 'ru':
            description = 'Цена: {0} грн    В наличии шт.: {1}'.format(price, stock)
        elif user.language == 'uk':
            description = 'Ціна: {0} грн    В наявності шт.: {1}'.format(price, stock)
        else:
            description = 'Cost: {0} uah    In stock: {1}'.format(price, stock)

        results.append(
            InlineQueryResultArticle(
            id=result_id, title=name, description=description,
            thumb_url=image_url,
            thumb_height=400, thumb_width=400,
            input_message_content=message_content,
            reply_markup=keyboard
        ))
    print(next_offset)

    try:
        await bot.answer_inline_query(inline_query.id, results=results, next_offset=str(next_offset), cache_time=1)
    except aiogram.utils.exceptions.NetworkError:
        print('Network error, file too large')


@dp.inline_handler()
async def show_by_articleee(inline_query):
    print(inline_query.query)
    print('TEST')


@dp.message_handler(commands=['admin'])
async def admin(message):
    tel_id = message.chat.id

    if tel_id not in ADMINS and tel_id != DEVELOPER_ID:
        await bot.send_message(tel_id, '❌ У вас нет прав администратора')
        return

    await bot.send_message(tel_id, 'Панель администратора', disable_notification=True, reply_markup=mk.admin_menu)


@dp.message_handler(commands=['cancel'])
async def cancel(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    await UsersDbManager.update_context(tel_id, '0', loop)

    if user.language == 'ru':
        text = 'Операция отменена'
    elif user.language == 'uk':
        text = 'Операція скасована'
    else:
        text = 'Operation canceled'
    await bot.send_message(tel_id, text, disable_notification=True)


@dp.message_handler(commands=['start', 'contacts'])
async def start(message):
    tel_id = message.chat.id
    lang = message.from_user.locale
    name = message.from_user.first_name
    print(name)

    if not await UsersDbManager.user_exist(tel_id, loop):
        if lang is not 'ru' and lang is not 'uk' and lang is not 'en':
            lang = 'ru'
        await UsersDbManager.add_user(tel_id, '0', lang, loop)
        await ActionsDbManager.add('new_user', datetime.datetime.now(), loop)

    user = await UsersDbManager.get_user(tel_id, loop)
    if not user.is_using:
        await UsersDbManager.update_is_using(tel_id, True, loop)
        await ActionsDbManager.add('user_returned', datetime.datetime.now(), loop)
    if user.language == 'ru':
        text = msg.greeting_ru.format(name)
        keyboard = mk.main_menu_ru
    elif user.language == 'uk':
        text = msg.greeting_ukr.format(name)
        keyboard = mk.main_menu_uk
    else:
        text = msg.greeting_en.format(name)
        keyboard = mk.main_menu_en

    await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)

    if message.text.startswith('/contacts'):
        if user.language == 'ru':
            text = msg.contacts_ru
        elif user.language == 'ukr':
            text = msg.contacts_ukr
        else:
            text = msg.contacts_en

        await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML')


@dp.message_handler(lambda message: message.text == '📩 Сделать рассылку')
async def send_message(message):
    tel_id = message.chat.id

    if tel_id not in ADMINS and tel_id != DEVELOPER_ID:
        await bot.send_message(tel_id, '❌ У вас нет прав администратора', disable_notification=True)
        return

    await bot.send_message(tel_id, ('Отправьте мне сообщение, которое нужно разослать. Это может быть текст, картинка,'
                                    ' видео, стикер или файл. Если хотите отменить операцию, используйте /cancel'), disable_notification=True)
    await UsersDbManager.update_context(tel_id, 'wait_for_message', loop)


@dp.message_handler(lambda message: message.text == '📊 Статистика')
async def stats(message):
    tel_id = message.chat.id

    if tel_id not in ADMINS and tel_id != DEVELOPER_ID:
        await bot.send_message(tel_id, '❌ У вас нет прав администратора')
        return

    first_date = datetime.datetime.now() - datetime.timedelta(days=1)
    second_date = datetime.datetime.now()
    actions = await ActionsDbManager.get_actions_beside_dates(first_date, second_date, loop)

    text = '''Статистика за последние сутки'''
    text += stats_text(actions)

    await bot.send_message(tel_id, text, disable_notification=True, reply_markup=mk.stats_keyboard())


@dp.callback_query_handler(lambda call: call.data.startswith('stats_'))
async def stats_per_days(call):
    tel_id = call.message.chat.id
    days = int(call.data[6:])
    print('Test')
    if tel_id not in ADMINS and tel_id != DEVELOPER_ID:
        await bot.send_message(tel_id, '❌ У вас нет прав администратора')
        return

    first_date = datetime.datetime.now() - datetime.timedelta(days=days)
    second_date = datetime.datetime.now()
    actions = await ActionsDbManager.get_actions_beside_dates(first_date, second_date, loop)

    if days == 1:
        text = '''Статистика за последние сутки'''
    elif days == 7:
        text = '''Статистика за последнюю неделю'''
    elif days == 30:
        text = '''Статистика за последний месяц'''

    text += stats_text(actions)

    try:
        await bot.edit_message_text(text, tel_id, message_id=call.message.message_id, reply_markup=mk.stats_keyboard())
    except exceptions.MessageNotModified:
        print('Message is not modified')

@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'wait_for_message',
                    content_types=['text', 'photo', 'video', 'sticker', 'document'])
async def wait_for_message(message):

    tel_id = message.chat.id
    await UsersDbManager.update_context(tel_id, '0', loop)
    message_counter = 0
    audience_lost = 0
    audience_returned = 0
    all_users = await UsersDbManager.get_all_users(loop)

    if message.text is not None:
        content = message.text
        for user in all_users:
            try:
                await bot.send_message(user.tel_id, content, parse_mode='HTML')
                if not user.is_using:
                    audience_returned += 1
                    await UsersDbManager.update_is_using(user.tel_id, True, loop)
                    await ActionsDbManager.add('user_returned', datetime.datetime.now(), loop)

                message_counter += 1
            except Exception:
                print('User not found')
                if user.is_using:
                    audience_lost+=1
                    await ActionsDbManager.add('user_lost', datetime.datetime.now(), loop)
                await UsersDbManager.update_is_using(user.tel_id, False, loop)

    elif message.sticker is not None:
        sticker_file_id = message.sticker.file_id
        for user in all_users:
            try:
                await bot.send_sticker(user.tel_id, sticker_file_id)
                if not user.is_using:
                    audience_returned += 1
                    await ActionsDbManager.add('user_returned', datetime.datetime.now(), loop)
                    await UsersDbManager.update_is_using(user.tel_id, True, loop)
            except Exception:
                print('User not found')
                if user.is_using:
                    audience_lost += 1
                    await ActionsDbManager.add('user_lost', datetime.datetime.now(), loop)
                await UsersDbManager.update_is_using(user.tel_id, False, loop)

    elif message.photo is []:
        photo_file_id = message.photo[0].file_id
        for user in all_users:
            try:
                await bot.send_photo(user.tel_id, photo_file_id)
                if not user.is_using:
                    audience_returned += 1
                    await ActionsDbManager.add('user_returned', datetime.datetime.now(), loop)
                    await UsersDbManager.update_is_using(user.tel_id, True, loop)
            except Exception:
                print('User not found')
                if user.is_using:
                    audience_lost += 1
                    await ActionsDbManager.add('user_lost', datetime.datetime.now(), loop)
                await UsersDbManager.update_is_using(user.tel_id, False, loop)

    elif message.video is not None:
        video_file_id = message.video.file_id
        for user in all_users:
            try:
                await bot.send_video(user.tel_id, video_file_id)
                if not user.is_using:
                    audience_returned += 1
                    await ActionsDbManager.add('user_returned', datetime.datetime.now(), loop)
                    await UsersDbManager.update_is_using(user.tel_id, True, loop)
            except Exception:
                print('User not found')
                if user.is_using:
                    audience_lost += 1
                    await ActionsDbManager.add('user_lost', datetime.datetime.now(), loop)
                await UsersDbManager.update_is_using(user.tel_id, False, loop)

    elif message.document is not None:
        file_id = message.document.file_id
        for user in all_users:
            try:
                await bot.send_document(user.tel_id, file_id)
                if not user.is_using:
                    audience_returned += 1
                    await ActionsDbManager.add('user_returned', datetime.datetime.now(), loop)
                    await UsersDbManager.update_is_using(user.tel_id, True, loop)
            except Exception:
                print('User not found')
                if user.is_using:
                    audience_lost += 1
                    await ActionsDbManager.add('user_lost', datetime.datetime.now(), loop)
                await UsersDbManager.update_is_using(user.tel_id, False, loop)

    text = '''✅ Рассылка закончена
 📩 {0} сообщений успешно доставлено
'''.format(message_counter)
    if audience_lost > 0:
        text += '''👤  {0} человек отписалось от бота и не получили сообщение'''.format(audience_lost)
    if audience_returned > 0:
        text += '''🚶‍♂️ {0} человек вернулись в бот'''.format(audience_returned)

    await bot.send_message(tel_id, text, disable_notification=True)


@dp.message_handler(lambda message: message.text == '⬅️ Назад' or
                                    message.text == '⬅️ Назад' or
                                    message.text == '⬅️ Back')
async def to_main_menu(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        keyboard = mk.main_menu_ru
        text = 'Главное меню'
    elif user.language == 'uk':
        keyboard = mk.main_menu_uk
        text = 'Головне меню'
    else:
        keyboard = mk.main_menu_en
        text = 'Main menu'

    await UsersDbManager.update_context(tel_id, '0', loop)
    await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)

''' 

    Language change                                       

'''


@dp.message_handler(lambda message: message.text == 'Сменить язык 🇷🇺' or
                                    message.text == 'Змінити мову 🇺🇦' or
                                    message.text == 'Change language 🇬🇧')
async def change_language(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = 'Выберите язык'
    elif user.language == 'uk':
        text = 'Виберіть мову'
    else:
        text = 'Choose language'

    keyboard = mk.language_keyboard

    await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)


@dp.message_handler(lambda message: message.text == 'Русский 🇷🇺' or
                                    message.text == 'Українська 🇺🇦' or
                                    message.text == 'English 🇬🇧')
async def choose_language(message):
    tel_id = message.chat.id

    if message.text == 'Русский 🇷🇺':
        new_lang = 'ru'
        await bot.send_message(tel_id, 'Язык изменен', reply_markup=mk.main_menu_ru, disable_notification=True)
    elif message.text == 'Українська 🇺🇦':
        new_lang = 'uk'
        await bot.send_message(tel_id, 'Мова змінена', reply_markup=mk.main_menu_uk, disable_notification=True)
    elif message.text == 'English 🇬🇧':
        new_lang = 'en'
        await bot.send_message(tel_id, 'Language changed', reply_markup=mk.main_menu_en, disable_notification=True)

    await UsersDbManager.update_language(tel_id, new_lang, loop)

''' 

    FAQ                                       

'''


@dp.message_handler(lambda message: message.text == '🖊 Вопросы и ответы' or
                                    message.text == '🖊 Питання і відповіді' or
                                    message.text == '🖊 FAQ')
async def faq(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        keyboard = mk.faq_keyboard_ru
    elif user.language == 'uk':
        keyboard = mk.faq_keyboard_ukr
    else:
        keyboard = mk.faq_keyboard_en

    await bot.send_message(tel_id, message.text, disable_notification=True, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Контакты' or
                                    message.text == 'Контакти' or
                                    message.text == 'Contacts')
async def contacts(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.contacts_ru
    elif user.language == 'uk':
        text = msg.contacts_ukr
    else:
        text = msg.contacts_en

    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML')


@dp.message_handler(lambda message: message.text == 'Где найти модель техники?' or
                                    message.text == 'Де знайти модель техніки?' or
                                    message.text == 'Where I can find model number')
async def where_model(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.where_model_ru
    elif user.language == 'uk':
        text = msg.where_model_ukr
    else:
        text = msg.where_model_en

    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='MARKDOWN')


@dp.message_handler(lambda message: message.text == 'Какие способы доставки?' or
                                    message.text == 'Які є способі доставки?' or
                                    message.text == 'Delivery')
async def what_delivery(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.delivery_method_ru
    elif user.language == 'uk':
        text = msg.delivery_method_ukr
    else:
        text = msg.delivery_method_en

    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML')


@dp.message_handler(lambda message: message.text == 'Какие способы оплаты?' or
                                    message.text == 'Які є способи оплати?' or
                                    message.text == 'Payment')
async def what_payments(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.payment_method_ru
    elif user.language == 'uk':
        text = msg.payment_method_ukr
    else:
        text = msg.payment_method_en

    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML')


@dp.message_handler(lambda message: message.text == 'Как стать оптовым клиентом?' or
                                    message.text == 'Як стати оптовим клієнтом?' or
                                    message.text == 'How to become a wholesale customer?')
async def how_can_opt(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.how_can_opt_ru
    elif user.language == 'uk':
        text = msg.how_can_opt_ukr
    else:
        text = msg.how_can_opt_en

    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='MARKDOWN')


@dp.message_handler(lambda message: message.text == 'Как вернуть или поменять товар?' or
                                    message.text == 'Як повернути або замінити товар?' or
                                    message.text == 'How to return or exchange an item?')
async def how_change(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.how_exchange_ru
    elif user.language == 'uk':
        text = msg.how_exchange_ukr
    else:
        text = msg.how_exchange_en

    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='MARKDOWN')

''' 

    Check order status                                       

'''


@dp.message_handler(lambda message: message.text == '🚚 Проверить статус заказа' or
                                    message.text == '🚚 Статус замовлення' or
                                    message.text == '🚚 Check order status')
async def check_order_status(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    keyboard = mk.get_order_method(user.language)

    await bot.delete_message(tel_id, message.message_id)
    await bot.send_message(tel_id, message.text, reply_markup=keyboard, disable_notification=True)


@dp.callback_query_handler(lambda call: call.data == 'orders_by_number')
async def order_by_number(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = 'Введите номер заказа'
    elif user.language == 'uk':
        text = 'Введіть номер замовлення'
    else:
        text = 'Please enter order number'

    await bot.send_message(tel_id, text, disable_notification=True)
    await UsersDbManager.update_context(tel_id, 'wait_order_number', loop)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'wait_order_number')
async def wait_order_number(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if message.text is None or any(c.isalpha() for c in message.text):
        if user.language == 'ru':
            text = msg.incorrect_ru
        elif user.language == 'uk':
            text = msg.incorrect_ukr
        else:
            text = msg.incorrect_en

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    order = await api.search_by_order(message.text, user.language)

    if order == []:
        if user.language == 'ru':
            text = msg.nothing_found_ru.format(message.text)
        elif user.language == 'uk':
            text = msg.nothing_found_ukr.format(message.text)
        else:
            text = msg.nothing_found_en.format(message.text)

        await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML')
        return

    text = get_order_text(message.text, order, user.language)

    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='MARKDOWN')
    await UsersDbManager.update_context(tel_id, '0', loop)


@dp.callback_query_handler(lambda call: call.data == 'orders_by_phone')
async def order_by_phone(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.phone == '0':
        if user.language == 'ru':
            text = msg.enter_mobile_ru
            keyboard = mk.share_contact_ru
        elif user.language == 'uk':
            text = msg.enter_mobile_ukr
            keyboard = mk.share_contact_ukr
        else:
            text = msg.enter_mobile_en
            keyboard = mk.share_contact_en

        await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)
        await UsersDbManager.update_context(tel_id, 'wait_new_phone', loop)
        return

    keyboard = mk.get_yes_no_phone(user.language)

    if user.language == 'ru':
        text = msg.this_is_your_number_ru
    elif user.language == 'uk':
        text = msg.this_is_your_number_ukr
    else:
        text = msg.this_is_your_number_en

    try:
        await bot.edit_message_text(text.format(user.phone), tel_id, call.message.message_id, reply_markup=keyboard)
    except exceptions.MessageNotModified:
        print('Message is not modified')


@dp.callback_query_handler(lambda call: call.data == 'change_number')
async def order_by_phone(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.enter_new_mobile_ru
        keyboard = mk.share_contact_ru
    elif user.language == 'uk':
        text = msg.enter_new_mobile_ukr
        keyboard = mk.share_contact_ukr
    else:
        text = msg.enter_new_mobile_en
        keyboard = mk.share_contact_en

    await bot.send_message(tel_id, text, disable_notification=True, reply_markup=keyboard)
    await UsersDbManager.update_context(tel_id, 'wait_new_phone', loop)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'wait_new_phone',
                    content_types=['contact', 'text'])
async def wait_new_phone(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if (message.text is None or len(message.text) < 10 or any(c.isalpha() for c in message.text)) and message.contact is None:
        if user.language == 'ru':
            text = msg.incorrect_ru
        elif user.language == 'uk':
            text = msg.incorrect_ukr
        else:
            text = msg.incorrect_en

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    if message.contact is not None:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await UsersDbManager.update_phone(tel_id, phone, loop)
    await UsersDbManager.update_context(tel_id, '0', loop)

    orders = await api.search_orders_by_phone(phone, user.language)

    if orders == []:
        if user.language == 'ru':
            text = msg.nothing_found_by_number_ru.format(phone)
            keyboard = mk.main_menu_ru
        elif user.language == 'uk':
            text = msg.nothing_found_by_number_ukr.format(phone)
            keyboard = mk.main_menu_uk
        else:
            text = msg.nothing_found_by_number_en.format(phone)
            keyboard = mk.main_menu_en

        await bot.send_message(tel_id, text, disable_notification=True, reply_markup=keyboard)
        return

    keyboard = mk.orders_by_phone(orders, user.phone, user.language)
    if user.language == 'ru':
        text = 'Ваши заказы'
    elif user.language == 'uk':
        text = 'Ваші замовлення'
    else:
        text = 'Your orders'

    await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)


@dp.callback_query_handler(lambda call: call.data == 'my_phone')
async def my_phone(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    orders = await api.search_orders_by_phone(user.phone, user.language)

    if orders == []:
        if user.language == 'ru':
            text = msg.nothing_found_by_number_ru.format(user.phone)
        elif user.language == 'uk':
            text = msg.nothing_found_by_number_ukr.format(user.phone)
        else:
            text = msg.nothing_found_by_number_en.format(user.phone)

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    keyboard = mk.orders_by_phone(orders, user.phone, user.language)
    if user.language == 'ru':
        text = 'Ваши заказы'
    elif user.language == 'uk':
        text = 'Ваші замовлення'
    else:
        text = 'Your orders'

    try:
        await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
    except exceptions.MessageNotModified:
        print('Message is not modified')


@dp.callback_query_handler(lambda call: call.data.startswith('more_orders_'))
async def more_orders(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    data = call.data[12:]
    data = data.split('|')
    phone = data[0]
    current_pos = int(data[1])

    orders = await api.search_orders_by_phone(phone, user.language)

    keyboard = mk.orders_by_phone(orders, phone, user.language, current_pos)
    if user.language == 'ru':
        text = 'Ваши заказы'
    elif user.language == 'uk':
        text = 'Ваші замовлення'
    else:
        text = 'Your orders'

    try:
        await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
    except exceptions.MessageNotModified:
        print('Message is not modified')


@dp.callback_query_handler(lambda call: call.data.startswith('order_'))
async def order_show(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    order_num = call.data[6:]

    order = await api.search_by_order(order_num, user.language)

    if order == []:
        if user.language == 'ru':
            text = msg.nothing_found_ru.format(order_num)
        elif user.language == 'uk':
            text = msg.nothing_found_ukr.format(order_num)
        else:
            text = msg.nothing_found_en.format(order_num)

        await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML')
        return

    text = get_order_text(order_num, order, user.language)
    keyboard = mk.back_to_orders(user.language)

    try:
        await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard, parse_mode='MARKDOWN')
    except exceptions.MessageNotModified:
        print("Message is not modified")


@dp.callback_query_handler(lambda call: call.data == 'back_to_orders')
async def back_to_orders(call):
    await my_phone(call)

''' 

    Search                                     

'''


@dp.message_handler(lambda message: message.text == '🔎 Найти деталь' or
                                    message.text == '🔎 Знайти деталь' or
                                    message.text == '🔎 Find spare part')
async def find_detail(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        keyboard = mk.find_detail_keyboard_ru
    elif user.language == 'uk':
        keyboard = mk.find_detail_keyboard_ukr
    else:
        keyboard = mk.find_detail_keyboard_en

    await bot.send_message(tel_id, message.text, disable_notification=True, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == 'Найти по названию' or
                                    message.text == 'Знайти за назвою' or
                                    message.text == 'Search by name')
async def search_by_name(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.enter_name_ru
    elif user.language == 'uk':
        text = msg.enter_namw_ukr
    else:
        text = msg.enter_name_en

    await bot.send_message(tel_id, text, disable_notification=True)
    await UsersDbManager.update_context(tel_id, 'wait_for_article', loop)


@dp.message_handler(lambda message: message.text == 'Поиск по фото (пересылка менеджеру)' or
                                    message.text == 'Пошук по фото (пересилання менеджеру)' or
                                    message.text == 'Photo search (send to manager)')
async def search_by_photo(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.enter_mobile_ru
        keyboard = mk.share_contact_ru
    elif user.language == 'uk':
        text = msg.enter_mobile_ukr
        keyboard = mk.share_contact_ukr
    else:
        text = msg.enter_mobile_en
        keyboard = mk.share_contact_en

    await bot.send_message(tel_id, text, disable_notification=True, reply_markup=keyboard)
    await UsersDbManager.update_context(tel_id, 'wait_phone_photo', loop)


@dp.message_handler(lambda message: message.text == 'Поиск по модели' or
                                    message.text == 'Пошук по моделі' or
                                    message.text == 'Search by model')
async def search_by_model(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.enter_model_name_ru
    elif user.language == 'uk':
        text = msg.enter_model_name_ukr
    else:
        text = msg.enter_model_name_en

    await bot.send_message(tel_id, text, disable_notification=True)
    await UsersDbManager.update_context(tel_id, 'wait_model_name', loop)


@dp.message_handler(lambda message: message.text == 'Знайти по артикулу' or
                                    message.text == 'Найти по артикулу' or
                                    message.text == 'Find by stock number')
async def find_by_article(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.enter_artickle_ru
    elif user.language == 'uk':
        text = msg.enter_artickle_ukr
    else:
        text = msg.enter_artickle_en

    await bot.send_message(tel_id, text, disable_notification=True)
    await UsersDbManager.update_context(tel_id, 'wait_for_article', loop)


@dp.message_handler(lambda message: message.text == '❌ Отмена' or
                                    message.text == '❌ Скасувати' or
                                    message.text == '❌ Cancel')
async def cancel_search(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.canceled_ru
        keyboard = mk.find_detail_keyboard_ru
    elif user.language == 'uk':
        text = msg.canceled_ukr
        keyboard = mk.find_detail_keyboard_ukr
    else:
        text = msg.canceled_en
        keyboard = mk.find_detail_keyboard_en

    await UsersDbManager.update_context(tel_id, '0', loop)
    await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)


@dp.message_handler(lambda message: message.text == 'Найти по коду товара' or
                                    message.text == 'Знайти за кодом товару' or
                                    message.text == 'Find by product code')
async def find_by_product_code(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if user.language == 'ru':
        text = msg.enter_product_code_ru
    elif user.language == 'uk':
        text = msg.enter_product_code_ukr
    else:
        text = msg.enter_product_code_en

    await bot.send_message(tel_id, text, disable_notification=True)
    await UsersDbManager.update_context(tel_id, 'wait_for_product_code', loop)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'wait_for_article')
async def wait_for_article(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if message.text is None or message.text == '' or len(message.text) < 4 or len(message.text) > 45:
        if user.language == 'ru':
            text = msg.incorrect_ru
        elif user.language == 'uk':
            text = msg.incorrect_ukr
        else:
            text = msg.incorrect_en

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    article = message.text
    products = await api.search_by_number(article, user.language)
    await UsersDbManager.update_context(tel_id, '0', loop)
    await ActionsDbManager.add('search_by_article', datetime.datetime.now(), loop)

    if products == []:
        if user.language == 'ru':
            text = msg.nothing_found_article_ru.format(article)
        elif user.language == 'uk':
            text = msg.nothing_found_article_ukr.format(article)
        else:
            text = msg.nothing_found_article_en.format(article)

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    if len(products) == 1:
        item_url = products[0]['url']
        text = await get_item_description(products[0], user.language, loop)
        keyboard = mk.go_to_site_keyboard(item_url, user.language)
        await bot.send_message(tel_id, text, disable_notification=True, reply_markup=keyboard, parse_mode='HTML')
        return

    if user.language == 'ru':
        text = msg.finded_ru.format(len(products))
    elif user.language == 'uk':
        text = msg.finded_ukr.format(len(products))
    else:
        text = msg.finded_en.format(len(products))

    keyboard = mk.show_results_by_article(user.language, article)

    await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'wait_for_product_code')
async def wait_for_product_code(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if message.text is None or message.text == '' or len(message.text) < 4 or any(c.isalpha() for c in message.text):
        if user.language == 'ru':
            text = msg.incorrect_ru
        elif user.language == 'uk':
            text = msg.incorrect_ukr
        else:
            text = msg.incorrect_en

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    code = message.text
    product = await api.search_by_code(code, user.language)
    await ActionsDbManager.add('search_by_product_code', datetime.datetime.now(), loop)

    if product is None or product == []:
        if user.language == 'ru':
            text = msg.nothing_found_code_ru.format(code)
        elif user.language == 'uk':
            text = msg.nothing_found_code_ukr.format(code)
        else:
            text = msg.nothing_found_code_en.format(code)

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    product_url = product[0]['url']
    text = await get_item_description(product[0], user.language, loop)
    keyboard = mk.go_to_site_keyboard(product_url, user.language)

    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML', reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith('item_'))
async def show_item(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    code = call.data[5:]
    print(code)
    item = await api.search_by_code(code, user.language)

    if item == None or item == []:
        if user.language == 'ru':
            text = msg.error_nothing_found_ru
        elif user.language == 'uk':
            text = msg.error_nothing_found_ukr
        else:
            text = msg.error_nothing_found_en
        try:
            await bot.edit_message_text(text, tel_id, call.message.message_id)
        except exceptions.MessageNotModified:
            print("Message is not modified")
        return

    url = item[0]['url']
    text = await get_item_description(item[0], user.language, loop)
    keyboard = mk.go_to_site_keyboard(url, user.language)

    await bot.send_message(tel_id, text, disable_notification=True, parse_mode='HTML', reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith('next|'))
async def next_page_article(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    data = call.data[5:]
    data = data.split('|')
    article = data[0]
    cur_pos = int(data[1])

    items = await api.search_by_number(article, user.language)

    if items == [] or items is None:
        if user.language == 'ru':
            text = msg.error_nothing_found_ru
        elif user.language == 'uk':
            text = msg.error_nothing_found_ukr
        else:
            text = msg.error_nothing_found_en
        try:
            await bot.edit_message_text(text, tel_id, call.message.message_id)
        except exceptions.MessageNotModified:
            print("Message is not modified")
        return

    keyboard = mk.get_next_page(article, cur_pos, items, user.language)
    if user.language == 'ru':
        text = msg.searching_results_ru
    elif user.language == 'uk':
        text = msg.searching_results_ukr
    else:
        text = msg.searching_results_en

    try:
        await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
    except exceptions.MessageNotModified:
        print("Message is not modified")


@dp.callback_query_handler(lambda call: call.data.startswith('back|'))
async def pervious_page_article(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    data = call.data[5:]
    data = data.split('|')
    article = data[0]
    cur_pos = int(data[1])

    items = await api.search_by_number(article, user.language)

    if items == [] or items is None:
        if user.language == 'ru':
            text = msg.error_nothing_found_ru
        elif user.language == 'uk':
            text = msg.error_nothing_found_ukr
        else:
            text = msg.error_nothing_found_en
        try:
            await bot.edit_message_text(text, tel_id, call.message.message_id)
        except exceptions.MessageNotModified:
            print("Message is not modified")
        return

    keyboard = mk.get_pervious_page(article, cur_pos, items, user.language)
    if user.language == 'ru':
        text = msg.searching_results_ru
    elif user.language == 'uk':
        text = msg.searching_results_ukr
    else:
        text = msg.searching_results_en

    try:
        await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
    except exceptions.MessageNotModified:
        print("Message is not modified")


@dp.message_handler(lambda message: (message.text == '📩 Отправить' or
                                    message.text == '📩 Відправити' or
                                    message.text == '📩 Submit') and UsersDbManager.sync_get_context(message.chat.id))
async def send(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    context = await UsersDbManager.get_context(tel_id, loop)
    data = context[15:]
    data = data.split('|')
    phone = data[0]

    if len(data) < 2:
        if user.language == 'ru':
            text = msg.no_photos_ru
        elif user.language == 'uk':
            text = msg.no_photos_ukr
        else:
            text = msg.no_photos_en
        await bot.send_message(tel_id, text, disable_notification=True)
        return

    if user.language == 'ru':
        text = msg.photo_sended_ru
        keyboard = mk.main_menu_ru
    elif user.language == 'uk':
        text = msg.photo_sended_ukr
        keyboard = mk.main_menu_uk
    else:
        text = msg.photo_sended_en
        keyboard = mk.main_menu_en

    await UsersDbManager.update_context(tel_id, '0', loop)
    await bot.send_message(tel_id, text, disable_notification=True, reply_markup=keyboard)

    byte_photos = []
    for i in range(1, len(data)):
        print(data[i])
        downloaded = await bot.download_file_by_id(data[i])
        byte_photos.append(downloaded)

    name = '{0} {1}'.format(message.from_user.first_name, message.from_user.last_name)
    await send_photo(byte_photos, name, phone)
    await ActionsDbManager.add('search_by_photo', datetime.datetime.now(), loop)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id).startswith('wait_for_photo_'), content_types=['photo', 'file', 'text'])
async def wait_for_photo(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if message.photo is None or len(message.photo) == 0:
        if user.language == 'ru':
            text = msg.incorrect_photo_ru
        elif user.language == 'uk':
            text = msg.incorrect_photo_ukr
        else:
            text = msg.incorrect_photo_en

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    data = await UsersDbManager.get_context(tel_id, loop)
    data = data[15:]
    data_reuse = data
    data = data.split('|')

    if len(data) >= 10:
        if user.language == 'ru':
            text = msg.too_many_photos_ru
        elif user.language == 'uk':
            text = msg.too_many_photos_ukr
        else:
            text = msg.too_many_photos_en

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    biggest_photo = message.photo[-1]

    context = 'wait_for_photo_' + data_reuse + '|{0}'.format(biggest_photo.file_id)

    if user.language == 'ru':
        text = msg.photo_loaded_ru
        keyboard = mk.more_photo_ru
    elif user.language == 'uk':
        text = msg.photo_loaded_ukr
        keyboard = mk.more_photo_ukr
    else:
        text = msg.photo_loaded_en
        keyboard = mk.more_photo_en

    await UsersDbManager.update_context(tel_id, context, loop)
    print(context)
    await bot.send_message(tel_id, text, disable_notification=True, reply_markup=keyboard)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id).startswith('wait_phone_photo'), content_types=['contact', 'text'])
async def wait_phone_photo(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if (message.text is None or len(message.text) < 10 or any(
            c.isalpha() for c in message.text)) and message.contact is None:
        if user.language == 'ru':
            text = msg.incorrect_ru
        elif user.language == 'uk':
            text = msg.incorrect_ukr
        else:
            text = msg.incorrect_en

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    if message.contact is not None:
        phone = message.contact.phone_number
    else:
        phone = message.text

    if user.language == 'ru':
        text = msg.enter_photos_ru
        keyboard = mk.more_photo_ru
    elif user.language == 'uk':
        text = msg.enter_photos_ukr
        keyboard = mk.more_photo_ukr
    else:
        text = msg.enter_mobile_en
        keyboard = mk.more_photo_en

    context = 'wait_for_photo_{0}'.format(phone)
    await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)
    await UsersDbManager.update_context(tel_id, context, loop)


@dp.message_handler(lambda message: UsersDbManager.sync_get_context(message.chat.id) == 'wait_model_name')
async def wait_for_model_name(message):
    tel_id = message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)

    if message.text is None or message.text == '' or len(message.text) < 4:
        if user.language == 'ru':
            text = msg.incorrect_ru
        elif user.language == 'uk':
            text = msg.incorrect_ukr
        else:
            text = msg.incorrect_en

        await bot.send_message(tel_id, text, disable_notification=True)
        return

    model_name = message.text
    search_result = await api.search_by_model(model_name, user.language)
    await ActionsDbManager.add('search_by_model', datetime.datetime.now(), loop)

    if search_result is None:
        await bot.send_message(tel_id, msg.error_request, disable_notification=True)
        return
    print(search_result['type'])
    print(search_result)
    if search_result['type'] == '1':
        item = search_result['data']['products'][0]

        text = await get_item_description(item, user.language, loop)
        keyboard = mk.go_to_site_keyboard(item['url'], user.language)
        await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True, parse_mode='HTML')
    elif search_result['type'] == '2':
        appliance_types = search_result['data']
        keyboard = mk.appliance_type_secification(appliance_types, model_name)

        if user.language == 'ru':
            text = msg.what_appliance_type_ru
        elif user.language == 'uk':
            text = msg.what_appliance_type_ukr
        else:
            text = msg.what_appliance_type_en

        await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)
    elif search_result['type'] == '4':
        keyboard = mk.spare_part_specification(model_name, search_result['data']['categories'])
        if user.language == 'ru':
            text = msg.сhoose_appliance_group_ru
        elif user.language == 'uk':
            text = msg.сhoose_appliance_group_ukr
        else:
            text = msg.сhoose_appliance_group_en
        await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)
    elif search_result['type'] == '5':
        if user.language == 'ru':
            text = msg.searching_results_ru
        elif user.language == 'uk':
            text = msg.searching_results_ukr
        else:
            text = msg.searching_results_en

        keyboard = mk.get_pagination_markup_by_model(model_name, 0, search_result['data'], user.language)
        await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)
    elif search_result['type'] == '6':
        if user.language == 'ru':
            text = msg.nothing_found_model_ru.format(message.text)
        elif user.language == 'uk':
            text = msg.nothing_found_model_ukr.format(message.text)
        else:
            text = msg.nothing_found_model_en.format(message.text)
        await bot.send_message(tel_id, text, disable_notification=True)


@dp.callback_query_handler(lambda call: call.data.startswith('specify_appliance_'))
async def specify_appliance(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    data = call.data[18:]
    data = data.split('|')
    model_name = data[0]
    appliance_id = data[1]

    search_result = await api.search_by_model(model_name, user.language, selected_category=appliance_id)
    print(search_result)

    if search_result['type'] == '1':
        item = search_result['data']['products'][0]

        text = await get_item_description(item, user.language, loop)
        keyboard = mk.go_to_site_keyboard(item['url'], user.language)
        await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True, parse_mode='HTML')

    elif search_result['type'] == '3':
        await bot.send_message(tel_id, '❌ Error')

    elif search_result['type'] == '4':
        keyboard = mk.spare_part_specification(model_name, search_result['data']['categories'])
        if user.language == 'ru':
            text = msg.сhoose_appliance_group_ru
        elif user.language == 'uk':
            text = msg.сhoose_appliance_group_ukr
        else:
            text = msg.сhoose_appliance_group_en
        try:
            await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
        except exceptions.MessageNotModified:
            print('Message is not modified')

    elif search_result['type'] == '5':
        if user.language == 'ru':
            text = msg.searching_results_ru
        elif user.language == 'uk':
            text = msg.searching_results_ukr
        else:
            text = msg.searching_results_en

        keyboard = mk.get_pagination_markup_by_model(model_name, appliance_id, search_result['data'], user.language)
        try:
            await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
        except exceptions.MessageNotModified:
            print('Message is not modified')
    await UsersDbManager.update_context(tel_id, '0', loop)


@dp.callback_query_handler(lambda call: call.data.startswith('itemspare_'))
async def itemspare(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    model_name = call.data[10:]

    search_results = await api.search_by_model(model_name, user.language)
    print(search_results)

    if search_results['type'] == '1':
        item = search_results['data']['products'][0]

        text = await get_item_description(item, user.language, loop)
        keyboard = mk.go_to_site_keyboard(item['url'], user.language)
        try:
            await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True, parse_mode='HTML')
        except exceptions.MessageNotModified:
            print('Message is not modified')
        return
    if search_results['type'] == '2':
        appliance_types = search_results['data']
        keyboard = mk.appliance_type_secification(appliance_types, model_name)

        if user.language == 'ru':
            text = msg.what_appliance_type_ru
        elif user.language == 'uk':
            text = msg.what_appliance_type_ukr
        else:
            text = msg.what_appliance_type_en

        try:
            await bot.send_message(tel_id, text, reply_markup=keyboard, disable_notification=True)
        except exceptions.MessageNotModified:
            print('Message is not modified')
            return

    keyboard = mk.spare_part_specification(model_name, search_results['data']['categories'])
    if user.language == 'ru':
        text = msg.сhoose_appliance_group_ru
    elif user.language == 'uk':
        text = msg.сhoose_appliance_group_ukr
    else:
        text = msg.сhoose_appliance_group_en
    try:
        await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
    except exceptions.MessageNotModified:
        print('Message is not modified')


@dp.callback_query_handler(lambda call: call.data.startswith('more_models_'))
async def more_models(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    data = call.data[12:]
    data = data.split('|')
    model_name = data[0]
    appliance_id = data[1]
    models_viewed = int(data[2])

    search_results = await api.search_by_model(model_name, user.language, selected_category=appliance_id)
    if search_results['type'] != '5':
        try:
            await bot.edit_message_text('❌ Error', tel_id, call.message.message_id)
        except exceptions.MessageNotModified:
            print('Message is not modified')

    keyboard = mk.get_pagination_markup_by_model(model_name, appliance_id, search_results['data'], user.language,
                                                 models_viewed)
    if user.language == 'ru':
        text = msg.searching_results_ru
    elif user.language == 'uk':
        text = msg.searching_results_ukr
    else:
        text = msg.searching_results_en

    try:
        await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
    except exceptions.MessageNotModified:
        print('Message is not modified')


@dp.callback_query_handler(lambda call: call.data.startswith('specify_spare_part_'))
async def specify_spare_part(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    data = call.data[19:]
    data = data.split('|')
    model_search = data[0]
    sub_category_id = data[1]

    search_results = await api.search_by_model(model_search, user.language)

    if search_results['type'] == '2':
        appliance_types = search_results['data']
        keyboard = mk.appliance_type_secification(appliance_types, model_search)
        print('Test')
        if user.language == 'ru':
            text = msg.what_appliance_type_ru
        elif user.language == 'uk':
            text = msg.what_appliance_type_ukr
        else:
            text = msg.what_appliance_type_en

        try:
            await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
        except exceptions.MessageNotModified:
            print('Message is not modified')
        return

    if search_results['type'] != '4':
        try:
            await bot.edit_message_text('❌ Error', tel_id, call.message.message_id)
        except exceptions.MessageNotModified:
            print('Message is not modified')

    items_in_category = []
    print(search_results)

    if type(search_results['data']['products']['products']) is dict:
        all_items = search_results['data']['products']['products'].values()
    else:
        all_items = search_results['data']['products']['products']

    for item in all_items:
        if item['category_id'] == int(sub_category_id):
            items_in_category.append(item)

    keyboard = mk.show_results_by_model(user.language, model_search, sub_category_id)
    if user.language == 'ru':
        text = msg.finded_ru.format(len(items_in_category))
    elif user.language == 'uk':
        text = msg.finded_ukr.format(len(items_in_category))
    else:
        text = msg.finded_en.format(len(items_in_category))

    await UsersDbManager.update_context(tel_id, '0', loop)

    try:
        await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
    except exceptions.MessageNotModified:
        print('Message is not modified')


@dp.callback_query_handler(lambda call: call.data.startswith('more_parts_'))
async def more_parts(call):
    tel_id = call.message.chat.id
    user = await UsersDbManager.get_user(tel_id, loop)
    data = call.data[11:]
    data = data.split('|')
    model_search = data[0]
    sub_category_id = data[1]
    models_viewed = int(data[2])

    search_results = await api.search_by_model(model_search, user.language)

    items_in_category = []

    if type(search_results['data']['products']['products']) is dict:
        all_items = search_results['data']['products']['products'].values()
    else:
        all_items = search_results['data']['products']['products']

    for item in all_items:
        if item['category_id'] == int(sub_category_id):
            items_in_category.append(item)

    keyboard = mk.get_pagination_markup_by_spare_parts(model_search, sub_category_id, items_in_category, user.language,
                                                       current_pos=models_viewed)

    if user.language == 'ru':
        text = msg.searching_results_ru
    elif user.language == 'uk':
        text = msg.searching_results_ukr
    else:
        text = msg.searching_results_en

    try:
        await bot.edit_message_text(text, tel_id, call.message.message_id, reply_markup=keyboard)
    except exceptions.MessageNotModified:
        print('Message is not modified')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

'''file_ids = data[17:]
    file_ids = file_ids.split('|')

    byte_photos = []
    for file_id in file_ids:
        downloaded = await bot.download_file_by_id(file_id)
        byte_photos.append(downloaded)

    name = '{0} {1}'.format(message.from_user.first_name, message.from_user.last_name)
    await send_photo(byte_photos, name, phone)
    await ActionsDbManager.add('search_by_photo', datetime.datetime.now(), loop)'''