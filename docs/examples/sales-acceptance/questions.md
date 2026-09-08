# 销售经营合成120题

合成数据，非真实业务金标。100道可回答、10道澄清、10道不支持；开发/留出各60题。50组可回答场景各有两个问法，同类筛选和改写不跨集合。留出答案随仓库公开，不是保密业务盲测。

| ID | 集合 | 问题与历史 | 预期动作 |
|---|---|---|---|
| sales-total-gross_sales-1 | dev | 按已发布的销售总额口径，全部日期、全部渠道和客户，给出结果。 | answer |
| sales-total-gross_sales-2 | dev | 请统计销售总额，范围是全部日期、全部渠道和客户，沿用已发布定义。 | answer |
| sales-total-refund_amount-1 | dev | 按已发布的退款金额口径，全部日期、全部渠道和客户，给出结果。 | answer |
| sales-total-refund_amount-2 | dev | 请统计退款金额，范围是全部日期、全部渠道和客户，沿用已发布定义。 | answer |
| sales-total-net_sales-1 | dev | 按已发布的净销售额口径，全部日期、全部渠道和客户，给出结果。 | answer |
| sales-total-net_sales-2 | dev | 请统计净销售额，范围是全部日期、全部渠道和客户，沿用已发布定义。 | answer |
| sales-total-order_count-1 | dev | 按已发布的支付订单数口径，全部日期、全部渠道和客户，给出结果。 | answer |
| sales-total-order_count-2 | dev | 请统计支付订单数，范围是全部日期、全部渠道和客户，沿用已发布定义。 | answer |
| sales-total-avg_order-1 | dev | 按已发布的客单价口径，全部日期、全部渠道和客户，给出结果。 | answer |
| sales-total-avg_order-2 | dev | 请统计客单价，范围是全部日期、全部渠道和客户，沿用已发布定义。 | answer |
| sales-day-gross_sales-1 | dev | 按已发布的销售总额口径，全部日期，按订单日期逐日分组，给出结果。 | answer |
| sales-day-gross_sales-2 | dev | 请统计销售总额，范围是全部日期，按订单日期逐日分组，沿用已发布定义。 | answer |
| sales-day-refund_amount-1 | dev | 按已发布的退款金额口径，全部日期，按订单日期逐日分组，给出结果。 | answer |
| sales-day-refund_amount-2 | dev | 请统计退款金额，范围是全部日期，按订单日期逐日分组，沿用已发布定义。 | answer |
| sales-day-net_sales-1 | dev | 按已发布的净销售额口径，全部日期，按订单日期逐日分组，给出结果。 | answer |
| sales-day-net_sales-2 | dev | 请统计净销售额，范围是全部日期，按订单日期逐日分组，沿用已发布定义。 | answer |
| sales-day-order_count-1 | dev | 按已发布的支付订单数口径，全部日期，按订单日期逐日分组，给出结果。 | answer |
| sales-day-order_count-2 | dev | 请统计支付订单数，范围是全部日期，按订单日期逐日分组，沿用已发布定义。 | answer |
| sales-day-avg_order-1 | dev | 按已发布的客单价口径，全部日期，按订单日期逐日分组，给出结果。 | answer |
| sales-day-avg_order-2 | dev | 请统计客单价，范围是全部日期，按订单日期逐日分组，沿用已发布定义。 | answer |
| sales-range-gross_sales-1 | dev | 按已发布的销售总额口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。 | answer |
| sales-range-gross_sales-2 | dev | 请统计销售总额，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。 | answer |
| sales-range-refund_amount-1 | dev | 按已发布的退款金额口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。 | answer |
| sales-range-refund_amount-2 | dev | 请统计退款金额，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。 | answer |
| sales-range-net_sales-1 | dev | 按已发布的净销售额口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。 | answer |
| sales-range-net_sales-2 | dev | 请统计净销售额，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。 | answer |
| sales-range-order_count-1 | dev | 按已发布的支付订单数口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。 | answer |
| sales-range-order_count-2 | dev | 请统计支付订单数，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。 | answer |
| sales-range-avg_order-1 | dev | 按已发布的客单价口径，订单日期从2026-09-01（含）到2026-09-03（不含），给出结果。 | answer |
| sales-range-avg_order-2 | dev | 请统计客单价，范围是订单日期从2026-09-01（含）到2026-09-03（不含），沿用已发布定义。 | answer |
| sales-online-gross_sales-1 | dev | 按已发布的销售总额口径，全部日期，仅线上直营渠道，给出结果。 | answer |
| sales-online-gross_sales-2 | dev | 按已发布的销售总额口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-online-refund_amount-1 | dev | 按已发布的退款金额口径，全部日期，仅线上直营渠道，给出结果。 | answer |
| sales-online-refund_amount-2 | dev | 按已发布的退款金额口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-online-net_sales-1 | dev | 按已发布的净销售额口径，全部日期，仅线上直营渠道，给出结果。 | answer |
| sales-online-net_sales-2 | dev | 按已发布的净销售额口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-online-order_count-1 | dev | 按已发布的支付订单数口径，全部日期，仅线上直营渠道，给出结果。 | answer |
| sales-online-order_count-2 | dev | 按已发布的支付订单数口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-online-avg_order-1 | dev | 按已发布的客单价口径，全部日期，仅线上直营渠道，给出结果。 | answer |
| sales-online-avg_order-2 | dev | 按已发布的客单价口径，全部日期，仅线上直营渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-partner-gross_sales-1 | dev | 按已发布的销售总额口径，全部日期，仅合作渠道，给出结果。 | answer |
| sales-partner-gross_sales-2 | dev | 按已发布的销售总额口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-partner-refund_amount-1 | dev | 按已发布的退款金额口径，全部日期，仅合作渠道，给出结果。 | answer |
| sales-partner-refund_amount-2 | dev | 按已发布的退款金额口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-partner-net_sales-1 | dev | 按已发布的净销售额口径，全部日期，仅合作渠道，给出结果。 | answer |
| sales-partner-net_sales-2 | dev | 按已发布的净销售额口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-partner-order_count-1 | dev | 按已发布的支付订单数口径，全部日期，仅合作渠道，给出结果。 | answer |
| sales-partner-order_count-2 | dev | 按已发布的支付订单数口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-partner-avg_order-1 | dev | 按已发布的客单价口径，全部日期，仅合作渠道，给出结果。 | answer |
| sales-partner-avg_order-2 | dev | 按已发布的客单价口径，全部日期，仅合作渠道，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-region-gross_sales-1 | blind | 按已发布的销售总额口径，全部日期，按客户区域分组，给出结果。 | answer |
| sales-region-gross_sales-2 | blind | 请统计销售总额，范围是全部日期，按客户区域分组，沿用已发布定义。 | answer |
| sales-region-refund_amount-1 | blind | 按已发布的退款金额口径，全部日期，按客户区域分组，给出结果。 | answer |
| sales-region-refund_amount-2 | blind | 请统计退款金额，范围是全部日期，按客户区域分组，沿用已发布定义。 | answer |
| sales-region-net_sales-1 | blind | 按已发布的净销售额口径，全部日期，按客户区域分组，给出结果。 | answer |
| sales-region-net_sales-2 | blind | 请统计净销售额，范围是全部日期，按客户区域分组，沿用已发布定义。 | answer |
| sales-region-order_count-1 | blind | 按已发布的支付订单数口径，全部日期，按客户区域分组，给出结果。 | answer |
| sales-region-order_count-2 | blind | 请统计支付订单数，范围是全部日期，按客户区域分组，沿用已发布定义。 | answer |
| sales-region-avg_order-1 | blind | 按已发布的客单价口径，全部日期，按客户区域分组，给出结果。 | answer |
| sales-region-avg_order-2 | blind | 请统计客单价，范围是全部日期，按客户区域分组，沿用已发布定义。 | answer |
| sales-channel-gross_sales-1 | blind | 按已发布的销售总额口径，全部日期，按销售渠道分组，给出结果。 | answer |
| sales-channel-gross_sales-2 | blind | 请统计销售总额，范围是全部日期，按销售渠道分组，沿用已发布定义。 | answer |
| sales-channel-refund_amount-1 | blind | 按已发布的退款金额口径，全部日期，按销售渠道分组，给出结果。 | answer |
| sales-channel-refund_amount-2 | blind | 请统计退款金额，范围是全部日期，按销售渠道分组，沿用已发布定义。 | answer |
| sales-channel-net_sales-1 | blind | 按已发布的净销售额口径，全部日期，按销售渠道分组，给出结果。 | answer |
| sales-channel-net_sales-2 | blind | 请统计净销售额，范围是全部日期，按销售渠道分组，沿用已发布定义。 | answer |
| sales-channel-order_count-1 | blind | 按已发布的支付订单数口径，全部日期，按销售渠道分组，给出结果。 | answer |
| sales-channel-order_count-2 | blind | 请统计支付订单数，范围是全部日期，按销售渠道分组，沿用已发布定义。 | answer |
| sales-channel-avg_order-1 | blind | 按已发布的客单价口径，全部日期，按销售渠道分组，给出结果。 | answer |
| sales-channel-avg_order-2 | blind | 请统计客单价，范围是全部日期，按销售渠道分组，沿用已发布定义。 | answer |
| sales-top-gross_sales-1 | blind | 按已发布的销售总额口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。 | answer |
| sales-top-gross_sales-2 | blind | 请统计销售总额，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。 | answer |
| sales-top-refund_amount-1 | blind | 按已发布的退款金额口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。 | answer |
| sales-top-refund_amount-2 | blind | 请统计退款金额，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。 | answer |
| sales-top-net_sales-1 | blind | 按已发布的净销售额口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。 | answer |
| sales-top-net_sales-2 | blind | 请统计净销售额，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。 | answer |
| sales-top-order_count-1 | blind | 按已发布的支付订单数口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。 | answer |
| sales-top-order_count-2 | blind | 请统计支付订单数，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。 | answer |
| sales-top-avg_order-1 | blind | 按已发布的客单价口径，全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，给出结果。 | answer |
| sales-top-avg_order-2 | blind | 请统计客单价，范围是全部日期，按客户分组，取该指标最高的前两名；并列按客户名称升序，沿用已发布定义。 | answer |
| sales-east-gross_sales-1 | blind | 按已发布的销售总额口径，全部日期，仅华东示例客户，给出结果。 | answer |
| sales-east-gross_sales-2 | blind | 按已发布的销售总额口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-east-refund_amount-1 | blind | 按已发布的退款金额口径，全部日期，仅华东示例客户，给出结果。 | answer |
| sales-east-refund_amount-2 | blind | 按已发布的退款金额口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-east-net_sales-1 | blind | 按已发布的净销售额口径，全部日期，仅华东示例客户，给出结果。 | answer |
| sales-east-net_sales-2 | blind | 按已发布的净销售额口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-east-order_count-1 | blind | 按已发布的支付订单数口径，全部日期，仅华东示例客户，给出结果。 | answer |
| sales-east-order_count-2 | blind | 按已发布的支付订单数口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-east-avg_order-1 | blind | 按已发布的客单价口径，全部日期，仅华东示例客户，给出结果。 | answer |
| sales-east-avg_order-2 | blind | 按已发布的客单价口径，全部日期，仅华东示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-south-gross_sales-1 | blind | 按已发布的销售总额口径，全部日期，仅华南示例客户，给出结果。 | answer |
| sales-south-gross_sales-2 | blind | 按已发布的销售总额口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-south-refund_amount-1 | blind | 按已发布的退款金额口径，全部日期，仅华南示例客户，给出结果。 | answer |
| sales-south-refund_amount-2 | blind | 按已发布的退款金额口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-south-net_sales-1 | blind | 按已发布的净销售额口径，全部日期，仅华南示例客户，给出结果。 | answer |
| sales-south-net_sales-2 | blind | 按已发布的净销售额口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-south-order_count-1 | blind | 按已发布的支付订单数口径，全部日期，仅华南示例客户，给出结果。 | answer |
| sales-south-order_count-2 | blind | 按已发布的支付订单数口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-south-avg_order-1 | blind | 按已发布的客单价口径，全部日期，仅华南示例客户，给出结果。 | answer |
| sales-south-avg_order-2 | blind | 按已发布的客单价口径，全部日期，仅华南示例客户，给出结果。 → 沿用刚才的客户或渠道筛选，再给我同一指标的结果。 | answer |
| sales-ambiguous-entity-1 | dev | 示例渠道的净销售额是多少？ | clarify |
| sales-ambiguous-entity-2 | dev | 统计示例渠道对应的净销售额。 | clarify |
| sales-missing-metric-1 | dev | 帮我看看销售经营情况。 | clarify |
| sales-missing-metric-2 | dev | 经营怎么样，帮我查一下。 | clarify |
| sales-missing-period-1 | dev | 统计那段时间的净销售额。 | clarify |
| sales-missing-period-2 | dev | 查询之前说的那个期间的净销售额。 | clarify |
| sales-missing-basis-1 | dev | 查询销售额，但我还没确定要退款前还是退款后口径。 | clarify |
| sales-missing-basis-2 | dev | 销售金额该看哪个数？我没决定是否扣除退款。 | clarify |
| sales-missing-ranking-1 | dev | 找出表现最好的客户，我尚未确定按什么指标排序。 | clarify |
| sales-missing-ranking-2 | dev | 哪些客户最好？我还没选评价指标。 | clarify |
| sales-yoy-1 | blind | 仅标准指标模式下计算净销售额同比增长率。 | unsupported |
| sales-yoy-2 | blind | 使用标准指标计划给出净销售额同比增幅。 | unsupported |
| sales-mom-1 | blind | 仅标准指标模式下计算净销售额环比增长率。 | unsupported |
| sales-mom-2 | blind | 使用标准指标计划给出净销售额环比增幅。 | unsupported |
| sales-profit-1 | blind | 计算销售毛利，必须扣除商品成本。 | unsupported |
| sales-profit-2 | blind | 统计扣除商品成本后的销售毛利润。 | unsupported |
| sales-inventory-1 | blind | 查询仓库当前库存数量。 | unsupported |
| sales-inventory-2 | blind | 现在仓库还剩多少件商品？ | unsupported |
| sales-cross-source-1 | blind | 把当前订单和另一个未接入数据源的收款流水关联核对。 | unsupported |
| sales-cross-source-2 | blind | 跨数据源联查销售订单与尚未接入的银行收款明细。 | unsupported |
