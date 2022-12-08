from app.database import get_cursor


class FocusPriceRepository:
    @staticmethod
    def get_prices_for_guild(guild_id: str):
        with get_cursor() as cursor:
            select_query = """
                SELECT id, user_id, focus_price, balance
                FROM focus_price
                WHERE guild_id = %s;
            """
            item_tuple = (guild_id,)
            cursor.execute(select_query, item_tuple)
            rows = cursor.fetchall()

            dict_result = []
            for obj_id, user_id, focus_price, balance in rows:
                dict_result.append(
                    dict(
                        id=obj_id,
                        user_id=user_id,
                        focus_price=focus_price,
                        balance=balance,
                    )
                )
            return dict_result

    @staticmethod
    def set_prices_for_guild(guild_id: str, user_id: str, focus_price: float):
        with get_cursor() as cursor:
            select_query = """
                INSERT INTO focus_price (guild_id, user_id, focus_price, balance)
                VALUES(%s, %s, %s, 0)
                ON CONFLICT (guild_id, user_id)
                DO UPDATE SET focus_price = %s;
            """
            item_tuple = (guild_id, user_id, focus_price, focus_price)
            cursor.execute(select_query, item_tuple)

    @staticmethod
    def get_user_balance(guild_id: str, user_id: str):
        user_focus_price = FocusPriceRepository.get_user_focus_price(guild_id, user_id)
        return user_focus_price.get("balance") if user_focus_price else 0

    @staticmethod
    def get_user_focus_price(guild_id: str, user_id: str):
        with get_cursor() as cursor:
            select_query = """
                SELECT id, user_id, focus_price, balance
                FROM focus_price
                WHERE guild_id = %s AND
                    user_id = %s;
            """
            item_tuple = (
                guild_id,
                user_id,
            )
            cursor.execute(select_query, item_tuple)
            row = cursor.fetchone()

            if row:
                return dict(
                    id=row.get("id"),
                    user_id=row.get("user_id"),
                    focus_price=row.get("focus_price"),
                    balance=row.get("balance"),
                )
            return None

    @staticmethod
    def set_user_balance(guild_id: str, user_id: str, balance: float):
        with get_cursor() as cursor:
            select_query = """
                INSERT INTO focus_price (guild_id, user_id, balance)
                VALUES(%s, %s, %s)
                ON CONFLICT (guild_id, user_id)
                DO UPDATE SET balance = %s;
            """
            item_tuple = (
                guild_id,
                user_id,
                balance,
                balance,
            )
            cursor.execute(select_query, item_tuple)
