import aiomysql
from pymysql import connect
from scripts.config import DB_NAME, DB_USER, DB_HOST, DB_PASSWORD
from scripts.models import User, Action


async def create_con(loop):
    con = await aiomysql.connect(host=DB_HOST, user=DB_USER, db=DB_NAME, password=DB_PASSWORD, loop=loop)
    cur = await con.cursor()
    return con, cur


def create_sync_con():
    con = connect(host=DB_HOST, user=DB_USER, db=DB_NAME,
                  password=DB_PASSWORD)
    cur = con.cursor()

    return con, cur


class UsersDbManager:
    @staticmethod
    def clear():
        con, cur = create_sync_con()
        cur.execute('delete from users')
        con.commit()
        con.close()

    @staticmethod
    async def user_exist(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute('select count(*) from users where tel_id = %s', tel_id)
        r = await cur.fetchone()
        count = r[0]
        return count > 0

    @staticmethod
    async def add_user(tel_id, username, lang, loop):
        con, cur = await create_con(loop)
        await cur.execute('insert into users values(%s, %s, %s, %s, %s, %s)', (tel_id, username, lang, '0', True, '0'))
        await con.commit()
        con.close()

    @staticmethod
    async def get_user(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute('select * from users where tel_id = %s', (tel_id))
        user = await cur.fetchone()
        con.close()

        if user is None:
            return None

        return User(user[0], user[1], user[2], user[3], user[4], user[5])

    @staticmethod
    async def update_language(tel_id, new_language, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set language = %s where tel_id = %s', (new_language, tel_id))
        await con.commit()
        con.close()

    @staticmethod
    async def update_is_using(tel_id, new_status, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set is_using = %s where tel_id = %s', (new_status, tel_id))
        await con.commit()
        con.close()

    @staticmethod
    async def update_context(tel_id, context, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set context = %s where tel_id = %s', (context, tel_id))
        await con.commit()
        con.close()

    @staticmethod
    async def update_phone(tel_id, new_phone, loop):
        con, cur = await create_con(loop)
        await cur.execute('update users set phone = %s where tel_id = %s', (new_phone, tel_id))
        await con.commit()
        con.close()

    @staticmethod
    async def get_context(tel_id, loop):
        con, cur = await create_con(loop)
        await cur.execute('select context from users where tel_id = {0}'.format(tel_id))
        context = await cur.fetchone()
        con.close()
        return context[0]

    @staticmethod
    def sync_get_context(tel_id):
        con, cur = create_sync_con()
        cur.execute('select context from users where tel_id = {0}'.format(tel_id))
        context = cur.fetchone()
        con.close()

        if context is None:
            return None

        return context[0]

    @staticmethod
    async def get_all_users(loop):
        con, cur = await create_con(loop)
        await cur.execute('select * from users')
        users = await cur.fetchall()
        con.close()

        result = []
        for user in users:
            result.append(User(user[0], user[1], user[2], user[3], user[4], user[5]))
        return result

# search_by_photo
# search_by_product_code
# search_by_article
# search_by_model
# new_user
# user_returned
# user_lost
# item_description


class ActionsDbManager:
    @staticmethod
    async def add(type, date, loop):
        con, cur = await create_con(loop)
        await cur.execute('insert into actions values(%s, %s)', (type, date))
        await con.commit()
        con.close()

    @staticmethod
    async def get_actions_beside_dates(date_first, date_second, loop):
        date_first = date_first.strftime('%Y-%m-%d %H:%M:%S')
        date_second = date_second.strftime('%Y-%m-%d %H:%M:%S')

        con, cur = await create_con(loop)
        await cur.execute('select * from actions where date > %s and date < %s', (date_first, date_second))
        actions = await cur.fetchall()
        con.close()

        result = []
        for action in actions:
            result.append(Action(action[0], action[1]))
        return result

