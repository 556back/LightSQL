-- Read-only PostgreSQL reference queries over the frozen M03 sample.

-- sales-total-gross_sales-1
-- 按已发布的销售总额口径，全部日期、全部渠道和客户，给出结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-total-gross_sales-2
-- 请统计销售总额，范围是全部日期、全部渠道和客户，沿用已发布定义。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-total-refund_amount-1
-- 按已发布的退款金额口径，全部日期、全部渠道和客户，给出结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-total-refund_amount-2
-- 请统计退款金额，范围是全部日期、全部渠道和客户，沿用已发布定义。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-total-net_sales-1
-- 按已发布的净销售额口径，全部日期、全部渠道和客户，给出结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-total-net_sales-2
-- 请统计净销售额，范围是全部日期、全部渠道和客户，沿用已发布定义。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-total-order_count-1
-- 按已发布的支付订单数口径，全部日期、全部渠道和客户，给出结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-total-order_count-2
-- 请统计支付订单数，范围是全部日期、全部渠道和客户，沿用已发布定义。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-total-avg_order-1
-- 按已发布的客单价口径，全部日期、全部渠道和客户，给出结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-total-avg_order-2
-- 请统计客单价，范围是全部日期、全部渠道和客户，沿用已发布定义。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid';

-- sales-day-gross_sales-1
-- 按已发布的销售总额口径，全部日期，按订单日期逐日分组，给出结果。
SELECT o.order_date AS order_day, SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-day-gross_sales-2
-- 请统计销售总额，范围是全部日期，按订单日期逐日分组，沿用已发布定义。
SELECT o.order_date AS order_day, SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-day-refund_amount-1
-- 按已发布的退款金额口径，全部日期，按订单日期逐日分组，给出结果。
SELECT o.order_date AS order_day, SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-day-refund_amount-2
-- 请统计退款金额，范围是全部日期，按订单日期逐日分组，沿用已发布定义。
SELECT o.order_date AS order_day, SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-day-net_sales-1
-- 按已发布的净销售额口径，全部日期，按订单日期逐日分组，给出结果。
SELECT o.order_date AS order_day, SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-day-net_sales-2
-- 请统计净销售额，范围是全部日期，按订单日期逐日分组，沿用已发布定义。
SELECT o.order_date AS order_day, SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-day-order_count-1
-- 按已发布的支付订单数口径，全部日期，按订单日期逐日分组，给出结果。
SELECT o.order_date AS order_day, COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-day-order_count-2
-- 请统计支付订单数，范围是全部日期，按订单日期逐日分组，沿用已发布定义。
SELECT o.order_date AS order_day, COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-day-avg_order-1
-- 按已发布的客单价口径，全部日期，按订单日期逐日分组，给出结果。
SELECT o.order_date AS order_day, 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-day-avg_order-2
-- 请统计客单价，范围是全部日期，按订单日期逐日分组，沿用已发布定义。
SELECT o.order_date AS order_day, 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.order_date;

-- sales-range-gross_sales-1
-- 按已发布的销售总额口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-range-gross_sales-2
-- 请统计销售总额，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-range-refund_amount-1
-- 按已发布的退款金额口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-range-refund_amount-2
-- 请统计退款金额，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-range-net_sales-1
-- 按已发布的净销售额口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-range-net_sales-2
-- 请统计净销售额，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-range-order_count-1
-- 按已发布的支付订单数口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-range-order_count-2
-- 请统计支付订单数，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-range-avg_order-1
-- 按已发布的客单价口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-range-avg_order-2
-- 请统计客单价，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.order_date >= '2026-09-01' AND o.order_date < '2026-09-03';

-- sales-online-gross_sales-1
-- 按已发布的销售总额口径，全部日期，仅线上直营渠道，给出结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-online-gross_sales-2
-- 按已发布的销售总额口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-online-refund_amount-1
-- 按已发布的退款金额口径，全部日期，仅线上直营渠道，给出结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-online-refund_amount-2
-- 按已发布的退款金额口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-online-net_sales-1
-- 按已发布的净销售额口径，全部日期，仅线上直营渠道，给出结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-online-net_sales-2
-- 按已发布的净销售额口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-online-order_count-1
-- 按已发布的支付订单数口径，全部日期，仅线上直营渠道，给出结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-online-order_count-2
-- 按已发布的支付订单数口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-online-avg_order-1
-- 按已发布的客单价口径，全部日期，仅线上直营渠道，给出结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-online-avg_order-2
-- 按已发布的客单价口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='online';

-- sales-partner-gross_sales-1
-- 按已发布的销售总额口径，全部日期，仅合作渠道，给出结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-partner-gross_sales-2
-- 按已发布的销售总额口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-partner-refund_amount-1
-- 按已发布的退款金额口径，全部日期，仅合作渠道，给出结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-partner-refund_amount-2
-- 按已发布的退款金额口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-partner-net_sales-1
-- 按已发布的净销售额口径，全部日期，仅合作渠道，给出结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-partner-net_sales-2
-- 按已发布的净销售额口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-partner-order_count-1
-- 按已发布的支付订单数口径，全部日期，仅合作渠道，给出结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-partner-order_count-2
-- 按已发布的支付订单数口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-partner-avg_order-1
-- 按已发布的客单价口径，全部日期，仅合作渠道，给出结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-partner-avg_order-2
-- 按已发布的客单价口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' AND o.channel='partner';

-- sales-region-gross_sales-1
-- 按已发布的销售总额口径，全部日期，按客户区域分组，给出结果。
SELECT c.region AS region, SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-region-gross_sales-2
-- 请统计销售总额，范围是全部日期，按客户区域分组，沿用已发布定义。
SELECT c.region AS region, SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-region-refund_amount-1
-- 按已发布的退款金额口径，全部日期，按客户区域分组，给出结果。
SELECT c.region AS region, SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-region-refund_amount-2
-- 请统计退款金额，范围是全部日期，按客户区域分组，沿用已发布定义。
SELECT c.region AS region, SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-region-net_sales-1
-- 按已发布的净销售额口径，全部日期，按客户区域分组，给出结果。
SELECT c.region AS region, SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-region-net_sales-2
-- 请统计净销售额，范围是全部日期，按客户区域分组，沿用已发布定义。
SELECT c.region AS region, SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-region-order_count-1
-- 按已发布的支付订单数口径，全部日期，按客户区域分组，给出结果。
SELECT c.region AS region, COUNT(*) AS order_count FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-region-order_count-2
-- 请统计支付订单数，范围是全部日期，按客户区域分组，沿用已发布定义。
SELECT c.region AS region, COUNT(*) AS order_count FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-region-avg_order-1
-- 按已发布的客单价口径，全部日期，按客户区域分组，给出结果。
SELECT c.region AS region, 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-region-avg_order-2
-- 请统计客单价，范围是全部日期，按客户区域分组，沿用已发布定义。
SELECT c.region AS region, 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.region;

-- sales-channel-gross_sales-1
-- 按已发布的销售总额口径，全部日期，按销售渠道分组，给出结果。
SELECT o.channel AS channel, SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-channel-gross_sales-2
-- 请统计销售总额，范围是全部日期，按销售渠道分组，沿用已发布定义。
SELECT o.channel AS channel, SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-channel-refund_amount-1
-- 按已发布的退款金额口径，全部日期，按销售渠道分组，给出结果。
SELECT o.channel AS channel, SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-channel-refund_amount-2
-- 请统计退款金额，范围是全部日期，按销售渠道分组，沿用已发布定义。
SELECT o.channel AS channel, SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-channel-net_sales-1
-- 按已发布的净销售额口径，全部日期，按销售渠道分组，给出结果。
SELECT o.channel AS channel, SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-channel-net_sales-2
-- 请统计净销售额，范围是全部日期，按销售渠道分组，沿用已发布定义。
SELECT o.channel AS channel, SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-channel-order_count-1
-- 按已发布的支付订单数口径，全部日期，按销售渠道分组，给出结果。
SELECT o.channel AS channel, COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-channel-order_count-2
-- 请统计支付订单数，范围是全部日期，按销售渠道分组，沿用已发布定义。
SELECT o.channel AS channel, COUNT(*) AS order_count FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-channel-avg_order-1
-- 按已发布的客单价口径，全部日期，按销售渠道分组，给出结果。
SELECT o.channel AS channel, 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-channel-avg_order-2
-- 请统计客单价，范围是全部日期，按销售渠道分组，沿用已发布定义。
SELECT o.channel AS channel, 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o WHERE o.status='paid' GROUP BY o.channel;

-- sales-top-gross_sales-1
-- 按已发布的销售总额口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。
SELECT c.customer_name AS customer, SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY gross_sales DESC, customer ASC LIMIT 2;

-- sales-top-gross_sales-2
-- 请统计销售总额，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。
SELECT c.customer_name AS customer, SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY gross_sales DESC, customer ASC LIMIT 2;

-- sales-top-refund_amount-1
-- 按已发布的退款金额口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。
SELECT c.customer_name AS customer, SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY refund_amount DESC, customer ASC LIMIT 2;

-- sales-top-refund_amount-2
-- 请统计退款金额，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。
SELECT c.customer_name AS customer, SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY refund_amount DESC, customer ASC LIMIT 2;

-- sales-top-net_sales-1
-- 按已发布的净销售额口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。
SELECT c.customer_name AS customer, SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY net_sales DESC, customer ASC LIMIT 2;

-- sales-top-net_sales-2
-- 请统计净销售额，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。
SELECT c.customer_name AS customer, SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY net_sales DESC, customer ASC LIMIT 2;

-- sales-top-order_count-1
-- 按已发布的支付订单数口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。
SELECT c.customer_name AS customer, COUNT(*) AS order_count FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY order_count DESC, customer ASC LIMIT 2;

-- sales-top-order_count-2
-- 请统计支付订单数，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。
SELECT c.customer_name AS customer, COUNT(*) AS order_count FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY order_count DESC, customer ASC LIMIT 2;

-- sales-top-avg_order-1
-- 按已发布的客单价口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。
SELECT c.customer_name AS customer, 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY avg_order DESC, customer ASC LIMIT 2;

-- sales-top-avg_order-2
-- 请统计客单价，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。
SELECT c.customer_name AS customer, 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' GROUP BY c.customer_name ORDER BY avg_order DESC, customer ASC LIMIT 2;

-- sales-east-gross_sales-1
-- 按已发布的销售总额口径，全部日期，仅华东示例客户，给出结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-east-gross_sales-2
-- 按已发布的销售总额口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-east-refund_amount-1
-- 按已发布的退款金额口径，全部日期，仅华东示例客户，给出结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-east-refund_amount-2
-- 按已发布的退款金额口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-east-net_sales-1
-- 按已发布的净销售额口径，全部日期，仅华东示例客户，给出结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-east-net_sales-2
-- 按已发布的净销售额口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-east-order_count-1
-- 按已发布的支付订单数口径，全部日期，仅华东示例客户，给出结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-east-order_count-2
-- 按已发布的支付订单数口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-east-avg_order-1
-- 按已发布的客单价口径，全部日期，仅华东示例客户，给出结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-east-avg_order-2
-- 按已发布的客单价口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华东示例客户';

-- sales-south-gross_sales-1
-- 按已发布的销售总额口径，全部日期，仅华南示例客户，给出结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';

-- sales-south-gross_sales-2
-- 按已发布的销售总额口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.gross_amount) AS gross_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';

-- sales-south-refund_amount-1
-- 按已发布的退款金额口径，全部日期，仅华南示例客户，给出结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';

-- sales-south-refund_amount-2
-- 按已发布的退款金额口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.refund_amount) AS refund_amount FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';

-- sales-south-net_sales-1
-- 按已发布的净销售额口径，全部日期，仅华南示例客户，给出结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';

-- sales-south-net_sales-2
-- 按已发布的净销售额口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT SUM(o.net_amount) AS net_sales FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';

-- sales-south-order_count-1
-- 按已发布的支付订单数口径，全部日期，仅华南示例客户，给出结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';

-- sales-south-order_count-2
-- 按已发布的支付订单数口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT COUNT(*) AS order_count FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';

-- sales-south-avg_order-1
-- 按已发布的客单价口径，全部日期，仅华南示例客户，给出结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';

-- sales-south-avg_order-2
-- 按已发布的客单价口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。
SELECT 1.0 * SUM(o.net_amount) / NULLIF(COUNT(*), 0) AS avg_order FROM demo_sales.m03_orders o LEFT JOIN demo_sales.m03_customers c ON o.tenant_id=c.tenant_id AND o.customer_id=c.customer_id WHERE o.status='paid' AND c.customer_name='华南示例客户';
