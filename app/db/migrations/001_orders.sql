CREATE TABLE customers (
    id text PRIMARY KEY,
    email text NOT NULL UNIQUE,
    name text NOT NULL,
    tier text NOT NULL CHECK (tier IN ('Standard', 'Summit', 'VIP')),
    flags jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id text PRIMARY KEY,
    customer_id text NOT NULL REFERENCES customers(id),
    status text NOT NULL CHECK (status IN ('Placed', 'Processing', 'Shipped', 'Delivered', 'Cancelled')),
    placed_at date,
    shipped_at date,
    delivered_at date,
    carrier text,
    tracking_number text,
    last_carrier_scan_at date,
    total numeric(12, 2) NOT NULL CHECK (total >= 0)
);

CREATE INDEX orders_customer_id_idx ON orders(customer_id);

CREATE TABLE order_items (
    id text PRIMARY KEY,
    order_id text NOT NULL REFERENCES orders(id),
    sku text NOT NULL,
    name text NOT NULL,
    price numeric(12, 2) NOT NULL CHECK (price >= 0),
    qty integer NOT NULL CHECK (qty > 0),
    category text NOT NULL
);

CREATE INDEX order_items_order_id_idx ON order_items(order_id);
