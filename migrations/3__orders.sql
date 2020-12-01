CREATE TYPE public.ORDER_STATUS AS ENUM ('NEW', 'IN_PROGRESS', 'FINISHED');

CREATE TABLE IF NOT EXISTS public.orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    address TEXT,
    name TEXT,
    surname TEXT,
    status public.ORDER_STATUS,
    shipping_price DECIMAL(20, 10)
);

CREATE TABLE IF NOT EXISTS order_product_link (
    order_id INTEGER, -- for test task no many constraints
    product_id INTEGER,
    amount INTEGER,
    PRIMARY KEY (order_id, product_id)
);