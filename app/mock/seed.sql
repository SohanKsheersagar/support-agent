-- Fictional fixtures from Doc 3. Unknown dates stay NULL rather than being invented.
INSERT INTO customers (id, name, email, tier, flags) VALUES
    ('C-001', 'Jordan Lee', 'jordan.lee@example.com', 'Standard', '{}'),
    ('C-002', 'Sam Patel', 'sam.patel@example.com', 'Summit', '{}'),
    ('C-003', 'Riley Chen', 'riley.chen@example.com', 'VIP', '{}'),
    ('C-004', 'Morgan Diaz', 'morgan.diaz@example.com', 'Standard', '{"delivered_not_received_claims_12m": 2}'),
    ('C-005', 'Taylor Brooks', 'taylor.brooks@example.com', 'Standard', '{}'),
    ('C-006', 'Casey Nguyen', 'casey.nguyen@example.com', 'Standard', '{}')
ON CONFLICT (id) DO NOTHING;

INSERT INTO orders (id, customer_id, total, status, placed_at, delivered_at, shipped_at, carrier, tracking_number, last_carrier_scan_at) VALUES
    ('TH-10482', 'C-001', 179.00, 'Delivered', '2026-10-22', '2026-10-27', NULL, NULL, NULL, NULL),
    ('TH-10390', 'C-001', 165.00, 'Delivered', NULL, '2026-09-20', NULL, NULL, NULL, NULL),
    ('TH-10455', 'C-002', 348.00, 'Delivered', NULL, '2026-10-05', NULL, NULL, NULL, NULL),
    ('TH-10501', 'C-005', 140.00, 'Shipped', NULL, NULL, '2026-10-29', 'UPS Ground', '1Z999AA10123456784', '2026-10-29'),
    ('TH-10510', 'C-004', 349.00, 'Delivered', NULL, '2026-10-28', NULL, NULL, NULL, NULL),
    ('TH-10520', 'C-003', 179.00, 'Delivered', NULL, '2026-10-20', NULL, NULL, NULL, NULL),
    ('TH-10530', 'C-005', 59.00, 'Placed', '2026-11-02', NULL, NULL, NULL, NULL, NULL),
    ('TH-10540', 'C-001', 59.00, 'Delivered', NULL, '2026-10-25', NULL, NULL, NULL, NULL)
ON CONFLICT (id) DO NOTHING;

INSERT INTO order_items (id, order_id, sku, name, price, qty, category) VALUES
    ('I-10482-1', 'TH-10482', 'BAG-45L-TRK', '45L Trekking Pack', 179.00, 1, 'backpacks'),
    ('I-10390-1', 'TH-10390', 'BTS-MID-WP', 'Mid Waterproof Boot', 165.00, 1, 'boots'),
    ('I-10455-1', 'TH-10455', 'SLP-20F-DWN', '20F Down Sleeping Bag', 289.00, 1, 'sleeping_bags'),
    ('I-10455-2', 'TH-10455', 'ACC-STV-LGT', 'Lightweight Stove', 59.00, 1, 'accessories'),
    ('I-10501-1', 'TH-10501', 'APP-JKT-SHL', 'Shell Jacket', 140.00, 1, 'apparel'),
    ('I-10510-1', 'TH-10510', 'TNT-2P-ALP', '2-person Alpine Tent', 349.00, 1, 'tents'),
    ('I-10520-1', 'TH-10520', 'BAG-45L-TRK', '45L Trekking Pack', 179.00, 1, 'backpacks'),
    ('I-10530-1', 'TH-10530', 'ACC-STV-LGT', 'Lightweight Stove', 59.00, 1, 'accessories'),
    ('I-10540-1', 'TH-10540', 'ACC-STV-LGT', 'Lightweight Stove', 59.00, 1, 'accessories')
ON CONFLICT (id) DO NOTHING;
