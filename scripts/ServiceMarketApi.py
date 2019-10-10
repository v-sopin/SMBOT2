import aiohttp
import asyncio
import json

UKRANIAN = 'uk'
RUSSIAN = 'ru'
ENGLISH = 'en'


async def get_categories(language):
    if language == RUSSIAN:
        URL = 'https://www.service-market.com.ua/bot_telegram/init/categories'
    elif language == UKRANIAN:
        URL = 'https://www.service-market.com.ua/ua/bot_telegram/init/categories'
    elif language == ENGLISH:
        URL = 'https://www.service-market.com.ua/en/bot_telegram/init/categories'
    else:
        raise Exception

    data = aiohttp.FormData({'key': '123AA'})

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.request('POST', URL, data=data) as response:
            res_dict = []
            if response.status != 200:
                return res_dict

            categories = await response.read()
            categories = json.loads(categories)
            for c in categories:
                res_dict.append(c)
            return res_dict


async def get_brands(category_id, language):
    if language == RUSSIAN:
        URL = 'https://www.service-market.com.ua/bot_telegram/init/brands'
    elif language == UKRANIAN:
        URL = 'https://www.service-market.com.ua/ua/bot_telegram/init/brands'
    elif language == ENGLISH:
        URL = 'https://www.service-market.com.ua/en/bot_telegram/init/brands'
    else:
        raise Exception

    data = aiohttp.FormData({'key': '123AA', 'selectedCategory': category_id})

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.request('POST', URL, data=data) as response:
            res_dict = []
            if response.status != 200:
                return res_dict

            brands = await response.read()
            brands = json.loads(brands)
            for b in brands:
                res_dict.append(b)
            return res_dict


async def search_by_order(order_id, language):
    if language == RUSSIAN:
        URL = 'https://www.service-market.com.ua/bot_telegram/init/search_by_order'
    elif language == UKRANIAN:
        URL = 'https://www.service-market.com.ua/ua/bot_telegram/init/search_by_order'
    elif language == ENGLISH:
        URL = 'https://www.service-market.com.ua/en/bot_telegram/init/search_by_order'
    else:
        raise Exception

    data = aiohttp.FormData({'key': '123AA', 'text': order_id})

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.request('POST', URL, data=data) as response:
            order = None
            if response.status != 200:
                return order

            order = await response.read()
            order = order.decode('utf-8')
            order = json.loads(order)

            return order


async def search_orders_by_phone(phone, language):
    if language == RUSSIAN:
        URL = 'https://www.service-market.com.ua/bot_telegram/init/search_orders_by_phone'
    elif language == UKRANIAN:
        URL = 'https://www.service-market.com.ua/ua/bot_telegram/init/search_orders_by_phone'
    elif language == ENGLISH:
        URL = 'https://www.service-market.com.ua/en/bot_telegram/init/search_orders_by_phone'
    else:
        raise Exception

    data = aiohttp.FormData({'key': '123AA', 'phone': phone})

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.request('POST', URL, data=data) as response:
            orders = []
            if response.status != 200:
                return orders

            res = await response.read()
            res = json.loads(res)
            for o in res:
                orders.append(o)

            return orders


async def search_by_code(code, language):
    if language == RUSSIAN:
        URL = 'https://www.service-market.com.ua/bot_telegram/init/search_by_code'
    elif language == UKRANIAN:
        URL = 'https://www.service-market.com.ua/ua/bot_telegram/init/search_by_code'
    elif language == ENGLISH:
        URL = 'https://www.service-market.com.ua/en/bot_telegram/init/search_by_code'
    else:
        raise Exception

    data = aiohttp.FormData({'key': '123AA', 'text': code})

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.request('POST', URL, data=data) as response:
            detail = None
            print(response.status)
            if response.status != 200:
                return detail

            res = await response.read()
            print(res)
            res = json.loads(res)
            if len(res) is not 0:
                detail = res['products']

            return detail


async def search_by_number(number, language):
    if language == RUSSIAN:
        URL = 'https://www.service-market.com.ua/bot_telegram/init/search_by_number'
    elif language == UKRANIAN:
        URL = 'https://www.service-market.com.ua/ua/bot_telegram/init/search_by_number'
    elif language == ENGLISH:
        URL = 'https://www.service-market.com.ua/en/bot_telegram/init/search_by_number'
    else:
        raise Exception

    data = aiohttp.FormData({'key': '123AA', 'text': number})

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.request('POST', URL, data=data) as response:
            if response.status is not 200:
                print('Error ' + response.status)
                return
            res = await response.read()
            res = json.loads(res)
            if res != []:
                return res['products']
            return []


async def search_by_model(search_model, language, selected_category=None, selected_brand=None):
    if language == RUSSIAN:
        URL = 'https://www.service-market.com.ua/bot_telegram/init/search_models'
    elif language == UKRANIAN:
        URL = 'https://www.service-market.com.ua/ua/bot_telegram/init/search_models'
    elif language == ENGLISH:
        URL = 'https://www.service-market.com.ua/en/bot_telegram/init/search_models'
    else:
        raise Exception

    data = {'key': '123AA', 'searchModel': search_model}
    if selected_category is not None:
        data.update({'selectedCategory': selected_category})
    if selected_brand is not None:
        data.update({'selectedBrand': selected_brand})

    data = aiohttp.FormData(data)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.request('POST', URL, data=data) as response:
            if response.status is not 200:
                print('Error ' + response.status)
                return
            res = await response.read()
            res = json.loads(res)
            print(res['type'])
            return res

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(search_by_model('bm900', RUSSIAN)))#, selected_category=3267) )) # 3109 3333 3426 3267