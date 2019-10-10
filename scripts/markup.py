from aiogram.types import reply_keyboard, inline_keyboard
main_menu_ru = reply_keyboard.ReplyKeyboardMarkup([['🔎 Найти деталь', '🚚 Проверить статус заказа'],
                                                   ['🖊 Вопросы и ответы', 'Сменить язык 🇷🇺']])
main_menu_uk = reply_keyboard.ReplyKeyboardMarkup([['🔎 Знайти деталь', '🚚 Статус замовлення'],
                                                   ['🖊 Питання і відповіді', 'Змінити мову 🇺🇦']])
main_menu_en = reply_keyboard.ReplyKeyboardMarkup([['🔎 Find spare part', '🚚 Check order status'],
                                                   ['🖊 FAQ', 'Change language 🇬🇧']])

admin_menu = reply_keyboard.ReplyKeyboardMarkup([['📩 Сделать рассылку', '📊 Статистика'],
                                                 ['⬅️ Назад']])

more_photo_ru = reply_keyboard.ReplyKeyboardMarkup([['📩 Отправить'],
                                                   ['❌ Отмена']])
more_photo_ukr = reply_keyboard.ReplyKeyboardMarkup([['📩 Відправити'],
                                                   ['❌ Скасувати']])
more_photo_en = reply_keyboard.ReplyKeyboardMarkup([['📩 Submit'],
                                                   ['❌ Cancel']])


language_keyboard = reply_keyboard.ReplyKeyboardMarkup([['Русский 🇷🇺'],
                                                        ['Українська 🇺🇦'],
                                                        ['English 🇬🇧']])
find_detail_keyboard_ru = reply_keyboard.ReplyKeyboardMarkup([['Поиск по модели'],
                                                        ['Найти по названию'],
                                                        ['Поиск по фото (пересылка менеджеру)'],
                                                        ['Найти по артикулу'],
                                                        ['Найти по коду товара'],
                                                        ['⬅️ Назад']])
find_detail_keyboard_ukr = reply_keyboard.ReplyKeyboardMarkup([['Пошук по моделі'],
                                                        ['Знайти за назвою'],
                                                        ['Пошук по фото (пересилання менеджеру)'],
                                                        ['Знайти по артикулу'],
                                                        ['Знайти за кодом товару'],
                                                        ['⬅️ Назад']])
find_detail_keyboard_en = reply_keyboard.ReplyKeyboardMarkup([['Search by model'],
                                                        ['Search by name'],
                                                        ['Photo search (send to manager)'],
                                                        ['Find by stock number'],
                                                        ['Find by product code'],
                                                        ['⬅️ Back']])

faq_keyboard_ru = reply_keyboard.ReplyKeyboardMarkup([['⬅️ Назад'],
                                                      ['Контакты'],
                                                      ['Где найти модель техники?'],
                                                      ['Какие способы доставки?'],
                                                      ['Какие способы оплаты?'],
                                                      ['Как стать оптовым клиентом?'],
                                                      ['Как вернуть или поменять товар?']])

faq_keyboard_ukr = reply_keyboard.ReplyKeyboardMarkup([['⬅️ Назад'],
                                                       ['Контакти'],
                                                       ['Де знайти модель техніки?'],
                                                       ['Які є способи доставки?'],
                                                       ['Які є способи оплати?'],
                                                       ['Як стати оптовим клієнтом?'],
                                                       ['Як повернути або замінити товар?']])

faq_keyboard_en = reply_keyboard.ReplyKeyboardMarkup([['⬅️ Back'],
                                                      ['Contacts'],
                                                      ['Where I can find model number'],
                                                      ['Delivery'],
                                                      ['Payment'],
                                                      ['How to become a wholesale customer?'],
                                                      ['How to return or exchange an item?']])

share_contact_button_ru = reply_keyboard.KeyboardButton('👤 Поделиться контактом', request_contact=True)
share_contact_button_ukr = reply_keyboard.KeyboardButton('👤 Поділитися контактом', request_contact=True)
share_contact_button_en = reply_keyboard.KeyboardButton('👤 Share contact', request_contact=True)
share_contact_ru = reply_keyboard.ReplyKeyboardMarkup([[share_contact_button_ru],
                                                       ['⬅️ Назад']])
share_contact_ukr = reply_keyboard.ReplyKeyboardMarkup([[share_contact_button_ukr],
                                                       ['⬅️ Назад']])
share_contact_en = reply_keyboard.ReplyKeyboardMarkup([[share_contact_button_en],
                                                       ['⬅️ Back']])


def get_order_method(language):
    if language == 'ru':
        by_phone = 'По номеру телефона'
        by_number = 'По номеру заказа'
    elif language == 'uk':
        by_phone = 'За номером телефону'
        by_number = 'За номером замовлення'
    else:
        by_phone = 'By phone number'
        by_number = 'By order number'

    k = inline_keyboard.InlineKeyboardMarkup()
    k.add(inline_keyboard.InlineKeyboardButton(by_phone, callback_data='orders_by_phone'))
    k.add(inline_keyboard.InlineKeyboardButton(by_number, callback_data='orders_by_number'))
    return k


def go_to_site_keyboard(url, language):
    if language == 'ru':
        text = '🛒 Заказать на сайте'
    elif language == 'uk':
        text = '🛒 Замовити на сайті'
    else:
        text = '🛒 Make an order'

    url = url + '?utm_source=telegram&utm_medium=telegram_bot'

    k = inline_keyboard.InlineKeyboardMarkup()
    k.add(inline_keyboard.InlineKeyboardButton(text, url=url))
    return k


def get_yes_no_phone(language):
    if language == 'ru':
        yes = 'Да'
        change = 'Нет'
    elif language == 'uk':
        yes = 'Так'
        change = 'Ні'
    else:
        yes = 'Yes'
        change = 'No'

    k = inline_keyboard.InlineKeyboardMarkup()
    k.add(inline_keyboard.InlineKeyboardButton(yes, callback_data='my_phone'))
    k.add(inline_keyboard.InlineKeyboardButton(change, callback_data='change_number'))
    return k


def orders_by_phone(orders, phone, language, current_pos=0):
    k = inline_keyboard.InlineKeyboardMarkup()
    counter = 1
    for order in orders:
        k.add(inline_keyboard.InlineKeyboardButton(order, callback_data='order_{0}'.format(order)))
        if counter == current_pos+5:
            break
        counter += 1

    if language == 'ru':
        more = 'Показать еще ⬇️'
    elif language == 'uk':
        more = 'Показати ще ⬇️'
    else:
        more = 'Show more ⬇️'

    if len(orders) > current_pos + 5:
        call_data_more = 'more_orders_{0}|{1}'.format(phone, current_pos + 5)
        k.add(inline_keyboard.InlineKeyboardButton(more, callback_data=call_data_more))

    return k


def back_to_orders(language):
    if language == 'ru':
        text = '⬅️ Назад'
    elif language == 'uk':
        text = '⬅️ Назад'
    else:
        text = '⬅️ Back'

    k = inline_keyboard.InlineKeyboardMarkup()
    k.add(inline_keyboard.InlineKeyboardButton(text, callback_data='back_to_orders'))
    return k


def get_catalog_by_article(article, items, language):
    if language == 'ru':
        next = 'Вперед ➡️'
    elif language == 'uk':
        next = 'Вперед ➡️'
    else:
        next = 'Forward ➡️'

    k = inline_keyboard.InlineKeyboardMarkup()

    position = 0
    if position+5 > len(items):
        end = len(items)
    else:
        end = position + 5

    for i in range(position, end):
        item = items[i]
        text = item['number']
        call_data = 'item_{0}'.format(item['code'])
        k.add(inline_keyboard.InlineKeyboardButton(text, callback_data=call_data))

    if len(items) > end:
        next_data = 'next|{0}|{1}'.format(article, end)
        k.add(inline_keyboard.InlineKeyboardButton(next, callback_data=next_data))
    return k


def get_next_page(article, cur_pos, items, language):
    if language == 'ru':
        next = 'Вперед ➡️'
        pervious = '⬅️ Назад'
    elif language == 'uk':
        next = 'Вперед ➡️'
        pervious = '⬅️ Назад'
    else:
        next = 'Forward ➡️'
        pervious = '⬅️ Назад'

    if cur_pos+5 > len(items):
        end = len(items)
    else:
        end = cur_pos + 5

    k = inline_keyboard.InlineKeyboardMarkup()
    for i in range(cur_pos, end):
        item = items[i]
        text = item['number']
        call_data = 'item_{0}'.format(item['code'])
        k.add(inline_keyboard.InlineKeyboardButton(text, callback_data=call_data))

    back_data = 'back|{0}|{1}'.format(article, end)
    if len(items) > end:
        next_data = 'next|{0}|{1}'.format(article, end)
        k.add(inline_keyboard.InlineKeyboardButton(pervious, callback_data=back_data), inline_keyboard.InlineKeyboardButton(next, callback_data=next_data))
    else:
        k.add(inline_keyboard.InlineKeyboardButton(pervious, callback_data=back_data))

    return k


def get_pervious_page(article, cur_pos, items, language):
    if language == 'ru':
        next = 'Вперед ➡️'
        pervious = '⬅️ Назад'
    elif language == 'uk':
        next = 'Вперед ➡️'
        pervious = '⬅️ Назад'
    else:
        next = 'Forward ➡️'
        pervious = '⬅️ Назад'

    if cur_pos - 10 > 0:
        start = cur_pos-10
    else:
        start = 0
    end = cur_pos - 5

    k = inline_keyboard.InlineKeyboardMarkup()
    for i in range(start, end):
        item = items[i]
        text = item['number']
        call_data = 'item_{0}'.format(item['code'])
        k.add(inline_keyboard.InlineKeyboardButton(text, callback_data=call_data))

    next_data = 'next|{0}|{1}'.format(article, end)
    back_data = 'back|{0}|{1}'.format(article, end)
    if cur_pos - 10 > 0:
        k.add(inline_keyboard.InlineKeyboardButton(pervious, callback_data=back_data), inline_keyboard.InlineKeyboardButton(next, callback_data=next_data))
    else:
        k.add(inline_keyboard.InlineKeyboardButton(next, callback_data=next_data))

    return k


def appliance_type_secification(appliance_types, model_name):
    k = inline_keyboard.InlineKeyboardMarkup()

    for at in appliance_types.values():
        k.add(inline_keyboard.InlineKeyboardButton(at['name'], callback_data='specify_appliance_{0}|{1}'.format(model_name, at['id'])))
    return k


def get_pagination_markup_by_model(model_search, appliance_id, models, language, current_pos=0):
    k = inline_keyboard.InlineKeyboardMarkup()
    counter = 0
    for m in models.values():
        text = m['name']
        call_data = 'itemspare_{0}'.format(m['name'])
        k.add(inline_keyboard.InlineKeyboardButton(text, callback_data=call_data))
        counter+=1
        if counter == current_pos+5:
            break

    if language == 'ru':
        more = 'Показать еще ⬇️'
    elif language == 'uk':
        more = 'Показати ще ⬇️'
    else:
        more = 'Show more ⬇️'

    if len(models) > current_pos+5:
        call_data_more = 'more_models_{0}|{1}|{2}'.format(model_search, appliance_id, current_pos+5)
        k.add(inline_keyboard.InlineKeyboardButton(more, callback_data=call_data_more))
    return k


def spare_part_specification(model_search, specifications):
    k = inline_keyboard.InlineKeyboardMarkup()

    for at in specifications.values():
        k.add(inline_keyboard.InlineKeyboardButton(at['name'],
                                                   callback_data='specify_spare_part_{0}|{1}'.format(model_search, at['id'])))
    return k


def get_pagination_markup_by_spare_parts(model_search, category_spec_id, models, language, current_pos=0):
    k = inline_keyboard.InlineKeyboardMarkup()
    counter = 0
    for m in models:
        text = m['name']
        call_data = 'item_{0}'.format(m['code'])
        k.add(inline_keyboard.InlineKeyboardButton(text, callback_data=call_data))
        counter+=1
        if counter == current_pos+5:
            break

    if language == 'ru':
        more = 'Показать еще ⬇️'
    elif language == 'uk':
        more = 'Показати ще ⬇️'
    else:
        more = 'Show more ⬇️'

    if len(models) > current_pos+5:
        call_data_more = 'more_parts_{0}|{1}|{2}'.format(model_search, category_spec_id, current_pos+5)
        k.add(inline_keyboard.InlineKeyboardButton(more, callback_data=call_data_more))
    return k


def stats_keyboard():
    k = inline_keyboard.InlineKeyboardMarkup()
    k.add(inline_keyboard.InlineKeyboardButton('За последние сутки', callback_data='stats_1'))
    k.add(inline_keyboard.InlineKeyboardButton('За последнюю неделю', callback_data='stats_7'))
    k.add(inline_keyboard.InlineKeyboardButton('За последний месяц', callback_data='stats_30'))
    return k


def show_results_by_article(language, parameter):
    k = inline_keyboard.InlineKeyboardMarkup()
    if language == 'ru':
        text = 'Показать'
    elif language == 'uk':
        text = 'Показати'
    else:
        text = 'Show'

    k.add(inline_keyboard.InlineKeyboardButton(text, switch_inline_query_current_chat='show_by_article_{0}'.format(parameter)))
    return k


def show_results_by_model(language, search_query, sub_category_id):
    k = inline_keyboard.InlineKeyboardMarkup()
    if language == 'ru':
        text = 'Показать'
    elif language == 'uk':
        text = 'Показати'
    else:
        text = 'Show'

    k.add(inline_keyboard.InlineKeyboardButton(text, switch_inline_query_current_chat='show_by_model_{0}|{1}'.format(search_query, sub_category_id)))
    return k

'''
def no_inline_results(language):
    if language == 'ru':
        text = msg.nothing_found_article_ru.format(data[0])
    elif language == 'uk':
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
'''