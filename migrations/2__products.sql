CREATE TABLE IF NOT EXISTS public.products (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    picture TEXT, -- link to picture
    price_dollar DECIMAL(20, 10) -- in dollars
);

-- fill at least 8 pizzas just in migration
INSERT INTO public.products (name, picture, price_dollar)
VALUES
    ('margarita', 'margarita.png', 12.07),
    ('pepperoni', 'pepperoni.png', 10.75),
    ('carbonara', 'carbonara.png', 11.26),
    ('americana', 'americana.png', 13.99),
    ('four cheeses', 'four_cheeses.png', 12.5),
    ('hawaiian', 'hawaiian.png', 14.25),
    ('neopolitano', 'neopolitana.png', 17.32),
    ('diablo', 'diablo.png', 23.99)
ON CONFLICT (name) DO NOTHING;

CREATE TABLE IF NOT EXISTS public.currencies (
    currency TEXT PRIMARY KEY,
    multiplier DECIMAL(20, 10)
);

INSERT INTO public.currencies (currency, multiplier)
VALUES
    ('USD', 1),
    ('RUB', 77.58),
    ('EUR', 0.85)
ON CONFLICT (currency)
DO UPDATE SET multiplier = excluded.multiplier