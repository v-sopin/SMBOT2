import datetime
from scripts.db_manager import ActionsDbManager


def get_order_text(order_num, order_json, language):
    try:
        status = order_json['status']
    except KeyError:
        status = None
    try:
        paid = order_json['paid']
    except KeyError:
        paid = None
    try:
        date_create = order_json['date_create']
    except KeyError:
        date_create = None
    try:
        address = order_json['address']
    except KeyError:
        address = None
    try:
        delivery_method = order_json['delivery_method']
    except KeyError:
        delivery_method = None
    try:
        ttn = order_json['ttn']
    except KeyError:
        ttn = None
    try:
        price = order_json['price']
    except KeyError:
        price = None
    try:
        currency = order_json['currency']
    except KeyError:
        currency = None

    if language == 'ru':
        header_text = 'Информация по заказу'
        status_text = 'Статус заказа'
        paid_text = 'Статус оплаты'
        date_create_text = 'Дата заказа'
        address_text = 'Адрес доставки'
        delivery_method_text = 'Способ доставки'
        ttn_text = 'ТТН'
        price_text = 'Сумма'
        paid_yes = 'Оплачено'
        paid_no = 'Не оплачено'
    elif language == 'uk':
        header_text = 'Інформація для замовлення'
        status_text = 'Статус замовлення'
        paid_text = 'Статус оплати'
        date_create_text = 'Дата замовлення'
        address_text = 'Адреса доставки'
        delivery_method_text = 'Спосіб доставки'
        ttn_text = 'ТТН'
        price_text = 'Сумма'
        paid_yes = 'Оплачено'
        paid_no = 'Не оплачено'
    else:
        header_text = 'Information about order'
        status_text = 'Order status'
        paid_text = 'Payment status'
        date_create_text = 'Order date'
        address_text = 'Delivery address'
        delivery_method_text = 'Delivery method'
        ttn_text = 'TTN'
        price_text = 'Price'
        paid_yes = 'Paid'
        paid_no = 'Not paid'

    text = '''*{0} {1}*

    '''.format(header_text, order_num)

    if status is not None:
        text += '''{0}: *{1}*
    '''.format(status_text, status)
    if paid is not None:
        if paid:
            text += '''{0}: *{1}*
    '''.format(paid_text, paid_yes)
        elif not paid:
            text += '''{0}: *{1}*
    '''.format(paid_text, paid_no)
    if date_create is not None:
        text += '''{0}: *{1}*
    '''.format(date_create_text, date_create)
    if address is not None:
        text += '''{0}: *{1}*
    '''.format(address_text, address)
    if delivery_method is not None:
        text += '''{0}: *{1}*
    '''.format(delivery_method_text, delivery_method)
    if ttn is not None:
        text += '''{0}: [{1}](https://novaposhta.ua/ru/tracking/?cargo_number={2})
    '''.format(ttn_text, ttn, ttn)
    if price is not None and currency is not None:
        text += '''{0}: *{1} {2}*
    '''.format(price_text, price, currency)

    return text


async def get_item_description(item, language, loop):
    description = item['description'].replace('\n', '')
    name = item['name']
    price = item['price']
    stock = item['stock']
    image_url = item['image']

    try:
        status = item['status']
    except KeyError:
        status = None

    if language == 'ru':
        cur = 'грн'
        status_text = 'Статус'
        price_text = 'Цена'
        in_stock = 'В наличии'
        description_text = 'Описание'
        if stock > 20:
            stock = 'более 20-ти'
    elif language == 'uk':
        cur = 'грн'
        status_text = 'Статус'
        price_text = 'Ціна'
        in_stock = 'В наявності'
        description_text = 'Опис'
        if stock > 20:
            stock = 'більше 20-ти'
    else:
        cur = 'uah'
        status_text = 'Status'
        price_text = 'Price'
        in_stock = 'Avalible'
        description_text = 'Description'
        if stock > 20:
            stock = 'more than 20'

    if len(description) > 500:
        description = description[:500] + '...'

    text = '''<b>{0}</b>

<i>{1}</i>: {2}

{3}: <b>{4}</b> {5}

{6}: <b>{7}</b>
'''.format(name, description_text, description, price_text, price, cur, in_stock, stock)

    if status != None:
        text += '''{0}: <b>{1}</b>'''.format(status_text, status)

    if image_url != 'https://www.service-market.com.ua/uploads/shop/products/../nophoto/nophoto.jpg':
        text += '''<a href="{0}">Photo</a>'''.format(image_url)

    await ActionsDbManager.add('item_description', datetime.datetime.now(), loop)
    return text


def stats_text(actions):
    new_users = 0
    users_lost = 0
    users_returned = 0

    searched_by_photo = 0
    searched_by_product_code = 0
    searched_by_article = 0
    searched_by_model = 0

    item_description_views = 0

    for action in actions:
        if action.type == 'new_user':
            new_users += 1
        elif action.type == 'user_lost':
            users_lost += 1
        elif action.type == 'user_returned':
            users_returned += 1
        elif action.type == 'search_by_photo':
            searched_by_photo += 1
        elif action.type == 'search_by_product_code':
            searched_by_product_code += 1
        elif action.type == 'search_by_article':
            searched_by_article += 1
        elif action.type == 'search_by_model':
            searched_by_model += 1
        elif action.type == 'item_description':
            item_description_views += 1

    text = '''
👤 Новых пользователей - {0}
❌ Ушло пользователей - {1}
🚶‍♂️ Вернулись - {2}

Поиск по фото {3} раз

Поиск по артикулу и названию {4} раз

Поиск по коду товара {5} раз

Поиск по модели {6} раз

Карточек товара просмотрено {7}'''.format(new_users, users_lost, users_returned, searched_by_photo, searched_by_article,
                                          searched_by_product_code, searched_by_model, item_description_views)

    return text
