from app.database import get_cursor


class FocusUsageRepository:
    @staticmethod
    def get_focus_usage_for_guild_by_user(guild_id):
        with get_cursor() as cursor:
            select_query = """
                SELECT user_id, SUM(focus_usage) as usage_sum
                FROM focus_usage
                WHERE guild_id = %s AND is_paid is not true GROUP BY user_id;
            """
            item_tuple = (guild_id,)
            cursor.execute(select_query, item_tuple)
            rows = cursor.fetchall()

            dict_result = []
            for user_id, usage_sum in rows:
                dict_result.append(dict(user_id=user_id, usage_sum=usage_sum))
            return dict_result

    @staticmethod
    def get_focus_usage_list(guild_id, user_id):
        with get_cursor() as cursor:
            select_query = """
                SELECT id, quantity, focus_usage, item_crafted
                FROM focus_usage
                WHERE guild_id = %s AND user_id = %s AND is_paid is not true;
            """
            item_tuple = (
                guild_id,
                user_id,
            )
            cursor.execute(select_query, item_tuple)
            rows = cursor.fetchall()

            dict_result = []
            for obj_id, quantity, focus_usage, item_crafted in rows:
                dict_result.append(
                    dict(
                        id=obj_id,
                        quantity=quantity,
                        focus_usage=focus_usage,
                        item_crafted=item_crafted,
                    )
                )
            return dict_result

    @staticmethod
    def set_user_paid(guild_id, user_id):
        with get_cursor() as cursor:
            select_query = """
                UPDATE focus_usage
                SET is_paid = true
                WHERE guild_id = %s AND
                    user_id = %s;
            """
            item_tuple = (
                guild_id,
                user_id,
            )
            cursor.execute(select_query, item_tuple)

    @staticmethod
    def create_focus_usage(
        guild_id, user_id, focus_usage: float, item_crafted: str, quantity: int
    ):
        with get_cursor() as cursor:
            select_query = """
                INSERT INTO focus_usage (guild_id, user_id, quantity, focus_usage, item_crafted)
                VALUES (%s, %s, %s, %s, %s);
            """
            item_tuple = (
                guild_id,
                user_id,
                quantity,
                focus_usage,
                item_crafted,
            )
            cursor.execute(select_query, item_tuple)

    @staticmethod
    def edit_focus_usage(
        guild_id,
        user_id,
        obj_id: int,
        focus_usage: float,
        item_crafted: str,
        quantity: int,
    ):
        with get_cursor() as cursor:
            select_query = """
                UPDATE focus_usage
                SET focus_usage = %s,
                item_crafted = %s,
                quantity = %s
                WHERE guild_id = %s AND
                    user_id = %s AND
                    id = %s AND
                    is_paid = false
            """
            item_tuple = (
                focus_usage,
                item_crafted,
                quantity,
                guild_id,
                user_id,
                obj_id,
            )
            cursor.execute(select_query, item_tuple)
            return cursor.rowcount
