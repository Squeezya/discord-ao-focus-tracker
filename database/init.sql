CREATE TABLE focus_price(
    id SERIAL PRIMARY KEY,
    guild_id VARCHAR(30),
    user_id VARCHAR(30),
    focus_price NUMERIC(7, 2)
);
CREATE UNIQUE INDEX uniq_idx_focus_price ON focus_price (guild_id, user_id);

CREATE TABLE focus_usage(
    id SERIAL PRIMARY KEY,
    guild_id VARCHAR(30),
    user_id VARCHAR(30),
    focus_usage NUMERIC(10, 2),
    item_crafted VARCHAR(100),
    quantity NUMERIC(5, 0),
    is_paid boolean
);