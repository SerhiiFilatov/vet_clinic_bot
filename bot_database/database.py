import asyncpg
import uuid

class Database:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.pool = connector

    async def check_time_exists(self, time, date):
        query = 'SELECT EXISTS(SELECT 1 FROM making_an_appointment WHERE time = $1 AND date = $2)'
        result = await self.pool.fetchval(query, time, date)
        return result

    async def get_time(self, date):
        query = 'SELECT time FROM making_an_appointment WHERE date = $1'
        result = await self.pool.fetch(query, date)
        times = [row['time'] for row in result]
        return times

    async def add_info(self, user_id, pet, date, time, problem):
        await self.pool.execute('INSERT INTO making_an_appointment (user_id, pet, date, time, problem) '
                                'VALUES($1, $2, $3, $4, $5)', user_id, pet, date, time, problem)

    async def add_info_doc_call(self, user_id, pet, date, time, problem, adress, phone_number):
        await self.pool.execute('INSERT INTO doctors_call (user_id, pet, date, time, problem, adress, phone_number) '
                                'VALUES($1, $2, $3, $4, $5, $6, $7)',
                                user_id, pet, date, time, problem, adress, phone_number)

    async def get_categories(self):
        query = 'SELECT id, title FROM product_category'
        result = await self.pool.fetch(query)
        titles = [record['title'] for record in result]
        return titles

    async def get_items(self, categories):
        query = 'SELECT id, title FROM product_list WHERE category = $1'
        result = await self.pool.fetch(query, categories)
        titles = [(record['id'], record['title']) for record in result]
        return titles

    async def add_order(self, user_id, title, price, quantity, status):
        await self.pool.execute('INSERT INTO product_orders (user_id, title, price, quantity, status) '
                                'VALUES($1, $2, $3, $4, $5)', user_id, title, price, quantity, status)

    async def get_order_info(self, user_id):
        query = 'SELECT * FROM product_orders WHERE user_id = $1 AND status = 1'
        result = await self.pool.fetch(query, user_id)
        order_info = [(record['id'], record['title'], record['price'], record['quantity']) for record in result]
        return order_info

    async def update_change_quantity(self, order_quantity, item_id):
        await self.pool.execute('UPDATE product_list SET quantity = quantity - $1  WHERE id=$2',
                                order_quantity, item_id)

    async def get_find_medicine(self, title):
        query = 'SELECT * FROM product_list WHERE title = $1'
        result = await self.pool.fetchrow(query, title)
        return result

    async def get_info_about_item(self, item_id):
        query = 'SELECT * FROM product_list WHERE id = $1'
        result = await self.pool.fetchrow(query, item_id)
        return result

