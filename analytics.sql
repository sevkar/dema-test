-- Number of orders by channel
SELECT
    ch.name,
    COUNT(DISTINCT o.order_id) AS total_orders
FROM staging.order AS o
JOIN staging.channel AS ch
    ON o.channel_id = ch.id
GROUP BY ch.name
ORDER BY total_orders DESC;

-- Top 10 products by revenue
SELECT
    p.name,
    SUM(oi.quantity * oi.amount) AS revenue
FROM staging.order_line_item AS oi
JOIN staging.product AS p
    ON oi.product_id = p.product_id
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 10;

-- Bestsellers by month
WITH monthly_product_revenue AS (
    SELECT
        TO_CHAR(o.created_at, 'YYYY-MM') AS year_month,
        p.product_id,
        p.name,
        SUM(oli.amount) AS total_revenue
    FROM staging.order_line_item AS oli
    JOIN staging.order AS o
        ON oli.order_id = o.order_id
    JOIN staging.product AS p
        ON oli.product_id = p.product_id
    GROUP BY
        TO_CHAR(o.created_at, 'YYYY-MM'),
        p.product_id,
        p.name
)
SELECT
    year_month,
    name,
    total_revenue,
    RANK() OVER (
        PARTITION BY year_month
        ORDER BY total_revenue DESC
    ) AS revenue_rank
FROM monthly_product_revenue
ORDER BY
    year_month,
    revenue_rank;