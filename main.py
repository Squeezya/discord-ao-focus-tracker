import os
from dotenv import load_dotenv

from interactions import (
    Client,
    CommandContext,
    Embed,
    EmbedField,
    EmbedFooter,
    Option,
    OptionType,
    User,
    Color,
)
from app.focus_price_repository import FocusPriceRepository
from app.focus_usage_repository import FocusUsageRepository

load_dotenv()

bot = Client(token=os.environ['DISCORD_TOKEN'])


@bot.command(
    name="pay",
    description="Command to set the price per focus of a member (Officers only).",
    options=[
        Option(
            name="user",
            description="User",
            type=OptionType.USER,
            required=True,
        ),
    ],
)
async def pay(ctx: CommandContext, user: User):
    if not check_user_role(ctx):
        return await ctx.send(embeds=[no_permissions_embed()])
    user_id = str(user.id)
    guild_id = str(ctx.guild_id)
    FocusUsageRepository.set_user_paid(guild_id, user_id)
    return await ctx.send(embeds=[Embed(
        title="Success!",
        description=f"Member {user.name} was paid.",
        color=Color.green(),
    )])


@bot.command(
    name="set-member-focus-price",
    description="Command to set the price per focus of a member (Officers only).",
    options=[
        Option(
            name="user",
            description="User",
            type=OptionType.USER,
            required=True,
        ),
        Option(
            name="price_per_focus",
            description="Price per focus",
            type=OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def set_member_focus_price(ctx: CommandContext, user: User, price_per_focus: float):
    if not check_user_role(ctx):
        return await ctx.send(embeds=[no_permissions_embed()])

    user_id = str(user.id)
    guild_id = str(ctx.guild_id)
    FocusPriceRepository.set_prices_for_guild(guild_id, user_id, price_per_focus)
    await ctx.send(embeds=[Embed(
        title="Success!",
        description=f"Price per focus for {user.name} set to {price_per_focus}",
        color=Color.green(),
        ephemeral=True,
    )])


@bot.command(
    name="list-payments",
    description="Command that lists all users and respective focus (Officers only).",
)
async def list_payments(ctx: CommandContext):
    if not check_user_role(ctx):
        return await ctx.send(embeds=[no_permissions_embed()])
    guild_id = str(ctx.guild_id)
    usages_by_user = FocusUsageRepository.get_focus_usage_for_guild_by_user(guild_id)
    embed = None
    context_guilds = list(filter(lambda guild: guild.id == ctx.guild_id, ctx.client.guilds))
    users = []
    if len(context_guilds) > 0:
        members = await context_guilds[0].get_all_members()
        users = list(map(lambda member: member.user, members))

    fields = _get_member_payment_embed_fields(ctx.guild, users, usages_by_user)
    if len(fields) > 0:
        embed = Embed(
            title="Focus per Member",
            fields=fields,
            color=Color.green(),
        )
    else:
        embed = Embed(
            title="User's Focus",
            description="All clear, nothing to see here.",
            color=Color.green(),
        )
    await ctx.send(
        embeds=[embed],
        ephemeral=True,
    )


@bot.command(
    name="list-my-focus",
    description="Command that lists user's focus unpaid.",
)
async def list_my_focus(ctx: CommandContext):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.user.id)
    user_focus_data = FocusUsageRepository.get_focus_usage_list(guild_id, user_id)
    if len(user_focus_data) > 0:
        embed = create_embed_for_focus_data(
            ctx.author,
            user_focus_data
        )
    else:
        embed = Embed(
            title='User Focus',
            description="All clear, nothing to see here.",
            color=Color.green(),
        )

    await ctx.send(
        embeds=[embed],
        ephemeral=True,
    )


@bot.command(
    name="focus-craft",
    description="Command to add focus spent (Roles: All).",
    options=[
        Option(
            name="focus_usage",
            description="Focus Usage",
            type=OptionType.INTEGER,
            required=True,
        ),
        Option(
            name="item_crafted",
            description="Crafted Item",
            type=OptionType.STRING,
            required=True,
        ),
        Option(
            name="quantity",
            description="Quantity",
            type=OptionType.INTEGER,
            required=True,
        ),
    ],
)
async def focus_craft(ctx: CommandContext, focus_usage, item_crafted, quantity):
    if int(focus_usage) > 30000:
        return await ctx.send(embeds=[Embed(
            title="Focus usage limit!",
            description="Max focus limit per action is 30k.",
            color=Color.red(),
            ephemeral=True,
        )])
    embed = create_embed_for_focus_data(ctx.author, [dict(
        focus_usage=focus_usage, crafted_item=item_crafted, quantity=quantity
    )])
    add_user_focus_data_item(ctx.guild, ctx.author.user, focus_usage, item_crafted, quantity)
    await ctx.send(
        embeds=[embed],
        ephemeral=True,
    )


def create_embed_for_focus_data(member, user_focus_data: list[dict]):
    total_user_focus = sum(map(lambda user_usage: user_usage.get("focus_usage"), user_focus_data))
    return Embed(
        title=f"{member.name}",
        color=Color.green(),
        fields=[
            EmbedField(
                name=f"{focus_entry.get('item_crafted')} x {focus_entry.get('quantity')}",
                value=f"{format_number(focus_entry.get('focus_usage'))}",
                inline=True
            )
            for focus_entry in user_focus_data
        ],
        footer=EmbedFooter(text=f"Total focus: {format_number(total_user_focus)}")
    )


def add_user_focus_data_item(guild, user, focus_usage, item_crafted, quantity):
    guild_id = str(guild.id)
    user_id = str(user.id)
    FocusUsageRepository.create_focus_usage(guild_id, user_id, focus_usage, item_crafted, quantity)


def _get_member_payment_embed_fields(guild, users, usages_by_user):
    fields = []
    guild_id = str(guild.id)
    prices_per_user = FocusPriceRepository.get_prices_for_guild(guild_id)
    for user_usage in usages_by_user:
        user_id = user_usage.get("user_id")
        filtered_users = list(filter(lambda u, u_id=user_id: u.id == u_id, users))
        user = filtered_users[0] if len(filtered_users) > 0 else None
        if user:
            user_focus_spent = user_usage.get("usage_sum")
            if user_focus_spent > 0:
                user_price = next(filter(
                    lambda price, u_id=user_id: price.get("user_id") == u_id,
                    prices_per_user
                ), None)
                user_price_per_focus = user_price.get("focus_price") if user_price else 0
                fields.append(
                    EmbedField(
                        name=f"{user.username}",
                        value=f"{format_number(user_focus_spent)} x {user_price_per_focus} = "
                              f"{format_number(user_focus_spent * user_price_per_focus)}",
                        inline=False
                    )
                )
    return fields


def check_user_role(ctx):
    context_guilds = list(filter(lambda guild: guild.id == ctx.guild_id, ctx.client.guilds))
    guild_manager_role = next(filter(lambda role: role.name == "FocusBotManager", context_guilds[0].roles), None)
    return guild_manager_role.id in ctx.author.roles


def format_number(nr):
    return '{:0,.0f}'.format(nr).replace(',', ' ')


def no_permissions_embed():
    return Embed(
        title="No Permissions!",
        color=Color.red(),
        ephemeral=True,
    )


bot.start()