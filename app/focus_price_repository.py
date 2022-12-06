from app.database import get_cursor


class FocusPriceRepository:
    @staticmethod
    def get_prices_for_guild(guild_id: str):
        with get_cursor() as cursor:
            select_query = """
                SELECT user_id, focus_price
                FROM focus_price
                WHERE guild_id = %s;
            """
            item_tuple = (guild_id,)
            cursor.execute(select_query, item_tuple)
            rows = cursor.fetchall()

            dict_result = []
            for user_id, focus_price in rows:
                dict_result.append(dict(user_id=user_id, focus_price=focus_price))
            return dict_result

    @staticmethod
    def set_prices_for_guild(guild_id: str, user_id: str, focus_price: float):
        with get_cursor() as cursor:
            select_query = """
                INSERT INTO focus_price (guild_id, user_id, focus_price)
                VALUES(%s, %s, %s)
                ON CONFLICT (guild_id, user_id)
                DO UPDATE SET focus_price = %s; """
            item_tuple = (guild_id, user_id, focus_price, focus_price)
            cursor.execute(select_query, item_tuple)
