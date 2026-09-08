qid000001	select 中文名 , 场上位置 from 篮球运动员 where 词条id not in ( select 球员id from 比赛记录 )	运动员比赛记录
qid000002	select 名称 from 高校 where 词条id not in ( select 高校id from 奖项 )	中国高校
qid000003	select 名称 , 所属省份 from 城市 where 词条id not in ( select 城市id from 都城 )	中国历史名城
qid000004	select 名称 , 类型 from 参考书 where 词条id not in ( select 试卷id from 参考试卷 )	教材辅助参考书
qid000005	select 名称 , 所属公司 from 洗衣机品牌 where 词条id not in ( select 品牌id from 洗衣机品牌门店 )	洗衣机
qid000006	select 名称 , 出品公司 from 电视剧 where 词条id not in ( select 电视剧id from 电视剧收视 )	中国卫视频道
qid000007	select 名称 , 类别 from 高校 where 词条id not in ( select 高校id from 名人 )	中国高校
qid000008	select 中文名 , 法定代表人 from 企业 where 词条id not in ( select 企业id from 投资公司 )	企业融资
qid000009	select 书名 , 作者 from 图书 where 词条id not in ( select 书名id from 电子书 )	购书平台
qid000010	select 姓名 , 性别 from 企业人物 where 词条id not in ( select 人物id from 人物公司职位 )	CCTV中国经济年度人物
qid000011	select 姓名 , 民族 from 明星 where 词条id not in ( select 明星id from 综艺节目嘉宾 )	综艺节目
qid000012	select 城市 , 所属省份 from 城市 where 词条id not in ( select 贫困城市id from 对口帮扶城市 )	友好城市
qid000013	select 城市 , 所属省份 from 城市 where 词条id not in ( select 帮助城市id from 对口帮扶城市 )	友好城市
qid000014	select 城市 , 所属省份 from 城市 where 词条id not in ( select 城市id from 一带一路的中国城市 )	友好城市
qid000015	select 名称 , 所属洲 from 国家 where 词条id not in ( select 国家id from 2008北京奥运会奖牌榜 )	奥运会参赛队伍
qid000016	select 中文队名 , 所属地区 from 球队 where 词条id not in ( select 冠军球队id from 欧冠冠亚军 )	欧洲杯球队
qid000017	select 中文队名 , 所属地区 from 球队 where 词条id not in ( select 亚军球队id from 欧冠冠亚军 )	欧洲杯球队
qid000018	select 名称 , 隶属机构 from 电视台 where 词条id not in ( select 首播平台id from 电视剧 )	中国卫视频道
qid000019	select 姓名 , 性别 from 企业人物 where 词条id not in ( select 获奖人id from 历届经济人物获奖名单 )	CCTV中国经济年度人物
qid000020	select 中文名 , 法定代表人 from 企业 where 词条id not in ( select 企业id from 企业融资 )	企业融资
qid000021	( select 城市id from 一带一路的中国城市 ) except ( select 贫困城市id from 对口帮扶城市 )	友好城市
qid000022	( select 贫困城市id from 对口帮扶城市 ) intersect ( select 城市id from 一带一路的中国城市 )	友好城市
qid000023	select T1.名称 , T2.名称 , T1.产品类别 , T2.市场份额 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id	洗衣机
qid000024	select T1.名称 , T2.名称 , T1.产品类别 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id	洗衣机
qid000025	select T1.名称 , T2.名称 , T1.售价 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id	洗衣机
qid000026	select T1.名称 , T2.名称 , T1.售价 , T2.市场份额 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id	洗衣机
qid000027	select T1.名称 , T2.名称 , T1.售价 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id	洗衣机
qid000028	select T1.名称 , T2.名称 , T1.参赛国家数量 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id	奥运会参赛队伍
qid000029	select T1.名称 , T2.名称 , T1.举办城市 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id	奥运会参赛队伍
qid000030	select T1.名称 , T2.名称 , T1.参赛国家数量 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id	奥运会参赛队伍
qid000031	select T1.名称 , T2.名称 , T1.出品公司 , T2.隶属机构 from 电视剧 as T1 join 电视台 as T2 on 电视剧.首播平台id == 电视台.词条id	中国卫视频道
qid000032	select T2.姓名 , T2.民族 from 综艺节目嘉宾 as T1 join 明星 as T2 on 综艺节目嘉宾.明星id == 明星.词条id	综艺节目
qid000033	select T2.中文名 , T2.注册资本 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id	企业融资
qid000034	select T2.中文名 , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id	企业融资
qid000035	select T2.中文名 , T2.年龄 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id	运动员比赛记录
qid000036	select T2.中文名 , T2.场上位置 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id	运动员比赛记录
qid000037	select T2.名称 , T2.饱和脂肪含量 from 坚果中国人均消费 as T1 join 坚果 as T2 on 坚果中国人均消费.坚果id == 坚果.词条id	坚果
qid000038	select T2.名称 , T2.类型 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id	教材辅助参考书
qid000039	select T2.名称 , T2.适用年级 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id	教材辅助参考书
qid000040	select T2.名称 , T2.市场份额 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id	洗衣机
qid000041	select T2.名称 , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id	洗衣机
qid000042	select T2.中文名 , T2.注册资本 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id	企业融资
qid000043	select T2.中文名 , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id	企业融资
qid000044	select T2.城市 , T2.所属省份 from 对口帮扶城市 as T1 join 城市 as T2 on 对口帮扶城市.贫困城市id == 城市.词条id	友好城市
qid000045	select T2.城市 , T2.建交国家数量 from 对口帮扶城市 as T1 join 城市 as T2 on 对口帮扶城市.贫困城市id == 城市.词条id	友好城市
qid000046	select T2.名称 , T2.市场份额 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id	洗衣机
qid000047	select T3.名称 , T2.app名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id	打车软件
qid000048	select T3.名称 , T3.理念 , T2.app名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id	打车软件
qid000049	select T3.名称 , T3.每公里价格 , T2.app名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id	打车软件
qid000050	select T3.名称 , T2.名称 , T1.时间段 from 电视剧收视 as T1 join 电视剧 as T2 join 电视台 as T3 on 电视剧收视.电视剧id == 电视剧.词条id and 电视剧收视.平台id == 电视台.词条id	中国卫视频道
qid000051	select T3.名称 , T2.名称 , T2.出品公司 , T1.时间段 from 电视剧收视 as T1 join 电视剧 as T2 join 电视台 as T3 on 电视剧收视.电视剧id == 电视剧.词条id and 电视剧收视.平台id == 电视台.词条id	中国卫视频道
qid000052	select T3.名称 , T2.书名 , T2.作者 , T1.售价 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id	购书平台
qid000053	select T3.名称 , T3.年营业额 , T2.书名 , T1.售价 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id	购书平台
qid000054	select T3.名称 , T2.书名 , T1.售价 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id	购书平台
qid000055	select T2.中文名 , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id	企业融资
qid000056	select T2.中文名 , T2.注册资本 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id	企业融资
qid000057	select T2.中文名 , T2.注册资本 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id	企业融资
qid000058	select T3.名称 , T2.书名 , T2.作者 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id	购书平台
qid000059	select T3.名称 , T2.书名 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id	购书平台
qid000060	select T3.名称 , T3.年营业额 , T2.书名 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id	购书平台
qid000061	select T3.名称 , T2.姓名 , T2.性别 , T1.职位 from 人物公司职位 as T1 join 企业人物 as T2 join 公司 as T3 on 人物公司职位.人物id == 企业人物.词条id and 人物公司职位.公司id == 公司.词条id	CCTV中国经济年度人物
qid000062	select T3.名称 , T2.姓名 , T1.职位 from 人物公司职位 as T1 join 企业人物 as T2 join 公司 as T3 on 人物公司职位.人物id == 企业人物.词条id and 人物公司职位.公司id == 公司.词条id	CCTV中国经济年度人物
qid000063	select T3.名称 , T3.年营业额 , T2.姓名 , T1.职位 from 人物公司职位 as T1 join 企业人物 as T2 join 公司 as T3 on 人物公司职位.人物id == 企业人物.词条id and 人物公司职位.公司id == 公司.词条id	CCTV中国经济年度人物
qid000064	select T3.名称 , T2.姓名 , T2.年龄 , T1.职位 from 人物公司职位 as T1 join 企业人物 as T2 join 公司 as T3 on 人物公司职位.人物id == 企业人物.词条id and 人物公司职位.公司id == 公司.词条id	CCTV中国经济年度人物
qid000065	select T2.名称 , T2.饱和脂肪含量 , T1.季节 from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.营业收入 >= 300000000	坚果
qid000066	select T2.名称 , T2.饱和脂肪含量 , T1.季节 from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.营业收入 < 500000000	坚果
qid000067	select T2.名称 , T2.饱和脂肪含量 , T1.季节 from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.营业收入 > 300000000	坚果
qid000068	select T2.名称 , T2.饱和脂肪含量 , T1.季节 from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.营业收入 <= 500000000	坚果
qid000069	select T2.名称 , T2.所属洲 , T1.举办城市 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 < 205	奥运会参赛队伍
qid000070	select T2.名称 , T2.所属洲 , T1.举办城市 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 <= 205	奥运会参赛队伍
qid000071	select T2.名称 , T2.所属洲 , T1.举办城市 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 >= 205	奥运会参赛队伍
qid000072	select T2.名称 , T2.所属洲 , T1.举办城市 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 > 205	奥运会参赛队伍
qid000073	select T2.中文名 , T2.注册资本 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 < 10000000	企业融资
qid000074	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 < 10000000	企业融资
qid000075	select T2.中文名 , T2.注册资本 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 > 10000000	企业融资
qid000076	select T2.中文名 , T2.注册资本 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 >= 10000000	企业融资
qid000077	select T2.名称 , T2.市场份额 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 < 3000	洗衣机
qid000078	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 <= 3000	洗衣机
qid000079	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 < 3000	洗衣机
qid000080	select T2.名称 , T2.市场份额 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 <= 3000	洗衣机
qid000081	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 < 500	洗衣机
qid000082	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 > 500	洗衣机
qid000083	select T2.名称 , T2.市场份额 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 >= 500	洗衣机
qid000084	select T2.名称 , T2.市场份额 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 < 500	洗衣机
qid000085	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 <= 1000000000	企业融资
qid000086	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 < 1000000000	企业融资
qid000087	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 > 1000000000	企业融资
qid000088	select T2.中文名 , T2.注册资本 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 < 1000000000	企业融资
qid000089	select T2.中文名 , T2.年龄 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 <= 40	运动员比赛记录
qid000090	select T2.中文名 , T2.年龄 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 >= 40	运动员比赛记录
qid000091	select T2.中文名 , T2.年龄 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 > 40	运动员比赛记录
qid000092	select T2.中文名 , T2.年龄 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 < 40	运动员比赛记录
qid000093	select T2.名称 , T2.饱和脂肪含量 , T1.产地 from 坚果产地 as T1 join 坚果 as T2 on 坚果产地.坚果id == 坚果.词条id where T1.市场占比 <= 0.44	坚果
qid000094	select T2.名称 , T2.饱和脂肪含量 , T1.产地 from 坚果产地 as T1 join 坚果 as T2 on 坚果产地.坚果id == 坚果.词条id where T1.市场占比 < 0.44	坚果
qid000095	select T2.名称 , T2.饱和脂肪含量 , T1.产地 from 坚果产地 as T1 join 坚果 as T2 on 坚果产地.坚果id == 坚果.词条id where T1.市场占比 > 0.44	坚果
qid000096	select T2.名称 , T2.饱和脂肪含量 , T1.产地 from 坚果产地 as T1 join 坚果 as T2 on 坚果产地.坚果id == 坚果.词条id where T1.市场占比 >= 0.44	坚果
qid000097	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 <= 10000000 and T2.注册资本 > 1000000	企业融资
qid000098	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 >= 10000000 and T2.注册资本 < 1000000	企业融资
qid000099	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 > 10000000 and T2.注册资本 < 1000000	企业融资
qid000100	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 > 10000000 and T2.注册资本 >= 1000000	企业融资
qid000101	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 > 10000000 and T2.注册资本 > 1000000	企业融资
qid000102	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 <= 10000000 and T2.注册资本 >= 1000000	企业融资
qid000103	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 > 10000000 and T2.注册资本 <= 1000000	企业融资
qid000104	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 < 10000000 and T2.注册资本 <= 1000000	企业融资
qid000105	select T2.中文名 , T2.法定代表人 , T1.投资公司 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T1.融资额 < 10000000 and T2.注册资本 > 1000000	企业融资
qid000106	select T2.中文名 , T2.场上位置 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 < 40 and T2.年龄 <= 25	运动员比赛记录
qid000107	select T2.中文名 , T2.场上位置 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 < 40 and T2.年龄 < 25	运动员比赛记录
qid000108	select T2.中文名 , T2.场上位置 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 > 40 and T2.年龄 >= 25	运动员比赛记录
qid000109	select T2.中文名 , T2.场上位置 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 <= 40 and T2.年龄 < 25	运动员比赛记录
qid000110	select T2.中文名 , T2.场上位置 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 >= 40 and T2.年龄 <= 25	运动员比赛记录
qid000111	select T2.中文名 , T2.场上位置 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 < 40 and T2.年龄 > 25	运动员比赛记录
qid000112	select T2.中文名 , T2.场上位置 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 >= 40 and T2.年龄 > 25	运动员比赛记录
qid000113	select T2.中文名 , T2.场上位置 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 > 40 and T2.年龄 < 25	运动员比赛记录
qid000114	select T2.中文名 , T2.场上位置 , T1.赛季 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T1.出场次数 < 40 and T2.年龄 >= 25	运动员比赛记录
qid000115	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 >= 3000 and T2.市场份额 > 0.102	洗衣机
qid000116	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 < 3000 and T2.市场份额 > 0.102	洗衣机
qid000117	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 >= 3000 and T2.市场份额 < 0.102	洗衣机
qid000118	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 >= 3000 and T2.市场份额 >= 0.102	洗衣机
qid000119	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 < 3000 and T2.市场份额 <= 0.102	洗衣机
qid000120	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 <= 3000 and T2.市场份额 > 0.102	洗衣机
qid000121	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 > 3000 and T2.市场份额 < 0.102	洗衣机
qid000122	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 > 3000 and T2.市场份额 > 0.102	洗衣机
qid000123	select T2.名称 , T2.所属公司 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 >= 3000 and T2.市场份额 <= 0.102	洗衣机
qid000124	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 < 500 and T2.市场份额 <= 0.102	洗衣机
qid000125	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 > 500 and T2.市场份额 >= 0.102	洗衣机
qid000126	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 > 500 and T2.市场份额 <= 0.102	洗衣机
qid000127	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 >= 500 and T2.市场份额 <= 0.102	洗衣机
qid000128	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 < 500 and T2.市场份额 >= 0.102	洗衣机
qid000129	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 < 500 and T2.市场份额 < 0.102	洗衣机
qid000130	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 >= 500 and T2.市场份额 >= 0.102	洗衣机
qid000131	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 <= 500 and T2.市场份额 > 0.102	洗衣机
qid000132	select T2.名称 , T2.所属公司 , T1.城市 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.门店数量 > 500 and T2.市场份额 < 0.102	洗衣机
qid000133	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 <= 1000000000 and T2.注册资本 > 1000000	企业融资
qid000134	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 > 1000000000 and T2.注册资本 < 1000000	企业融资
qid000135	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 > 1000000000 and T2.注册资本 >= 1000000	企业融资
qid000136	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 >= 1000000000 and T2.注册资本 > 1000000	企业融资
qid000137	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 >= 1000000000 and T2.注册资本 <= 1000000	企业融资
qid000138	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 >= 1000000000 and T2.注册资本 >= 1000000	企业融资
qid000139	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 < 1000000000 and T2.注册资本 > 1000000	企业融资
qid000140	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 < 1000000000 and T2.注册资本 < 1000000	企业融资
qid000141	select T2.中文名 , T2.法定代表人 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T1.融资总额 > 1000000000 and T2.注册资本 <= 1000000	企业融资
qid000142	select avg ( T2.饱和脂肪含量 ) , sum ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.全年占比 <= 0.15 and T2.每100克热量 <= 212	坚果
qid000143	select min ( T2.饱和脂肪含量 ) , min ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.全年占比 > 0.15 and T2.每100克热量 < 212	坚果
qid000144	select sum ( T2.饱和脂肪含量 ) , min ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.全年占比 <= 0.15 and T2.每100克热量 <= 212	坚果
qid000145	select avg ( T2.饱和脂肪含量 ) , sum ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.全年占比 > 0.15 and T2.每100克热量 < 212	坚果
qid000146	select max ( T2.饱和脂肪含量 ) , min ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.全年占比 <= 0.15 and T2.不饱和脂肪含量 > 33	坚果
qid000147	select max ( T2.饱和脂肪含量 ) , max ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id where T1.全年占比 > 0.15 and T2.每100克热量 < 212	坚果
qid000148	select max ( T2.年营业额 ) , min ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T1.会员价格 >= 5.99 and T2.会员费 > 150	购书平台
qid000149	select avg ( T2.年营业额 ) , min ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T1.购买人数 > 100 and T2.会员费 > 150	购书平台
qid000150	select max ( T2.年营业额 ) , max ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T1.会员价格 >= 5.99 and T2.会员费 < 150	购书平台
qid000151	select sum ( T2.年营业额 ) , avg ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T1.购买人数 <= 100 and T2.会员费 >= 150	购书平台
qid000152	select sum ( T2.年营业额 ) , avg ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T1.会员价格 < 5.99 and T2.会员费 >= 150	购书平台
qid000153	select avg ( T2.年营业额 ) , min ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T1.会员价格 < 5.99 and T2.会员费 <= 150	购书平台
qid000154	select min ( T2.年营业额 ) , max ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T1.加入购物车人数 >= 540000 and T2.会员费 < 150	购书平台
qid000155	select avg ( T2.年营业额 ) , min ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T1.购买人数 >= 50000 and T2.会员费 <= 150	购书平台
qid000156	select max ( T2.年营业额 ) , max ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T1.购买人数 >= 50000 and T2.会员费 <= 150	购书平台
qid000157	select sum ( T2.年营业额 ) , min ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T1.评分 < 5 and T2.会员费 < 150	购书平台
qid000158	select max ( T2.年营业额 ) , sum ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T1.购买人数 < 50000 and T2.会员费 < 150	购书平台
qid000159	select max ( T2.年营业额 ) , max ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T1.评分人数 <= 1000 and T2.会员费 >= 150	购书平台
qid000160	select avg ( T2.饱和脂肪含量 ) , sum ( T1.人均摄入量 ) from 坚果摄入量 as T1 join 坚果 as T2 on 坚果摄入量.坚果id == 坚果.词条id where T1.世界人均摄入量 >= 0.09 and T2.不饱和脂肪含量 >= 33	坚果
qid000161	select max ( T2.饱和脂肪含量 ) , min ( T1.人均摄入量 ) from 坚果摄入量 as T1 join 坚果 as T2 on 坚果摄入量.坚果id == 坚果.词条id where T1.世界人均摄入量 > 0.09 and T2.不饱和脂肪含量 <= 33	坚果
qid000162	select sum ( T2.饱和脂肪含量 ) , sum ( T1.人均摄入量 ) from 坚果摄入量 as T1 join 坚果 as T2 on 坚果摄入量.坚果id == 坚果.词条id where T1.世界人均摄入量 < 0.09 and T2.不饱和脂肪含量 <= 33	坚果
qid000163	select min ( T2.饱和脂肪含量 ) , max ( T1.人均摄入量 ) from 坚果摄入量 as T1 join 坚果 as T2 on 坚果摄入量.坚果id == 坚果.词条id where T1.世界人均摄入量 <= 0.09 and T2.不饱和脂肪含量 > 33	坚果
qid000164	select min ( T2.饱和脂肪含量 ) , min ( T1.人均摄入量 ) from 坚果摄入量 as T1 join 坚果 as T2 on 坚果摄入量.坚果id == 坚果.词条id where T1.世界人均摄入量 <= 0.09 and T2.每100克热量 <= 212	坚果
qid000165	select avg ( T2.饱和脂肪含量 ) , max ( T1.人均摄入量 ) from 坚果摄入量 as T1 join 坚果 as T2 on 坚果摄入量.坚果id == 坚果.词条id where T1.世界人均摄入量 >= 0.09 and T2.不饱和脂肪含量 > 33	坚果
qid000166	select max ( T2.市场份额 ) , max ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.售卖量 < 5000000 and T2.2018年营业额 < 200700000000	洗衣机
qid000167	select sum ( T2.市场份额 ) , sum ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.售卖量 < 5000000 and T2.2018年利润 <= 15000000000	洗衣机
qid000168	select min ( T2.市场份额 ) , sum ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.售卖量 > 5000000 and T2.2018年营业额 <= 200700000000	洗衣机
qid000169	select sum ( T2.市场份额 ) , max ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.售卖量 <= 5000000 and T2.2018年营业额 >= 200700000000	洗衣机
qid000170	select max ( T2.市场份额 ) , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.售卖量 <= 5000000 and T2.2018年利润 >= 15000000000	洗衣机
qid000171	select sum ( T2.市场份额 ) , min ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T1.售卖量 <= 5000000 and T2.2018年利润 > 15000000000	洗衣机
qid000172	select min ( T2.覆盖城市数 ) , sum ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车APP as T2 on 各打车APP支持的方式.appid == 打车APP.词条id where T1.市场份额 >= 0.1 and T2.服务用户数量 < 10000000	打车软件
qid000173	select min ( T2.覆盖城市数 ) , min ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车APP as T2 on 各打车APP支持的方式.appid == 打车APP.词条id where T1.市场份额 >= 0.1 and T2.服务用户数量 >= 10000000	打车软件
qid000174	select max ( T2.覆盖城市数 ) , min ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车APP as T2 on 各打车APP支持的方式.appid == 打车APP.词条id where T1.每日打车单数 >= 100000 and T2.服务用户数量 < 10000000	打车软件
qid000175	select max ( T2.覆盖城市数 ) , sum ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车APP as T2 on 各打车APP支持的方式.appid == 打车APP.词条id where T1.市场份额 < 0.1 and T2.服务用户数量 > 10000000	打车软件
qid000176	select avg ( T2.覆盖城市数 ) , max ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车APP as T2 on 各打车APP支持的方式.appid == 打车APP.词条id where T1.每日营收 <= 100000 and T2.服务用户数量 < 10000000	打车软件
qid000177	select sum ( T2.覆盖城市数 ) , avg ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车APP as T2 on 各打车APP支持的方式.appid == 打车APP.词条id where T1.市场份额 >= 0.1 and T2.服务用户数量 >= 10000000	打车软件
qid000178	select min ( T2.饱和脂肪含量 ) , max ( T1.消费次数 ) from 坚果中国人均消费 as T1 join 坚果 as T2 on 坚果中国人均消费.坚果id == 坚果.词条id where T1.占比 >= 0.02 and T2.不饱和脂肪含量 <= 33	坚果
qid000179	select max ( T2.饱和脂肪含量 ) , min ( T1.消费次数 ) from 坚果中国人均消费 as T1 join 坚果 as T2 on 坚果中国人均消费.坚果id == 坚果.词条id where T1.占比 <= 0.02 and T2.不饱和脂肪含量 > 33	坚果
qid000180	select min ( T2.饱和脂肪含量 ) , avg ( T1.消费次数 ) from 坚果中国人均消费 as T1 join 坚果 as T2 on 坚果中国人均消费.坚果id == 坚果.词条id where T1.占比 <= 0.02 and T2.不饱和脂肪含量 >= 33	坚果
qid000181	select min ( T2.饱和脂肪含量 ) , sum ( T1.消费次数 ) from 坚果中国人均消费 as T1 join 坚果 as T2 on 坚果中国人均消费.坚果id == 坚果.词条id where T1.占比 >= 0.02 and T2.不饱和脂肪含量 > 33	坚果
qid000182	select max ( T2.饱和脂肪含量 ) , max ( T1.消费次数 ) from 坚果中国人均消费 as T1 join 坚果 as T2 on 坚果中国人均消费.坚果id == 坚果.词条id where T1.占比 < 0.02 and T2.不饱和脂肪含量 > 33	坚果
qid000183	select sum ( T2.饱和脂肪含量 ) , avg ( T1.消费次数 ) from 坚果中国人均消费 as T1 join 坚果 as T2 on 坚果中国人均消费.坚果id == 坚果.词条id where T1.占比 <= 0.02 and T2.每100克热量 >= 212	坚果
qid000184	select T3.名称 , T2.app名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id where T1.每日打车单数 <= 100000	打车软件
qid000185	select T3.名称 , T2.app名称 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id where T1.车数量 >= 100000	打车软件
qid000186	select T3.名称 , T2.app名称 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id where T1.车数量 >= 100000	打车软件
qid000187	select T3.名称 , T2.app名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id where T1.市场份额 >= 0.1	打车软件
qid000188	select T3.名称 , T2.app名称 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id where T1.车数量 <= 100000	打车软件
qid000189	select T3.名称 , T2.app名称 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id where T1.车数量 < 100000	打车软件
qid000190	select T3.名称 , T2.app名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id where T1.每日打车单数 < 100000	打车软件
qid000191	select T3.名称 , T2.书名 , T1.售价 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id where T1.购买人数 < 50000	购书平台
qid000192	select T3.名称 , T2.书名 , T1.售价 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id where T1.购买人数 > 50000	购书平台
qid000193	select T3.名称 , T2.书名 , T1.售价 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id where T1.收藏人数 >= 23000	购书平台
qid000194	select T3.名称 , T2.书名 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id where T1.会员价格 < 5.99	购书平台
qid000195	select T3.名称 , T2.书名 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id where T1.会员价格 > 5.99	购书平台
qid000196	select T3.名称 , T2.书名 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id where T1.购买人数 >= 100	购书平台
qid000197	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 < 205 order by T1.小项项目数 asc	奥运会参赛队伍
qid000198	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 <= 205 order by T1.参赛运动员数量 desc	奥运会参赛队伍
qid000199	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 > 205 order by T1.小项项目数 asc	奥运会参赛队伍
qid000200	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 > 205 order by T1.小项项目数 desc	奥运会参赛队伍
qid000201	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 >= 205 order by T1.参赛运动员数量 desc	奥运会参赛队伍
qid000202	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 < 205 order by T1.小项项目数 desc	奥运会参赛队伍
qid000203	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 < 205 order by T1.大项项目数 desc limit 3	奥运会参赛队伍
qid000204	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 >= 205 order by T1.大项项目数 desc limit 3	奥运会参赛队伍
qid000205	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 <= 205 order by T1.参赛运动员数量 desc limit 3	奥运会参赛队伍
qid000206	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 <= 205 order by T1.小项项目数 asc limit 3	奥运会参赛队伍
qid000207	select T1.名称 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 > 205 order by T1.小项项目数 desc limit 3	奥运会参赛队伍
qid000208	select T1.名称 , T1.举办城市 , T2.名称 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 <= 205 order by T1.参赛运动员数量 asc limit 3	奥运会参赛队伍
qid000209	select T1.名称 , T1.参赛国家数量 , T2.名称 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛运动员数量 >= 311 order by T1.参赛国家数量 asc limit 3	奥运会参赛队伍
qid000210	select T1.名称 , T1.举办城市 , T2.名称 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 >= 205 order by T1.大项项目数 asc limit 3	奥运会参赛队伍
qid000211	select T1.名称 , T1.举办城市 , T2.名称 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 < 205 order by T1.参赛运动员数量 asc limit 3	奥运会参赛队伍
qid000212	select T1.名称 , T1.参赛国家数量 , T2.名称 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 <= 205 order by T1.参赛运动员数量 asc limit 3	奥运会参赛队伍
qid000213	select T2.中文名 , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 > 1000000 group by T1.企业id order by count ( * ) desc limit 5	企业融资
qid000214	select T2.中文名 , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 >= 1000000 group by T1.企业id order by count ( * ) desc limit 1	企业融资
qid000215	select T2.中文名 , T2.场上位置 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id where T2.年龄 <= 25 group by T1.球员id order by count ( * ) desc limit 5	运动员比赛记录
qid000216	select T2.中文名 , T2.场上位置 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id where T2.年龄 < 25 group by T1.球员id order by count ( * ) asc limit 1	运动员比赛记录
qid000217	select T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id order by sum ( T1.售价 ) asc limit 1	洗衣机
qid000218	select T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id order by avg ( T1.售价 ) desc limit 1	洗衣机
qid000219	select T2.名称 , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id order by count ( * ) desc limit 5	洗衣机
qid000220	select T2.名称 , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id order by count ( * ) desc limit 1	洗衣机
qid000221	select T2.姓名 , T2.性别 from 历届经济人物获奖名单 as T1 join 企业人物 as T2 on 历届经济人物获奖名单.获奖人id == 企业人物.词条id where T2.年龄 > 50 group by T1.获奖人id order by count ( * ) asc limit 1	CCTV中国经济年度人物
qid000222	select T2.姓名 , T2.性别 from 历届经济人物获奖名单 as T1 join 企业人物 as T2 on 历届经济人物获奖名单.获奖人id == 企业人物.词条id where T2.年龄 >= 50 group by T1.获奖人id order by count ( * ) desc limit 5	CCTV中国经济年度人物
qid000223	select T2.名称 , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 > 12 group by T1.方式id order by sum ( T1.车数量 ) desc limit 1	打车软件
qid000224	select T2.名称 , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 >= 12 group by T1.方式id order by sum ( T1.车数量 ) asc limit 1	打车软件
qid000225	select T2.名称 , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id order by avg ( T1.总评分 ) asc limit 1	洗衣机
qid000226	select T2.名称 , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id order by avg ( T1.总评分 ) asc limit 1	洗衣机
qid000227	select T2.名称 , T2.类型 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id where T2.适用年级 <= 3 group by T1.试卷id order by count ( * ) desc limit 1	教材辅助参考书
qid000228	select T2.名称 , T2.类型 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id where T2.适用年级 > 3 group by T1.试卷id order by count ( * ) desc limit 5	教材辅助参考书
qid000229	select T2.中文名 , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 > 25 group by T1.球员id order by avg ( T1.出场次数 ) asc limit 1	运动员比赛记录
qid000230	select T2.中文名 , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 >= 25 group by T1.球员id order by count ( * ) asc limit 1	运动员比赛记录
qid000231	select T2.姓名 , T2.性别 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id where T2.年龄 <= 50 group by T1.人物id order by count ( * ) asc limit 5	CCTV中国经济年度人物
qid000232	select T2.姓名 , T2.性别 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id where T2.年龄 > 50 group by T1.人物id order by count ( * ) asc limit 5	CCTV中国经济年度人物
qid000233	select T2.中文名 , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 > 1000000 group by T1.企业id order by sum ( T1.融资总额 ) asc limit 1	企业融资
qid000234	select T2.中文名 , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 > 1000000 group by T1.企业id order by avg ( T1.融资总额 ) asc limit 1	企业融资
qid000235	select T2.中文名 , min ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 >= 1000000 group by T1.企业id	企业融资
qid000236	select T2.中文名 , sum ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id	企业融资
qid000237	select T2.中文名 , max ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 > 1000000 group by T1.企业id	企业融资
qid000238	select T2.中文名 , avg ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 < 1000000 group by T1.企业id	企业融资
qid000239	select T2.中文名 , sum ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 >= 1000000 group by T1.企业id	企业融资
qid000240	select T2.名称 , max ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid000241	select T2.名称 , sum ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid000242	select T2.名称 , sum ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid000243	select T2.名称 , max ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid000244	select T2.名称 , min ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id	洗衣机
qid000245	select T2.名称 , min ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid000246	select T2.名称 , max ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id	洗衣机
qid000247	select T2.名称 , max ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id	洗衣机
qid000248	select T2.名称 , min ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid000249	select T2.名称 , max ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid000250	select T2.名称 , max ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 <= 12 group by T1.方式id	打车软件
qid000251	select T2.名称 , avg ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 < 12 group by T1.方式id	打车软件
qid000252	select T2.名称 , min ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 <= 12 group by T1.方式id	打车软件
qid000253	select T2.名称 , sum ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 > 12 group by T1.方式id	打车软件
qid000254	select T2.名称 , max ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 >= 12 group by T1.方式id	打车软件
qid000255	select T2.名称 , avg ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid000256	select T2.名称 , sum ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid000257	select T2.名称 , avg ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id	洗衣机
qid000258	select T2.名称 , min ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id	洗衣机
qid000259	select T2.名称 , sum ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid000260	select T2.中文名 , sum ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 >= 25 group by T1.球员id	运动员比赛记录
qid000261	select T2.中文名 , sum ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 < 25 group by T1.球员id	运动员比赛记录
qid000262	select T2.中文名 , min ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 <= 25 group by T1.球员id	运动员比赛记录
qid000263	select T2.中文名 , avg ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 >= 25 group by T1.球员id	运动员比赛记录
qid000264	select T2.中文名 , max ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 > 25 group by T1.球员id	运动员比赛记录
qid000265	select T2.中文名 , max ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id	企业融资
qid000266	select T2.中文名 , min ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id	企业融资
qid000267	select T2.中文名 , sum ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 > 1000000 group by T1.企业id	企业融资
qid000268	select T2.中文名 , min ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 >= 1000000 group by T1.企业id	企业融资
qid000269	select T2.中文名 , max ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 > 1000000 group by T1.企业id	企业融资
qid000270	select T2.中文名 , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id having sum ( T1.融资额 ) > 800000000	企业融资
qid000271	select T2.中文名 , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 >= 1000000 group by T1.企业id having count ( * ) >= 5	企业融资
qid000272	select T2.中文名 , T2.场上位置 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id where T2.年龄 > 25 group by T1.球员id having count ( * ) < 5	运动员比赛记录
qid000273	select T2.中文名 , T2.场上位置 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id where T2.年龄 > 25 group by T1.球员id having count ( * ) > 5	运动员比赛记录
qid000274	select T2.名称 , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 <= 12 group by T1.方式id having sum ( T1.车数量 ) < 50000	打车软件
qid000275	select T2.名称 , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 >= 12 group by T1.方式id having count ( * ) == 5	打车软件
qid000276	select T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id having sum ( T1.售价 ) > 5000	洗衣机
qid000277	select T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id having count ( * ) < 5	洗衣机
qid000278	select T2.名称 , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id having sum ( T1.门店数量 ) <= 500	洗衣机
qid000279	select T2.名称 , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id having avg ( T1.门店数量 ) < 500	洗衣机
qid000280	select T2.中文名 , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id having avg ( T1.融资总额 ) < 500000000	企业融资
qid000281	select T2.中文名 , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 >= 1000000 group by T1.企业id having count ( * ) <= 5	企业融资
qid000282	select T2.姓名 , T2.性别 from 历届经济人物获奖名单 as T1 join 企业人物 as T2 on 历届经济人物获奖名单.获奖人id == 企业人物.词条id where T2.年龄 < 50 group by T1.获奖人id having count ( * ) > 5	CCTV中国经济年度人物
qid000283	select T2.姓名 , T2.性别 from 历届经济人物获奖名单 as T1 join 企业人物 as T2 on 历届经济人物获奖名单.获奖人id == 企业人物.词条id where T2.年龄 > 50 group by T1.获奖人id having count ( * ) <= 5	CCTV中国经济年度人物
qid000284	select T2.名称 , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id having avg ( T1.总评分 ) >= 80	洗衣机
qid000285	select T2.名称 , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id having sum ( T1.总评分 ) > 200	洗衣机
qid000286	select T2.名称 , T2.类型 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id where T2.适用年级 < 3 group by T1.试卷id having count ( * ) > 5	教材辅助参考书
qid000287	select T2.名称 , T2.类型 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id where T2.适用年级 < 3 group by T1.试卷id having count ( * ) == 5	教材辅助参考书
qid000288	select T2.中文名 , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 < 25 group by T1.球员id having count ( * ) == 5	运动员比赛记录
qid000289	select T2.中文名 , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 >= 25 group by T1.球员id having sum ( T1.出场次数 ) < 10	运动员比赛记录
qid000290	select T2.姓名 , T2.性别 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id where T2.年龄 <= 50 group by T1.人物id having count ( * ) == 5	CCTV中国经济年度人物
qid000291	select T2.姓名 , T2.性别 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id where T2.年龄 >= 50 group by T1.人物id having count ( * ) >= 5	CCTV中国经济年度人物
qid000292	select T2.名称 , max ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T2.年营业额 < 7177800000000 group by T1.平台id having count ( * ) <= 5	购书平台
qid000293	select T2.名称 , avg ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T2.年营业额 < 7177800000000 group by T1.平台id having sum ( T1.评分人数 ) >= 100	购书平台
qid000294	select T2.中文名 , max ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 < 1000000 group by T1.企业id having count ( * ) < 5	企业融资
qid000295	select T2.中文名 , sum ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 < 1000000 group by T1.企业id having avg ( T1.投资公司持股比例 ) < 0.75	企业融资
qid000296	select T2.名称 , min ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 <= 12 group by T1.方式id having avg ( T1.每日打车单数 ) > 8000	打车软件
qid000297	select T2.名称 , min ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 > 12 group by T1.方式id having sum ( T1.每日打车单数 ) < 100000	打车软件
qid000298	select T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id having count ( * ) == 5	洗衣机
qid000299	select T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id having count ( * ) <= 5	洗衣机
qid000300	select T2.名称 , sum ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id having count ( * ) == 5	洗衣机
qid000301	select T2.名称 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id having sum ( T1.售卖量 ) <= 100000	洗衣机
qid000302	select T2.中文名 , sum ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id having count ( * ) <= 5	企业融资
qid000303	select T2.中文名 , avg ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id having count ( * ) >= 5	企业融资
qid000304	select T2.名称 , max ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id having count ( * ) < 5	洗衣机
qid000305	select T2.名称 , min ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id having avg ( T1.功能得分 ) <= 6.5	洗衣机
qid000306	select T2.中文名 , max ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 > 25 group by T1.球员id having count ( * ) >= 5	运动员比赛记录
qid000307	select T2.中文名 , min ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 <= 25 group by T1.球员id having avg ( T1.犯规 ) > 9	运动员比赛记录
qid000308	select T2.名称 , avg ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T2.年营业额 >= 7177800000000 and T2.会员费 >= 150 group by T1.平台id having count ( * ) == 5	购书平台
qid000309	select T2.名称 , sum ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年利润 >= 15000000000 group by T1.品牌id having count ( * ) > 5	洗衣机
qid000310	select T2.名称 , min ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年利润 <= 15000000000 group by T1.品牌id having count ( * ) < 5	洗衣机
qid000311	select T2.名称 , min ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年利润 >= 15000000000 group by T1.品牌id having count ( * ) <= 5	洗衣机
qid000312	select T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年营业额 >= 200700000000 group by T1.品牌id having count ( * ) <= 5	洗衣机
qid000313	select T2.名称 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年利润 < 15000000000 group by T1.品牌id having count ( * ) == 5	洗衣机
qid000314	select T2.名称 , max ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T2.年营业额 >= 7177800000000 or T2.会员费 <= 150 group by T1.平台id having count ( * ) > 5	购书平台
qid000315	select T2.名称 , sum ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T2.年营业额 <= 7177800000000 or T2.会员费 < 150 group by T1.平台id having count ( * ) > 5	购书平台
qid000316	select T2.名称 , max ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T2.年营业额 > 7177800000000 or T2.会员费 >= 150 group by T1.平台id having count ( * ) > 5	购书平台
qid000317	select T2.名称 , min ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T2.年营业额 > 7177800000000 or T2.会员费 >= 150 group by T1.平台id having count ( * ) >= 5	购书平台
qid000318	select T2.名称 , sum ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 or T2.2018年利润 <= 15000000000 group by T1.品牌id having count ( * ) > 5	洗衣机
qid000319	select T2.名称 , avg ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 or T2.2018年利润 <= 15000000000 group by T1.品牌id having count ( * ) > 5	洗衣机
qid000320	select T2.名称 , min ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 or T2.2018年利润 >= 15000000000 group by T1.品牌id having count ( * ) > 5	洗衣机
qid000321	select T2.名称 , sum ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 or T2.2018年利润 <= 15000000000 group by T1.品牌id having count ( * ) > 5	洗衣机
qid000322	select T2.所属洲 , T2.名称 , max ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id	奥运会参赛队伍
qid000323	select T2.所属洲 , T2.名称 , sum ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id	奥运会参赛队伍
qid000324	select T2.所属洲 , T2.名称 , avg ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id	奥运会参赛队伍
qid000325	select T2.所属洲 , T2.名称 , min ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id	奥运会参赛队伍
qid000326	select T2.作者 , T2.书名 , max ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id	购书平台
qid000327	select T2.作者 , T2.书名 , avg ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id	购书平台
qid000328	select T2.作者 , T2.书名 , sum ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id	购书平台
qid000329	select T2.作者 , T2.书名 , min ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id	购书平台
qid000330	select T2.法定代表人 , T2.中文名 , avg ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id	企业融资
qid000331	select T2.法定代表人 , T2.中文名 , sum ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id	企业融资
qid000332	select T2.法定代表人 , T2.中文名 , min ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id	企业融资
qid000333	select T2.法定代表人 , T2.中文名 , max ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id	企业融资
qid000334	select T2.理念 , T2.名称 , max ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id	打车软件
qid000335	select T2.理念 , T2.名称 , min ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id	打车软件
qid000336	select T2.理念 , T2.名称 , sum ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id	打车软件
qid000337	select T2.理念 , T2.名称 , avg ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id	打车软件
qid000338	select T2.所属公司 , T2.名称 , sum ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000339	select T2.所属公司 , T2.名称 , min ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000340	select T2.所属公司 , T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000341	select T2.所属公司 , T2.名称 , max ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000342	select T2.所属公司 , T2.名称 , min ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000343	select T2.所属公司 , T2.名称 , sum ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000344	select T2.所属公司 , T2.名称 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000345	select T2.所属公司 , T2.名称 , max ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000346	select T2.法定代表人 , T2.中文名 , sum ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id	企业融资
qid000347	select T2.法定代表人 , T2.中文名 , max ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id	企业融资
qid000348	select T2.法定代表人 , T2.中文名 , min ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id	企业融资
qid000349	select T2.法定代表人 , T2.中文名 , avg ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id	企业融资
qid000350	select T2.所属公司 , T2.名称 , max ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000351	select T2.所属公司 , T2.名称 , sum ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000352	select T2.所属公司 , T2.名称 , avg ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000353	select T2.所属公司 , T2.名称 , min ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid000354	select T2.所属洲 , T2.名称 , sum ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id	奥运会参赛队伍
qid000355	select T2.所属洲 , T2.名称 , min ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id	奥运会参赛队伍
qid000356	select T2.所属洲 , T2.名称 , avg ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id	奥运会参赛队伍
qid000357	select T2.所属洲 , T2.名称 , max ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id	奥运会参赛队伍
qid000358	select T2.所属地区 , T2.中文队名 , avg ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id	欧洲杯球队
qid000359	select T2.所属地区 , T2.中文队名 , max ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id	欧洲杯球队
qid000360	select T2.所属地区 , T2.中文队名 , sum ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id	欧洲杯球队
qid000361	select T2.所属地区 , T2.中文队名 , min ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id	欧洲杯球队
qid000362	select T2.场上位置 , T2.中文名 , max ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id	运动员比赛记录
qid000363	select T2.场上位置 , T2.中文名 , min ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id	运动员比赛记录
qid000364	select T2.场上位置 , T2.中文名 , sum ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id	运动员比赛记录
qid000365	select T2.场上位置 , T2.中文名 , avg ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id	运动员比赛记录
qid000366	select T2.性别 , T2.姓名 from 历届经济人物获奖名单 as T1 join 企业人物 as T2 on 历届经济人物获奖名单.获奖人id == 企业人物.词条id group by T1.获奖人id having count ( * ) >= 5	CCTV中国经济年度人物
qid000367	select T2.性别 , T2.姓名 from 历届经济人物获奖名单 as T1 join 企业人物 as T2 on 历届经济人物获奖名单.获奖人id == 企业人物.词条id group by T1.获奖人id having count ( * ) == 5	CCTV中国经济年度人物
qid000368	select T2.类型 , T2.名称 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id group by T1.试卷id having count ( * ) <= 5	教材辅助参考书
qid000369	select T2.类型 , T2.名称 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id group by T1.试卷id having count ( * ) == 5	教材辅助参考书
qid000370	select T2.所属公司 , T2.名称 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) > 5	洗衣机
qid000371	select T2.所属公司 , T2.名称 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id having avg ( T1.售价 ) >= 1500	洗衣机
qid000372	select T2.理念 , T2.名称 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id having avg ( T1.车数量 ) <= 50	打车软件
qid000373	select T2.理念 , T2.名称 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id having sum ( T1.车数量 ) < 100	打车软件
qid000374	select T2.所属地区 , T2.中文队名 from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id having count ( * ) < 5	欧洲杯球队
qid000375	select T2.所属地区 , T2.中文队名 from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id having avg ( T1.届数 ) >= 5	欧洲杯球队
qid000376	select T2.性别 , T2.姓名 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id group by T1.人物id having count ( * ) <= 5	CCTV中国经济年度人物
qid000377	select T2.性别 , T2.姓名 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id group by T1.人物id having count ( * ) >= 5	CCTV中国经济年度人物
qid000378	select T2.民族 , T2.姓名 from 综艺节目嘉宾 as T1 join 明星 as T2 on 综艺节目嘉宾.明星id == 明星.词条id group by T1.明星id having count ( * ) >= 5	综艺节目
qid000379	select T2.民族 , T2.姓名 from 综艺节目嘉宾 as T1 join 明星 as T2 on 综艺节目嘉宾.明星id == 明星.词条id group by T1.明星id having count ( * ) == 5	综艺节目
qid000380	select T2.所属地区 , T2.中文队名 from 欧冠冠亚军 as T1 join 球队 as T2 on 欧冠冠亚军.亚军球队id == 球队.词条id group by T1.亚军球队id having count ( * ) <= 5	欧洲杯球队
qid000381	select T2.所属地区 , T2.中文队名 from 欧冠冠亚军 as T1 join 球队 as T2 on 欧冠冠亚军.冠军球队id == 球队.词条id group by T1.冠军球队id having count ( * ) <= 5	欧洲杯球队
qid000382	select T2.类别 , T2.名称 from 高校属性 as T1 join 高校 as T2 on 高校属性.高校id == 高校.词条id group by T1.高校id having count ( * ) >= 5	中国高校
qid000383	select T2.类别 , T2.名称 from 高校属性 as T1 join 高校 as T2 on 高校属性.高校id == 高校.词条id group by T1.高校id having count ( * ) > 5	中国高校
qid000384	select T2.类别 , T2.名称 from 名人 as T1 join 高校 as T2 on 名人.高校id == 高校.词条id group by T1.高校id having count ( * ) <= 5	中国高校
qid000385	select T2.类别 , T2.名称 from 名人 as T1 join 高校 as T2 on 名人.高校id == 高校.词条id group by T1.高校id having count ( * ) < 5	中国高校
qid000386	select T2.所属洲 , T2.名称 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id having count ( * ) > 5	奥运会参赛队伍
qid000387	select T2.所属洲 , T2.名称 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id having avg ( T1.参赛国家数量 ) >= 35	奥运会参赛队伍
qid000388	select T2.法定代表人 , T2.中文名 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id having count ( * ) <= 5	企业融资
qid000389	select T2.法定代表人 , T2.中文名 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id having sum ( T1.融资额 ) >= 6000000	企业融资
qid000390	select T2.场上位置 , T2.中文名 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id group by T1.球员id having count ( * ) <= 5	运动员比赛记录
qid000391	select T2.场上位置 , T2.中文名 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id group by T1.球员id having count ( * ) < 5	运动员比赛记录
qid000392	select T2.所属公司 , T2.名称 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id having avg ( T1.门店数量 ) <= 50	洗衣机
qid000393	select T2.所属公司 , T2.名称 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) < 5	洗衣机
qid000394	select T2.法定代表人 , T2.中文名 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id having sum ( T1.融资总额 ) > 1000000000	企业融资
qid000395	select T2.法定代表人 , T2.中文名 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id having sum ( T1.融资总额 ) < 1000000000	企业融资
qid000396	select T2.场上位置 , T2.中文名 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id having avg ( T1.出场次数 ) >= 10	运动员比赛记录
qid000397	select T2.场上位置 , T2.中文名 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id having count ( * ) > 5	运动员比赛记录
qid000398	select T2.所属省份 , T2.城市 from 对口帮扶城市 as T1 join 城市 as T2 on 对口帮扶城市.帮助城市id == 城市.词条id group by T1.帮助城市id having count ( * ) <= 5	友好城市
qid000399	select T2.所属省份 , T2.城市 from 对口帮扶城市 as T1 join 城市 as T2 on 对口帮扶城市.帮助城市id == 城市.词条id group by T1.帮助城市id having count ( * ) >= 5	友好城市
qid000400	select T2.作者 , T2.书名 from 电子书 as T1 join 图书 as T2 on 电子书.书名id == 图书.词条id group by T1.书名id having sum ( T1.电子书售价 ) > 80	购书平台
qid000401	select T2.作者 , T2.书名 from 电子书 as T1 join 图书 as T2 on 电子书.书名id == 图书.词条id group by T1.书名id having sum ( T1.电子书售价 ) < 80	购书平台
qid000402	select T2.名称 , min ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id group by T1.坚果id having count ( * ) >= 5	坚果
qid000403	select T2.名称 , avg ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id group by T1.坚果id having count ( * ) == 5	坚果
qid000404	select T2.名称 , sum ( T1.枪击事件数量 ) from 枪击事件 as T1 join 国家 as T2 on 枪击事件.国家id == 国家.词条id group by T1.国家id having sum ( T1.受伤人数 ) <= 100	枪击事件
qid000405	select T2.名称 , avg ( T1.枪击事件数量 ) from 枪击事件 as T1 join 国家 as T2 on 枪击事件.国家id == 国家.词条id group by T1.国家id having avg ( T1.受伤人数 ) >= 100	枪击事件
qid000406	select T2.名称 , min ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id having sum ( T1.大项项目数 ) < 100	奥运会参赛队伍
qid000407	select T2.名称 , avg ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id having sum ( T1.小项项目数 ) < 100	奥运会参赛队伍
qid000408	select T2.书名 , avg ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id having sum ( T1.收藏人数 ) > 100	购书平台
qid000409	select T2.书名 , sum ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id having count ( * ) < 5	购书平台
qid000410	select T2.中文名 , avg ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id having avg ( T1.投资公司持股比例 ) < 0.8	企业融资
qid000411	select T2.中文名 , min ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id having count ( * ) < 5	企业融资
qid000412	select T2.名称 , avg ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id having sum ( T1.每日打车单数 ) <= 100	打车软件
qid000413	select T2.名称 , sum ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id having count ( * ) >= 5	打车软件
qid000414	select T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) == 5	洗衣机
qid000415	select T2.名称 , sum ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) == 5	洗衣机
qid000416	select T2.名称 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id having avg ( T1.售卖量 ) == 100	洗衣机
qid000417	select T2.名称 , max ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id having avg ( T1.售卖量 ) > 100	洗衣机
qid000418	select T2.中文名 , max ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id having count ( * ) > 5	企业融资
qid000419	select T2.中文名 , min ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id having count ( * ) <= 5	企业融资
qid000420	select T2.名称 , max ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id group by T1.平台id having sum ( T1.加入购物车人数 ) <= 100	购书平台
qid000421	select T2.名称 , avg ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id group by T1.平台id having count ( * ) == 5	购书平台
qid000422	select T2.名称 , avg ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) > 5	洗衣机
qid000423	select T2.名称 , min ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) > 5	洗衣机
qid000424	select T2.app名称 , sum ( T1.占所在城市份额 ) from 打车软件开通城市 as T1 join 打车APP as T2 on 打车软件开通城市.appid == 打车APP.词条id group by T1.appid having count ( * ) < 5	打车软件
qid000425	select T2.app名称 , min ( T1.占所在城市份额 ) from 打车软件开通城市 as T1 join 打车APP as T2 on 打车软件开通城市.appid == 打车APP.词条id group by T1.appid having count ( * ) >= 5	打车软件
qid000426	select T2.名称 , sum ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id having avg ( T1.铜牌数 ) == 100	奥运会参赛队伍
qid000427	select T2.名称 , max ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id having count ( * ) < 5	奥运会参赛队伍
qid000428	select T2.中文队名 , min ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id having count ( * ) > 5	欧洲杯球队
qid000429	select T2.中文队名 , min ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id having avg ( T1.净胜球 ) == 100	欧洲杯球队
qid000430	select T2.中文名 , min ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id having count ( * ) < 5	运动员比赛记录
qid000431	select T2.中文名 , sum ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id having sum ( T1.投篮 ) >= 100	运动员比赛记录
qid000432	select T2.名称 , min ( T1.线上销售收入 ) from 坚果销售渠道 as T1 join 坚果 as T2 on 坚果销售渠道.坚果id == 坚果.词条id group by T1.坚果id having sum ( T1.线下销售收入 ) > 100	坚果
qid000433	select T2.名称 , sum ( T1.线上销售收入 ) from 坚果销售渠道 as T1 join 坚果 as T2 on 坚果销售渠道.坚果id == 坚果.词条id group by T1.坚果id having sum ( T1.线下销售收入 ) >= 100	坚果
qid000434	select T2.名称 , sum ( T1.市场占比 ) from 坚果产地 as T1 join 坚果 as T2 on 坚果产地.坚果id == 坚果.词条id group by T1.坚果id having count ( * ) > 5	坚果
qid000435	select T2.名称 , sum ( T1.市场占比 ) from 坚果产地 as T1 join 坚果 as T2 on 坚果产地.坚果id == 坚果.词条id group by T1.坚果id having count ( * ) < 5	坚果
qid000436	select T2.app名称 , avg ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车APP as T2 on 各打车APP支持的方式.appid == 打车APP.词条id group by T1.appid having sum ( T1.每日营收 ) <= 100	打车软件
qid000437	select T2.app名称 , sum ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车APP as T2 on 各打车APP支持的方式.appid == 打车APP.词条id group by T1.appid having avg ( T1.每日营收 ) == 100	打车软件
qid000438	select T2.名称 , T2.所属洲 , max ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id order by avg ( T1.小项项目数 ) desc limit 1	奥运会参赛队伍
qid000439	select T2.名称 , T2.所属洲 , min ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id order by avg ( T1.小项项目数 ) asc limit 1	奥运会参赛队伍
qid000440	select T2.书名 , T2.作者 , avg ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id order by count ( * ) desc limit 1	购书平台
qid000441	select T2.书名 , T2.作者 , avg ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id order by count ( * ) asc limit 3	购书平台
qid000442	select T2.中文名 , T2.法定代表人 , sum ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id order by count ( * ) asc limit 1	企业融资
qid000443	select T2.中文名 , T2.法定代表人 , max ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id order by count ( * ) desc limit 3	企业融资
qid000444	select T2.名称 , T2.所属公司 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id order by count ( * ) desc limit 3	洗衣机
qid000445	select T2.名称 , T2.所属公司 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id order by avg ( T1.售卖量 ) desc limit 1	洗衣机
qid000446	select T2.中文名 , T2.法定代表人 , min ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id order by count ( * ) desc limit 3	企业融资
qid000447	select T2.中文名 , T2.法定代表人 , max ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id order by count ( * ) desc limit 3	企业融资
qid000448	select T2.名称 , T2.理念 , avg ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id order by count ( * ) asc limit 1	打车软件
qid000449	select T2.名称 , T2.理念 , max ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id order by count ( * ) desc limit 1	打车软件
qid000450	select T2.名称 , T2.所属公司 , max ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id order by sum ( T1.外观得分 ) asc limit 3	洗衣机
qid000451	select T2.名称 , T2.所属公司 , avg ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id order by count ( * ) desc limit 1	洗衣机
qid000452	select T2.名称 , T2.所属洲 , max ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id order by count ( * ) desc limit 3	奥运会参赛队伍
qid000453	select T2.名称 , T2.所属洲 , sum ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id order by avg ( T1.银牌数 ) desc limit 5	奥运会参赛队伍
qid000454	select T2.中文队名 , T2.所属地区 , max ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id order by avg ( T1.胜次数 ) asc limit 5	欧洲杯球队
qid000455	select T2.中文队名 , T2.所属地区 , min ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id order by count ( * ) asc limit 3	欧洲杯球队
qid000456	select T2.名称 , T2.所属公司 , sum ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id order by count ( * ) asc limit 3	洗衣机
qid000457	select T2.名称 , T2.所属公司 , sum ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id order by count ( * ) desc limit 3	洗衣机
qid000458	select T2.中文名 , T2.场上位置 , max ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id order by sum ( T1.三分球 ) asc limit 3	运动员比赛记录
qid000459	select T2.中文名 , T2.场上位置 , sum ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id order by count ( * ) desc limit 1	运动员比赛记录
qid000460	select T2.名称 , T2.类型 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id group by T1.试卷id order by count ( * ) asc limit 1	教材辅助参考书
qid000461	select T2.名称 , T2.类型 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id group by T1.试卷id order by count ( * ) desc limit 1	教材辅助参考书
qid000462	select T2.名称 , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id order by avg ( T1.车数量 ) desc limit 5	打车软件
qid000463	select T2.名称 , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id order by count ( * ) asc limit 5	打车软件
qid000464	select T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id order by sum ( T1.售价 ) desc limit 1	洗衣机
qid000465	select T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id order by avg ( T1.售价 ) desc limit 1	洗衣机
qid000466	select T2.中文队名 , T2.所属地区 from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id order by sum ( T1.届数 ) asc limit 3	欧洲杯球队
qid000467	select T2.中文队名 , T2.所属地区 from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id order by count ( * ) desc limit 3	欧洲杯球队
qid000468	select T2.姓名 , T2.性别 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id group by T1.人物id order by count ( * ) desc limit 1	CCTV中国经济年度人物
qid000469	select T2.姓名 , T2.性别 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id group by T1.人物id order by count ( * ) desc limit 3	CCTV中国经济年度人物
qid000470	select T2.城市 , T2.所属省份 from 一带一路的中国城市 as T1 join 城市 as T2 on 一带一路的中国城市.城市id == 城市.词条id group by T1.城市id order by count ( * ) desc limit 1	友好城市
qid000471	select T2.城市 , T2.所属省份 from 一带一路的中国城市 as T1 join 城市 as T2 on 一带一路的中国城市.城市id == 城市.词条id group by T1.城市id order by count ( * ) desc limit 3	友好城市
qid000472	select T2.姓名 , T2.民族 from 综艺节目嘉宾 as T1 join 明星 as T2 on 综艺节目嘉宾.明星id == 明星.词条id group by T1.明星id order by count ( * ) asc limit 1	综艺节目
qid000473	select T2.姓名 , T2.民族 from 综艺节目嘉宾 as T1 join 明星 as T2 on 综艺节目嘉宾.明星id == 明星.词条id group by T1.明星id order by count ( * ) desc limit 3	综艺节目
qid000474	select T2.中文队名 , T2.所属地区 from 欧冠冠亚军 as T1 join 球队 as T2 on 欧冠冠亚军.冠军球队id == 球队.词条id group by T1.冠军球队id order by count ( * ) asc limit 1	欧洲杯球队
qid000475	select T2.中文队名 , T2.所属地区 from 欧冠冠亚军 as T1 join 球队 as T2 on 欧冠冠亚军.亚军球队id == 球队.词条id group by T1.亚军球队id order by count ( * ) asc limit 3	欧洲杯球队
qid000476	select T2.名称 , T2.隶属机构 from 电视剧 as T1 join 电视台 as T2 on 电视剧.首播平台id == 电视台.词条id group by T1.首播平台id order by count ( * ) desc limit 3	中国卫视频道
qid000477	select T2.名称 , T2.隶属机构 from 电视剧 as T1 join 电视台 as T2 on 电视剧.首播平台id == 电视台.词条id group by T1.首播平台id order by count ( * ) asc limit 1	中国卫视频道
qid000478	select T2.名称 , T2.类别 from 高校属性 as T1 join 高校 as T2 on 高校属性.高校id == 高校.词条id group by T1.高校id order by count ( * ) desc limit 3	中国高校
qid000479	select T2.名称 , T2.类别 from 高校属性 as T1 join 高校 as T2 on 高校属性.高校id == 高校.词条id group by T1.高校id order by count ( * ) desc limit 1	中国高校
qid000480	select T2.名称 , T2.类别 from 名人 as T1 join 高校 as T2 on 名人.高校id == 高校.词条id group by T1.高校id order by count ( * ) asc limit 1	中国高校
qid000481	select T2.名称 , T2.类别 from 名人 as T1 join 高校 as T2 on 名人.高校id == 高校.词条id group by T1.高校id order by count ( * ) desc limit 1	中国高校
qid000482	select T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id order by count ( * ) asc limit 3	奥运会参赛队伍
qid000483	select T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id order by sum ( T1.参赛国家数量 ) asc limit 1	奥运会参赛队伍
qid000484	select T2.中文名 , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id order by count ( * ) asc limit 3	企业融资
qid000485	select T2.中文名 , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id order by sum ( T1.融资额 ) asc limit 3	企业融资
qid000486	select T2.中文名 , T2.场上位置 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id group by T1.球员id order by count ( * ) desc limit 1	运动员比赛记录
qid000487	select T2.中文名 , T2.场上位置 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id group by T1.球员id order by count ( * ) asc limit 3	运动员比赛记录
qid000488	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 <= ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000489	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 > ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000490	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 > ( select min ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000491	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 < ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000492	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 == ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000493	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 >= ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000494	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 < ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000495	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 < ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000496	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 == ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000497	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 >= ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000498	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 > ( select min ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000499	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 < ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000500	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 <= ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000501	select T1.名称 , T1.举办城市 , T2.名称 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id where T1.参赛国家数量 > ( select avg ( T1.参赛国家数量 ) from T1 )	奥运会参赛队伍
qid000502	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 < ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000503	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 < ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000504	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 > ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000505	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 >= ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000506	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 > ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000507	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 == ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000508	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 <= ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000509	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 < ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000510	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 > ( select min ( T1.售价 ) from T1 )	洗衣机
qid000511	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 <= ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000512	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 >= ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000513	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 < ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000514	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 == ( select avg ( T1.售价 ) from T1 )	洗衣机
qid000515	select T1.名称 , T1.产品类别 , T2.名称 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T1.售价 > ( select min ( T1.售价 ) from T1 )	洗衣机
qid000516	select T2.名称 , T1.产品类别 , T2.市场份额 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 asc	洗衣机
qid000517	select T2.名称 , T1.产品类别 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 asc	洗衣机
qid000518	select T2.名称 , T1.产品类别 , T2.市场份额 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 asc	洗衣机
qid000519	select T2.名称 , T1.产品类别 , T2.市场份额 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 desc	洗衣机
qid000520	select T2.名称 , T1.产品类别 , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 desc	洗衣机
qid000521	select T2.名称 , T1.产品类别 , T2.市场份额 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 desc	洗衣机
qid000522	select T2.名称 , T1.举办城市 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛国家数量 asc	奥运会参赛队伍
qid000523	select T2.名称 , T1.参赛国家数量 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.大项项目数 asc	奥运会参赛队伍
qid000524	select T2.名称 , T1.参赛国家数量 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛运动员数量 desc	奥运会参赛队伍
qid000525	select T2.名称 , T1.举办城市 , T2.所属洲 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛国家数量 desc	奥运会参赛队伍
qid000526	select T2.名称 , T1.产品类别 , T1.售价 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 asc limit 3	洗衣机
qid000527	select T2.名称 , T1.产品类别 , T1.售价 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 desc limit 3	洗衣机
qid000528	select T2.名称 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 asc limit 3	洗衣机
qid000529	select T2.名称 , T1.产品类别 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id order by T1.售价 desc limit 3	洗衣机
qid000530	select T2.名称 , T1.参赛国家数量 , T1.举办城市 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛运动员数量 desc limit 3	奥运会参赛队伍
qid000531	select T2.名称 , T1.举办城市 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛国家数量 asc limit 3	奥运会参赛队伍
qid000532	select T2.名称 , T1.参赛国家数量 , T1.举办城市 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.大项项目数 asc limit 3	奥运会参赛队伍
qid000533	select T2.名称 , T1.举办城市 , T1.吉祥物 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛国家数量 desc limit 3	奥运会参赛队伍
qid000534	select T2.名称 , T1.举办城市 , T1.吉祥物 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛国家数量 asc limit 3	奥运会参赛队伍
qid000535	select T2.名称 , T1.举办城市 , T1.参赛国家数量 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛国家数量 desc limit 3	奥运会参赛队伍
qid000536	select T2.名称 , T1.举办城市 , T1.参赛国家数量 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛国家数量 asc limit 3	奥运会参赛队伍
qid000537	select T2.名称 , T1.举办城市 from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id order by T1.参赛国家数量 desc limit 3	奥运会参赛队伍
qid000538	select T3.名称 , T2.app名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id order by T1.市场份额 asc	打车软件
qid000539	select T3.名称 , T2.app名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id order by T1.每日打车单数 desc	打车软件
qid000540	select T3.中文名 , T2.中文名 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 join 企业 as T3 on 企业融资.企业id == 企业.词条id and 投资公司.企业id == 企业.词条id order by T1.融资总额 desc	企业融资
qid000541	select T3.中文名 , T2.中文名 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 join 企业 as T3 on 企业融资.企业id == 企业.词条id and 投资公司.企业id == 企业.词条id order by T1.融资总额 asc	企业融资
qid000542	select T3.名称 , T2.书名 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id order by T1.会员价格 desc	购书平台
qid000543	select T3.名称 , T2.书名 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id order by T1.购买人数 asc	购书平台
qid000544	select T2.app名称 , T3.名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id order by T1.每日营收 desc limit 3	打车软件
qid000545	select T2.app名称 , T3.名称 , T1.车数量 from 各打车APP支持的方式 as T1 join 打车APP as T2 join 打车方式 as T3 on 各打车APP支持的方式.appid == 打车APP.词条id and 各打车APP支持的方式.方式id == 打车方式.词条id order by T1.每日营收 asc limit 3	打车软件
qid000546	select T2.书名 , T3.名称 , T1.售价 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id order by T1.评分 asc limit 3	购书平台
qid000547	select T2.书名 , T3.名称 , T1.售价 , T1.加入购物车人数 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id order by T1.收藏人数 asc limit 3	购书平台
qid000548	select T2.书名 , T3.名称 , T1.售价 , T1.加入购物车人数 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id order by T1.评分 desc limit 3	购书平台
qid000549	select T2.书名 , T3.名称 , T1.售价 from 图书与平台 as T1 join 图书 as T2 join 平台 as T3 on 图书与平台.书名id == 图书.词条id and 图书与平台.平台id == 平台.词条id order by T1.评分 desc limit 3	购书平台
qid000550	select T2.中文名 , T3.中文名 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 join 企业 as T3 on 企业融资.企业id == 企业.词条id and 投资公司.企业id == 企业.词条id order by T1.融资总额 asc limit 3	企业融资
qid000551	select T2.中文名 , T3.中文名 , T1.融资轮次 from 企业融资 as T1 join 企业 as T2 join 企业 as T3 on 企业融资.企业id == 企业.词条id and 投资公司.企业id == 企业.词条id order by T1.融资总额 desc limit 3	企业融资
qid000552	select T2.书名 , T3.名称 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id order by T1.会员价格 desc limit 3	购书平台
qid000553	select T2.书名 , T3.名称 , T1.电子书售价 from 电子书 as T1 join 图书 as T2 join 平台 as T3 on 电子书.书名id == 图书.词条id and 电子书.平台id == 平台.词条id order by T1.购买人数 asc limit 3	购书平台
qid000554	( select 词条id from 城市 ) except ( select 城市id from 一带一路的中国城市 )	友好城市
qid000555	( select 词条id from 球队 ) except ( select 冠军球队id from 欧冠冠亚军 )	欧洲杯球队
qid000556	( select 词条id from 球队 ) except ( select 亚军球队id from 欧冠冠亚军 )	欧洲杯球队
qid000557	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having sum ( T1.收视份额 ) > 0.003	综艺节目
qid000558	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having sum ( T1.收视份额 ) < 0.003	综艺节目
qid000559	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having sum ( T1.收视份额 ) >= 0.003	综艺节目
qid000560	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having sum ( T1.收视份额 ) <= 0.003	综艺节目
qid000561	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having sum ( T1.奖项数量 ) > 30	中国高校
qid000562	select T2.名称 , sum ( T1.奖项数量 ) from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id	中国高校
qid000563	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having avg ( T1.奖项数量 ) <= 30	中国高校
qid000564	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having avg ( T1.奖项数量 ) >= 30	中国高校
qid000565	select T2.名称 , T2.类别 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id order by sum ( T1.奖项数量 ) asc limit 1	中国高校
qid000566	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having sum ( T1.奖项数量 ) >= 30	中国高校
qid000567	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having avg ( T1.奖项数量 ) < 30	中国高校
qid000568	select T2.名称 , T2.类别 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id order by sum ( T1.奖项数量 ) desc limit 1	中国高校
qid000569	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having sum ( T1.奖项数量 ) < 30	中国高校
qid000570	select T2.名称 , T2.类别 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id order by sum ( T1.奖项数量 ) asc limit 3	中国高校
qid000571	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having sum ( T1.奖项数量 ) <= 30	中国高校
qid000572	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id order by sum ( T1.奖项数量 ) asc limit 1	中国高校
qid000573	select T2.名称 , T2.类别 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id having sum ( T1.奖项数量 ) <= 30	中国高校
qid000574	select T2.名称 , T2.类别 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id having sum ( T1.奖项数量 ) >= 30	中国高校
qid000575	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id order by sum ( T1.奖项数量 ) desc limit 1	中国高校
qid000576	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id order by sum ( T1.奖项数量 ) asc limit 3	中国高校
qid000577	select T2.名称 , T2.类别 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id having sum ( T1.奖项数量 ) < 30	中国高校
qid000578	select T2.名称 , T2.类别 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id having sum ( T1.奖项数量 ) > 30	中国高校
qid000579	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) > 0.003	综艺节目
qid000580	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) < 0.003	综艺节目
qid000581	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) <= 0.003	综艺节目
qid000582	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) >= 0.003	综艺节目
qid000583	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) == 0.003	综艺节目
qid000584	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) < 5	综艺节目
qid000585	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) <= 5	综艺节目
qid000586	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) == 5	综艺节目
qid000587	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) > 5	综艺节目
qid000588	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) >= 5	综艺节目
qid000589	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by count ( * ) asc limit 1	综艺节目
qid000590	select T2.节目名称 , count ( * ) from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id	综艺节目
qid000591	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by count ( * ) desc limit3	综艺节目
qid000592	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by count ( * ) desc limit 1	综艺节目
qid000593	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by count ( * ) asc limit 3	综艺节目
qid000594	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by sum ( T1.收视份额 ) desc limit 1	综艺节目
qid000595	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by sum ( T1.收视份额 ) asc limit 1	综艺节目
qid000596	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by sum ( T1.收视份额 ) asc limit 2	综艺节目
qid000597	select T2.节目名称 , T2.系列名 , T1.播放数 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T1.在线平台 == '湖南卫视'	综艺节目
qid000598	select T2.节目名称 , T2.系列名 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id order by count ( * ) desc limit 3	综艺节目
qid000599	select T2.节目名称 , T2.系列名 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id order by count ( * ) desc limit 1	综艺节目
qid000600	select T2.节目名称 , T2.系列名 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id order by avg ( T1.收视率 ) desc limit 5	综艺节目
qid000601	select T2.节目名称 , T2.系列名 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id order by count ( * ) asc limit 3	综艺节目
qid000602	select T2.节目名称 , T2.系列名 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id order by avg ( T1.收视率 ) asc limit 1	综艺节目
qid000603	select T2.节目名称 , T2.系列名 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id order by count ( * ) asc limit 1	综艺节目
qid000604	select T2.节目名称 , T2.系列名 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id order by avg ( T1.收视率 ) desc limit 1	综艺节目
qid000605	select T2.节目名称 , T2.系列名 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id order by avg ( T1.收视率 ) asc limit 5	综艺节目
qid000606	select T2.名称 , avg ( T1.电子书售价 ) from 电子书 as T1 join 平台 as T2 on 电子书.平台id == 平台.词条id where T2.年营业额 >= 7177800000000 and T2.会员费 >= 150 group by T1.平台id having count ( * ) == 5	购书平台
qid000607	select T2.名称 , sum ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年利润 >= 15000000000 group by T1.品牌id having count ( * ) > 5	洗衣机
qid000608	select T2.名称 , min ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年利润 <= 15000000000 group by T1.品牌id having count ( * ) < 5	洗衣机
qid000609	select T2.名称 , min ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年利润 >= 15000000000 group by T1.品牌id having count ( * ) <= 5	洗衣机
qid000610	select T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年营业额 >= 200700000000 group by T1.品牌id having count ( * ) <= 5	洗衣机
qid000611	select T2.名称 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 and T2.2018年利润 < 15000000000 group by T1.品牌id having count ( * ) == 5	洗衣机
qid000612	select 季节 , count ( * ) from 坚果季节性营业收入 group by 季节	坚果
qid000613	select 系列名 , count ( * ) from 综艺节目 group by 系列名	综艺节目
qid000614	select 投资公司 , count ( * ) from 投资公司 group by 投资公司	企业融资
qid000615	select 所属公司 , count ( * ) from 打车APP group by 所属公司	打车软件
qid000616	select 城市 , count ( * ) from 洗衣机品牌门店 group by 城市	洗衣机
qid000617	select 营养成分 , count ( * ) from 每100克坚果营养成分 group by 营养成分	坚果
qid000618	select 产品类别 , count ( * ) from 洗衣机型号 group by 产品类别	洗衣机
qid000619	select 国家 , count ( * ) from 坚果摄入量 group by 国家	坚果
qid000620	select 法定代表人 , count ( * ) from 企业 group by 法定代表人	企业融资
qid000621	select 类型 , count ( * ) from 参考书 group by 类型	教材辅助参考书
qid000622	select 出品公司 , count ( * ) from 电视剧 group by 出品公司	中国卫视频道
qid000623	select 所属省 , count ( * ) from 一带一路的中国城市 group by 所属省	友好城市
qid000624	select 国家 , count ( * ) from 一带一路线路上的国家 group by 国家	友好城市
qid000625	select 场上位置 , count ( * ) from 篮球运动员 group by 场上位置	运动员比赛记录
qid000626	select 平台 , count ( * ) from 洗衣机品牌平台评分 group by 平台	洗衣机
qid000627	select 所属省 , count ( * ) from 对口帮扶城市 group by 所属省	友好城市
qid000628	select 民族 , count ( * ) from 明星 group by 民族	综艺节目
qid000629	select 所属地区 , count ( * ) from 球队 group by 所属地区	欧洲杯球队
qid000630	select 产地 , count ( * ) from 坚果产地 group by 产地	坚果
qid000631	select 所属洲 , count ( * ) from 国家 group by 所属洲	奥运会参赛队伍
qid000632	select 作者 , count ( * ) from 图书 group by 作者	购书平台
qid000633	select 法定代表人 from 企业 group by 法定代表人 having avg ( 注册资本 ) == ( select avg ( 注册资本 ) from 企业 )	企业融资
qid000634	select 所属地区 from 球队 group by 所属地区 having avg ( 容纳人数 ) <= ( select avg ( 容纳人数 ) from 球队 )	欧洲杯球队
qid000635	select 所属公司 from 洗衣机品牌 group by 所属公司 having avg ( 市场份额 ) >= ( select avg ( 市场份额 ) from 洗衣机品牌 )	洗衣机
qid000636	select 所属公司 from 打车APP group by 所属公司 having avg ( 覆盖城市数 ) == ( select avg ( 覆盖城市数 ) from 打车APP )	打车软件
qid000637	select 举办城市 from 夏季奥运会 group by 举办城市 having avg ( 参赛国家数量 ) <= ( select avg ( 参赛国家数量 ) from 夏季奥运会 )	奥运会参赛队伍
qid000638	select 场上位置 from 篮球运动员 group by 场上位置 having avg ( 年龄 ) == ( select avg ( 年龄 ) from 篮球运动员 )	运动员比赛记录
qid000639	select 所属省份 from 城市 group by 所属省份 having avg ( 建交国家数量 ) <= ( select avg ( 建交国家数量 ) from 城市 )	友好城市
qid000640	select 产品类别 from 洗衣机型号 group by 产品类别 having avg ( 售价 ) > ( select avg ( 售价 ) from 洗衣机型号 )	洗衣机
qid000641	select 法定代表人 from 企业 group by 法定代表人 having avg ( 注册资本 ) >= ( select min ( 注册资本 ) from 企业 where 成立时间 >= 2015 )	企业融资
qid000642	select 类型 from 参考书 group by 类型 having avg ( 适用年级 ) > ( select max ( 适用年级 ) from 参考书 where 价格 != 50 )	教材辅助参考书
qid000643	select 所属地区 from 球队 group by 所属地区 having avg ( 容纳人数 ) == ( select min ( 容纳人数 ) from 球队 where 成立时间 >= 1960 )	欧洲杯球队
qid000644	select 城市 from 打车软件开通城市 group by 城市 having avg ( 占所在城市份额 ) <= ( select avg ( 占所在城市份额 ) from 打车软件开通城市 where 城市 == '北京' )	打车软件
qid000645	select 发生城市 from 美国近几年校园枪击事件 group by 发生城市 having avg ( 受影响学生数量 ) > ( select min ( 受影响学生数量 ) from 美国近几年校园枪击事件 where 伤亡人数 < 20 )	枪击事件
qid000646	select 所属公司 from 洗衣机品牌 group by 所属公司 having avg ( 市场份额 ) == ( select max ( 市场份额 ) from 洗衣机品牌 where 2018年利润 != 15000000000 )	洗衣机
qid000647	select 举办城市 from 夏季奥运会 group by 举办城市 having avg ( 参赛国家数量 ) == ( select avg ( 参赛国家数量 ) from 夏季奥运会 where 大项项目数 < 16 )	奥运会参赛队伍
qid000648	select 所属省份 from 城市 group by 所属省份 having avg ( 建交国家数量 ) > ( select avg ( 建交国家数量 ) from 城市 where 国外驻华大使馆数量 != 0 )	友好城市
qid000649	select 所属公司 from 打车APP group by 所属公司 having avg ( 覆盖城市数 ) <= ( select avg ( 覆盖城市数 ) from 打车APP where 上线时间 < 2014 )	打车软件
qid000650	select 中文名 from 企业 where 法定代表人 in ( select 法定代表人 from 企业 group by 法定代表人 order by avg ( 注册资本 ) desc limit 2 )	企业融资
qid000651	select 名称 from 电视剧 where 出品公司 in ( select 出品公司 from 电视剧 group by 出品公司 order by count ( * ) desc limit 2 )	中国卫视频道
qid000652	select 节目名称 from 综艺节目 where 系列名 in ( select 系列名 from 综艺节目 group by 系列名 order by count ( * ) desc limit 2 )	综艺节目
qid000653	select 名称 from 高校 where 类别 in ( select 类别 from 高校 group by 类别 order by count ( * ) asc limit 2 )	中国高校
qid000654	select 名称 from 国家 where 所属洲 in ( select 所属洲 from 国家 group by 所属洲 order by count ( * ) desc limit 2 )	奥运会参赛队伍
qid000655	select 中文名 from 企业 where 注册资本 < ( select avg ( 注册资本 ) from 企业 )	企业融资
qid000656	select 姓名 from 企业人物 where 年龄 <= ( select avg ( 年龄 ) from 企业人物 )	CCTV中国经济年度人物
qid000657	select 名称 from 参考书 where 适用年级 >= ( select avg ( 适用年级 ) from 参考书 )	教材辅助参考书
qid000658	select 中文队名 from 球队 where 容纳人数 == ( select avg ( 容纳人数 ) from 球队 )	欧洲杯球队
qid000659	select 名称 from 打车方式 where 每公里价格 > ( select avg ( 每公里价格 ) from 打车方式 )	打车软件
qid000660	select 名称 from 洗衣机品牌 where 市场份额 == ( select avg ( 市场份额 ) from 洗衣机品牌 )	洗衣机
qid000661	select 名称 from 平台 where 年营业额 < ( select avg ( 年营业额 ) from 平台 )	购书平台
qid000662	select 省份 from 各省财政收入 where GDP总计(亿) == ( select avg ( GDP总计(亿) ) from 各省财政收入 )	城市财政收入
qid000663	select 名称 from 公司 where 年营业额 <= ( select avg ( 年营业额 ) from 公司 )	CCTV中国经济年度人物
qid000664	select 名称 from 坚果 where 饱和脂肪含量 < ( select max ( 饱和脂肪含量 ) from 坚果 )	坚果
qid000665	select 城市 from 城市 where 建交国家数量 > ( select avg ( 建交国家数量 ) from 城市 )	友好城市
qid000666	select 名称 from 洗衣机型号 where 售价 <= ( select avg ( 售价 ) from 洗衣机型号 )	洗衣机
qid000667	select 名称 from 夏季奥运会 where 参赛国家数量 == ( select avg ( 参赛国家数量 ) from 夏季奥运会 )	奥运会参赛队伍
qid000668	select 名称 from 国家 where 人口数量 > ( select avg ( 人口数量 ) from 国家 )	枪击事件
qid000669	select 中文名 法定代表人 from 企业 where 注册资本 == ( select avg ( 注册资本 ) from 企业 )	企业融资
qid000670	select 中文名 法定代表人 from 企业 where 注册资本 < ( select avg ( 注册资本 ) from 企业 )	企业融资
qid000671	select 姓名 性别 from 企业人物 where 年龄 <= ( select avg ( 年龄 ) from 企业人物 )	CCTV中国经济年度人物
qid000672	select 姓名 性别 from 企业人物 where 年龄 > ( select min ( 年龄 ) from 企业人物 )	CCTV中国经济年度人物
qid000673	select 名称 类型 from 参考书 where 适用年级 == ( select avg ( 适用年级 ) from 参考书 )	教材辅助参考书
qid000674	select 名称 类型 from 参考书 where 适用年级 < ( select max ( 适用年级 ) from 参考书 )	教材辅助参考书
qid000675	select 中文队名 所属地区 from 球队 where 容纳人数 > ( select avg ( 容纳人数 ) from 球队 )	欧洲杯球队
qid000676	select 中文队名 所属地区 from 球队 where 容纳人数 <= ( select avg ( 容纳人数 ) from 球队 )	欧洲杯球队
qid000677	select 名称 理念 from 打车方式 where 每公里价格 >= ( select avg ( 每公里价格 ) from 打车方式 )	打车软件
qid000678	select 名称 理念 from 打车方式 where 每公里价格 <= ( select avg ( 每公里价格 ) from 打车方式 )	打车软件
qid000679	select 名称 所属公司 from 洗衣机品牌 where 市场份额 >= ( select avg ( 市场份额 ) from 洗衣机品牌 )	洗衣机
qid000680	select 名称 所属公司 from 洗衣机品牌 where 市场份额 > ( select min ( 市场份额 ) from 洗衣机品牌 )	洗衣机
qid000681	select 名称 举办城市 from 夏季奥运会 where 参赛国家数量 <= ( select avg ( 参赛国家数量 ) from 夏季奥运会 )	奥运会参赛队伍
qid000682	select 名称 举办城市 from 夏季奥运会 where 参赛国家数量 > ( select avg ( 参赛国家数量 ) from 夏季奥运会 )	奥运会参赛队伍
qid000683	select 中文名 场上位置 from 篮球运动员 where 年龄 >= ( select avg ( 年龄 ) from 篮球运动员 )	运动员比赛记录
qid000684	select 中文名 from 企业 where 注册资本 < ( select avg ( 注册资本 ) from 企业 where 法定代表人 == '刘墨' )	企业融资
qid000685	select 中文名 from 企业 where 注册资本 < ( select avg ( 注册资本 ) from 企业 where 法定代表人 == '刘墨' )	企业融资
qid000686	select 姓名 from 企业人物 where 年龄 >= ( select avg ( 年龄 ) from 企业人物 where 性别 == '女' )	CCTV中国经济年度人物
qid000687	select 姓名 from 企业人物 where 年龄 < ( select max ( 年龄 ) from 企业人物 where 性别 == '女' )	CCTV中国经济年度人物
qid000688	select 中文队名 from 球队 where 容纳人数 > ( select min ( 容纳人数 ) from 球队 where 所属地区 == '巴西' )	欧洲杯球队
qid000689	select 中文队名 from 球队 where 容纳人数 < ( select avg ( 容纳人数 ) from 球队 where 所属地区 == '巴西' )	欧洲杯球队
qid000690	select 名称 from 洗衣机品牌 where 市场份额 == ( select avg ( 市场份额 ) from 洗衣机品牌 where 所属公司 == '韩国LG集团' )	洗衣机
qid000691	select 名称 from 洗衣机品牌 where 市场份额 < ( select max ( 市场份额 ) from 洗衣机品牌 where 所属公司 == '韩国LG集团' )	洗衣机
qid000692	select 名称 from 参考书 where 适用年级 == ( select avg ( 适用年级 ) from 参考书 where 类型 == '出版书' )	教材辅助参考书
qid000693	select 名称 from 参考书 where 适用年级 > ( select min ( 适用年级 ) from 参考书 where 类型 == '出版书' )	教材辅助参考书
qid000694	select 名称 from 夏季奥运会 where 参赛国家数量 < ( select avg ( 参赛国家数量 ) from 夏季奥运会 where 举办城市 == '雅典' )	奥运会参赛队伍
qid000695	select 名称 from 夏季奥运会 where 参赛国家数量 > ( select avg ( 参赛国家数量 ) from 夏季奥运会 where 举办城市 == '雅典' )	奥运会参赛队伍
qid000696	select 城市 from 城市 where 建交国家数量 <= ( select avg ( 建交国家数量 ) from 城市 where 所属省份 == '广东' )	友好城市
qid000697	select 城市 from 城市 where 建交国家数量 < ( select avg ( 建交国家数量 ) from 城市 where 所属省份 == '广东' )	友好城市
qid000698	select 名称 from 洗衣机型号 where 售价 < ( select max ( 售价 ) from 洗衣机型号 where 产品类别 == '双缸' )	洗衣机
qid000699	select 名称 from 洗衣机型号 where 售价 == ( select avg ( 售价 ) from 洗衣机型号 where 产品类别 == '双缸' )	洗衣机
qid000700	select 中文名 from 篮球运动员 where 年龄 == ( select avg ( 年龄 ) from 篮球运动员 where 场上位置 == '控球后卫' )	运动员比赛记录
qid000701	select 中文名 from 篮球运动员 where 年龄 < ( select avg ( 年龄 ) from 篮球运动员 where 场上位置 == '控球后卫' )	运动员比赛记录
qid000702	select 中文队名 主场馆 from 球队 where 容纳人数 < ( select avg ( 容纳人数 ) from 球队 where 所属地区 == '巴西' )	欧洲杯球队
qid000703	select 中文队名 主场馆 from 球队 where 容纳人数 > ( select avg ( 容纳人数 ) from 球队 where 所属地区 == '巴西' )	欧洲杯球队
qid000704	select 中文队名 主场馆 from 球队 where 容纳人数 == ( select avg ( 容纳人数 ) from 球队 where 所属地区 == '巴西' )	欧洲杯球队
qid000705	select 名称 小项项目数 from 夏季奥运会 where 参赛国家数量 <= ( select avg ( 参赛国家数量 ) from 夏季奥运会 where 举办城市 == '雅典' )	奥运会参赛队伍
qid000706	select 名称 参赛运动员数量 from 夏季奥运会 where 参赛国家数量 > ( select avg ( 参赛国家数量 ) from 夏季奥运会 where 举办城市 == '雅典' )	奥运会参赛队伍
qid000707	select 名称 吉祥物 from 夏季奥运会 where 参赛国家数量 <= ( select avg ( 参赛国家数量 ) from 夏季奥运会 where 举办城市 == '雅典' )	奥运会参赛队伍
qid000708	select 名称 2018年利润 from 洗衣机品牌 where 市场份额 > ( select min ( 市场份额 ) from 洗衣机品牌 where 所属公司 == '韩国LG集团' )	洗衣机
qid000709	select 名称 2018年利润 from 洗衣机品牌 where 市场份额 < ( select avg ( 市场份额 ) from 洗衣机品牌 where 所属公司 == '韩国LG集团' )	洗衣机
qid000710	select 名称 2018年营业额 from 洗衣机品牌 where 市场份额 >= ( select avg ( 市场份额 ) from 洗衣机品牌 where 所属公司 == '韩国LG集团' )	洗衣机
qid000711	select 城市 国外驻华大使馆数量 from 城市 where 建交国家数量 < ( select avg ( 建交国家数量 ) from 城市 where 所属省份 == '广东' )	友好城市
qid000712	select 城市 跨国公司数量 from 城市 where 建交国家数量 <= ( select avg ( 建交国家数量 ) from 城市 where 所属省份 == '广东' )	友好城市
qid000713	select 城市 跨国公司数量 from 城市 where 建交国家数量 > ( select min ( 建交国家数量 ) from 城市 where 所属省份 == '广东' )	友好城市
qid000714	select 名称 价格 from 参考书 where 适用年级 > ( select min ( 适用年级 ) from 参考书 where 类型 == '出版书' )	教材辅助参考书
qid000715	select 名称 价格 from 参考书 where 适用年级 < ( select avg ( 适用年级 ) from 参考书 where 类型 == '出版书' )	教材辅助参考书
qid000716	select 姓名 from 明星 where 民族 in ( select 民族 from 明星 group by 民族 having count ( * ) >= 5 )	综艺节目
qid000717	select 姓名 from 企业人物 where 性别 in ( select 性别 from 企业人物 group by 性别 having count ( * ) > 5 )	CCTV中国经济年度人物
qid000718	select 名称 from 参考书 where 类型 in ( select 类型 from 参考书 group by 类型 having count ( * ) >= 5 )	教材辅助参考书
qid000719	select 中文队名 from 球队 where 所属地区 in ( select 所属地区 from 球队 group by 所属地区 having avg ( 容纳人数 ) == 2000 )	欧洲杯球队
qid000720	select 名称 from 夏季奥运会 where 举办城市 in ( select 举办城市 from 夏季奥运会 group by 举办城市 having count ( * ) < 5 )	奥运会参赛队伍
qid000721	select 城市 from 城市 where 所属省份 in ( select 所属省份 from 城市 group by 所属省份 having sum ( 建交国家数量 ) >= 15 )	友好城市
qid000722	select 名称 from 国家 where 所属洲 in ( select 所属洲 from 国家 group by 所属洲 having count ( * ) <= 5 )	奥运会参赛队伍
qid000723	select 名称 from 洗衣机型号 where 产品类别 in ( select 产品类别 from 洗衣机型号 group by 产品类别 having count ( * ) > 5 )	洗衣机
qid000724	( select 中文名 from 企业 order by 成立时间 asc limit 3 ) intersect ( select 中文名 from 企业 order by 注册资本 asc limit 5 )	企业融资
qid000725	( select 姓名 from 韩国自杀的娱乐明星 order by 死亡时间 asc limit 3 ) intersect ( select 姓名 from 韩国自杀的娱乐明星 order by 年龄 asc limit 5 )	枪击事件
qid000726	( select 名称 from 洗衣机品牌 order by 成立时间 asc limit 3 ) intersect ( select 名称 from 洗衣机品牌 order by 市场份额 asc limit 5 )	洗衣机
qid000727	( select 名称 from 平台 order by 成立时间 asc limit 3 ) intersect ( select 名称 from 平台 order by 年营业额 desc limit 5 )	购书平台
qid000728	( select 名称 from 参考书 order by 适用年级 desc limit 3 ) intersect ( select 名称 from 参考书 order by 价格 asc limit 5 )	教材辅助参考书
qid000729	( select 名称 from 坚果 order by 饱和脂肪含量 desc limit 3 ) intersect ( select 名称 from 坚果 order by 不饱和脂肪含量 asc limit 5 )	坚果
qid000730	( select 名称 from 夏季奥运会 order by 参赛国家数量 asc limit 3 ) intersect ( select 名称 from 夏季奥运会 order by 大项项目数 desc limit 5 )	奥运会参赛队伍
qid000731	( select 名称 from 公司 order by 成立时间 asc limit 3 ) intersect ( select 名称 from 公司 order by 年营业额 desc limit 5 )	CCTV中国经济年度人物
qid000732	( select 名称 from 国家 order by 人口数量 desc limit 3 ) intersect ( select 名称 from 国家 order by 民用枪支数 asc limit 5 )	枪击事件
qid000733	( select 名称 from 参考书 order by 适用年级 desc limit 3 ) union ( select 名称 from 参考书 order by 价格 asc limit 5 )	教材辅助参考书
qid000734	( select 中文名 from 企业 order by 成立时间 asc limit 3 ) union ( select 中文名 from 企业 order by 注册资本 desc limit 5 )	企业融资
qid000735	( select 姓名 from 韩国自杀的娱乐明星 order by 死亡时间 asc limit 3 ) union ( select 姓名 from 韩国自杀的娱乐明星 order by 年龄 asc limit 5 )	枪击事件
qid000736	( select 中文队名 from 球队 order by 成立时间 asc limit 3 ) union ( select 中文队名 from 球队 order by 容纳人数 desc limit 5 )	欧洲杯球队
qid000737	( select 名称 from 公司 order by 年营业额 desc limit 3 ) union ( select 名称 from 公司 order by 员工数 asc limit 5 )	CCTV中国经济年度人物
qid000738	( select 名称 from 洗衣机品牌 order by 成立时间 asc limit 3 ) union ( select 名称 from 洗衣机品牌 order by 市场份额 desc limit 5 )	洗衣机
qid000739	( select 名称 from 平台 order by 成立时间 asc limit 3 ) union ( select 名称 from 平台 order by 年营业额 desc limit 5 )	购书平台
qid000740	( select 名称 from 坚果 order by 饱和脂肪含量 asc limit 3 ) union ( select 名称 from 坚果 order by 不饱和脂肪含量 desc limit 5 )	坚果
qid000741	( select 省份 from 各省财政收入 order by GDP总计(亿) asc limit 3 ) union ( select 省份 from 各省财政收入 order by 财政预算收入(亿) desc limit 5 )	城市财政收入
qid000742	( select 名称 from 夏季奥运会 order by 参赛国家数量 desc limit 3 ) union ( select 名称 from 夏季奥运会 order by 小项项目数 asc limit 5 )	奥运会参赛队伍
qid000743	( select 姓名 from 韩国自杀的娱乐明星 order by 死亡时间 asc limit 3 ) except ( select 姓名 from 韩国自杀的娱乐明星 order by 年龄 desc limit 5 )	枪击事件
qid000744	( select 中文队名 from 球队 order by 成立时间 asc limit 3 ) except ( select 中文队名 from 球队 order by 容纳人数 asc limit 5 )	欧洲杯球队
qid000745	( select 名称 from 夏季奥运会 order by 参赛国家数量 asc limit 3 ) except ( select 名称 from 夏季奥运会 order by 大项项目数 desc limit 5 )	奥运会参赛队伍
qid000746	( select 名称 from 洗衣机品牌 order by 成立时间 asc limit 3 ) except ( select 名称 from 洗衣机品牌 order by 市场份额 asc limit 5 )	洗衣机
qid000747	( select 名称 from 平台 order by 成立时间 asc limit 3 ) except ( select 名称 from 平台 order by 年营业额 asc limit 5 )	购书平台
qid000748	( select 省份 from 各省财政收入 order by GDP总计(亿) asc limit 3 ) except ( select 省份 from 各省财政收入 order by 财政预算同比增速 desc limit 5 )	城市财政收入
qid000749	( select 名称 from 公司 order by 成立时间 asc limit 3 ) except ( select 名称 from 公司 order by 年营业额 asc limit 5 )	CCTV中国经济年度人物
qid000750	( select app名称 from 打车APP order by 上线时间 asc limit 3 ) except ( select app名称 from 打车APP order by 覆盖城市数 desc limit 5 )	打车软件
qid000751	( select 名称 from 坚果 order by 饱和脂肪含量 asc limit 3 ) except ( select 名称 from 坚果 order by 不饱和脂肪含量 desc limit 5 )	坚果
qid000752	( select 名称 from 电视台 order by 开播时间 asc limit 3 ) except ( select 名称 from 电视台 where 上线时间 > 1998-01-01 )	中国卫视频道
qid000753	( select 名称 from 电视台 where 开播时间 < 1997-01-01 ) except ( select 名称 from 电视台 order by 上线时间 asc limit 3 )	中国卫视频道
qid000754	( select 姓名 from 韩国自杀的娱乐明星 order by 年龄 desc limit 3 ) except ( select 姓名 from 韩国自杀的娱乐明星 where 死亡时间 < '2019-11-30' )	枪击事件
qid000755	( select 姓名 from 韩国自杀的娱乐明星 order by 年龄 asc limit 3 ) except ( select 姓名 from 韩国自杀的娱乐明星 where 死亡时间 <= '2019-11-30' )	枪击事件
qid000756	( select 名称 from 参考书 where 适用年级 <= 3 ) except ( select 名称 from 参考书 order by 价格 asc limit 3 )	教材辅助参考书
qid000757	( select 名称 from 参考书 order by 适用年级 asc limit 3 ) except ( select 名称 from 参考书 where 价格 > 99 )	教材辅助参考书
qid000758	( select 中文队名 from 球队 where 成立时间 > 1964 ) except ( select 中文队名 from 球队 order by 容纳人数 desc limit 3 )	欧洲杯球队
qid000759	( select 中文队名 from 球队 where 成立时间 <= 1964 ) except ( select 中文队名 from 球队 order by 容纳人数 desc limit 3 )	欧洲杯球队
qid000760	( select 名称 from 公司 order by 年营业额 desc limit 3 ) except ( select 名称 from 公司 where 成立时间 >= 2014 )	CCTV中国经济年度人物
qid000761	( select 名称 from 公司 where 成立时间 < 2014 ) except ( select 名称 from 公司 order by 年营业额 asc limit 3 )	CCTV中国经济年度人物
qid000762	( select 名称 from 洗衣机品牌 where 市场份额 < 0.02 ) except ( select 名称 from 洗衣机品牌 order by 2018年营业额 desc limit 3 )	洗衣机
qid000763	( select 名称 from 洗衣机品牌 order by 市场份额 desc limit 3 ) except ( select 名称 from 洗衣机品牌 where 成立时间 < 1955 )	洗衣机
qid000764	( select 名称 from 平台 where 年营业额 >= 1400000000 ) except ( select 名称 from 平台 order by 成立时间 asc limit 3 )	购书平台
qid000765	( select 名称 from 平台 where 成立时间 >= '2015-07-15' ) except ( select 名称 from 平台 order by 年营业额 asc limit 3 )	购书平台
qid000766	( select 节目名称 from 综艺节目 where 首播时间 >= 2014-10-01 ) except ( select 节目名称 from 综艺节目 order by 播出时间 asc limit 3 )	综艺节目
qid000767	( select 节目名称 from 综艺节目 order by 首播时间 asc limit 3 ) except ( select 节目名称 from 综艺节目 where 播出时间 > '22:00' )	综艺节目
qid000768	( select 省份 from 各省财政收入 order by GDP总计(亿) asc limit 3 ) except ( select 省份 from 各省财政收入 where 预算赤字率 > 0.05 )	城市财政收入
qid000769	( select 省份 from 各省财政收入 order by GDP总计(亿) desc limit 3 ) except ( select 省份 from 各省财政收入 where 固定资产投资同比增速 >= -6 )	城市财政收入
qid000770	( select 名称 from 夏季奥运会 order by 参赛国家数量 asc limit 3 ) except ( select 名称 from 夏季奥运会 where 大项项目数 > 16 )	奥运会参赛队伍
qid000771	( select 名称 from 夏季奥运会 where 参赛国家数量 > 30 ) except ( select 名称 from 夏季奥运会 order by 大项项目数 desc limit 3 )	奥运会参赛队伍
qid000772	( select 名称 from 电视台 order by 开播时间 asc limit 3 ) union ( select 名称 from 电视台 where 上线时间 > 1998-01-01 )	中国卫视频道
qid000773	( select 名称 from 电视台 where 开播时间 < 1997-01-01 ) union ( select 名称 from 电视台 order by 上线时间 asc limit 3 )	中国卫视频道
qid000774	( select 姓名 from 韩国自杀的娱乐明星 where 死亡时间 < '2019-11-30' ) union ( select 姓名 from 韩国自杀的娱乐明星 order by 年龄 desc limit 3 )	枪击事件
qid000775	( select 姓名 from 韩国自杀的娱乐明星 where 死亡时间 >= '2019-11-30' ) union ( select 姓名 from 韩国自杀的娱乐明星 order by 年龄 desc limit 3 )	枪击事件
qid000776	( select 名称 from 参考书 where 适用年级 >= 1 ) union ( select 名称 from 参考书 order by 价格 asc limit 3 )	教材辅助参考书
qid000777	( select 名称 from 参考书 where 适用年级 < 3 ) union ( select 名称 from 参考书 order by 价格 desc limit 3 )	教材辅助参考书
qid000778	( select 中文队名 from 球队 order by 成立时间 asc limit 3 ) union ( select 中文队名 from 球队 where 容纳人数 > 21000 )	欧洲杯球队
qid000779	( select 中文队名 from 球队 where 容纳人数 >= 21000 ) union ( select 中文队名 from 球队 order by 成立时间 asc limit 3 )	欧洲杯球队
qid000780	( select 名称 from 夏季奥运会 where 参赛国家数量 > 30 ) union ( select 名称 from 夏季奥运会 order by 参赛运动员数量 desc limit 3 )	奥运会参赛队伍
qid000781	( select 名称 from 夏季奥运会 order by 参赛国家数量 desc limit 3 ) union ( select 名称 from 夏季奥运会 where 参赛运动员数量 < 500 )	奥运会参赛队伍
qid000782	( select 名称 from 洗衣机品牌 where 成立时间 < 1955 ) union ( select 名称 from 洗衣机品牌 order by 市场份额 desc limit 3 )	洗衣机
qid000783	( select 名称 from 洗衣机品牌 where 市场份额 < 0.02 ) union ( select 名称 from 洗衣机品牌 order by 成立时间 asc limit 3 )	洗衣机
qid000784	( select 名称 from 平台 order by 年营业额 desc limit 3 ) union ( select 名称 from 平台 where 成立时间 > '2015-07-15' )	购书平台
qid000785	( select 名称 from 平台 where 成立时间 < '2015-07-15' ) union ( select 名称 from 平台 order by 年营业额 asc limit 3 )	购书平台
qid000786	( select 节目名称 from 综艺节目 order by 首播时间 asc limit 3 ) union ( select 节目名称 from 综艺节目 where 播出时间 < '22:00' )	综艺节目
qid000787	( select 节目名称 from 综艺节目 order by 首播时间 asc limit 3 ) union ( select 节目名称 from 综艺节目 where 播出时间 > '22:00' )	综艺节目
qid000788	( select 名称 from 坚果 order by 饱和脂肪含量 asc limit 3 ) union ( select 名称 from 坚果 where 每100克热量 <= 600 )	坚果
qid000789	( select 名称 from 坚果 order by 饱和脂肪含量 asc limit 3 ) union ( select 名称 from 坚果 where 不饱和脂肪含量 >= 51 )	坚果
qid000790	( select 省份 from 各省财政收入 order by GDP总计(亿) asc limit 3 ) union ( select 省份 from 各省财政收入 where 固定资产投资同比增速 > -6 )	城市财政收入
qid000791	( select 省份 from 各省财政收入 order by GDP总计(亿) asc limit 3 ) union ( select 省份 from 各省财政收入 where 财政预算同比增速 < -0.16 )	城市财政收入
qid000792	( select 名称 from 公司 where 年营业额 >= 20000000 ) union ( select 名称 from 公司 order by 成立时间 asc limit 3 )	CCTV中国经济年度人物
qid000793	( select 名称 from 公司 where 成立时间 < 2014 ) union ( select 名称 from 公司 order by 年营业额 asc limit 3 )	CCTV中国经济年度人物
qid000794	( select app名称 from 打车APP order by 上线时间 asc limit 3 ) union ( select app名称 from 打车APP where 覆盖城市数 <= 100 )	打车软件
qid000795	( select app名称 from 打车APP where 上线时间 >= 2014 ) union ( select app名称 from 打车APP order by 覆盖城市数 asc limit 3 )	打车软件
qid000796	select 一线城市累计同比 from 300城土地供给 where 年份 < 2017	城市财政收入
qid000797	select 一线城市累计同比 from 300城土地供给 where 年份 > 2017	城市财政收入
qid000798	select 一线城市累计同比 from 300城土地供给 where 年份 <= 2017	城市财政收入
qid000799	select 一线城市累计同比 from 300城土地供给 where 年份 >= 2017	城市财政收入
qid000800	select 一线城市累计同比 from 300城土地供给 where 年份 == 2017	城市财政收入
qid000801	select 成交建筑面积 from 300城土地成交 where 年份 > 2018	城市财政收入
qid000802	select 成交建筑面积 from 300城土地成交 where 年份 >= 2018	城市财政收入
qid000803	select 成交建筑面积 from 300城土地成交 where 年份 <= 2018	城市财政收入
qid000804	select 成交建筑面积 from 300城土地成交 where 年份 < 2018	城市财政收入
qid000805	select 成交建筑面积 from 300城土地成交 where 年份 == 2018	城市财政收入
qid000806	select 年份 from 300城土地成交 where 成交建筑面积 > 350000	城市财政收入
qid000807	select 年份 from 300城土地成交 where 成交建筑面积 <= 350000	城市财政收入
qid000808	select 年份 from 300城土地成交 where 成交建筑面积 >= 350000	城市财政收入
qid000809	select 年份 from 300城土地成交 where 成交建筑面积 == 350000	城市财政收入
qid000810	select 年份 from 300城土地成交 where 成交建筑面积 < 350000	城市财政收入
qid000811	select app名称 from 打车APP where TIME_NOW - 上线时间 > 13 or 覆盖城市数 != 100	打车软件
qid000812	select app名称 from 打车APP where TIME_NOW - 上线时间 != 17 and 覆盖城市数 <= 100	打车软件
qid000813	select app名称 from 打车APP where TIME_NOW - 上线时间 <= 15 or 覆盖城市数 != 100	打车软件
qid000814	select app名称 from 打车APP where TIME_NOW - 上线时间 < 5 or 覆盖城市数 == 100	打车软件
qid000815	select app名称 from 打车APP where TIME_NOW - 上线时间 <= 11 or 覆盖城市数 < 100	打车软件
qid000816	select app名称 from 打车APP where TIME_NOW - 上线时间 <= 3 and 覆盖城市数 <= 100	打车软件
qid000817	select app名称 from 打车APP where TIME_NOW - 上线时间 > 18 or 覆盖城市数 >= 100	打车软件
qid000818	select app名称 from 打车APP where TIME_NOW - 上线时间 == 10 and 覆盖城市数 >= 100	打车软件
qid000819	select app名称 所属公司 from 打车APP where TIME_NOW - 上线时间 != 13	打车软件
qid000820	select app名称 from 打车APP where TIME_NOW - 上线时间 < 14 and 覆盖城市数 <= 100	打车软件
qid000821	select app名称 from 打车APP where TIME_NOW - 上线时间 == 2 and 覆盖城市数 < 100	打车软件
qid000822	select app名称 from 打车APP where TIME_NOW - 上线时间 != 6	打车软件
qid000823	select app名称 from 打车APP where TIME_NOW - 上线时间 < 4 and 覆盖城市数 >= 100	打车软件
qid000824	select app名称 from 打车APP where TIME_NOW - 上线时间 == 14 or 覆盖城市数 != 100	打车软件
qid000825	select app名称 from 打车APP where TIME_NOW - 上线时间 != 3 and 覆盖城市数 > 100	打车软件
qid000826	select app名称 from 打车APP where TIME_NOW - 上线时间 >= 18 and 覆盖城市数 >= 100	打车软件
qid000827	select app名称 from 打车APP where TIME_NOW - 上线时间 > 20 and 覆盖城市数 == 100	打车软件
qid000828	select app名称 from 打车APP where TIME_NOW - 上线时间 > 12 and 覆盖城市数 > 100	打车软件
qid000829	select app名称 from 打车APP where TIME_NOW - 上线时间 != 9 and 覆盖城市数 == 100	打车软件
qid000830	select app名称 所属公司 from 打车APP where TIME_NOW - 上线时间 >= 13	打车软件
qid000831	select 名称 from 公司 where TIME_NOW - 成立时间 != 11 or 年营业额 > 20000000	CCTV中国经济年度人物
qid000832	select 名称 from 公司 where TIME_NOW - 成立时间 == 1 and 年营业额 <= 20000000	CCTV中国经济年度人物
qid000833	select 名称 from 公司 where TIME_NOW - 成立时间 < 14 and 年营业额 > 20000000	CCTV中国经济年度人物
qid000834	select 名称 from 公司 where TIME_NOW - 成立时间 >= 4 and 年营业额 == 20000000	CCTV中国经济年度人物
qid000835	select 名称 from 公司 where TIME_NOW - 成立时间 != 12 or 年营业额 != 20000000	CCTV中国经济年度人物
qid000836	select 名称 from 公司 where TIME_NOW - 成立时间 <= 8	CCTV中国经济年度人物
qid000837	select 名称 from 公司 where TIME_NOW - 成立时间 >= 13 or 年营业额 > 20000000	CCTV中国经济年度人物
qid000838	select 名称 from 公司 where TIME_NOW - 成立时间 != 12 and 年营业额 == 20000000	CCTV中国经济年度人物
qid000839	select 名称 from 公司 where TIME_NOW - 成立时间 <= 18 or 年营业额 != 20000000	CCTV中国经济年度人物
qid000840	select 名称 from 公司 where TIME_NOW - 成立时间 < 8 or 年营业额 == 20000000	CCTV中国经济年度人物
qid000841	select 名称 from 公司 where TIME_NOW - 成立时间 <= 15 and 年营业额 == 20000000	CCTV中国经济年度人物
qid000842	select 名称 from 公司 where TIME_NOW - 成立时间 < 13 and 年营业额 < 20000000	CCTV中国经济年度人物
qid000843	select 名称 from 公司 where TIME_NOW - 成立时间 == 16	CCTV中国经济年度人物
qid000844	select 名称 from 公司 where TIME_NOW - 成立时间 > 11 or 年营业额 != 20000000	CCTV中国经济年度人物
qid000845	select 名称 from 公司 where TIME_NOW - 成立时间 != 20 or 年营业额 <= 20000000	CCTV中国经济年度人物
qid000846	select 名称 from 公司 where TIME_NOW - 成立时间 > 1 and 年营业额 != 20000000	CCTV中国经济年度人物
qid000847	select 名称 from 公司 where TIME_NOW - 成立时间 != 4 and 年营业额 >= 20000000	CCTV中国经济年度人物
qid000848	select 名称 from 公司 where TIME_NOW - 成立时间 > 9 and 年营业额 >= 20000000	CCTV中国经济年度人物
qid000849	select 名称 from 公司 where TIME_NOW - 成立时间 > 15 and 年营业额 > 20000000	CCTV中国经济年度人物
qid000850	select 名称 from 公司 where TIME_NOW - 成立时间 <= 17 or 年营业额 >= 20000000	CCTV中国经济年度人物
qid000851	select 名称 from 平台 where TIME_NOW - 成立时间 < 19 or 年营业额 >= 1400000000	购书平台
qid000852	select 名称 from 平台 where TIME_NOW - 成立时间 <= 10 or 年营业额 == 1400000000	购书平台
qid000853	select 名称 from 平台 where TIME_NOW - 成立时间 < 15 and 年营业额 == 1400000000	购书平台
qid000854	select 名称 from 平台 where TIME_NOW - 成立时间 >= 4 and 年营业额 >= 1400000000	购书平台
qid000855	select 名称 from 平台 where TIME_NOW - 成立时间 >= 1	购书平台
qid000856	select 名称 from 平台 where TIME_NOW - 成立时间 >= 15 or 年营业额 == 1400000000	购书平台
qid000857	select 名称 from 平台 where TIME_NOW - 成立时间 != 2	购书平台
qid000858	select 名称 from 平台 where TIME_NOW - 成立时间 != 7 and 年营业额 < 1400000000	购书平台
qid000859	select 名称 from 平台 where TIME_NOW - 成立时间 > 5 or 年营业额 >= 1400000000	购书平台
qid000860	select 名称 from 平台 where TIME_NOW - 成立时间 >= 15 or 年营业额 <= 1400000000	购书平台
qid000861	select 名称 from 平台 where TIME_NOW - 成立时间 != 15 and 年营业额 >= 1400000000	购书平台
qid000862	select 名称 from 平台 where TIME_NOW - 成立时间 < 1 or 年营业额 <= 1400000000	购书平台
qid000863	select 名称 from 平台 where TIME_NOW - 成立时间 != 6 and 年营业额 != 1400000000	购书平台
qid000864	select 名称 from 平台 where TIME_NOW - 成立时间 >= 2 and 年营业额 <= 1400000000	购书平台
qid000865	select 名称 from 平台 where TIME_NOW - 成立时间 != 3 and 年营业额 <= 1400000000	购书平台
qid000866	select 名称 from 平台 where TIME_NOW - 成立时间 < 4 and 年营业额 < 1400000000	购书平台
qid000867	select 名称 from 平台 where TIME_NOW - 成立时间 <= 13 and 年营业额 >= 1400000000	购书平台
qid000868	select 名称 from 平台 where TIME_NOW - 成立时间 > 2 or 年营业额 == 1400000000	购书平台
qid000869	select 名称 from 平台 where TIME_NOW - 成立时间 != 19 and 年营业额 > 1400000000	购书平台
qid000870	select 名称 from 平台 where TIME_NOW - 成立时间 == 8 or 年营业额 != 1400000000	购书平台
qid000871	select 名称 所属公司 from 洗衣机品牌 where TIME_NOW - 成立时间 != 18	洗衣机
qid000872	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 <= 13 or 市场份额 == 0.02	洗衣机
qid000873	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 >= 7 or 市场份额 >= 0.02	洗衣机
qid000874	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 <= 18	洗衣机
qid000875	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 < 5 and 市场份额 <= 0.02	洗衣机
qid000876	select 名称 所属公司 from 洗衣机品牌 where TIME_NOW - 成立时间 == 4	洗衣机
qid000877	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 <= 4 and 市场份额 < 0.02	洗衣机
qid000878	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 != 12 and 市场份额 > 0.02	洗衣机
qid000879	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 != 13 or 市场份额 <= 0.02	洗衣机
qid000880	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 == 1 or 市场份额 > 0.02	洗衣机
qid000881	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 <= 4 and 市场份额 <= 0.02	洗衣机
qid000882	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 > 4 and 市场份额 <= 0.02	洗衣机
qid000883	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 > 3 or 市场份额 <= 0.02	洗衣机
qid000884	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 == 4 or 市场份额 == 0.02	洗衣机
qid000885	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 <= 8 and 市场份额 == 0.02	洗衣机
qid000886	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 > 6 and 市场份额 == 0.02	洗衣机
qid000887	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 >= 1 and 所属公司 != '三星集团'	洗衣机
qid000888	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 > 16 and 市场份额 != 0.02	洗衣机
qid000889	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 <= 7 or 市场份额 >= 0.02	洗衣机
qid000890	select 名称 from 洗衣机品牌 where TIME_NOW - 成立时间 < 5	洗衣机
qid000891	select 中文名 from 企业 where TIME_NOW - 成立时间 <= 1 or 注册资本 != 1000000	企业融资
qid000892	select 中文名 from 企业 where TIME_NOW - 成立时间 >= 5 and 法定代表人 != '张超'	企业融资
qid000893	select 中文名 from 企业 where TIME_NOW - 成立时间 >= 3 or 注册资本 <= 1000000	企业融资
qid000894	select 中文名 法定代表人 from 企业 where TIME_NOW - 成立时间 < 14	企业融资
qid000895	select 中文名 from 企业 where TIME_NOW - 成立时间 > 7 or 注册资本 == 1000000	企业融资
qid000896	select 中文名 from 企业 where TIME_NOW - 成立时间 > 2 and 注册资本 != 1000000	企业融资
qid000897	select 中文名 from 企业 where TIME_NOW - 成立时间 <= 9 and 注册资本 < 1000000	企业融资
qid000898	select 中文名 from 企业 where TIME_NOW - 成立时间 == 4 and 注册资本 != 1000000	企业融资
qid000899	select 中文名 from 企业 where TIME_NOW - 成立时间 >= 15 and 注册资本 == 1000000	企业融资
qid000900	select 中文名 from 企业 where TIME_NOW - 成立时间 != 20 and 注册资本 != 1000000	企业融资
qid000901	select 中文名 from 企业 where TIME_NOW - 成立时间 >= 18 and 注册资本 <= 1000000	企业融资
qid000902	select 中文名 from 企业 where TIME_NOW - 成立时间 < 14 and 注册资本 < 1000000	企业融资
qid000903	select 中文名 from 企业 where TIME_NOW - 成立时间 > 15 and 注册资本 == 1000000	企业融资
qid000904	select 中文名 from 企业 where TIME_NOW - 成立时间 == 12 or 注册资本 != 1000000	企业融资
qid000905	select 中文名 from 企业 where TIME_NOW - 成立时间 >= 8 and 注册资本 < 1000000	企业融资
qid000906	select 中文名 from 企业 where TIME_NOW - 成立时间 == 17 or 注册资本 >= 1000000	企业融资
qid000907	select 中文名 from 企业 where TIME_NOW - 成立时间 < 13 or 注册资本 < 1000000	企业融资
qid000908	select 中文名 from 企业 where TIME_NOW - 成立时间 > 10 and 注册资本 < 1000000	企业融资
qid000909	select 中文名 from 企业 where TIME_NOW - 成立时间 > 18 and 注册资本 <= 1000000	企业融资
qid000910	select 中文名 from 企业 where TIME_NOW - 成立时间 > 16	企业融资
qid000911	select 所属公司 from 打车APP where 覆盖城市数 < 40 group by 所属公司 having sum ( 服务用户数量 / 覆盖城市数 ) <= 100000	打车软件
qid000912	select 所属公司 from 打车APP where 覆盖城市数 > 40 group by 所属公司 having sum ( 服务用户数量 / 覆盖城市数 ) >= 100000	打车软件
qid000913	select 所属公司 from 洗衣机品牌 where 市场份额 != 0.02 group by 所属公司 having avg ( 2018年营业额 - 2018年利润 ) > 300000000	洗衣机
qid000914	select 所属公司 from 洗衣机品牌 where 成立时间 > 1935 group by 所属公司 having sum ( 2018年营业额 - 2018年利润 ) > 300000000	洗衣机
qid000915	select 国家 from 坚果摄入量 where 人均摄入量 < 0.003 group by 国家 having avg ( 人均摄入量 - 世界人均摄入量 ) > 0.001	坚果
qid000916	select 国家 from 坚果摄入量 where 人均摄入量 > 0.003 group by 国家 having avg ( 人均摄入量 - 世界人均摄入量 ) == 0.001	坚果
qid000917	select 城市 from 洗衣机品牌门店 where 门店数量 > 100 group by 城市 having sum ( 售卖量 * 平均售价 ) < 50000000	洗衣机
qid000918	select 城市 from 洗衣机品牌门店 where 门店数量 <= 100 group by 城市 having avg ( 售卖量 * 平均售价 ) < 1000000	洗衣机
qid000919	select 所属公司 from 洗衣机品牌 group by 所属公司 order by avg ( 2018年营业额 - 2018年利润 ) desc limit 1	洗衣机
qid000920	select 所属公司 from 洗衣机品牌 group by 所属公司 order by avg ( 2018年营业额 - 2018年利润 ) asc limit 1	洗衣机
qid000921	select 类别 from 高校 group by 类别 order by avg ( 本科生数量 + 研究生数量 ) desc limit 1	中国高校
qid000922	select 类别 from 高校 group by 类别 order by avg ( 本科生数量 + 研究生数量 ) asc limit 1	中国高校
qid000923	select 国家 from 坚果摄入量 group by 国家 order by avg ( 人均摄入量 - 世界人均摄入量 ) asc limit 5	坚果
qid000924	select 国家 from 坚果摄入量 group by 国家 order by avg ( 人均摄入量 - 世界人均摄入量 ) desc limit 3	坚果
qid000925	select 城市 from 洗衣机品牌门店 group by 城市 order by avg ( 售卖量 * 平均售价 ) asc limit 5	洗衣机
qid000926	select 城市 from 洗衣机品牌门店 group by 城市 order by avg ( 售卖量 * 平均售价 ) desc limit 1	洗衣机
qid000927	select 球队 from 比赛记录 group by 球队 order by avg ( 抢断 + 助攻 ) desc limit 3	运动员比赛记录
qid000928	select 球队 from 比赛记录 group by 球队 order by avg ( 抢断 + 助攻 ) asc limit 5	运动员比赛记录
qid000929	select 所属公司 from 打车APP group by 所属公司 order by avg ( 服务用户数量 / 覆盖城市数 ) asc limit 5	打车软件
qid000930	select 所属公司 from 打车APP group by 所属公司 order by avg ( 服务用户数量 / 覆盖城市数 ) asc limit 1	打车软件
qid000931	select 所属省份 from 城市 group by 所属省份 order by avg ( 常住人口 / 城区面积 ) asc limit 5	中国历史名城
qid000932	select 所属省份 from 城市 group by 所属省份 order by avg ( 常住人口 / 城区面积 ) desc limit 3	中国历史名城
qid000933	select 2018年营业额 - 2018年利润 from 洗衣机品牌	洗衣机
qid000934	select 饱和脂肪含量 + 不饱和脂肪含量 from 坚果	坚果
qid000935	select 财政预算收入(亿) - 预算支出额度(亿) from 各省财政收入	城市财政收入
qid000936	select 本科生数量 + 研究生数量 from 高校	中国高校
qid000937	select 常住人口 / 城区面积 from 城市	中国历史名城
qid000938	select 民用枪支数 + 军用枪支数 from 国家	枪击事件
qid000939	select 服务用户数量 / 覆盖城市数 from 打车APP	打车软件
qid000940	select 上线时间 - 开播时间 , 开播时间 from 电视台	中国卫视频道
qid000941	select 上线时间 - 开播时间 , 隶属机构 from 电视台	中国卫视频道
qid000942	select 2018年营业额 - 2018年利润 , 市场份额 from 洗衣机品牌	洗衣机
qid000943	select 2018年营业额 - 2018年利润 , 所属公司 from 洗衣机品牌	洗衣机
qid000944	select 2018年营业额 - 2018年利润 , 成立时间 from 洗衣机品牌	洗衣机
qid000945	select 饱和脂肪含量 + 不饱和脂肪含量 , 饱和脂肪含量 from 坚果	坚果
qid000946	select 财政预算收入(亿) - 预算支出额度(亿) , GDP总计(亿) from 各省财政收入	城市财政收入
qid000947	select 本科生数量 + 研究生数量 , 类别 from 高校	中国高校
qid000948	select 本科生数量 + 研究生数量 , 创办时间 from 高校	中国高校
qid000949	select 服务用户数量 / 覆盖城市数 , 所属公司 from 打车APP	打车软件
qid000950	select 服务用户数量 / 覆盖城市数 , 上线时间 from 打车APP	打车软件
qid000951	select 服务用户数量 / 覆盖城市数 , 覆盖城市数 from 打车APP	打车软件
qid000952	select 民用枪支数 + 军用枪支数 , 人口数量 from 国家	枪击事件
qid000953	select 常住人口 / 城区面积 , 所属省份 from 城市	中国历史名城
qid000954	select max ( 2018年营业额 - 2018年利润 ) from 洗衣机品牌	洗衣机
qid000955	select sum ( 2018年营业额 - 2018年利润 ) from 洗衣机品牌	洗衣机
qid000956	select avg ( 2018年营业额 - 2018年利润 ) from 洗衣机品牌	洗衣机
qid000957	select min ( 饱和脂肪含量 + 不饱和脂肪含量 ) from 坚果	坚果
qid000958	select max ( 饱和脂肪含量 + 不饱和脂肪含量 ) from 坚果	坚果
qid000959	select sum ( 饱和脂肪含量 + 不饱和脂肪含量 ) from 坚果	坚果
qid000960	select min ( 财政预算收入(亿) - 预算支出额度(亿) ) from 各省财政收入	城市财政收入
qid000961	select max ( 财政预算收入(亿) - 预算支出额度(亿) ) from 各省财政收入	城市财政收入
qid000962	select sum ( 财政预算收入(亿) - 预算支出额度(亿) ) from 各省财政收入	城市财政收入
qid000963	select min ( 本科生数量 + 研究生数量 ) from 高校	中国高校
qid000964	select avg ( 本科生数量 + 研究生数量 ) from 高校	中国高校
qid000965	select max ( 本科生数量 + 研究生数量 ) from 高校	中国高校
qid000966	select min ( 常住人口 / 城区面积 ) from 城市	中国历史名城
qid000967	select avg ( 常住人口 / 城区面积 ) from 城市	中国历史名城
qid000968	select sum ( 常住人口 / 城区面积 ) from 城市	中国历史名城
qid000969	select avg ( 民用枪支数 + 军用枪支数 ) from 国家	枪击事件
qid000970	select sum ( 民用枪支数 + 军用枪支数 ) from 国家	枪击事件
qid000971	select min ( 民用枪支数 + 军用枪支数 ) from 国家	枪击事件
qid000972	select min ( 服务用户数量 / 覆盖城市数 ) from 打车APP	打车软件
qid000973	select sum ( 服务用户数量 / 覆盖城市数 ) from 打车APP	打车软件
qid000974	select max ( 服务用户数量 / 覆盖城市数 ) from 打车APP	打车软件
qid000975	select max ( 民用枪支数 + 军用枪支数 ) , avg ( 人口数量 ) from 国家	枪击事件
qid000976	select avg ( 民用枪支数 + 军用枪支数 ) , sum ( 人口数量 ) from 国家	枪击事件
qid000977	select sum ( 民用枪支数 + 军用枪支数 ) , min ( 人口数量 ) from 国家	枪击事件
qid000978	select min ( 服务用户数量 / 覆盖城市数 ) , sum ( 覆盖城市数 ) from 打车APP	打车软件
qid000979	select avg ( 服务用户数量 / 覆盖城市数 ) , sum ( 覆盖城市数 ) from 打车APP	打车软件
qid000980	select avg ( 服务用户数量 / 覆盖城市数 ) , min ( 覆盖城市数 ) from 打车APP	打车软件
qid000981	select max ( 2018年营业额 - 2018年利润 ) , min ( 市场份额 ) from 洗衣机品牌	洗衣机
qid000982	select min ( 2018年营业额 - 2018年利润 ) , max ( 市场份额 ) from 洗衣机品牌	洗衣机
qid000983	select sum ( 财政预算收入(亿) - 预算支出额度(亿) ) , avg ( GDP总计(亿) ) from 各省财政收入	城市财政收入
qid000984	select avg ( 财政预算收入(亿) - 预算支出额度(亿) ) , avg ( GDP总计(亿) ) from 各省财政收入	城市财政收入
qid000985	select sum ( 财政预算收入(亿) - 预算支出额度(亿) ) , sum ( GDP总计(亿) ) from 各省财政收入	城市财政收入
qid000986	select min ( 饱和脂肪含量 + 不饱和脂肪含量 ) , avg ( 饱和脂肪含量 ) from 坚果	坚果
qid000987	select avg ( 饱和脂肪含量 + 不饱和脂肪含量 ) , avg ( 饱和脂肪含量 ) from 坚果	坚果
qid000988	select min ( 饱和脂肪含量 + 不饱和脂肪含量 ) , min ( 饱和脂肪含量 ) from 坚果	坚果
qid000989	select 名称 from 电视台 order by 上线时间 - 开播时间 desc	中国卫视频道
qid000990	select 名称 from 电视台 order by 上线时间 - 开播时间 asc	中国卫视频道
qid000991	select 名称 from 洗衣机品牌 order by 2018年营业额 - 2018年利润 asc	洗衣机
qid000992	select 名称 from 洗衣机品牌 order by 2018年营业额 - 2018年利润 desc	洗衣机
qid000993	select 名称 from 坚果 order by 饱和脂肪含量 + 不饱和脂肪含量 asc	坚果
qid000994	select 名称 from 坚果 order by 饱和脂肪含量 + 不饱和脂肪含量 desc	坚果
qid000995	select 省份 from 各省财政收入 order by 财政预算收入(亿) - 预算支出额度(亿) desc	城市财政收入
qid000996	select 省份 from 各省财政收入 order by 财政预算收入(亿) - 预算支出额度(亿) asc	城市财政收入
qid000997	select 名称 from 高校 order by 本科生数量 + 研究生数量 desc	中国高校
qid000998	select 名称 from 高校 order by 本科生数量 + 研究生数量 asc	中国高校
qid000999	select app名称 from 打车APP order by 服务用户数量 / 覆盖城市数 asc	打车软件
qid001000	select app名称 from 打车APP order by 服务用户数量 / 覆盖城市数 desc	打车软件
qid001001	select 名称 from 城市 order by 常住人口 / 城区面积 desc	中国历史名城
qid001002	select 名称 from 城市 order by 常住人口 / 城区面积 asc	中国历史名城
qid001003	select 名称 from 国家 order by 民用枪支数 + 军用枪支数 desc	枪击事件
qid001004	select 名称 from 国家 order by 民用枪支数 + 军用枪支数 asc	枪击事件
qid001005	select 名称 from 电视台 order by 上线时间 - 开播时间 asc limit 3	中国卫视频道
qid001006	select 名称 from 电视台 order by 上线时间 - 开播时间 desc limit 3	中国卫视频道
qid001007	select 名称 from 洗衣机品牌 order by 2018年营业额 - 2018年利润 asc limit 3	洗衣机
qid001008	select 名称 from 洗衣机品牌 order by 2018年营业额 - 2018年利润 desc limit 3	洗衣机
qid001009	select 名称 from 坚果 order by 饱和脂肪含量 + 不饱和脂肪含量 asc limit 3	坚果
qid001010	select 名称 from 坚果 order by 饱和脂肪含量 + 不饱和脂肪含量 desc limit 3	坚果
qid001011	select 省份 from 各省财政收入 order by 财政预算收入(亿) - 预算支出额度(亿) asc limit 3	城市财政收入
qid001012	select 省份 from 各省财政收入 order by 财政预算收入(亿) - 预算支出额度(亿) desc limit 3	城市财政收入
qid001013	select 名称 from 高校 order by 本科生数量 + 研究生数量 asc limit 3	中国高校
qid001014	select 名称 from 高校 order by 本科生数量 + 研究生数量 desc limit 3	中国高校
qid001015	select app名称 from 打车APP order by 服务用户数量 / 覆盖城市数 desc limit 3	打车软件
qid001016	select app名称 from 打车APP order by 服务用户数量 / 覆盖城市数 asc limit 3	打车软件
qid001017	select 名称 from 城市 order by 常住人口 / 城区面积 desc limit 3	中国历史名城
qid001018	select 名称 from 城市 order by 常住人口 / 城区面积 asc limit 3	中国历史名城
qid001019	select 名称 from 国家 order by 民用枪支数 + 军用枪支数 asc limit 3	枪击事件
qid001020	select 名称 from 国家 order by 民用枪支数 + 军用枪支数 desc limit 3	枪击事件
qid001021	select app名称 , 服务用户数量 / 覆盖城市数 from 打车APP where 上线时间 >= 2014	打车软件
qid001022	select app名称 , 服务用户数量 / 覆盖城市数 from 打车APP where 上线时间 > 2014	打车软件
qid001023	select app名称 , 服务用户数量 / 覆盖城市数 from 打车APP where 覆盖城市数 < 400	打车软件
qid001024	select app名称 , 服务用户数量 / 覆盖城市数 from 打车APP where 覆盖城市数 != 400	打车软件
qid001025	select 名称 , 上线时间 - 开播时间 from 电视台 where 开播时间 <= 1997-01-01	中国卫视频道
qid001026	select 名称 , 上线时间 - 开播时间 from 电视台 where 开播时间 >= 1997-01-01	中国卫视频道
qid001027	select 名称 , 上线时间 - 开播时间 from 电视台 where 开播时间 < 1997-01-01	中国卫视频道
qid001028	select 名称 , 上线时间 - 开播时间 from 电视台 where 开播时间 > 1997-01-01	中国卫视频道
qid001029	select 名称 , 2018年营业额 - 2018年利润 from 洗衣机品牌 where 成立时间 > 1935	洗衣机
qid001030	select 名称 , 2018年营业额 - 2018年利润 from 洗衣机品牌 where 市场份额 < 0.02	洗衣机
qid001031	select 名称 , 2018年营业额 - 2018年利润 from 洗衣机品牌 where 成立时间 <= 1935	洗衣机
qid001032	select 名称 , 2018年营业额 - 2018年利润 from 洗衣机品牌 where 市场份额 != 0.02	洗衣机
qid001033	select 名称 , 民用枪支数 + 军用枪支数 from 国家 where 人口数量 <= 27580000	枪击事件
qid001034	select 名称 , 民用枪支数 + 军用枪支数 from 国家 where 人口数量 > 27580000	枪击事件
qid001035	select 名称 , 民用枪支数 + 军用枪支数 from 国家 where 人口数量 >= 27580000	枪击事件
qid001036	select 名称 , 民用枪支数 + 军用枪支数 from 国家 where 人口数量 == 27580000	枪击事件
qid001037	select 名称 , 饱和脂肪含量 + 不饱和脂肪含量 from 坚果 where 饱和脂肪含量 == 3	坚果
qid001038	select 名称 , 饱和脂肪含量 + 不饱和脂肪含量 from 坚果 where 饱和脂肪含量 < 3	坚果
qid001039	select 名称 , 饱和脂肪含量 + 不饱和脂肪含量 from 坚果 where 饱和脂肪含量 >= 3	坚果
qid001040	select 名称 , 饱和脂肪含量 + 不饱和脂肪含量 from 坚果 where 饱和脂肪含量 <= 3	坚果
qid001041	select 名称 , 本科生数量 + 研究生数量 from 高校 where 创办时间 > 1924	中国高校
qid001042	select 名称 , 本科生数量 + 研究生数量 from 高校 where 创办时间 >= 1924	中国高校
qid001043	select 名称 , 本科生数量 + 研究生数量 from 高校 where 创办时间 <= 1924	中国高校
qid001044	select 名称 , 本科生数量 + 研究生数量 from 高校 where 创办时间 < 1924	中国高校
qid001045	select 名称 , 2018年营业额 - 2018年利润 , 所属公司 from 洗衣机品牌 where 市场份额 != 0.02	洗衣机
qid001046	select 名称 , 2018年营业额 - 2018年利润 , 所属公司 from 洗衣机品牌 where 市场份额 > 0.02	洗衣机
qid001047	select 名称 , 2018年营业额 - 2018年利润 , 所属公司 from 洗衣机品牌 where 成立时间 <= 1935	洗衣机
qid001048	select 名称 , 本科生数量 + 研究生数量 , 类别 from 高校 where 创办时间 <= 1924	中国高校
qid001049	select 名称 , 本科生数量 + 研究生数量 , 类别 from 高校 where 创办时间 < 1924	中国高校
qid001050	select 名称 , 本科生数量 + 研究生数量 , 类别 from 高校 where 创办时间 >= 1924	中国高校
qid001051	select 名称 , 上线时间 - 开播时间 , 隶属机构 from 电视台 where 开播时间 >= 1997-01-01	中国卫视频道
qid001052	select 名称 , 上线时间 - 开播时间 , 隶属机构 from 电视台 where 开播时间 < 1997-01-01	中国卫视频道
qid001053	select 名称 , 上线时间 - 开播时间 , 隶属机构 from 电视台 where 开播时间 > 1997-01-01	中国卫视频道
qid001054	select app名称 , 服务用户数量 / 覆盖城市数 , 所属公司 from 打车APP where 覆盖城市数 == 400	打车软件
qid001055	select app名称 , 服务用户数量 / 覆盖城市数 , 所属公司 from 打车APP where 上线时间 > 2014	打车软件
qid001056	select app名称 , 服务用户数量 / 覆盖城市数 , 所属公司 from 打车APP where 覆盖城市数 > 400	打车软件
qid001057	select 名称 , 上线时间 - 开播时间 from 电视台 where 上线时间 - 开播时间 < 1	中国卫视频道
qid001058	select 名称 , 上线时间 - 开播时间 from 电视台 where 上线时间 - 开播时间 >= 3	中国卫视频道
qid001059	select 名称 , 上线时间 - 开播时间 from 电视台 where 上线时间 - 开播时间 > 3	中国卫视频道
qid001060	select 名称 , 2018年营业额 - 2018年利润 from 洗衣机品牌 where 2018年营业额 - 2018年利润 < 300000	洗衣机
qid001061	select 名称 , 2018年营业额 - 2018年利润 from 洗衣机品牌 where 2018年营业额 - 2018年利润 >= 300000	洗衣机
qid001062	select 名称 , 2018年营业额 - 2018年利润 from 洗衣机品牌 where 2018年营业额 - 2018年利润 <= 300000	洗衣机
qid001063	select 名称 , 饱和脂肪含量 + 不饱和脂肪含量 from 坚果 where 饱和脂肪含量 + 不饱和脂肪含量 > 0.003	坚果
qid001064	select 名称 , 饱和脂肪含量 + 不饱和脂肪含量 from 坚果 where 饱和脂肪含量 + 不饱和脂肪含量 < 0.003	坚果
qid001065	select 名称 , 饱和脂肪含量 + 不饱和脂肪含量 from 坚果 where 饱和脂肪含量 + 不饱和脂肪含量 <= 0.003	坚果
qid001066	select 省份 , 财政预算收入(亿) - 预算支出额度(亿) from 各省财政收入 where 财政预算收入(亿) - 预算支出额度(亿) <= 100	城市财政收入
qid001067	select 省份 , 财政预算收入(亿) - 预算支出额度(亿) from 各省财政收入 where 财政预算收入(亿) - 预算支出额度(亿) >= 100	城市财政收入
qid001068	select 省份 , 财政预算收入(亿) - 预算支出额度(亿) from 各省财政收入 where 财政预算收入(亿) - 预算支出额度(亿) < 100	城市财政收入
qid001069	select 名称 , 本科生数量 + 研究生数量 from 高校 where 本科生数量 + 研究生数量 != 20000	中国高校
qid001070	select 名称 , 本科生数量 + 研究生数量 from 高校 where 本科生数量 + 研究生数量 <= 20000	中国高校
qid001071	select 名称 , 本科生数量 + 研究生数量 from 高校 where 本科生数量 + 研究生数量 >= 20000	中国高校
qid001072	select app名称 , 服务用户数量 / 覆盖城市数 from 打车APP where 服务用户数量 / 覆盖城市数 < 100000	打车软件
qid001073	select app名称 , 服务用户数量 / 覆盖城市数 from 打车APP where 服务用户数量 / 覆盖城市数 <= 100000	打车软件
qid001074	select 名称 , 常住人口 / 城区面积 from 城市 where 常住人口 / 城区面积 >= 3.3	中国历史名城
qid001075	select 名称 , 常住人口 / 城区面积 from 城市 where 常住人口 / 城区面积 <= 3.3	中国历史名城
qid001076	select 名称 , 常住人口 / 城区面积 from 城市 where 常住人口 / 城区面积 > 3.3	中国历史名城
qid001077	select 名称 , 民用枪支数 + 军用枪支数 from 国家 where 民用枪支数 + 军用枪支数 < 30000	枪击事件
qid001078	select 名称 , 民用枪支数 + 军用枪支数 from 国家 where 民用枪支数 + 军用枪支数 >= 30000	枪击事件
qid001079	select 名称 , 民用枪支数 + 军用枪支数 from 国家 where 民用枪支数 + 军用枪支数 <= 30000	枪击事件
qid001080	select 名称 , 所属公司 from 洗衣机品牌 where 2018年营业额 - 2018年利润 == 300000000	洗衣机
qid001081	select 名称 , 2018年营业额 - 2018年利润 , 所属公司 from 洗衣机品牌 where 2018年营业额 - 2018年利润 > 300000000	洗衣机
qid001082	select 名称 , 2018年营业额 - 2018年利润 , 所属公司 from 洗衣机品牌 where 2018年营业额 - 2018年利润 >= 300000000	洗衣机
qid001083	select 名称 , 类别 from 高校 where 本科生数量 + 研究生数量 == 10000	中国高校
qid001084	select 名称 , 本科生数量 + 研究生数量 , 类别 from 高校 where 本科生数量 + 研究生数量 != 10000	中国高校
qid001085	select 名称 , 本科生数量 + 研究生数量 , 类别 from 高校 where 本科生数量 + 研究生数量 >= 10000	中国高校
qid001086	select 名称 , 上线时间 - 开播时间 , 隶属机构 from 电视台 where 上线时间 - 开播时间 < 1	中国卫视频道
qid001087	select 名称 , 上线时间 - 开播时间 , 隶属机构 from 电视台 where 上线时间 - 开播时间 > 1	中国卫视频道
qid001088	select 名称 , 隶属机构 from 电视台 where 上线时间 - 开播时间 == 1	中国卫视频道
qid001089	select app名称 , 服务用户数量 / 覆盖城市数 , 所属公司 from 打车APP where 服务用户数量 / 覆盖城市数 > 100	打车软件
qid001090	select app名称 , 服务用户数量 / 覆盖城市数 , 所属公司 from 打车APP where 服务用户数量 / 覆盖城市数 <= 100	打车软件
qid001091	select app名称 , 服务用户数量 / 覆盖城市数 , 所属公司 from 打车APP where 服务用户数量 / 覆盖城市数 >= 100	打车软件
qid001092	select 名称 , 常住人口 / 城区面积 , 所属省份 from 城市 where 常住人口 / 城区面积 < 3.3	中国历史名城
qid001093	select 名称 , 常住人口 / 城区面积 , 所属省份 from 城市 where 常住人口 / 城区面积 >= 3.3	中国历史名城
qid001094	select 名称 from 电视台 where 上线时间 - 开播时间 > ( select avg ( 上线时间 - 开播时间 ) from 电视台 )	中国卫视频道
qid001095	select 名称 from 电视台 where 上线时间 - 开播时间 <= ( select avg ( 上线时间 - 开播时间 ) from 电视台 )	中国卫视频道
qid001096	select 名称 from 电视台 where 上线时间 - 开播时间 < ( select avg ( 上线时间 - 开播时间 ) from 电视台 )	中国卫视频道
qid001097	select 名称 from 洗衣机品牌 where 2018年营业额 - 2018年利润 > ( select avg ( 2018年营业额 - 2018年利润 ) from 洗衣机品牌 )	洗衣机
qid001098	select 名称 from 洗衣机品牌 where 2018年营业额 - 2018年利润 >= ( select avg ( 2018年营业额 - 2018年利润 ) from 洗衣机品牌 )	洗衣机
qid001099	select 名称 from 洗衣机品牌 where 2018年营业额 - 2018年利润 == ( select avg ( 2018年营业额 - 2018年利润 ) from 洗衣机品牌 )	洗衣机
qid001100	select 名称 from 坚果 where 饱和脂肪含量 + 不饱和脂肪含量 < ( select avg ( 饱和脂肪含量 + 不饱和脂肪含量 ) from 坚果 )	坚果
qid001101	select 名称 from 坚果 where 饱和脂肪含量 + 不饱和脂肪含量 >= ( select avg ( 饱和脂肪含量 + 不饱和脂肪含量 ) from 坚果 )	坚果
qid001102	select 名称 from 坚果 where 饱和脂肪含量 + 不饱和脂肪含量 == ( select avg ( 饱和脂肪含量 + 不饱和脂肪含量 ) from 坚果 )	坚果
qid001103	select 省份 from 各省财政收入 where 财政预算收入(亿) - 预算支出额度(亿) > ( select avg ( 财政预算收入(亿) - 预算支出额度(亿) ) from 各省财政收入 )	城市财政收入
qid001104	select 省份 from 各省财政收入 where 财政预算收入(亿) - 预算支出额度(亿) <= ( select avg ( 财政预算收入(亿) - 预算支出额度(亿) ) from 各省财政收入 )	城市财政收入
qid001105	select 省份 from 各省财政收入 where 财政预算收入(亿) - 预算支出额度(亿) < ( select avg ( 财政预算收入(亿) - 预算支出额度(亿) ) from 各省财政收入 )	城市财政收入
qid001106	select 名称 from 高校 where 本科生数量 + 研究生数量 == ( select avg ( 本科生数量 + 研究生数量 ) from 高校 )	中国高校
qid001107	select 名称 from 高校 where 本科生数量 + 研究生数量 >= ( select avg ( 本科生数量 + 研究生数量 ) from 高校 )	中国高校
qid001108	select 名称 from 高校 where 本科生数量 + 研究生数量 < ( select avg ( 本科生数量 + 研究生数量 ) from 高校 )	中国高校
qid001109	select app名称 from 打车APP where 服务用户数量 / 覆盖城市数 < ( select avg ( 服务用户数量 / 覆盖城市数 ) from 打车APP )	打车软件
qid001110	select app名称 from 打车APP where 服务用户数量 / 覆盖城市数 <= ( select avg ( 服务用户数量 / 覆盖城市数 ) from 打车APP )	打车软件
qid001111	select app名称 from 打车APP where 服务用户数量 / 覆盖城市数 == ( select avg ( 服务用户数量 / 覆盖城市数 ) from 打车APP )	打车软件
qid001112	select 名称 from 城市 where 常住人口 / 城区面积 == ( select avg ( 常住人口 / 城区面积 ) from 城市 )	中国历史名城
qid001113	select 名称 from 城市 where 常住人口 / 城区面积 >= ( select avg ( 常住人口 / 城区面积 ) from 城市 )	中国历史名城
qid001114	select 名称 from 城市 where 常住人口 / 城区面积 <= ( select avg ( 常住人口 / 城区面积 ) from 城市 )	中国历史名城
qid001115	select 名称 from 国家 where 民用枪支数 + 军用枪支数 > ( select avg ( 民用枪支数 + 军用枪支数 ) from 国家 )	枪击事件
qid001116	select 名称 from 国家 where 民用枪支数 + 军用枪支数 < ( select avg ( 民用枪支数 + 军用枪支数 ) from 国家 )	枪击事件
qid001117	select 名称 from 国家 where 民用枪支数 + 军用枪支数 == ( select avg ( 民用枪支数 + 军用枪支数 ) from 国家 )	枪击事件
qid001118	select 名称 from 洗衣机品牌 where 2018年营业额 - 2018年利润 > ( select sum ( 2018年营业额 - 2018年利润 ) from 洗衣机品牌 where 所属公司 == '西门子集团' )	洗衣机
qid001119	select 名称 from 洗衣机品牌 where 2018年营业额 - 2018年利润 == ( select avg ( 2018年营业额 - 2018年利润 ) from 洗衣机品牌 where 所属公司 == '西门子集团' )	洗衣机
qid001120	select 名称 from 洗衣机品牌 where 2018年营业额 - 2018年利润 == ( select max ( 2018年营业额 - 2018年利润 ) from 洗衣机品牌 where 所属公司 == '西门子集团' )	洗衣机
qid001121	select 名称 from 高校 where 本科生数量 + 研究生数量 <= ( select sum ( 本科生数量 + 研究生数量 ) from 高校 where 类别 == '公立大学' )	中国高校
qid001122	select 名称 from 高校 where 本科生数量 + 研究生数量 >= ( select sum ( 本科生数量 + 研究生数量 ) from 高校 where 类别 == '公立大学' )	中国高校
qid001123	select 名称 from 高校 where 本科生数量 + 研究生数量 == ( select avg ( 本科生数量 + 研究生数量 ) from 高校 where 类别 == '公立大学' )	中国高校
qid001124	select 名称 from 城市 where 常住人口 / 城区面积 == ( select max ( 常住人口 / 城区面积 ) from 城市 where 所属省份 == '湖北' )	中国历史名城
qid001125	select 名称 from 城市 where 常住人口 / 城区面积 > ( select min ( 常住人口 / 城区面积 ) from 城市 where 所属省份 == '湖北' )	中国历史名城
qid001126	select 名称 from 城市 where 常住人口 / 城区面积 >= ( select sum ( 常住人口 / 城区面积 ) from 城市 where 所属省份 == '湖北' )	中国历史名城
qid001127	select 姓名 , 民族 , 职业 from 明星 where 出生地 like '江苏'	综艺节目
qid001128	select 姓名 , 民族 from 明星 where 出生地 like '湖北'	综艺节目
qid001129	select 姓名 from 明星 where 出生地 like '湖北'	综艺节目
qid001130	select 姓名 , 性别 , 民族 from 企业人物 where 出生地 like '湖北'	CCTV中国经济年度人物
qid001131	select 姓名 , 民族 from 企业人物 where 出生地 like '湖北' and 性别 != '女'	CCTV中国经济年度人物
qid001132	select 姓名 , 性别 from 企业人物 where 出生地 like '湖北' or 年龄 == 50	CCTV中国经济年度人物
qid001133	select max ( 饱和脂肪含量 ) from 坚果	坚果
qid001134	select avg ( 饱和脂肪含量 ) from 坚果	坚果
qid001135	select max ( 覆盖城市数 ) from 打车APP	打车软件
qid001136	select avg ( 建交国家数量 ) from 城市	友好城市
qid001137	select max ( 建交国家数量 ) from 城市	友好城市
qid001138	select avg ( 售价 ) from 洗衣机型号	洗衣机
qid001139	select avg ( 注册资本 ) from 企业	企业融资
qid001140	select max ( 适用年级 ) from 参考书	教材辅助参考书
qid001141	select min ( 适用年级 ) from 参考书	教材辅助参考书
qid001142	select max ( 年营业额 ) from 公司	CCTV中国经济年度人物
qid001143	select avg ( 年营业额 ) from 公司	CCTV中国经济年度人物
qid001144	select max ( 每公里价格 ) from 打车方式	打车软件
qid001145	select min ( 每公里价格 ) from 打车方式	打车软件
qid001146	select max ( 年营业额 ) from 平台	购书平台
qid001147	select min ( 年龄 ) from 篮球运动员	运动员比赛记录
qid001148	select avg ( 容纳人数 ) from 球队	欧洲杯球队
qid001149	select sum ( 人口数量 ) from 国家	枪击事件
qid001150	select count ( * ) from 球队	欧洲杯球队
qid001151	select count ( * ) from 洗衣机品牌	洗衣机
qid001152	select max ( 适用年级 ) , avg ( 价格 ) from 参考书	教材辅助参考书
qid001153	select min ( 年营业额 ) , min ( 市值 ) from 公司	CCTV中国经济年度人物
qid001154	select avg ( 年营业额 ) , min ( 会员费 ) from 平台	购书平台
qid001155	select avg ( 年营业额 ) , sum ( 会员费 ) from 平台	购书平台
qid001156	select min ( GDP总计(亿) ) , min ( GDP同比增速 ) from 各省财政收入	城市财政收入
qid001157	select min ( 覆盖城市数 ) , min ( 服务用户数量 ) from 打车APP	打车软件
qid001158	select min ( 人口数量 ) , min ( 军用枪支数 ) from 国家	枪击事件
qid001159	select min ( 年龄 ) , count ( * ) from 企业人物	CCTV中国经济年度人物
qid001160	select count ( * ) , avg ( 年龄 ) from 韩国自杀的娱乐明星	枪击事件
qid001161	select count ( * ) , min ( 每公里价格 ) from 打车方式	打车软件
qid001162	select min ( 参赛国家数量 ) , min ( 参赛运动员数量 ) , max ( 小项项目数 ) from 夏季奥运会	奥运会参赛队伍
qid001163	select avg ( 市场份额 ) , max ( 2018年营业额 ) , avg ( 2018年利润 ) from 洗衣机品牌	洗衣机
qid001164	select avg ( 市场份额 ) , min ( 2018年营业额 ) , max ( 2018年利润 ) from 洗衣机品牌	洗衣机
qid001165	select avg ( 饱和脂肪含量 ) , sum ( 不饱和脂肪含量 ) , min ( 每100克热量 ) from 坚果	坚果
qid001166	select max ( 饱和脂肪含量 ) , sum ( 每100克热量 ) , avg ( 不饱和脂肪含量 ) from 坚果	坚果
qid001167	select min ( GDP总计(亿) ) , min ( 固定资产投资同比增速 ) , max ( 收入透明度 ) from 各省财政收入	城市财政收入
qid001168	select avg ( GDP总计(亿) ) , max ( 财政预算同比增速 ) , max ( 收入透明度 ) from 各省财政收入	城市财政收入
qid001169	select avg ( 年营业额 ) , min ( 员工数 ) , sum ( 市值 ) from 公司	CCTV中国经济年度人物
qid001170	select avg ( 年营业额 ) , sum ( 市值 ) , max ( 员工数 ) from 公司	CCTV中国经济年度人物
qid001171	select avg ( 建交国家数量 ) , min ( 跨国公司数量 ) , max ( 国外驻华大使馆数量 ) from 城市	友好城市
qid001172	select avg ( 建交国家数量 ) , avg ( 建交城市数量 ) , avg ( 国外驻华大使馆数量 ) from 城市	友好城市
qid001173	select avg ( 人口数量 ) , min ( 民用枪支数 ) , sum ( 军用枪支数 ) from 国家	枪击事件
qid001174	select 主要成就 from 名人	中国高校
qid001175	select 民族 from 明星	综艺节目
qid001176	select 性别 from 企业人物	CCTV中国经济年度人物
qid001177	select 隶属机构 from 电视台	中国卫视频道
qid001178	select 类型 from 参考书	教材辅助参考书
qid001179	select 所属地区 from 球队	欧洲杯球队
qid001180	select 出品公司 from 电视剧	中国卫视频道
qid001181	select 所属公司 from 洗衣机品牌	洗衣机
qid001182	select 系列名 from 综艺节目	综艺节目
qid001183	select 民族 , 出生地 from 明星	综艺节目
qid001184	select 性别 , 毕业院校 from 企业人物	CCTV中国经济年度人物
qid001185	select 出品公司 , 发行公司 from 电视剧	中国卫视频道
qid001186	select 类型 , 特点 from 参考书	教材辅助参考书
qid001187	select 所属地区 , 主席 from 球队	欧洲杯球队
qid001188	select 系列名 , 播出频道 from 综艺节目	综艺节目
qid001189	select 举办城市 , 吉祥物 from 夏季奥运会	奥运会参赛队伍
qid001190	select 类别 , 所属城市 from 高校	中国高校
qid001191	select 场上位置 , 球队 from 篮球运动员	运动员比赛记录
qid001192	select 产品类别 , 自动化程度 from 洗衣机型号	洗衣机
qid001193	select 作者 , 类型 from 图书	购书平台
qid001194	select 所属省 , 帮助城市id from 对口帮扶城市	友好城市
qid001195	select 法定代表人 , 所属省份 from 企业	企业融资
qid001196	select 姓名 , 性别 , 年龄 from 韩国自杀的娱乐明星	枪击事件
qid001197	select 所属地区 , 主场馆 , 容纳人数 from 球队	欧洲杯球队
qid001198	select 所属公司 , 市场份额 , 2018年营业额 from 洗衣机品牌	洗衣机
qid001199	select 类型 , 适用年级 , 价格 from 参考书	教材辅助参考书
qid001200	select 举办城市 , 吉祥物 , 参赛国家数量 from 夏季奥运会	奥运会参赛队伍
qid001201	select 场上位置 , 球队 , 年龄 from 篮球运动员	运动员比赛记录
qid001202	select 所属省份 , 建交国家数量 , 国外驻华大使馆数量 from 城市	友好城市
qid001203	select 中文名 from 企业 where 法定代表人 != '张超'	企业融资
qid001204	select 名称 from 电视台 where 隶属机构 != '北京电视台'	中国卫视频道
qid001205	select 姓名 from 韩国自杀的娱乐明星 where 年龄 >= 40	枪击事件
qid001206	select 名称 from 电视剧 where 出品公司 != '北京爱奇艺科技有限公司'	中国卫视频道
qid001207	select 名称 from 洗衣机品牌 where 市场份额 >= 0.02	洗衣机
qid001208	select 名称 from 平台 where 年营业额 <= 1400000000	购书平台
qid001209	select 节目名称 from 综艺节目 where 系列名 == '欢乐喜剧人'	综艺节目
qid001210	select 名称 from 公司 where 年营业额 >= 20000000	CCTV中国经济年度人物
qid001211	select 名称 from 打车方式 where 每公里价格 != 15	打车软件
qid001212	select app名称 from 打车APP where 覆盖城市数 < 100	打车软件
qid001213	select 名称 from 坚果 where 饱和脂肪含量 < 3	坚果
qid001214	select 城市 from 城市 where 建交国家数量 == 72	友好城市
qid001215	select 名称 from 洗衣机型号 where 售价 != 3000	洗衣机
qid001216	select 中文名 , 法定代表人 from 企业 where 注册资本 != 1000000	企业融资
qid001217	select 中文名 , 法定代表人 from 企业 where 成立时间 < 2015	企业融资
qid001218	select 姓名 , 性别 from 企业人物 where 年龄 == 35	CCTV中国经济年度人物
qid001219	select 名称 , 隶属机构 from 电视台 where 开播时间 > 1997-01-01	中国卫视频道
qid001220	select 名称 , 出品公司 from 电视剧 where 出品时间 <= 2013	中国卫视频道
qid001221	select 名称 , 出品公司 from 电视剧 where 出品时间 < 2013	中国卫视频道
qid001222	select 名称 , 所属公司 from 洗衣机品牌 where 市场份额 < 0.02	洗衣机
qid001223	select 名称 , 所属公司 from 洗衣机品牌 where 成立时间 >= 1935	洗衣机
qid001224	select 节目名称 , 系列名 from 综艺节目 where 首播时间 >= 2014-10-01	综艺节目
qid001225	select 名称 , 理念 from 打车方式 where 每公里价格 <= 15	打车软件
qid001226	select 名称 , 理念 from 打车方式 where 每公里价格 < 15	打车软件
qid001227	select app名称 , 所属公司 from 打车APP where 覆盖城市数 == 100	打车软件
qid001228	select app名称 , 所属公司 from 打车APP where 覆盖城市数 <= 100	打车软件
qid001229	select 城市 , 所属省份 from 城市 where 建交国家数量 == 72	友好城市
qid001230	select 名称 , 产品类别 from 洗衣机型号 where 售价 < 3000	洗衣机
qid001231	select 名称 , 产品类别 from 洗衣机型号 where 售价 > 3000	洗衣机
qid001232	select 书名 , 作者 from 图书 where 作者 != '路遥'	购书平台
qid001233	select 中文名 , 场上位置 from 篮球运动员 where 年龄 < 19	运动员比赛记录
qid001234	select 姓名 , 民族 from 明星 where 民族 != '演员'	综艺节目
qid001235	select 姓名 , 民族 from 明星 where 民族 == '演员'	综艺节目
qid001236	select 中文名 , 法定代表人 , 所属省份 from 企业 where 注册资本 <= 1000000	企业融资
qid001237	select 中文名 , 法定代表人 , 所属省份 from 企业 where 注册资本 > 1000000	企业融资
qid001238	select 姓名 , 性别 , 出生地 from 企业人物 where 年龄 >= 35	CCTV中国经济年度人物
qid001239	select 名称 , 出品公司 , 发行公司 from 电视剧 where 出品时间 < 2013	中国卫视频道
qid001240	select 节目名称 , 系列名 , 冠名商 from 综艺节目 where 首播时间 < 2014-10-01	综艺节目
qid001241	select 中文名 , 场上位置 , 球队 from 篮球运动员 where 年龄 >= 19	运动员比赛记录
qid001242	select 中文名 , 场上位置 , 球队 from 篮球运动员 where 场上位置 != '控球后卫'	运动员比赛记录
qid001243	select 名称 , 产品类别 , 自动化程度 from 洗衣机型号 where 售价 != 3000	洗衣机
qid001244	select 书名 , 作者 , 类型 from 图书 where 作者 != '路遥'	购书平台
qid001245	select 中文名 , 法定代表人 from 企业 where 注册资本 != 1000000 and 成立时间 > 2015	企业融资
qid001246	select 中文名 , 法定代表人 from 企业 where 法定代表人 != '张超' and 成立时间 <= 2015	企业融资
qid001247	select 名称 , 发行公司 from 电视剧 where 出品时间 >= 2013 and 出品公司 == '北京爱奇艺科技有限公司'	中国卫视频道
qid001248	select 名称 , 出品公司 from 电视剧 where 出品公司 != '北京爱奇艺科技有限公司' and 发行公司 == '东阳正午阳光影视有限公司'	中国卫视频道
qid001249	select 名称 , 出品公司 from 电视剧 where 出品公司 != '北京爱奇艺科技有限公司' and 出品时间 <= 2013	中国卫视频道
qid001250	select 名称 , 所属公司 from 洗衣机品牌 where 市场份额 > 0.02 and 2018年利润 == 10000000000	洗衣机
qid001251	select 名称 , 所属公司 from 洗衣机品牌 where 成立时间 < 1935 and 市场份额 != 0.02	洗衣机
qid001252	select 名称 , 所属公司 from 洗衣机品牌 where 成立时间 == 1935 and 市场份额 <= 0.02	洗衣机
qid001253	select 中文名 , 场上位置 from 篮球运动员 where 场上位置 != '控球后卫' and 年龄 < 19	运动员比赛记录
qid001254	select app名称 , 所属公司 from 打车APP where 覆盖城市数 == 100 and 上线时间 > 2014	打车软件
qid001255	select app名称 , 所属公司 from 打车APP where 上线时间 < 2014 and 覆盖城市数 < 100	打车软件
qid001256	select app名称 , 所属公司 from 打车APP where 上线时间 > 2014 and 覆盖城市数 > 100	打车软件
qid001257	select 城市 , 所属省份 from 城市 where 建交国家数量 >= 72 and 留学生数量 > 7000	友好城市
qid001258	select 城市 , 所属省份 from 城市 where 建交国家数量 < 72 and 国外驻华大使馆数量 < 137	友好城市
qid001259	select 名称 , 产品类别 from 洗衣机型号 where 产品类别 != '滚筒式' and 售价 <= 3000	洗衣机
qid001260	select 名称 , 自动化程度 from 洗衣机型号 where 售价 <= 3000 and 产品类别 == '滚筒式'	洗衣机
qid001261	select 书名 , 作者 from 图书 where 作者 != '路遥' and 类型 != '网络小说'	购书平台
qid001262	select 名称 , 隶属机构 from 电视台 where 隶属机构 != '北京电视台' or 开播时间 < 1997-01-01	中国卫视频道
qid001263	select 名称 , 隶属机构 from 电视台 where 隶属机构 != '北京电视台' or 开播时间 >= 1997-01-01	中国卫视频道
qid001264	select 名称 , 隶属机构 from 电视台 where 隶属机构 == '北京电视台' or 开播时间 >= 1997-01-01	中国卫视频道
qid001265	select 中文名 , 法定代表人 from 企业 where 法定代表人 != '张超' or 注册资本 <= 1000000	企业融资
qid001266	select 中文名 , 法定代表人 from 企业 where 注册资本 != 1000000 or 成立时间 <= 2015	企业融资
qid001267	select 姓名 , 民族 from 企业人物 where 年龄 <= 35 or 性别 != '女'	CCTV中国经济年度人物
qid001268	select 姓名 , 性别 from 企业人物 where 性别 != '女' or 毕业院校 == '武汉大学'	CCTV中国经济年度人物
qid001269	select 名称 , 出品公司 from 电视剧 where 出品公司 != '北京爱奇艺科技有限公司' or 发行公司 != '东阳正午阳光影视有限公司'	中国卫视频道
qid001270	select 名称 , 所属公司 from 洗衣机品牌 where 市场份额 > 0.02 or 成立时间 < 1935	洗衣机
qid001271	select 节目名称 , 系列名 from 综艺节目 where 首播时间 > '2014-10-01' or 播出时间 < '22:00'	综艺节目
qid001272	select 名称 , 理念 from 打车方式 where 理念 != '优惠出行' or 每公里价格 != 15	打车软件
qid001273	select app名称 , 所属公司 from 打车APP where 覆盖城市数 != 100 or 服务用户数量 != 10000000	打车软件
qid001274	select app名称 , 所属公司 from 打车APP where 覆盖城市数 <= 100 or 上线时间 <= 2014	打车软件
qid001275	select app名称 , 所属公司 from 打车APP where 覆盖城市数 == 100 or 上线时间 >= 2014	打车软件
qid001276	select 名称 , 产品类别 from 洗衣机型号 where 产品类别 == '滚筒式' or 售价 > 3000	洗衣机
qid001277	select 名称 , 自动化程度 from 洗衣机型号 where 售价 == 3000 or 产品类别 == '滚筒式'	洗衣机
qid001278	select 书名 , 作者 from 图书 where 作者 != '路遥' or 类型 == '网络小说'	购书平台
qid001279	select 书名 , 作者 from 图书 where 作者 != '路遥' or 类型 != '网络小说'	购书平台
qid001280	select 中文名 , 场上位置 from 篮球运动员 where 场上位置 != '控球后卫' or 年龄 >= 19	运动员比赛记录
qid001281	select 名称 , 主要成就 from 名人 where 主要成就 != '“1+2”是哥德巴赫猜想研究的丰碑' order by 职业 asc	中国高校
qid001282	select 名称 , 隶属机构 from 电视台 where 开播时间 > 1997-01-01 order by 上线时间 asc	中国卫视频道
qid001283	select 名称 , 隶属机构 from 电视台 where 开播时间 < 1997-01-01 order by 上线时间 asc	中国卫视频道
qid001284	select 中文名 , 法定代表人 from 企业 where 成立时间 < 2015 order by 注册资本 desc	企业融资
qid001285	select 中文名 , 法定代表人 from 企业 where 注册资本 <= 10000000 order by 成立时间 asc	企业融资
qid001286	select 姓名 , 性别 from 企业人物 where 性别 != '男' order by 年龄 asc	CCTV中国经济年度人物
qid001287	select 姓名 , 性别 from 企业人物 where 性别 != '男' order by 年龄 desc	CCTV中国经济年度人物
qid001288	select 名称 , 类型 from 参考书 where 适用年级 < 5 order by 价格 desc	教材辅助参考书
qid001289	select 名称 , 类型 from 参考书 where 类型 != '试卷' order by 适用年级 asc	教材辅助参考书
qid001290	select 中文队名 , 所属地区 from 球队 where 成立时间 > 1960 order by 容纳人数 desc	欧洲杯球队
qid001291	select 中文队名 , 所属地区 from 球队 where 成立时间 > 1960 order by 容纳人数 asc	欧洲杯球队
qid001292	select 名称 , 理念 from 打车方式 where 理念 != '方便出行' order by 每公里价格 asc	打车软件
qid001293	select 名称 , 理念 from 打车方式 where 理念 != '方便出行' order by 每公里价格 desc	打车软件
qid001294	select 名称 , 出品公司 from 电视剧 where 出品公司 != '腾讯影业' order by 出品时间 asc	中国卫视频道
qid001295	select 名称 , 所属公司 from 洗衣机品牌 where 成立时间 <= 1935 order by 市场份额 asc	洗衣机
qid001296	select 名称 , 所属公司 from 洗衣机品牌 where 成立时间 < 1935 order by 市场份额 asc	洗衣机
qid001297	select 节目名称 , 系列名 from 综艺节目 where 系列名 != '向往的生活' order by 首播时间 asc	综艺节目
qid001298	select 节目名称 , 系列名 from 综艺节目 where 首播时间 > 2018-12-20 order by 播出时间 asc	综艺节目
qid001299	select 名称 , 类别 from 高校 where 类别 != '公立大学' order by 创办时间 asc	中国高校
qid001300	select 名称 , 举办城市 from 夏季奥运会 where 参赛国家数量 > 205 order by 小项项目数 desc	奥运会参赛队伍
qid001301	select 名称 , 举办城市 from 夏季奥运会 where 参赛国家数量 <= 205 order by 参赛运动员数量 asc	奥运会参赛队伍
qid001302	select app名称 , 所属公司 from 打车APP where 上线时间 <= 2014 order by 覆盖城市数 desc	打车软件
qid001303	select app名称 , 所属公司 from 打车APP where 覆盖城市数 <= 400 order by 服务用户数量 desc	打车软件
qid001304	select 名称 , 产品类别 from 洗衣机型号 where 产品类别 != '波轮' order by 售价 asc	洗衣机
qid001305	select 名称 , 产品类别 from 洗衣机型号 where 产品类别 != '波轮' order by 售价 desc	洗衣机
qid001306	select 中文名 , 场上位置 from 篮球运动员 where 场上位置 != '小前锋' order by 年龄 desc	运动员比赛记录
qid001307	select 中文名 , 场上位置 from 篮球运动员 where 场上位置 != '小前锋' order by 年龄 asc	运动员比赛记录
qid001308	select 名称 , 隶属机构 from 电视台 where 开播时间 < 1997-01-01 order by 上线时间 asc limit 10	中国卫视频道
qid001309	select 名称 , 隶属机构 from 电视台 where 开播时间 <= 1997-01-01 order by 上线时间 desc limit 10	中国卫视频道
qid001310	select 中文名 , 法定代表人 from 企业 where 成立时间 > 2015 order by 注册资本 desc limit 10	企业融资
qid001311	select 中文名 , 法定代表人 from 企业 where 成立时间 >= 2015 order by 注册资本 desc limit 10	企业融资
qid001312	select 中文队名 , 所属地区 from 球队 where 成立时间 >= 1960 order by 容纳人数 desc limit 10	欧洲杯球队
qid001313	select 中文队名 , 所属地区 from 球队 where 成立时间 > 1960 order by 容纳人数 desc limit 10	欧洲杯球队
qid001314	select 名称 , 所属公司 from 洗衣机品牌 where 市场份额 >= 0.02 order by 2018年营业额 desc limit 10	洗衣机
qid001315	select 名称 , 所属公司 from 洗衣机品牌 where 市场份额 != 0.02 order by 2018年营业额 desc limit 10	洗衣机
qid001316	select 节目名称 , 系列名 from 综艺节目 where 首播时间 > 2018-12-20 order by 播出时间 asc limit 10	综艺节目
qid001317	select 节目名称 , 系列名 from 综艺节目 where 首播时间 <= 2018-12-20 order by 播出时间 asc limit 10	综艺节目
qid001318	select 名称 , 类型 from 参考书 where 适用年级 != '1-3' order by 价格 desc limit 10	教材辅助参考书
qid001319	select 名称 , 类型 from 参考书 where 适用年级 >= 3 order by 价格 desc limit 10	教材辅助参考书
qid001320	select 名称 , 举办城市 from 夏季奥运会 where 参赛国家数量 < 205 order by 小项项目数 desc limit 10	奥运会参赛队伍
qid001321	select 名称 , 举办城市 from 夏季奥运会 where 参赛国家数量 != 205 order by 大项项目数 asc limit 10	奥运会参赛队伍
qid001322	select app名称 , 所属公司 from 打车APP where 覆盖城市数 < 400 order by 服务用户数量 desc limit 10	打车软件
qid001323	select app名称 , 所属公司 from 打车APP where 上线时间 <= 2014 order by 覆盖城市数 desc limit 10	打车软件
qid001324	select 城市 , 所属省份 from 城市 where 建交国家数量 != 72 order by 留学生数量 asc limit 10	友好城市
qid001325	select 城市 , 所属省份 from 城市 where 建交国家数量 != 72 order by 建交城市数量 desc limit 10	友好城市
qid001326	select 名称 , 隶属机构 from 电视台 where 隶属机构 != '北京电视台' or 开播时间 <= 1997-01-01 order by 上线时间 asc limit 3	中国卫视频道
qid001327	select 名称 , 隶属机构 from 电视台 where 隶属机构 != '北京电视台' or 开播时间 > 1997-01-01 order by 上线时间 asc limit 3	中国卫视频道
qid001328	select 中文名 , 法定代表人 from 企业 where 法定代表人 != '刘墨' or 注册资本 != 1000000 order by 成立时间 asc limit 3	企业融资
qid001329	select 中文名 , 所属省份 from 企业 where 注册资本 >= 1000000 or 法定代表人 != '刘墨' order by 成立时间 asc limit 10	企业融资
qid001330	select 姓名 , 性别 from 韩国自杀的娱乐明星 where 性别 != '女' or 死亡时间 <= '2019-11-30' order by 年龄 asc limit 3	枪击事件
qid001331	select 姓名 , 性别 from 韩国自杀的娱乐明星 where 性别 != '女' or 死亡时间 > '2019-11-30' order by 年龄 desc limit 3	枪击事件
qid001332	select 名称 , 类型 from 参考书 where 类型 != '出版书' or 适用年级 < 3 order by 价格 asc limit 3	教材辅助参考书
qid001333	select 名称 , 类型 from 参考书 where 类型 != '出版书' or 适用年级 != '1-3' order by 价格 desc limit 3	教材辅助参考书
qid001334	select 中文队名 , 创始人 from 球队 where 成立时间 > 1964 or 所属地区 != '巴西' order by 容纳人数 asc limit 10	欧洲杯球队
qid001335	select 中文队名 , 所属地区 from 球队 where 所属地区 != '巴西' or 成立时间 <= 1964 order by 容纳人数 desc limit 3	欧洲杯球队
qid001336	select 名称 , 所属公司 from 洗衣机品牌 where 市场份额 >= 0.02 or 2018年营业额 < 200700000000 order by 成立时间 asc limit 10	洗衣机
qid001337	select 名称 , 所属公司 from 洗衣机品牌 where 市场份额 < 0.02 or 成立时间 >= 1955 order by 2018年利润 desc limit 3	洗衣机
qid001338	select 节目名称 , 系列名 from 综艺节目 where 系列名 != '欢乐喜剧人' or 首播时间 >= 2014-10-01 order by 播出时间 asc limit 3	综艺节目
qid001339	select 节目名称 , 播出频道 from 综艺节目 where 首播时间 < 2014-10-01 or 系列名 != '欢乐喜剧人' order by 播出时间 asc limit 3	综艺节目
qid001340	select 名称 , 吉祥物 from 夏季奥运会 where 参赛国家数量 != 30 or 举办城市 != '雅典' order by 大项项目数 asc limit 3	奥运会参赛队伍
qid001341	select 名称 , 举办城市 from 夏季奥运会 where 举办城市 != '雅典' or 参赛国家数量 < 30 order by 小项项目数 desc limit 10	奥运会参赛队伍
qid001342	select app名称 , 所属公司 from 打车APP where 上线时间 < 2014 or 覆盖城市数 > 100 order by 服务用户数量 asc limit 3	打车软件
qid001343	select app名称 , 所属公司 from 打车APP where 上线时间 > 2014 or 覆盖城市数 < 100 order by 服务用户数量 desc limit 3	打车软件
qid001344	select 城市 , 所属省份 from 城市 where 建交国家数量 > 10 or 建交城市数量 < 13 order by 跨国公司数量 desc limit 3	友好城市
qid001345	select 城市 , 所属省份 from 城市 where 建交国家数量 < 10 or 建交城市数量 != 13 order by 跨国公司数量 desc limit 3	友好城市
qid001346	select 名称 , 隶属机构 from 电视台 where 隶属机构 != '北京电视台' and 开播时间 > 1997-01-01 order by 上线时间 asc limit 5	中国卫视频道
qid001347	select 名称 , 隶属机构 from 电视台 where 隶属机构 != '北京电视台' and 开播时间 <= 1997-01-01 order by 上线时间 asc limit 5	中国卫视频道
qid001348	select 中文名 , 法定代表人 from 企业 where 法定代表人 != '刘墨' and 成立时间 < 2015 order by 注册资本 asc limit 10	企业融资
qid001349	select 中文名 , 法定代表人 from 企业 where 法定代表人 != '刘墨' and 注册资本 > 1000000 order by 成立时间 asc limit 9	企业融资
qid001350	select 姓名 , 性别 from 韩国自杀的娱乐明星 where 性别 != '李恩珠' and 年龄 <= 20 order by 死亡时间 asc limit 5	枪击事件
qid001351	select 姓名 , 性别 from 韩国自杀的娱乐明星 where 性别 != '李恩珠' and 年龄 < 20 order by 死亡时间 asc limit 5	枪击事件
qid001352	select 中文队名 , 所属地区 from 球队 where 所属地区 != '巴西' and 成立时间 > 1964 order by 容纳人数 asc limit 10	欧洲杯球队
qid001353	select 中文队名 , 主场馆 from 球队 where 容纳人数 < 21000 and 所属地区 != '巴西' order by 成立时间 asc limit 10	欧洲杯球队
qid001354	select 名称 , 所属公司 from 洗衣机品牌 where 成立时间 >= 1955 and 市场份额 >= 0.02 order by 2018年利润 desc limit 10	洗衣机
qid001355	select 名称 , 所属公司 from 洗衣机品牌 where 市场份额 >= 0.02 and 成立时间 > 1955 order by 2018年营业额 asc limit 10	洗衣机
qid001356	select 节目名称 , 播出频道 from 综艺节目 where 首播时间 > 2014-10-01 and 系列名 != '欢乐喜剧人' order by 播出时间 asc limit 5	综艺节目
qid001357	select 节目名称 , 播出频道 from 综艺节目 where 首播时间 < 2014-10-01 and 系列名 != '欢乐喜剧人' order by 播出时间 asc limit 5	综艺节目
qid001358	select 名称 , 类型 from 参考书 where 类型 != '出版书' and 适用年级 != '1-3' order by 价格 desc limit 10	教材辅助参考书
qid001359	select 名称 , 科目类型 from 参考书 where 适用年级 <= 3 and 类型 != '出版书' order by 价格 asc limit 10	教材辅助参考书
qid001360	select app名称 , 所属公司 from 打车APP where 上线时间 < 2014 and 覆盖城市数 >= 100 order by 服务用户数量 desc limit 1	打车软件
qid001361	select app名称 , 所属公司 from 打车APP where 覆盖城市数 < 100 and 上线时间 >= 2014 order by 服务用户数量 desc limit 1	打车软件
qid001362	select 城市 , 所属省份 from 城市 where 所属省份 != '广东' and 建交国家数量 > 10 order by 留学生数量 asc limit 1	友好城市
qid001363	select 城市 , 所属省份 from 城市 where 所属省份 != '广东' and 建交国家数量 <= 10 order by 建交城市数量 asc limit 3	友好城市
qid001364	select 系列名 from 综艺节目 where 首播时间 <= 2014-10-01 group by 系列名 order by count ( * ) desc limit 1	综艺节目
qid001365	select 系列名 from 综艺节目 where 首播时间 <= 2014-10-01 group by 系列名 order by count ( * ) desc limit 3	综艺节目
qid001366	select 系列名 from 综艺节目 where 首播时间 <= 2014-10-01 group by 系列名 order by count ( * ) asc limit 3	综艺节目
qid001367	select 季节 from 坚果季节性营业收入 where 营业收入 >= 300000000 group by 季节 order by sum ( 全年占比 ) desc limit 1	坚果
qid001368	select 季节 from 坚果季节性营业收入 where 营业收入 != 300000000 group by 季节 order by count ( * ) desc limit 1	坚果
qid001369	select 季节 from 坚果季节性营业收入 where 营业收入 > 300000000 group by 季节 order by sum ( 全年占比 ) desc limit 1	坚果
qid001370	select 国家 from 坚果摄入量 where 人均摄入量 != 0.05 group by 国家 order by avg ( 世界人均摄入量 ) asc limit 1	坚果
qid001371	select 国家 from 坚果摄入量 where 人均摄入量 <= 0.05 group by 国家 order by avg ( 世界人均摄入量 ) asc limit 5	坚果
qid001372	select 国家 from 坚果摄入量 where 人均摄入量 > 0.05 group by 国家 order by count ( * ) desc limit 1	坚果
qid001373	select 法定代表人 from 企业 where 注册资本 > 1000000 group by 法定代表人 order by count ( * ) desc limit 3	企业融资
qid001374	select 法定代表人 from 企业 where 成立时间 < 2015 group by 法定代表人 order by avg ( 注册资本 ) asc limit 5	企业融资
qid001375	select 法定代表人 from 企业 where 成立时间 >= 2015 group by 法定代表人 order by avg ( 注册资本 ) desc limit 5	企业融资
qid001376	select 性别 from 企业人物 where 年龄 < 50 group by 性别 order by count ( * ) asc limit 1	CCTV中国经济年度人物
qid001377	select 出品公司 from 电视剧 where 出品时间 >= 2018 group by 出品公司 order by count ( * ) asc limit 3	中国卫视频道
qid001378	select 出品公司 from 电视剧 where 出品时间 > 2018 group by 出品公司 order by count ( * ) desc limit 1	中国卫视频道
qid001379	select 出品公司 from 电视剧 where 出品时间 >= 2018 group by 出品公司 order by count ( * ) desc limit 1	中国卫视频道
qid001380	select 球队 from 比赛记录 where 出场次数 < 40 group by 球队 order by sum ( 罚球 ) asc limit 3	运动员比赛记录
qid001381	select 球队 from 比赛记录 where 出场次数 != 40 group by 球队 order by count ( * ) asc limit 1	运动员比赛记录
qid001382	select 球队 from 比赛记录 where 出场次数 >= 40 group by 球队 order by count ( * ) asc limit 1	运动员比赛记录
qid001383	select 融资轮次 from 企业融资 where 融资总额 > 1000000000 group by 融资轮次 order by count ( * ) asc limit 1	企业融资
qid001384	select 融资轮次 from 企业融资 where 年份 >= 2010 group by 融资轮次 order by sum ( 融资总额 ) desc limit 1	企业融资
qid001385	select 融资轮次 from 企业融资 where 年份 < 2010 group by 融资轮次 order by count ( * ) asc limit 1	企业融资
qid001386	select 所属地区 from 球队 where 容纳人数 > 21000 group by 所属地区 order by count ( * ) desc limit 3	欧洲杯球队
qid001387	select 所属地区 from 球队 where 容纳人数 != 21000 group by 所属地区 order by count ( * ) asc limit 3	欧洲杯球队
qid001388	select 所属地区 from 球队 where 容纳人数 < 21000 group by 所属地区 order by count ( * ) asc limit 3	欧洲杯球队
qid001389	select 城市 from 打车软件开通城市 where 开通时间 > 2018-07 group by 城市 order by count ( * ) desc limit 1	打车软件
qid001390	select 城市 from 打车软件开通城市 where 开通时间 >= 2018-07 group by 城市 order by count ( * ) asc limit 1	打车软件
qid001391	select 城市 from 打车软件开通城市 where 开通时间 > 2018-07 group by 城市 order by count ( * ) asc limit 3	打车软件
qid001392	select 所属公司 from 洗衣机品牌 where 成立时间 < 1955 group by 所属公司 order by sum ( 市场份额 ) asc limit 3	洗衣机
qid001393	select 所属公司 from 洗衣机品牌 where 成立时间 > 1955 group by 所属公司 order by avg ( 市场份额 ) desc limit 5	洗衣机
qid001394	select 所属公司 from 洗衣机品牌 where 市场份额 <= 0.02 group by 所属公司 order by count ( * ) asc limit 3	洗衣机
qid001395	select 发生城市 from 美国近几年校园枪击事件 where 受影响学生数量 > 10000 group by 发生城市 order by count ( * ) desc limit 3	枪击事件
qid001396	select 发生城市 from 美国近几年校园枪击事件 where 受影响学生数量 != 10000 group by 发生城市 order by count ( * ) asc limit 1	枪击事件
qid001397	select 发生城市 from 美国近几年校园枪击事件 where 受影响学生数量 <= 10000 group by 发生城市 order by count ( * ) asc limit 1	枪击事件
qid001398	select 朝代 from 都城 where 建都起始时间 <= 403 group by 朝代 order by count ( * ) desc limit 1	中国历史名城
qid001399	select 朝代 from 都城 where 建都起始时间 > 403 group by 朝代 order by count ( * ) desc limit 1	中国历史名城
qid001400	select 朝代 from 都城 where 古称 != '洛' group by 朝代 order by count ( * ) desc limit 1	中国历史名城
qid001401	select 产地 from 坚果产地 where 市场占比 != 0.44 group by 产地 order by count ( * ) desc limit 1	坚果
qid001402	select 产地 from 坚果产地 where 市场占比 > 0.44 group by 产地 order by count ( * ) desc limit 1	坚果
qid001403	select 产地 from 坚果产地 where 市场占比 > 0.44 group by 产地 order by count ( * ) asc limit 1	坚果
qid001404	select 类型 from 参考书 where 适用年级 != '1-3' group by 类型 order by count ( * ) desc limit 1	教材辅助参考书
qid001405	select 类型 from 参考书 where 适用年级 <= 3 group by 类型 order by count ( * ) desc limit 1	教材辅助参考书
qid001406	select 类型 from 参考书 where 适用年级 != '1-3' group by 类型 order by count ( * ) desc limit 3	教材辅助参考书
qid001407	select 季节 , max ( 全年占比 ) from 坚果季节性营业收入 where 营业收入 < 300000000 group by 季节 order by count ( * ) desc limit 1	坚果
qid001408	select 国家 , avg ( 世界人均摄入量 ) from 坚果摄入量 where 人均摄入量 > 0.05 group by 国家 order by count ( * ) asc limit 3	坚果
qid001409	select 国家 , sum ( 世界人均摄入量 ) from 坚果摄入量 where 人均摄入量 < 0.05 group by 国家 order by count ( * ) asc limit 3	坚果
qid001410	select 国家 , sum ( 世界人均摄入量 ) from 坚果摄入量 where 人均摄入量 > 0.05 group by 国家 order by count ( * ) desc limit 1	坚果
qid001411	select 法定代表人 , min ( 注册资本 ) from 企业 where 成立时间 <= 2015 group by 法定代表人 order by count ( * ) desc limit 1	企业融资
qid001412	select 法定代表人 , avg ( 注册资本 ) from 企业 where 成立时间 >= 2015 group by 法定代表人 order by count ( * ) asc limit 3	企业融资
qid001413	select 法定代表人 , min ( 注册资本 ) from 企业 where 成立时间 <= 2015 group by 法定代表人 order by count ( * ) desc limit 3	企业融资
qid001414	select 球队 , sum ( 总篮板 ) from 比赛记录 where 出场次数 > 40 group by 球队 order by sum ( 得分 ) desc limit 1	运动员比赛记录
qid001415	select 球队 , sum ( 得分 ) from 比赛记录 where 出场次数 <= 40 group by 球队 order by count ( * ) desc limit 3	运动员比赛记录
qid001416	select 融资轮次 , avg ( 融资总额 ) from 企业融资 where 年份 <= 2010 group by 融资轮次 order by count ( * ) asc limit 3	企业融资
qid001417	select 融资轮次 , sum ( 融资总额 ) from 企业融资 where 年份 > 2010 group by 融资轮次 order by count ( * ) asc limit 3	企业融资
qid001418	select 融资轮次 , max ( 融资总额 ) from 企业融资 where 年份 > 2010 group by 融资轮次 order by count ( * ) desc limit 3	企业融资
qid001419	select 所属地区 , avg ( 容纳人数 ) from 球队 where 主场馆 != '波尔多体育场' group by 所属地区 order by count ( * ) desc limit 3	欧洲杯球队
qid001420	select 所属地区 , max ( 容纳人数 ) from 球队 where 成立时间 < 1964 group by 所属地区 order by count ( * ) desc limit 1	欧洲杯球队
qid001421	select 所属地区 , avg ( 容纳人数 ) from 球队 where 成立时间 >= 1964 group by 所属地区 order by count ( * ) asc limit 1	欧洲杯球队
qid001422	select 城市 , max ( 占所在城市份额 ) from 打车软件开通城市 where 开通时间 >= 2018-07 group by 城市 order by count ( * ) asc limit 3	打车软件
qid001423	select 城市 , min ( 占所在城市份额 ) from 打车软件开通城市 where 开通时间 < 2018-07 group by 城市 order by count ( * ) asc limit 1	打车软件
qid001424	select 城市 , avg ( 占所在城市份额 ) from 打车软件开通城市 where 开通时间 > 2018-07 group by 城市 order by count ( * ) desc limit 3	打车软件
qid001425	select 所属公司 , avg ( 市场份额 ) from 洗衣机品牌 where 成立时间 <= 1955 group by 所属公司 order by count ( * ) desc limit 1	洗衣机
qid001426	select 所属公司 , sum ( 市场份额 ) from 洗衣机品牌 where 成立时间 > 1955 group by 所属公司 order by count ( * ) asc limit 3	洗衣机
qid001427	select 所属公司 , min ( 2018年营业额 ) from 洗衣机品牌 where 市场份额 >= 0.02 group by 所属公司 order by count ( * ) asc limit 1	洗衣机
qid001428	select 发生城市 , avg ( 枪击者年龄 ) from 美国近几年校园枪击事件 where 受影响学生数量 >= 10000 group by 发生城市 order by avg ( 伤亡人数 ) asc limit 5	枪击事件
qid001429	select 发生城市 , min ( 枪击者年龄 ) from 美国近几年校园枪击事件 where 受影响学生数量 != 10000 group by 发生城市 order by count ( * ) asc limit 1	枪击事件
qid001430	select 发生城市 , sum ( 枪击者年龄 ) from 美国近几年校园枪击事件 where 受影响学生数量 > 10000 group by 发生城市 order by sum ( 伤亡人数 ) desc limit 1	枪击事件
qid001431	select 类型 , sum ( 价格 ) from 参考书 where 适用年级 <= 3 group by 类型 order by count ( * ) asc limit 1	教材辅助参考书
qid001432	select 类型 , sum ( 价格 ) from 参考书 where 适用年级 > 3 group by 类型 order by count ( * ) desc limit 1	教材辅助参考书
qid001433	select 类型 , sum ( 价格 ) from 参考书 where 适用年级 <= 3 group by 类型 order by count ( * ) desc limit 3	教材辅助参考书
qid001434	select 举办城市 , sum ( 大项项目数 ) from 夏季奥运会 where 参赛国家数量 < 30 group by 举办城市 order by avg ( 参赛运动员数量 ) desc limit 5	奥运会参赛队伍
qid001435	select 举办城市 , max ( 参赛国家数量 ) from 夏季奥运会 where 吉祥物 != '欢欢' group by 举办城市 order by count ( * ) desc limit 1	奥运会参赛队伍
qid001436	select 举办城市 , avg ( 小项项目数 ) from 夏季奥运会 where 参赛国家数量 != 30 group by 举办城市 order by avg ( 大项项目数 ) desc limit 5	奥运会参赛队伍
qid001437	select 所属公司 , avg ( 服务用户数量 ) from 打车APP where 上线时间 >= 2014 group by 所属公司 order by avg ( 覆盖城市数 ) desc limit 1	打车软件
qid001438	select 所属公司 , avg ( 服务用户数量 ) from 打车APP where 覆盖城市数 <= 100 group by 所属公司 order by count ( * ) desc limit 1	打车软件
qid001439	select 城市 , avg ( 售卖量 ) from 洗衣机品牌门店 where 门店数量 > 500 group by 城市 order by count ( * ) desc limit 3	洗衣机
qid001440	select 城市 , sum ( 平均售价 ) from 洗衣机品牌门店 where 门店数量 >= 500 group by 城市 order by count ( * ) desc limit 3	洗衣机
qid001441	select 城市 , min ( 售卖量 ) from 洗衣机品牌门店 where 门店数量 != 500 group by 城市 order by avg ( 平均售价 ) asc limit 5	洗衣机
qid001442	select 所属省份 , min ( 跨国公司数量 ) from 城市 where 建交国家数量 >= 10 group by 所属省份 order by count ( * ) desc limit 1	友好城市
qid001443	select 所属省份 , avg ( 国外驻华大使馆数量 ) from 城市 where 建交国家数量 != 10 group by 所属省份 order by count ( * ) desc limit 1	友好城市
qid001444	select 所属省份 , sum ( 留学生数量 ) from 城市 where 建交国家数量 >= 10 group by 所属省份 order by count ( * ) desc limit 1	友好城市
qid001445	select max ( 注册资本 ) , 法定代表人 from 企业 where 成立时间 >= 2015 group by 法定代表人	企业融资
qid001446	select max ( 注册资本 ) , 法定代表人 from 企业 where 成立时间 <= 2015 group by 法定代表人	企业融资
qid001447	select sum ( 注册资本 ) , 法定代表人 from 企业 where 成立时间 >= 2015 group by 法定代表人	企业融资
qid001448	select max ( 容纳人数 ) , 所属地区 from 球队 where 成立时间 <= 1964 group by 所属地区	欧洲杯球队
qid001449	select sum ( 容纳人数 ) , 所属地区 from 球队 where 成立时间 < 1964 group by 所属地区	欧洲杯球队
qid001450	select sum ( 容纳人数 ) , 所属地区 from 球队 where 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001451	select max ( 2018年营业额 ) , 所属公司 from 洗衣机品牌 where 市场份额 == 0.02 group by 所属公司	洗衣机
qid001452	select max ( 市场份额 ) , 所属公司 from 洗衣机品牌 where 成立时间 > 1955 group by 所属公司	洗衣机
qid001453	select min ( 2018年营业额 ) , 所属公司 from 洗衣机品牌 where 市场份额 == 0.02 group by 所属公司	洗衣机
qid001454	select sum ( 价格 ) , 类型 from 参考书 where 适用年级 == '1-3' group by 类型	教材辅助参考书
qid001455	select avg ( 价格 ) , 类型 from 参考书 where 适用年级 >= 3 group by 类型	教材辅助参考书
qid001456	select max ( 价格 ) , 类型 from 参考书 where 适用年级 < 3 group by 类型	教材辅助参考书
qid001457	select min ( 小项项目数 ) , 举办城市 from 夏季奥运会 where 参赛国家数量 < 30 group by 举办城市	奥运会参赛队伍
qid001458	select avg ( 大项项目数 ) , 举办城市 from 夏季奥运会 where 参赛国家数量 <= 30 group by 举办城市	奥运会参赛队伍
qid001459	select max ( 小项项目数 ) , 举办城市 from 夏季奥运会 where 参赛国家数量 >= 30 group by 举办城市	奥运会参赛队伍
qid001460	select min ( 覆盖城市数 ) , 所属公司 from 打车APP where 上线时间 >= 2014 group by 所属公司	打车软件
qid001461	select min ( 覆盖城市数 ) , 所属公司 from 打车APP where 上线时间 < 2014 group by 所属公司	打车软件
qid001462	select max ( 覆盖城市数 ) , 所属公司 from 打车APP where 上线时间 < 2014 group by 所属公司	打车软件
qid001463	select max ( 留学生数量 ) , 所属省份 from 城市 where 建交国家数量 < 10 group by 所属省份	友好城市
qid001464	select sum ( 建交城市数量 ) , 所属省份 from 城市 where 建交国家数量 < 10 group by 所属省份	友好城市
qid001465	select min ( 建交城市数量 ) , 所属省份 from 城市 where 建交国家数量 < 10 group by 所属省份	友好城市
qid001466	select 所属地区 , sum ( 容纳人数 ) from 球队 where 成立时间 > 1964 and 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001467	select 所属地区 , sum ( 容纳人数 ) from 球队 where 成立时间 < 1964 and 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001468	select 所属地区 , min ( 容纳人数 ) from 球队 where 成立时间 <= 1964 and 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001469	select 所属地区 , max ( 容纳人数 ) from 球队 where 成立时间 < 1964 and 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001470	select 所属地区 , min ( 容纳人数 ) from 球队 where 成立时间 < 1964 and 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001471	select 举办城市 , max ( 大项项目数 ) from 夏季奥运会 where 参赛国家数量 >= 30 and 参赛运动员数量 < 500 group by 举办城市	奥运会参赛队伍
qid001472	select 举办城市 , avg ( 大项项目数 ) from 夏季奥运会 where 吉祥物 != '欢欢' and 参赛国家数量 == 30 group by 举办城市	奥运会参赛队伍
qid001473	select 举办城市 , min ( 小项项目数 ) from 夏季奥运会 where 参赛国家数量 <= 30 and 参赛运动员数量 > 500 group by 举办城市	奥运会参赛队伍
qid001474	select 举办城市 , avg ( 参赛运动员数量 ) from 夏季奥运会 where 吉祥物 != '欢欢' and 参赛国家数量 < 30 group by 举办城市	奥运会参赛队伍
qid001475	select 举办城市 , max ( 参赛运动员数量 ) from 夏季奥运会 where 吉祥物 != '欢欢' and 参赛国家数量 <= 30 group by 举办城市	奥运会参赛队伍
qid001476	select 所属公司 , min ( 2018年利润 ) from 洗衣机品牌 where 成立时间 <= 1955 and 市场份额 >= 0.02 group by 所属公司	洗衣机
qid001477	select 所属公司 , sum ( 2018年利润 ) from 洗衣机品牌 where 成立时间 >= 1955 and 市场份额 <= 0.02 group by 所属公司	洗衣机
qid001478	select 所属公司 , avg ( 2018年利润 ) from 洗衣机品牌 where 成立时间 >= 1955 and 市场份额 > 0.02 group by 所属公司	洗衣机
qid001479	select 所属公司 , avg ( 2018年营业额 ) from 洗衣机品牌 where 市场份额 >= 0.02 and 2018年利润 > 15000000000 group by 所属公司	洗衣机
qid001480	select 所属公司 , max ( 2018年营业额 ) from 洗衣机品牌 where 成立时间 < 1955 and 市场份额 < 0.02 group by 所属公司	洗衣机
qid001481	select 所属省份 , sum ( 跨国公司数量 ) from 城市 where 建交国家数量 < 10 and 国外驻华大使馆数量 >= 137 group by 所属省份	友好城市
qid001482	select 所属省份 , min ( 跨国公司数量 ) from 城市 where 建交国家数量 <= 10 and 留学生数量 < 25000 group by 所属省份	友好城市
qid001483	select 所属省份 , avg ( 留学生数量 ) from 城市 where 建交国家数量 <= 10 and 建交城市数量 == 13 group by 所属省份	友好城市
qid001484	select 所属省份 , max ( 国外驻华大使馆数量 ) from 城市 where 建交国家数量 > 10 and 跨国公司数量 == 183 group by 所属省份	友好城市
qid001485	select 所属省份 , sum ( 跨国公司数量 ) from 城市 where 建交国家数量 > 10 and 国外驻华大使馆数量 == 137 group by 所属省份	友好城市
qid001486	select max ( 覆盖城市数 ) , avg ( 服务用户数量 ) , 所属公司 from 打车APP where 上线时间 >= 2014 group by 所属公司	打车软件
qid001487	select min ( 覆盖城市数 ) , max ( 服务用户数量 ) , 所属公司 from 打车APP where 上线时间 >= 2014 group by 所属公司	打车软件
qid001488	select sum ( 覆盖城市数 ) , min ( 服务用户数量 ) , 所属公司 from 打车APP where 上线时间 < 2014 group by 所属公司	打车软件
qid001489	select min ( 覆盖城市数 ) , sum ( 服务用户数量 ) , 所属公司 from 打车APP where 上线时间 >= 2014 group by 所属公司	打车软件
qid001490	select min ( 覆盖城市数 ) , max ( 服务用户数量 ) , 所属公司 from 打车APP where 上线时间 <= 2014 group by 所属公司	打车软件
qid001491	select max ( 大项项目数 ) , avg ( 参赛运动员数量 ) , 举办城市 from 夏季奥运会 where 参赛国家数量 < 30 group by 举办城市	奥运会参赛队伍
qid001492	select avg ( 参赛运动员数量 ) , sum ( 小项项目数 ) , 举办城市 from 夏季奥运会 where 参赛国家数量 <= 30 group by 举办城市	奥运会参赛队伍
qid001493	select max ( 小项项目数 ) , sum ( 大项项目数 ) , 举办城市 from 夏季奥运会 where 参赛国家数量 >= 30 group by 举办城市	奥运会参赛队伍
qid001494	select sum ( 小项项目数 ) , avg ( 参赛运动员数量 ) , 举办城市 from 夏季奥运会 where 参赛国家数量 >= 30 group by 举办城市	奥运会参赛队伍
qid001495	select sum ( 参赛运动员数量 ) , max ( 大项项目数 ) , 举办城市 from 夏季奥运会 where 参赛国家数量 <= 30 group by 举办城市	奥运会参赛队伍
qid001496	select avg ( 2018年利润 ) , sum ( 2018年营业额 ) , 所属公司 from 洗衣机品牌 where 市场份额 >= 0.02 group by 所属公司	洗衣机
qid001497	select max ( 市场份额 ) , min ( 2018年营业额 ) , 所属公司 from 洗衣机品牌 where 成立时间 > 1955 group by 所属公司	洗衣机
qid001498	select min ( 2018年利润 ) , avg ( 2018年营业额 ) , 所属公司 from 洗衣机品牌 where 市场份额 <= 0.02 group by 所属公司	洗衣机
qid001499	select min ( 市场份额 ) , max ( 2018年利润 ) , 所属公司 from 洗衣机品牌 where 成立时间 >= 1955 group by 所属公司	洗衣机
qid001500	select min ( 市场份额 ) , avg ( 2018年利润 ) , 所属公司 from 洗衣机品牌 where 成立时间 < 1955 group by 所属公司	洗衣机
qid001501	select sum ( 国外驻华大使馆数量 ) , max ( 留学生数量 ) , 所属省份 from 城市 where 建交国家数量 < 10 group by 所属省份	友好城市
qid001502	select sum ( 国外驻华大使馆数量 ) , min ( 跨国公司数量 ) , 所属省份 from 城市 where 建交国家数量 >= 10 group by 所属省份	友好城市
qid001503	select max ( 跨国公司数量 ) , sum ( 建交城市数量 ) , 所属省份 from 城市 where 建交国家数量 < 10 group by 所属省份	友好城市
qid001504	select avg ( 建交城市数量 ) , max ( 留学生数量 ) , 所属省份 from 城市 where 建交国家数量 <= 10 group by 所属省份	友好城市
qid001505	select min ( 跨国公司数量 ) , max ( 建交城市数量 ) , 所属省份 from 城市 where 建交国家数量 >= 10 group by 所属省份	友好城市
qid001506	select 所属地区 , max ( 容纳人数 ) from 球队 where 成立时间 >= 1964 or 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001507	select 所属地区 , min ( 容纳人数 ) from 球队 where 成立时间 <= 1964 or 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001508	select 所属地区 , max ( 容纳人数 ) from 球队 where 成立时间 <= 1964 or 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001509	select 所属地区 , sum ( 容纳人数 ) from 球队 where 成立时间 <= 1964 or 主场馆 == '波尔多体育场' group by 所属地区	欧洲杯球队
qid001510	select 所属地区 , avg ( 容纳人数 ) from 球队 where 成立时间 <= 1964 or 主场馆 != '波尔多体育场' group by 所属地区	欧洲杯球队
qid001511	select 所属公司 , sum ( 服务用户数量 ) from 打车APP where 上线时间 >= 2014 or 覆盖城市数 == 100 group by 所属公司	打车软件
qid001512	select 所属公司 , avg ( 服务用户数量 ) from 打车APP where 上线时间 < 2014 and 覆盖城市数 <= 100 group by 所属公司	打车软件
qid001513	select 所属公司 , avg ( 服务用户数量 ) from 打车APP where 上线时间 < 2014 or 覆盖城市数 == 100 group by 所属公司	打车软件
qid001514	select 所属公司 , sum ( 服务用户数量 ) from 打车APP where 上线时间 < 2014 or 覆盖城市数 > 100 group by 所属公司	打车软件
qid001515	select 所属公司 , max ( 服务用户数量 ) from 打车APP where 上线时间 >= 2014 or 覆盖城市数 > 100 group by 所属公司	打车软件
qid001516	select 举办城市 , sum ( 参赛运动员数量 ) from 夏季奥运会 where 吉祥物 != '欢欢' or 参赛国家数量 > 30 group by 举办城市	奥运会参赛队伍
qid001517	select 举办城市 , avg ( 小项项目数 ) from 夏季奥运会 where 吉祥物 != '欢欢' or 参赛国家数量 > 30 group by 举办城市	奥运会参赛队伍
qid001518	select 举办城市 , sum ( 小项项目数 ) from 夏季奥运会 where 参赛国家数量 <= 30 or 大项项目数 == 16 group by 举办城市	奥运会参赛队伍
qid001519	select 举办城市 , min ( 参赛运动员数量 ) from 夏季奥运会 where 参赛国家数量 == 30 or 大项项目数 > 16 group by 举办城市	奥运会参赛队伍
qid001520	select 举办城市 , sum ( 小项项目数 ) from 夏季奥运会 where 吉祥物 != '欢欢' or 参赛国家数量 >= 30 group by 举办城市	奥运会参赛队伍
qid001521	select 所属公司 , sum ( 2018年营业额 ) from 洗衣机品牌 where 成立时间 <= 1955 or 市场份额 <= 0.02 group by 所属公司	洗衣机
qid001522	select 所属公司 , min ( 2018年利润 ) from 洗衣机品牌 where 成立时间 > 1955 or 市场份额 > 0.02 group by 所属公司	洗衣机
qid001523	select 所属公司 , max ( 2018年利润 ) from 洗衣机品牌 where 成立时间 < 1955 or 市场份额 > 0.02 group by 所属公司	洗衣机
qid001524	select 所属公司 , max ( 2018年利润 ) from 洗衣机品牌 where 成立时间 > 1955 or 市场份额 >= 0.02 group by 所属公司	洗衣机
qid001525	select 所属公司 , avg ( 2018年营业额 ) from 洗衣机品牌 where 市场份额 == 0.02 or 2018年利润 <= 15000000000 group by 所属公司	洗衣机
qid001526	select 所属省份 , avg ( 跨国公司数量 ) from 城市 where 建交国家数量 == 10 or 建交城市数量 <= 13 group by 所属省份	友好城市
qid001527	select 所属省份 , max ( 国外驻华大使馆数量 ) from 城市 where 建交国家数量 <= 10 or 留学生数量 < 25000 group by 所属省份	友好城市
qid001528	select 所属省份 , sum ( 国外驻华大使馆数量 ) from 城市 where 建交国家数量 <= 10 or 留学生数量 == 25000 group by 所属省份	友好城市
qid001529	select 所属省份 , min ( 留学生数量 ) from 城市 where 建交国家数量 < 10 or 跨国公司数量 > 183 group by 所属省份	友好城市
qid001530	select 所属省份 , avg ( 跨国公司数量 ) from 城市 where 建交国家数量 > 10 or 建交城市数量 <= 13 group by 所属省份	友好城市
qid001531	select 法定代表人 from 企业 where 注册资本 == 10000000 group by 法定代表人 having count ( * ) < 5	企业融资
qid001532	select 法定代表人 from 企业 where 成立时间 <= 2015 group by 法定代表人 having count ( * ) == 5	企业融资
qid001533	select 性别 from 企业人物 where 年龄 >= 35 group by 性别 having count ( * ) == 5	CCTV中国经济年度人物
qid001534	select 性别 from 企业人物 where 年龄 >= 35 group by 性别 having count ( * ) >= 5	CCTV中国经济年度人物
qid001535	select 所属地区 from 球队 where 容纳人数 < 21000 group by 所属地区 having count ( * ) == 5	欧洲杯球队
qid001536	select 所属地区 from 球队 where 成立时间 <= 1960 group by 所属地区 having sum ( 容纳人数 ) < 10000	欧洲杯球队
qid001537	select 出品公司 from 电视剧 where 出品时间 > 2017 group by 出品公司 having count ( * ) == 5	中国卫视频道
qid001538	select 出品公司 from 电视剧 where 出品时间 >= 2017 group by 出品公司 having count ( * ) == 5	中国卫视频道
qid001539	select 所属公司 from 洗衣机品牌 where 成立时间 <= 1935 group by 所属公司 having count ( * ) < 5	洗衣机
qid001540	select 所属公司 from 洗衣机品牌 where 市场份额 != 0.02 group by 所属公司 having avg ( 2018年营业额 ) >= 1000000	洗衣机
qid001541	select 系列名 from 综艺节目 where 首播时间 >= 2018-12-20 group by 系列名 having count ( * ) >= 5	综艺节目
qid001542	select 系列名 from 综艺节目 where 首播时间 <= 2018-12-20 group by 系列名 having count ( * ) < 5	综艺节目
qid001543	select 类型 from 参考书 where 适用年级 != '1-3' group by 类型 having sum ( 价格 ) > 100	教材辅助参考书
qid001544	select 类型 from 参考书 where 适用年级 == '1-3' group by 类型 having avg ( 价格 ) <= 100	教材辅助参考书
qid001545	select 举办城市 from 夏季奥运会 where 参赛国家数量 >= 205 group by 举办城市 having sum ( 参赛运动员数量 ) > 100	奥运会参赛队伍
qid001546	select 举办城市 from 夏季奥运会 where 参赛国家数量 <= 205 group by 举办城市 having count ( * ) < 5	奥运会参赛队伍
qid001547	select 所属公司 from 打车APP where 覆盖城市数 <= 400 group by 所属公司 having count ( * ) < 5	打车软件
qid001548	select 所属公司 from 打车APP where 上线时间 < 2014 group by 所属公司 having avg ( 覆盖城市数 ) >= 100	打车软件
qid001549	select 所属省份 from 城市 where 建交国家数量 != 72 group by 所属省份 having sum ( 建交城市数量 ) > 100	友好城市
qid001550	select 所属省份 from 城市 where 建交国家数量 <= 72 group by 所属省份 having count ( * ) <= 5	友好城市
qid001551	select 产品类别 from 洗衣机型号 where 售价 > 10000 group by 产品类别 having count ( * ) <= 5	洗衣机
qid001552	select 产品类别 from 洗衣机型号 where 售价 != 10000 group by 产品类别 having count ( * ) >= 5	洗衣机
qid001553	select 场上位置 from 篮球运动员 where 年龄 != 30 group by 场上位置 having count ( * ) <= 5	运动员比赛记录
qid001554	select 场上位置 from 篮球运动员 where 年龄 > 30 group by 场上位置 having count ( * ) > 5	运动员比赛记录
qid001555	select 所属地区 from 球队 where 容纳人数 != 21000 and 成立时间 <= 1960 group by 所属地区 having count ( * ) >= 5	欧洲杯球队
qid001556	select 所属地区 from 球队 where 成立时间 >= 1960 and 容纳人数 == 21000 group by 所属地区 having count ( * ) > 5	欧洲杯球队
qid001557	select 所属地区 from 球队 where 成立时间 < 1960 and 容纳人数 > 21000 group by 所属地区 having count ( * ) > 5	欧洲杯球队
qid001558	select 所属公司 from 打车APP where 覆盖城市数 <= 400 and 上线时间 > 2014 group by 所属公司 having count ( * ) >= 5	打车软件
qid001559	select 所属公司 from 打车APP where 上线时间 >= 2014 and 覆盖城市数 != 400 group by 所属公司 having sum ( 服务用户数量 ) < 3000000	打车软件
qid001560	select 所属公司 from 打车APP where 上线时间 <= 2014 and 覆盖城市数 < 400 group by 所属公司 having count ( * ) <= 5	打车软件
qid001561	select 举办城市 from 夏季奥运会 where 参赛国家数量 == 205 and 小项项目数 > 80 group by 举办城市 having sum ( 大项项目数 ) <= 100	奥运会参赛队伍
qid001562	select 举办城市 from 夏季奥运会 where 参赛国家数量 != 205 and 小项项目数 == 80 group by 举办城市 having count ( * ) < 5	奥运会参赛队伍
qid001563	select 举办城市 from 夏季奥运会 where 参赛国家数量 == 205 and 参赛运动员数量 != 10303 group by 举办城市 having count ( * ) <= 5	奥运会参赛队伍
qid001564	select 所属公司 from 洗衣机品牌 where 市场份额 != 0.02 and 成立时间 < 1935 group by 所属公司 having avg ( 2018年营业额 ) <= 200000	洗衣机
qid001565	select 所属公司 from 洗衣机品牌 where 市场份额 > 0.02 and 成立时间 >= 1935 group by 所属公司 having count ( * ) <= 5	洗衣机
qid001566	select 所属公司 from 洗衣机品牌 where 市场份额 <= 0.02 and 2018年营业额 == 200700000000 group by 所属公司 having count ( * ) > 5	洗衣机
qid001567	select 系列名 from 综艺节目 where 首播时间 <= '2018-12-20' and 播出时间 < '12:00' group by 系列名 having count ( * ) <= 5	综艺节目
qid001568	select 系列名 from 综艺节目 where 首播时间 < '2018-12-20' and 播出时间 > '12:00' group by 系列名 having count ( * ) == 5	综艺节目
qid001569	select 系列名 from 综艺节目 where 首播时间 >= '2018-12-20' and 播出时间 < '12:00' group by 系列名 having count ( * ) > 5	综艺节目
qid001570	select 法定代表人 from 企业 where 成立时间 >= 2015 and 注册资本 >= 10000000 group by 法定代表人 having count ( * ) <= 5	企业融资
qid001571	select 法定代表人 from 企业 where 注册资本 != 10000000 and 成立时间 >= 2015 group by 法定代表人 having count ( * ) < 5	企业融资
qid001572	select 法定代表人 from 企业 where 成立时间 < 2015 and 注册资本 == 10000000 group by 法定代表人 having count ( * ) < 5	企业融资
qid001573	select 所属省份 from 城市 where 建交国家数量 == 72 and 留学生数量 != 25000 group by 所属省份 having avg ( 跨国公司数量 ) <= 5000	友好城市
qid001574	select 所属省份 from 城市 where 建交国家数量 == 72 and 国外驻华大使馆数量 != 0 group by 所属省份 having sum ( 跨国公司数量 ) > 100	友好城市
qid001575	select 所属省份 from 城市 where 建交国家数量 == 72 and 建交城市数量 != 13 group by 所属省份 having count ( * ) >= 5	友好城市
qid001576	select 类型 from 参考书 where 适用年级 != '1-3' and 价格 > 50 group by 类型 having count ( * ) == 5	教材辅助参考书
qid001577	select 类型 from 参考书 where 适用年级 == '1-3' and 价格 <= 50 group by 类型 having count ( * ) < 5	教材辅助参考书
qid001578	select 类型 from 参考书 where 适用年级 >= 3 and 价格 == 50 group by 类型 having count ( * ) < 5	教材辅助参考书
qid001579	select 国家 , min ( 世界人均摄入量 ) from 坚果摄入量 where 人均摄入量 > 0.05 group by 国家 having count ( * ) >= 5	坚果
qid001580	select 国家 , max ( 世界人均摄入量 ) from 坚果摄入量 where 人均摄入量 != 0.05 group by 国家 having count ( * ) < 5	坚果
qid001581	select 法定代表人 , avg ( 注册资本 ) from 企业 where 成立时间 >= 2015 group by 法定代表人 having count ( * ) >= 5	企业融资
qid001582	select 法定代表人 , min ( 注册资本 ) from 企业 where 成立时间 >= 2015 group by 法定代表人 having count ( * ) >= 5	企业融资
qid001583	select 球队 , sum ( 总篮板 ) from 比赛记录 where 出场次数 > 40 group by 球队 having count ( * ) > 5	运动员比赛记录
qid001584	select 球队 , avg ( 抢断 ) from 比赛记录 where 出场次数 < 40 group by 球队 having count ( * ) >= 5	运动员比赛记录
qid001585	select 融资轮次 , min ( 融资总额 ) from 企业融资 where 年份 <= 2010 group by 融资轮次 having count ( * ) >= 5	企业融资
qid001586	select 融资轮次 , sum ( 融资总额 ) from 企业融资 where 年份 <= 2010 group by 融资轮次 having count ( * ) <= 5	企业融资
qid001587	select 所属地区 , avg ( 容纳人数 ) from 球队 where 成立时间 < 1964 group by 所属地区 having count ( * ) < 5	欧洲杯球队
qid001588	select 所属地区 , avg ( 容纳人数 ) from 球队 where 主场馆 != '波尔多体育场' group by 所属地区 having count ( * ) > 5	欧洲杯球队
qid001589	select 城市 , max ( 占所在城市份额 ) from 打车软件开通城市 where 开通时间 <= 2018-07 group by 城市 having count ( * ) < 5	打车软件
qid001590	select 城市 , min ( 占所在城市份额 ) from 打车软件开通城市 where 开通时间 < 2018-07 group by 城市 having count ( * ) == 5	打车软件
qid001591	select 发生城市 , min ( 伤亡人数 ) from 美国近几年校园枪击事件 where 受影响学生数量 >= 10000 group by 发生城市 having count ( * ) > 5	枪击事件
qid001592	select 类型 , avg ( 价格 ) from 参考书 where 适用年级 <= 3 group by 类型 having count ( * ) <= 5	教材辅助参考书
qid001593	select 类型 , max ( 价格 ) from 参考书 where 适用年级 != '1-3' group by 类型 having count ( * ) >= 5	教材辅助参考书
qid001594	select 举办城市 , max ( 大项项目数 ) from 夏季奥运会 where 参赛国家数量 != 30 group by 举办城市 having count ( * ) == 5	奥运会参赛队伍
qid001595	select 举办城市 , sum ( 参赛运动员数量 ) from 夏季奥运会 where 参赛国家数量 < 30 group by 举办城市 having sum ( 大项项目数 ) > 500	奥运会参赛队伍
qid001596	select 所属公司 , avg ( 覆盖城市数 ) from 打车APP where 上线时间 < 2014 group by 所属公司 having count ( * ) > 5	打车软件
qid001597	select 所属公司 , min ( 覆盖城市数 ) from 打车APP where 上线时间 < 2014 group by 所属公司 having count ( * ) <= 5	打车软件
qid001598	select 城市 , min ( 售卖量 ) from 洗衣机品牌门店 where 门店数量 != 500 group by 城市 having count ( * ) == 5	洗衣机
qid001599	select 城市 , min ( 售卖量 ) from 洗衣机品牌门店 where 门店数量 < 500 group by 城市 having count ( * ) == 5	洗衣机
qid001600	select 所属省份 , min ( 国外驻华大使馆数量 ) from 城市 where 建交国家数量 <= 10 group by 所属省份 having sum ( 建交城市数量 ) < 500	友好城市
qid001601	select 所属省份 , avg ( 建交城市数量 ) from 城市 where 建交国家数量 <= 10 group by 所属省份 having sum ( 留学生数量 ) <= 500	友好城市
qid001602	select 法定代表人 from 企业 where 注册资本 >= 1000000 or 成立时间 > 2015 group by 法定代表人 having count ( * ) == 5	企业融资
qid001603	select 法定代表人 from 企业 where 成立时间 < 2015 or 注册资本 > 1000000 group by 法定代表人 having count ( * ) <= 5	企业融资
qid001604	select 所属地区 from 球队 where 成立时间 >= 1964 or 容纳人数 <= 21000 group by 所属地区 having count ( * ) == 5	欧洲杯球队
qid001605	select 所属地区 from 球队 where 成立时间 < 1964 or 容纳人数 != 21000 group by 所属地区 having count ( * ) <= 5	欧洲杯球队
qid001606	select 所属公司 from 洗衣机品牌 where 市场份额 != 0.02 or 2018年利润 < 15000000000 group by 所属公司 having count ( * ) > 5	洗衣机
qid001607	select 所属公司 from 洗衣机品牌 where 市场份额 < 0.02 or 2018年利润 <= 15000000000 group by 所属公司 having count ( * ) > 5	洗衣机
qid001608	select 系列名 from 综艺节目 where 首播时间 > '2014-10-01' or 播出时间 <= '22:00' group by 系列名 having count ( * ) == 5	综艺节目
qid001609	select 系列名 from 综艺节目 where 首播时间 > '2014-10-01' or 播出时间 >= '22:00' group by 系列名 having count ( * ) >= 5	综艺节目
qid001610	select 类型 from 参考书 where 适用年级 <= 3 or 价格 != 99 group by 类型 having count ( * ) > 5	教材辅助参考书
qid001611	select 类型 from 参考书 where 适用年级 != '1-3' or 价格 <= 99 group by 类型 having count ( * ) <= 5	教材辅助参考书
qid001612	select 类别 from 高校 where 所属城市 != '厦门' or 创办时间 > 1893 group by 类别 having count ( * ) >= 5	中国高校
qid001613	select 类别 from 高校 where 所属城市 != '厦门' or 创办时间 <= 1893 group by 类别 having count ( * ) == 5	中国高校
qid001614	select 举办城市 from 夏季奥运会 where 参赛国家数量 >= 30 or 参赛运动员数量 < 500 group by 举办城市 having sum ( 大项项目数 ) <= 30	奥运会参赛队伍
qid001615	select 举办城市 from 夏季奥运会 where 参赛国家数量 != 30 or 吉祥物 != '欢欢' group by 举办城市 having count ( * ) <= 5	奥运会参赛队伍
qid001616	select 所属公司 from 打车APP where 覆盖城市数 >= 100 or 上线时间 > 2014 group by 所属公司 having avg ( 服务用户数量 ) == 500	打车软件
qid001617	select 所属公司 from 打车APP where 覆盖城市数 > 100 or 上线时间 >= 2014 group by 所属公司 having avg ( 服务用户数量 ) < 500	打车软件
qid001618	select 所属省份 from 城市 where 建交国家数量 != 10 or 建交城市数量 > 13 group by 所属省份 having count ( * ) <= 5	友好城市
qid001619	select 所属省份 from 城市 where 建交国家数量 >= 10 or 跨国公司数量 > 183 group by 所属省份 having sum ( 建交城市数量 ) <= 50	友好城市
qid001620	select 国家 , sum ( 人均摄入量 ) from 坚果摄入量 group by 国家	坚果
qid001621	select 国家 , min ( 人均摄入量 ) from 坚果摄入量 group by 国家	坚果
qid001622	select 法定代表人 , avg ( 注册资本 ) from 企业 group by 法定代表人	企业融资
qid001623	select 法定代表人 , max ( 注册资本 ) from 企业 group by 法定代表人	企业融资
qid001624	select 性别 , min ( 年龄 ) from 企业人物 group by 性别	CCTV中国经济年度人物
qid001625	select 性别 , sum ( 年龄 ) from 企业人物 group by 性别	CCTV中国经济年度人物
qid001626	select 球队 , min ( 出场次数 ) from 比赛记录 group by 球队	运动员比赛记录
qid001627	select 球队 , max ( 出场次数 ) from 比赛记录 group by 球队	运动员比赛记录
qid001628	select 类型 , max ( 适用年级 ) from 参考书 group by 类型	教材辅助参考书
qid001629	select 融资轮次 , min ( 融资总额 ) from 企业融资 group by 融资轮次	企业融资
qid001630	select 融资轮次 , avg ( 融资总额 ) from 企业融资 group by 融资轮次	企业融资
qid001631	select 所属地区 , sum ( 容纳人数 ) from 球队 group by 所属地区	欧洲杯球队
qid001632	select 所属地区 , max ( 容纳人数 ) from 球队 group by 所属地区	欧洲杯球队
qid001633	select 发生城市 , sum ( 受影响学生数量 ) from 美国近几年校园枪击事件 group by 发生城市	枪击事件
qid001634	select 发生城市 , min ( 受影响学生数量 ) from 美国近几年校园枪击事件 group by 发生城市	枪击事件
qid001635	select 城市 , sum ( 占所在城市份额 ) from 打车软件开通城市 group by 城市	打车软件
qid001636	select 城市 , avg ( 占所在城市份额 ) from 打车软件开通城市 group by 城市	打车软件
qid001637	select 所属公司 , avg ( 市场份额 ) from 洗衣机品牌 group by 所属公司	洗衣机
qid001638	select 所属公司 , sum ( 市场份额 ) from 洗衣机品牌 group by 所属公司	洗衣机
qid001639	select 季节 , min ( 营业收入 ) from 坚果季节性营业收入 group by 季节	坚果
qid001640	select 季节 , max ( 营业收入 ) from 坚果季节性营业收入 group by 季节	坚果
qid001641	select 产地 , sum ( 市场占比 ) from 坚果产地 group by 产地	坚果
qid001642	select 产地 , max ( 市场占比 ) from 坚果产地 group by 产地	坚果
qid001643	select 投资公司 , max ( 融资额 ) from 投资公司 group by 投资公司	企业融资
qid001644	select 投资公司 , avg ( 融资额 ) from 投资公司 group by 投资公司	企业融资
qid001645	select 所属公司 , max ( 覆盖城市数 ) from 打车APP group by 所属公司	打车软件
qid001646	select 所属公司 , avg ( 覆盖城市数 ) from 打车APP group by 所属公司	打车软件
qid001647	select 举办城市 , max ( 参赛国家数量 ) from 夏季奥运会 group by 举办城市	奥运会参赛队伍
qid001648	select 举办城市 , min ( 参赛国家数量 ) from 夏季奥运会 group by 举办城市	奥运会参赛队伍
qid001649	select 场上位置 , max ( 年龄 ) from 篮球运动员 group by 场上位置	运动员比赛记录
qid001650	select 场上位置 , min ( 年龄 ) from 篮球运动员 group by 场上位置	运动员比赛记录
qid001651	select 城市 , avg ( 门店数量 ) from 洗衣机品牌门店 group by 城市	洗衣机
qid001652	select 城市 , sum ( 门店数量 ) from 洗衣机品牌门店 group by 城市	洗衣机
qid001653	select 平台 , avg ( 总评分 ) from 洗衣机品牌平台评分 group by 平台	洗衣机
qid001654	select 平台 , sum ( 总评分 ) from 洗衣机品牌平台评分 group by 平台	洗衣机
qid001655	select 所属省份 , min ( 建交国家数量 ) from 城市 group by 所属省份	友好城市
qid001656	select 所属省份 , sum ( 建交国家数量 ) from 城市 group by 所属省份	友好城市
qid001657	select 营养成分 , max ( 含量 ) from 每100克坚果营养成分 group by 营养成分	坚果
qid001658	select 营养成分 , sum ( 含量 ) from 每100克坚果营养成分 group by 营养成分	坚果
qid001659	select 产品类别 , avg ( 售价 ) from 洗衣机型号 group by 产品类别	洗衣机
qid001660	select 产品类别 , min ( 售价 ) from 洗衣机型号 group by 产品类别	洗衣机
qid001661	select 平台 , min ( 总评分 ) , min ( 性价比得分 ) from 洗衣机品牌平台评分 group by 平台	洗衣机
qid001662	select 平台 , min ( 总评分 ) , max ( 性价比得分 ) from 洗衣机品牌平台评分 group by 平台	洗衣机
qid001663	select 平台 , max ( 总评分 ) , sum ( 做工得分 ) from 洗衣机品牌平台评分 group by 平台	洗衣机
qid001664	select 季节 , min ( 营业收入 ) , max ( 全年占比 ) from 坚果季节性营业收入 group by 季节	坚果
qid001665	select 季节 , avg ( 营业收入 ) , min ( 全年占比 ) from 坚果季节性营业收入 group by 季节	坚果
qid001666	select 季节 , max ( 营业收入 ) , min ( 全年占比 ) from 坚果季节性营业收入 group by 季节	坚果
qid001667	select 国家 , min ( 人均摄入量 ) , max ( 世界人均摄入量 ) from 坚果摄入量 group by 国家	坚果
qid001668	select 国家 , avg ( 人均摄入量 ) , avg ( 世界人均摄入量 ) from 坚果摄入量 group by 国家	坚果
qid001669	select 国家 , max ( 人均摄入量 ) , max ( 世界人均摄入量 ) from 坚果摄入量 group by 国家	坚果
qid001670	select 类型 , min ( 适用年级 ) , min ( 价格 ) from 参考书 group by 类型	教材辅助参考书
qid001671	select 类型 , sum ( 适用年级 ) , min ( 价格 ) from 参考书 group by 类型	教材辅助参考书
qid001672	select 类型 , avg ( 适用年级 ) , avg ( 价格 ) from 参考书 group by 类型	教材辅助参考书
qid001673	select 球队 , avg ( 出场次数 ) , sum ( 总篮板 ) from 比赛记录 group by 球队	运动员比赛记录
qid001674	select 球队 , max ( 出场次数 ) , min ( 三分球 ) from 比赛记录 group by 球队	运动员比赛记录
qid001675	select 球队 , min ( 出场次数 ) , max ( 总篮板 ) from 比赛记录 group by 球队	运动员比赛记录
qid001676	select 所属公司 , max ( 市场份额 ) , min ( 2018年营业额 ) from 洗衣机品牌 group by 所属公司	洗衣机
qid001677	select 所属公司 , sum ( 市场份额 ) , sum ( 2018年营业额 ) from 洗衣机品牌 group by 所属公司	洗衣机
qid001678	select 所属公司 , min ( 市场份额 ) , min ( 2018年利润 ) from 洗衣机品牌 group by 所属公司	洗衣机
qid001679	select 发生城市 , sum ( 受影响学生数量 ) , avg ( 枪击者年龄 ) from 美国近几年校园枪击事件 group by 发生城市	枪击事件
qid001680	select 发生城市 , max ( 受影响学生数量 ) , avg ( 伤亡人数 ) from 美国近几年校园枪击事件 group by 发生城市	枪击事件
qid001681	select 发生城市 , min ( 受影响学生数量 ) , sum ( 伤亡人数 ) from 美国近几年校园枪击事件 group by 发生城市	枪击事件
qid001682	select 投资公司 , max ( 融资额 ) , sum ( 投资公司持股比例 ) from 投资公司 group by 投资公司	企业融资
qid001683	select 投资公司 , avg ( 融资额 ) , avg ( 投资公司持股比例 ) from 投资公司 group by 投资公司	企业融资
qid001684	select 投资公司 , max ( 融资额 ) , min ( 投资公司持股比例 ) from 投资公司 group by 投资公司	企业融资
qid001685	select 举办城市 , avg ( 参赛国家数量 ) , avg ( 大项项目数 ) from 夏季奥运会 group by 举办城市	奥运会参赛队伍
qid001686	select 举办城市 , sum ( 参赛国家数量 ) , max ( 参赛运动员数量 ) from 夏季奥运会 group by 举办城市	奥运会参赛队伍
qid001687	select 举办城市 , max ( 参赛国家数量 ) , min ( 小项项目数 ) from 夏季奥运会 group by 举办城市	奥运会参赛队伍
qid001688	select 所属公司 , sum ( 覆盖城市数 ) , min ( 服务用户数量 ) from 打车APP group by 所属公司	打车软件
qid001689	select 所属公司 , avg ( 覆盖城市数 ) , max ( 服务用户数量 ) from 打车APP group by 所属公司	打车软件
qid001690	select 所属公司 , sum ( 覆盖城市数 ) , sum ( 服务用户数量 ) from 打车APP group by 所属公司	打车软件
qid001691	select 城市 , max ( 门店数量 ) , sum ( 售卖量 ) from 洗衣机品牌门店 group by 城市	洗衣机
qid001692	select 城市 , sum ( 门店数量 ) , max ( 售卖量 ) from 洗衣机品牌门店 group by 城市	洗衣机
qid001693	select 城市 , avg ( 门店数量 ) , min ( 售卖量 ) from 洗衣机品牌门店 group by 城市	洗衣机
qid001694	select 所属省份 , sum ( 建交国家数量 ) , avg ( 国外驻华大使馆数量 ) from 城市 group by 所属省份	友好城市
qid001695	select 所属省份 , avg ( 建交国家数量 ) , sum ( 国外驻华大使馆数量 ) from 城市 group by 所属省份	友好城市
qid001696	select 所属省份 , avg ( 建交国家数量 ) , max ( 留学生数量 ) from 城市 group by 所属省份	友好城市
qid001697	select 季节 from 坚果季节性营业收入 group by 季节 having count ( * ) < 5	坚果
qid001698	select 系列名 from 综艺节目 group by 系列名 having count ( * ) < 5	综艺节目
qid001699	select 投资公司 from 投资公司 group by 投资公司 having avg ( 融资额 ) >= 1000000	企业融资
qid001700	select 所属公司 from 打车APP group by 所属公司 having avg ( 覆盖城市数 ) < 10	打车软件
qid001701	select 城市 from 洗衣机品牌门店 group by 城市 having sum ( 门店数量 ) <= 500	洗衣机
qid001702	select 所属省份 from 城市 group by 所属省份 having count ( * ) > 15	友好城市
qid001703	select 营养成分 from 每100克坚果营养成分 group by 营养成分 having count ( * ) > 5	坚果
qid001704	select 产品类别 from 洗衣机型号 group by 产品类别 having count ( * ) == 5	洗衣机
qid001705	select 国家 from 坚果摄入量 group by 国家 having count ( * ) < 5	坚果
qid001706	select 朝代 from 都城 group by 朝代 having count ( * ) < 5	中国历史名城
qid001707	select 法定代表人 from 企业 group by 法定代表人 having avg ( 注册资本 ) <= 500000	企业融资
qid001708	select 类型 from 参考书 group by 类型 having count ( * ) < 5	教材辅助参考书
qid001709	select 出品公司 from 电视剧 group by 出品公司 having count ( * ) < 5	中国卫视频道
qid001710	select 所属省 from 一带一路的中国城市 group by 所属省 having count ( * ) > 5	友好城市
qid001711	select 国家 from 一带一路线路上的国家 group by 国家 having count ( * ) > 2	友好城市
qid001712	select 职位 from 人物公司职位 group by 职位 having count ( * ) >= 5	CCTV中国经济年度人物
qid001713	select 场上位置 from 篮球运动员 group by 场上位置 having avg ( 年龄 ) >= 30	运动员比赛记录
qid001714	select 平台 from 洗衣机品牌平台评分 group by 平台 having count ( * ) < 5	洗衣机
qid001715	select 所属省 from 对口帮扶城市 group by 所属省 having count ( * ) < 5	友好城市
qid001716	select 民族 from 明星 group by 民族 having count ( * ) >= 50	综艺节目
qid001717	select 性别 from 企业人物 group by 性别 having count ( * ) > 500	CCTV中国经济年度人物
qid001718	select 所属地区 from 球队 group by 所属地区 having avg ( 容纳人数 ) < 8000	欧洲杯球队
qid001719	select 产地 from 坚果产地 group by 产地 having count ( * ) <= 5	坚果
qid001720	select 所属洲 from 国家 group by 所属洲 having count ( * ) > 5	奥运会参赛队伍
qid001721	select 作者 from 图书 group by 作者 having count ( * ) <= 5	购书平台
qid001722	select 所属省份 from 城市 group by 所属省份 having count ( * ) >= 15	中国历史名城
qid001723	select 融资轮次 from 企业融资 group by 融资轮次 having avg ( 融资总额 ) <= 10000000	企业融资
qid001724	select 城市 from 打车软件开通城市 group by 城市 having count ( * ) == 5	打车软件
qid001725	select 所属公司 from 洗衣机品牌 group by 所属公司 having count ( * ) < 5	洗衣机
qid001726	select 城市 from 软件对租车的支持 group by 城市 having count ( * ) < 5	打车软件
qid001727	select 发生城市 from 美国近几年校园枪击事件 group by 发生城市 having sum ( 受影响学生数量 ) > 100000	枪击事件
qid001728	select 举办城市 from 夏季奥运会 group by 举办城市 having avg ( 参赛国家数量 ) == 180	奥运会参赛队伍
qid001729	select 类别 from 高校 group by 类别 having count ( * ) <= 5	中国高校
qid001730	select 奖项名称 from 历届经济人物获奖名单 group by 奖项名称 having count ( * ) >= 5	CCTV中国经济年度人物
qid001731	select 国家 , sum ( 人均摄入量 ) from 坚果摄入量 group by 国家 having count ( * ) >= 5	坚果
qid001732	select 国家 , sum ( 人均摄入量 ) from 坚果摄入量 group by 国家 having count ( * ) == 5	坚果
qid001733	select 法定代表人 , sum ( 注册资本 ) from 企业 group by 法定代表人 having count ( * ) == 5	企业融资
qid001734	select 法定代表人 , sum ( 注册资本 ) from 企业 group by 法定代表人 having count ( * ) < 5	企业融资
qid001735	select 性别 , min ( 年龄 ) from 企业人物 group by 性别 having count ( * ) >= 5	CCTV中国经济年度人物
qid001736	select 球队 , avg ( 出场次数 ) from 比赛记录 group by 球队 having count ( * ) <= 5	运动员比赛记录
qid001737	select 球队 , max ( 出场次数 ) from 比赛记录 group by 球队 having count ( * ) == 5	运动员比赛记录
qid001738	select 类型 , min ( 适用年级 ) from 参考书 group by 类型 having count ( * ) > 5	教材辅助参考书
qid001739	select 类型 , min ( 适用年级 ) from 参考书 group by 类型 having count ( * ) == 5	教材辅助参考书
qid001740	select 所属地区 , min ( 容纳人数 ) from 球队 group by 所属地区 having count ( * ) <= 5	欧洲杯球队
qid001741	select 所属地区 , avg ( 容纳人数 ) from 球队 group by 所属地区 having count ( * ) <= 5	欧洲杯球队
qid001742	select 发生城市 , min ( 受影响学生数量 ) from 美国近几年校园枪击事件 group by 发生城市 having count ( * ) == 5	枪击事件
qid001743	select 发生城市 , avg ( 受影响学生数量 ) from 美国近几年校园枪击事件 group by 发生城市 having count ( * ) <= 5	枪击事件
qid001744	select 所属公司 , max ( 市场份额 ) from 洗衣机品牌 group by 所属公司 having count ( * ) == 5	洗衣机
qid001745	select 所属公司 , avg ( 2018年营业额 ) from 洗衣机品牌 group by 所属公司 having avg ( 市场份额 ) < 1000000	洗衣机
qid001746	select 季节 , avg ( 全年占比 ) from 坚果季节性营业收入 group by 季节 having avg ( 营业收入 ) > 2000000	坚果
qid001747	select 季节 , max ( 全年占比 ) from 坚果季节性营业收入 group by 季节 having avg ( 营业收入 ) < 2000000	坚果
qid001748	select 投资公司 , max ( 投资公司持股比例 ) from 投资公司 group by 投资公司 having sum ( 融资额 ) >= 100000000	企业融资
qid001749	select 所属公司 , max ( 服务用户数量 ) from 打车APP group by 所属公司 having avg ( 覆盖城市数 ) > 100	打车软件
qid001750	select 举办城市 , avg ( 参赛运动员数量 ) from 夏季奥运会 group by 举办城市 having sum ( 参赛国家数量 ) >= 100	奥运会参赛队伍
qid001751	select 举办城市 , max ( 参赛国家数量 ) from 夏季奥运会 group by 举办城市 having count ( * ) < 5	奥运会参赛队伍
qid001752	select 场上位置 , avg ( 年龄 ) from 篮球运动员 group by 场上位置 having count ( * ) == 5	运动员比赛记录
qid001753	select 场上位置 , sum ( 年龄 ) from 篮球运动员 group by 场上位置 having count ( * ) >= 5	运动员比赛记录
qid001754	select 城市 , avg ( 门店数量 ) from 洗衣机品牌门店 group by 城市 having count ( * ) > 5	洗衣机
qid001755	select 城市 , max ( 门店数量 ) from 洗衣机品牌门店 group by 城市 having count ( * ) <= 5	洗衣机
qid001756	select 平台 , avg ( 总评分 ) from 洗衣机品牌平台评分 group by 平台 having count ( * ) >= 5	洗衣机
qid001757	select 平台 , min ( 功能得分 ) from 洗衣机品牌平台评分 group by 平台 having sum ( 总评分 ) > 7	洗衣机
qid001758	select 所属省份 , avg ( 国外驻华大使馆数量 ) from 城市 group by 所属省份 having sum ( 建交国家数量 ) >= 70	友好城市
qid001759	select 所属省份 , max ( 国外驻华大使馆数量 ) from 城市 group by 所属省份 having sum ( 建交国家数量 ) > 70	友好城市
qid001760	select 产品类别 , max ( 售价 ) from 洗衣机型号 group by 产品类别 having count ( * ) <= 5	洗衣机
qid001761	select 产品类别 , min ( 售价 ) from 洗衣机型号 group by 产品类别 having count ( * ) == 5	洗衣机
qid001762	select 国家 from 坚果摄入量 group by 国家 having sum ( 人均摄入量 ) >= 100 or sum ( 世界人均摄入量 ) < 50	坚果
qid001763	select 法定代表人 from 企业 group by 法定代表人 having count ( * ) == 5 or sum ( 注册资本 ) <= 3000000	企业融资
qid001764	select 类型 from 参考书 group by 类型 having avg ( 适用年级 ) < 3 or count ( * ) < 5	教材辅助参考书
qid001765	select 所属地区 from 球队 group by 所属地区 having count ( * ) <= 5 or sum ( 容纳人数 ) >= 100000	欧洲杯球队
qid001766	select 所属公司 from 洗衣机品牌 group by 所属公司 having count ( * ) == 5 or avg ( 市场份额 ) >= 0.1	洗衣机
qid001767	select 所属公司 from 洗衣机品牌 group by 所属公司 having sum ( 市场份额 ) >= 0.3 or avg ( 2018年营业额 ) == 5000000000	洗衣机
qid001768	select 季节 from 坚果季节性营业收入 group by 季节 having avg ( 营业收入 ) < 100000 or count ( * ) <= 5	坚果
qid001769	select 产地 from 坚果产地 group by 产地 having count ( * ) >= 5 or sum ( 市场占比 ) >= 0.3	坚果
qid001770	select 国家 from 坚果摄入量 group by 国家 having sum ( 人均摄入量 ) < 50 and sum ( 世界人均摄入量 ) > 30	坚果
qid001771	select 国家 from 坚果摄入量 group by 国家 having count ( * ) > 5 and avg ( 人均摄入量 ) == 50	坚果
qid001772	select 法定代表人 from 企业 group by 法定代表人 having count ( * ) >= 5 and sum ( 注册资本 ) < 5000000	企业融资
qid001773	select 球队 from 比赛记录 group by 球队 having count ( * ) >= 5 and sum ( 出场次数 ) <= 20	运动员比赛记录
qid001774	select 融资轮次 from 企业融资 group by 融资轮次 having count ( * ) < 5 and avg ( 融资总额 ) == 200000000	企业融资
qid001775	select 季节 from 坚果季节性营业收入 group by 季节 having avg ( 营业收入 ) <= 20000000 and sum ( 全年占比 ) >= 0.1	坚果
qid001776	select 举办城市 from 夏季奥运会 group by 举办城市 having sum ( 参赛国家数量 ) > 80 and avg ( 小项项目数 ) == 200	奥运会参赛队伍
qid001777	select 季节 from 坚果季节性营业收入 group by 季节 order by sum ( 营业收入 ) desc limit 1	坚果
qid001778	select 出品公司 from 电视剧 group by 出品公司 order by count ( * ) limit 3	中国卫视频道
qid001779	select 出品公司 from 电视剧 group by 出品公司 order by count ( * ) desc limit 3	中国卫视频道
qid001780	select 系列名 from 综艺节目 group by 系列名 order by count ( * ) desc limit 3	综艺节目
qid001781	select 系列名 from 综艺节目 group by 系列名 order by count ( * ) asc limit 1	综艺节目
qid001782	select 国家 from 一带一路线路上的国家 group by 国家 order by count ( * ) asc limit 1	友好城市
qid001783	select 国家 from 一带一路线路上的国家 group by 国家 order by count ( * ) desc limit 1	友好城市
qid001784	select 所属公司 from 打车APP group by 所属公司 order by avg ( 覆盖城市数 ) desc limit 1	打车软件
qid001785	select 所属公司 from 打车APP group by 所属公司 order by avg ( 覆盖城市数 ) asc limit 1	打车软件
qid001786	select 城市 from 洗衣机品牌门店 group by 城市 order by avg ( 门店数量 ) desc limit 1	洗衣机
qid001787	select 城市 from 洗衣机品牌门店 group by 城市 order by sum ( 门店数量 ) asc limit 1	洗衣机
qid001788	select 所属省份 from 城市 group by 所属省份 order by sum ( 建交国家数量 ) asc limit 1	友好城市
qid001789	select 所属省份 from 城市 group by 所属省份 order by avg ( 建交国家数量 ) desc limit 5	友好城市
qid001790	select 营养成分 from 每100克坚果营养成分 group by 营养成分 order by avg ( 含量 ) desc limit 5	坚果
qid001791	select 营养成分 from 每100克坚果营养成分 group by 营养成分 order by sum ( 含量 ) asc limit 3	坚果
qid001792	select 产品类别 from 洗衣机型号 group by 产品类别 order by avg ( 售价 ) asc limit 1	洗衣机
qid001793	select 产品类别 from 洗衣机型号 group by 产品类别 order by avg ( 售价 ) desc limit 3	洗衣机
qid001794	select 朝代 from 都城 group by 朝代 order by count ( * ) desc limit 1	中国历史名城
qid001795	select 朝代 from 都城 group by 朝代 order by count ( * ) asc limit 1	中国历史名城
qid001796	select 法定代表人 from 企业 group by 法定代表人 order by count ( * ) desc limit 1	企业融资
qid001797	select 法定代表人 from 企业 group by 法定代表人 order by sum ( 注册资本 ) desc limit 1	企业融资
qid001798	select 类型 from 参考书 group by 类型 order by avg ( 适用年级 ) desc limit 1	教材辅助参考书
qid001799	select 类型 from 参考书 group by 类型 order by avg ( 适用年级 ) asc limit 1	教材辅助参考书
qid001800	select 所属省 from 一带一路的中国城市 group by 所属省 order by count ( * ) asc limit 2	友好城市
qid001801	select 所属省 from 一带一路的中国城市 group by 所属省 order by count ( * ) desc limit 1	友好城市
qid001802	select 职位 from 人物公司职位 group by 职位 order by count ( * ) asc limit 1	CCTV中国经济年度人物
qid001803	select 职位 from 人物公司职位 group by 职位 order by count ( * ) desc limit 3	CCTV中国经济年度人物
qid001804	select 场上位置 from 篮球运动员 group by 场上位置 order by sum ( 年龄 ) desc limit 1	运动员比赛记录
qid001805	select 场上位置 from 篮球运动员 group by 场上位置 order by avg ( 年龄 ) desc limit 1	运动员比赛记录
qid001806	select 所属省 from 对口帮扶城市 group by 所属省 order by count ( * ) desc limit 3	友好城市
qid001807	select 所属省 from 对口帮扶城市 group by 所属省 order by count ( * ) asc limit 3	友好城市
qid001808	select 平台 from 洗衣机品牌平台评分 group by 平台 order by sum ( 总评分 ) desc limit 1	洗衣机
qid001809	select 平台 from 洗衣机品牌平台评分 group by 平台 order by avg ( 总评分 ) desc limit 1	洗衣机
qid001810	select 民族 from 明星 group by 民族 order by count ( * ) desc limit 1	综艺节目
qid001811	select 民族 from 明星 group by 民族 order by count ( * ) limit 3	综艺节目
qid001812	select 性别 from 企业人物 group by 性别 order by avg ( 年龄 ) asc limit 1	CCTV中国经济年度人物
qid001813	select 所属地区 from 球队 group by 所属地区 order by sum ( 容纳人数 ) asc limit 1	欧洲杯球队
qid001814	select 所属地区 from 球队 group by 所属地区 order by count ( * ) asc limit 1	欧洲杯球队
qid001815	select 产地 from 坚果产地 group by 产地 order by avg ( 市场占比 ) asc limit 1	坚果
qid001816	select 产地 from 坚果产地 group by 产地 order by avg ( 市场占比 ) asc limit 5	坚果
qid001817	select 所属洲 from 国家 group by 所属洲 order by count ( * ) asc limit 1	奥运会参赛队伍
qid001818	select 所属洲 from 国家 group by 所属洲 order by count ( * ) desc limit 2	奥运会参赛队伍
qid001819	select 投资公司 from 投资公司 group by 投资公司 order by sum ( 融资额 ) asc limit 1	企业融资
qid001820	select 投资公司 from 投资公司 group by 投资公司 order by avg ( 融资额 ) asc limit 1	企业融资
qid001821	select 作者 from 图书 group by 作者 order by count ( * ) asc limit 1	购书平台
qid001822	select 作者 from 图书 group by 作者 order by count ( * ) desc limit 3	购书平台
qid001823	select 球队 , min ( 罚球 ) from 比赛记录 group by 球队 order by sum ( 出场次数 ) desc limit 1	运动员比赛记录
qid001824	select 球队 , sum ( 出场次数 ) from 比赛记录 group by 球队 order by count ( * ) asc limit 1	运动员比赛记录
qid001825	select 球队 , avg ( 出场次数 ) from 比赛记录 group by 球队 order by count ( * ) desc limit 1	运动员比赛记录
qid001826	select 球队 , min ( 防守 ) from 比赛记录 group by 球队 order by avg ( 出场次数 ) desc limit 1	运动员比赛记录
qid001827	select 球队 , avg ( 出场次数 ) from 比赛记录 group by 球队 order by count ( * ) asc limit 1	运动员比赛记录
qid001828	select 类型 , min ( 价格 ) from 参考书 group by 类型 order by avg ( 适用年级 ) asc limit 5	教材辅助参考书
qid001829	select 类型 , min ( 价格 ) from 参考书 group by 类型 order by avg ( 适用年级 ) desc limit 5	教材辅助参考书
qid001830	select 类型 , avg ( 适用年级 ) from 参考书 group by 类型 order by count ( * ) asc limit 1	教材辅助参考书
qid001831	select 类型 , sum ( 适用年级 ) from 参考书 group by 类型 order by count ( * ) asc limit 1	教材辅助参考书
qid001832	select 融资轮次 , max ( 融资总额 ) from 企业融资 group by 融资轮次 order by count ( * ) desc limit 1	企业融资
qid001833	select 融资轮次 , sum ( 融资总额 ) from 企业融资 group by 融资轮次 order by count ( * ) asc limit 1	企业融资
qid001834	select 融资轮次 , avg ( 融资总额 ) from 企业融资 group by 融资轮次 order by count ( * ) asc limit 1	企业融资
qid001835	select 所属地区 , sum ( 容纳人数 ) from 球队 group by 所属地区 order by count ( * ) asc limit 1	欧洲杯球队
qid001836	select 所属地区 , max ( 容纳人数 ) from 球队 group by 所属地区 order by count ( * ) asc limit 1	欧洲杯球队
qid001837	select 所属地区 , avg ( 容纳人数 ) from 球队 group by 所属地区 order by count ( * ) desc limit 1	欧洲杯球队
qid001838	select 所属地区 , avg ( 容纳人数 ) from 球队 group by 所属地区 order by count ( * ) asc limit 1	欧洲杯球队
qid001839	select 城市 , avg ( 占所在城市份额 ) from 打车软件开通城市 group by 城市 order by count ( * ) asc limit 1	打车软件
qid001840	select 城市 , sum ( 占所在城市份额 ) from 打车软件开通城市 group by 城市 order by count ( * ) desc limit 1	打车软件
qid001841	select 城市 , sum ( 占所在城市份额 ) from 打车软件开通城市 group by 城市 order by count ( * ) asc limit 1	打车软件
qid001842	select 所属公司 , avg ( 2018年利润 ) from 洗衣机品牌 group by 所属公司 order by sum ( 市场份额 ) asc limit 1	洗衣机
qid001843	select 所属公司 , avg ( 2018年利润 ) from 洗衣机品牌 group by 所属公司 order by sum ( 市场份额 ) asc limit 10	洗衣机
qid001844	select 所属公司 , avg ( 市场份额 ) from 洗衣机品牌 group by 所属公司 order by count ( * ) asc limit 1	洗衣机
qid001845	select 所属公司 , max ( 2018年利润 ) from 洗衣机品牌 group by 所属公司 order by sum ( 市场份额 ) desc limit 1	洗衣机
qid001846	select 所属公司 , sum ( 2018年利润 ) from 洗衣机品牌 group by 所属公司 order by sum ( 市场份额 ) asc limit 1	洗衣机
qid001847	select 发生城市 , min ( 受影响学生数量 ) from 美国近几年校园枪击事件 group by 发生城市 order by count ( * ) asc limit 10	枪击事件
qid001848	select 发生城市 , sum ( 枪击者年龄 ) from 美国近几年校园枪击事件 group by 发生城市 order by avg ( 受影响学生数量 ) desc limit 1	枪击事件
qid001849	select 发生城市 , avg ( 受影响学生数量 ) from 美国近几年校园枪击事件 group by 发生城市 order by count ( * ) desc limit 1	枪击事件
qid001850	select 发生城市 , avg ( 枪击者年龄 ) from 美国近几年校园枪击事件 group by 发生城市 order by avg ( 受影响学生数量 ) asc limit 1	枪击事件
qid001851	select 发生城市 , avg ( 枪击者年龄 ) from 美国近几年校园枪击事件 group by 发生城市 order by avg ( 受影响学生数量 ) asc limit 5	枪击事件
qid001852	select 产地 , sum ( 市场占比 ) from 坚果产地 group by 产地 order by count ( * ) desc limit 1	坚果
qid001853	select 产地 , min ( 市场占比 ) from 坚果产地 group by 产地 order by count ( * ) asc limit 10	坚果
qid001854	select 产地 , max ( 市场占比 ) from 坚果产地 group by 产地 order by count ( * ) asc limit 1	坚果
qid001855	select 产地 , sum ( 市场占比 ) from 坚果产地 group by 产地 order by count ( * ) asc limit 10	坚果
qid001856	select 产地 , max ( 市场占比 ) from 坚果产地 group by 产地 order by count ( * ) asc limit 10	坚果
qid001857	select 名称 from 电视台 order by 开播时间 asc	中国卫视频道
qid001858	select 中文名 from 企业 order by 注册资本 desc	企业融资
qid001859	select 姓名 from 企业人物 order by 年龄 asc	CCTV中国经济年度人物
qid001860	select 名称 from 电视剧 order by 出品时间 asc	中国卫视频道
qid001861	select 姓名 from 韩国自杀的娱乐明星 order by 年龄 asc	枪击事件
qid001862	select 名称 from 参考书 order by 适用年级 desc	教材辅助参考书
qid001863	select 中文队名 from 球队 order by 容纳人数 desc	欧洲杯球队
qid001864	select 名称 from 打车方式 order by 每公里价格 asc	打车软件
qid001865	select 名称 from 洗衣机品牌 order by 市场份额 desc	洗衣机
qid001866	select 名称 from 平台 order by 年营业额 desc	购书平台
qid001867	select 节目名称 from 综艺节目 order by 首播时间 asc	综艺节目
qid001868	select 名称 from 高校 order by 创办时间 asc	中国高校
qid001869	select app名称 from 打车APP order by 覆盖城市数 desc	打车软件
qid001870	select 名称 from 公司 order by 成立时间 asc	CCTV中国经济年度人物
qid001871	select 中文名 from 篮球运动员 order by 年龄 desc	运动员比赛记录
qid001872	select 名称 from 坚果 order by 饱和脂肪含量 asc	坚果
qid001873	select 城市 from 城市 order by 建交国家数量 desc	友好城市
qid001874	select 名称 , 主要成就 from 名人 order by 职业 asc	中国高校
qid001875	select 名称 , 隶属机构 from 电视台 order by 开播时间 asc	中国卫视频道
qid001876	select 中文名 , 法定代表人 from 企业 order by 注册资本 desc	企业融资
qid001877	select 姓名 , 性别 from 企业人物 order by 年龄 desc	CCTV中国经济年度人物
qid001878	select 名称 , 类型 from 参考书 order by 适用年级 desc	教材辅助参考书
qid001879	select 中文队名 , 所属地区 from 球队 order by 成立时间 asc	欧洲杯球队
qid001880	select 名称 , 理念 from 打车方式 order by 每公里价格 desc	打车软件
qid001881	select 名称 , 出品公司 from 电视剧 order by 出品时间 asc	中国卫视频道
qid001882	select 名称 , 所属公司 from 洗衣机品牌 order by 成立时间 asc	洗衣机
qid001883	select 节目名称 , 系列名 from 综艺节目 order by 首播时间 asc	综艺节目
qid001884	select 名称 , 类别 from 高校 order by 创办时间 asc	中国高校
qid001885	select 名称 , 举办城市 from 夏季奥运会 order by 参赛国家数量 asc	奥运会参赛队伍
qid001886	select 中文名 , 场上位置 from 篮球运动员 order by 年龄 desc	运动员比赛记录
qid001887	select 城市 , 所属省份 from 城市 order by 建交国家数量 desc	友好城市
qid001888	select 名称 , 产品类别 from 洗衣机型号 order by 售价 asc	洗衣机
qid001889	select app名称 , 所属公司 from 打车APP order by 覆盖城市数 asc	打车软件
qid001890	select 中文名 , 法定代表人 , 注册资本 from 企业 order by 成立时间 asc	企业融资
qid001891	select 中文名 , 法定代表人 , 所属省份 from 企业 order by 注册资本 asc	企业融资
qid001892	select 姓名 , 性别 , 民族 from 企业人物 order by 年龄 desc	CCTV中国经济年度人物
qid001893	select 姓名 , 性别 , 出生地 from 企业人物 order by 年龄 asc	CCTV中国经济年度人物
qid001894	select 中文队名 , 所属地区 , 体育经理 from 球队 order by 容纳人数 desc	欧洲杯球队
qid001895	select 中文队名 , 所属地区 , 创始人 from 球队 order by 成立时间 asc	欧洲杯球队
qid001896	select 名称 , 出品公司 , 发行公司 from 电视剧 order by 出品时间 asc	中国卫视频道
qid001897	select 名称 , 所属公司 , 2018年利润 from 洗衣机品牌 order by 市场份额 asc	洗衣机
qid001898	select 名称 , 所属公司 , 市场份额 from 洗衣机品牌 order by 成立时间 asc	洗衣机
qid001899	select 节目名称 , 系列名 , 播出频道 from 综艺节目 order by 首播时间 asc	综艺节目
qid001900	select 名称 , 类型 , 价格 from 参考书 order by 适用年级 asc	教材辅助参考书
qid001901	select 名称 , 类型 , 价格 from 参考书 order by 适用年级 desc	教材辅助参考书
qid001902	select 名称 , 举办城市 , 小项项目数 from 夏季奥运会 order by 参赛国家数量 asc	奥运会参赛队伍
qid001903	select 名称 , 举办城市 , 吉祥物 from 夏季奥运会 order by 参赛国家数量 desc	奥运会参赛队伍
qid001904	select app名称 , 所属公司 , 覆盖城市数 from 打车APP order by 上线时间 asc	打车软件
qid001905	select 中文名 , 法定代表人 , 所属省份 from 企业 order by 注册资本 asc limit 3	企业融资
qid001906	select 中文名 , 法定代表人 , 注册资本 from 企业 order by 成立时间 asc limit 3	企业融资
qid001907	select 姓名 , 性别 , 出生地 from 企业人物 order by 年龄 desc limit 3	CCTV中国经济年度人物
qid001908	select 姓名 , 性别 , 毕业院校 from 企业人物 order by 年龄 asc limit 3	CCTV中国经济年度人物
qid001909	select 中文队名 , 所属地区 , 主场馆 from 球队 order by 容纳人数 asc limit 3	欧洲杯球队
qid001910	select 中文队名 , 所属地区 , 主场馆 from 球队 order by 成立时间 asc limit 3	欧洲杯球队
qid001911	select 名称 , 所属公司 , 2018年营业额 from 洗衣机品牌 order by 市场份额 asc limit 3	洗衣机
qid001912	select 名称 , 所属公司 , 市场份额 from 洗衣机品牌 order by 成立时间 asc limit 3	洗衣机
qid001913	select 名称 , 类型 , 特点 from 参考书 order by 适用年级 asc limit 3	教材辅助参考书
qid001914	select 名称 , 类型 , 科目类型 from 参考书 order by 适用年级 desc limit 3	教材辅助参考书
qid001915	select 名称 , 举办城市 , 吉祥物 from 夏季奥运会 order by 参赛国家数量 desc limit 3	奥运会参赛队伍
qid001916	select app名称 , 所属公司 , 服务用户数量 from 打车APP order by 覆盖城市数 desc limit 3	打车软件
qid001917	select app名称 , 所属公司 , 覆盖城市数 from 打车APP order by 上线时间 asc limit 3	打车软件
qid001918	select a.总评分 - b.总评分 from ( select 总评分 from 洗衣机品牌平台评分 where 平台 == '京东商城' and 品牌id == 'item_product_4_17' ) a , ( select 总评分 from 洗衣机品牌平台评分 where 平台 == '京东商城' and 品牌id == 'item_product_4_18' ) b	洗衣机
qid001919	select a.总评分 - b.总评分 from ( select 总评分 from 洗衣机品牌平台评分 where 品牌id == 'item_product_4_18' and 平台 == '京东商城' ) a , ( select 总评分 from 洗衣机品牌平台评分 where 品牌id == 'item_product_4_18' and 平台 == '天猫商城' ) b	洗衣机
qid001920	select a.评分 - b.评分 from ( select 评分 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_11' ) a , ( select 评分 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) b	购书平台
qid001921	select a.加入购物车人数 - b.加入购物车人数 from ( select 加入购物车人数 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_11' ) a , ( select 加入购物车人数 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) b	购书平台
qid001922	select a.售价 - b.售价 from ( select 售价 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_11' ) a , ( select 售价 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) b	购书平台
qid001923	select a.购买人数 - b.购买人数 from ( select 购买人数 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_11' ) a , ( select 购买人数 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) b	购书平台
qid001924	select a.收藏人数 - b.收藏人数 from ( select 收藏人数 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) a , ( select 收藏人数 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_11' ) b	购书平台
qid001925	select a.购买人数 / b.购买人数 from ( select 购买人数 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) a , ( select sum ( 购买人数 ) from 图书与平台 where 书名id == 'item_book.2_2_17' ) b	购书平台
qid001926	select a.评分人数 - b.评分人数 from ( select 评分人数 from 图书与平台 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) a , ( select 评分人数 from 图书与平台 where 书名id == 'item_book.2_2_16' and 平台id == 'item_book.2_2_13' ) b	购书平台
qid001927	select a.人均摄入量 - b.人均摄入量 from ( select 人均摄入量 from 坚果摄入量 where 国家 == '美国' and 坚果id == 'item_animal_food_8_61' ) a , ( select 人均摄入量 from 坚果摄入量 where 国家 == '美国' and 坚果id == 'item_animal_food_8_62' ) b	坚果
qid001928	select a.人均摄入量 / b.人均摄入量 from ( select 人均摄入量 from 坚果摄入量 where 坚果id == 'item_animal_food_8_61' and 国家 == '中国' ) a , ( select sum ( 人均摄入量 ) from 坚果摄入量 where 坚果id == 'item_animal_food_8_61' ) b	坚果
qid001929	select a.人均摄入量 - b.人均摄入量 from ( select 人均摄入量 from 坚果摄入量 where 坚果id == 'item_animal_food_8_61' and 国家 == '美国' ) a , ( select 人均摄入量 from 坚果摄入量 where 坚果id == 'item_animal_food_8_61' and 国家 == '印度' ) b	坚果
qid001930	select a.人均摄入量 + b.人均摄入量 from ( select 人均摄入量 from 坚果摄入量 where 国家 == '美国' and 坚果id == 'item_animal_food_8_61' ) a , ( select 人均摄入量 from 坚果摄入量 where 国家 == '美国' and 坚果id == 'item_animal_food_8_62' ) b	坚果
qid001931	select a.会员价格 - b.会员价格 from ( select 会员价格 from 电子书 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) a , ( select 会员价格 from 电子书 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_11' ) b	购书平台
qid001932	select a.购买人数 / b.购买人数 from ( select 购买人数 from 电子书 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) a , ( select sum ( 购买人数 ) from 电子书 where 书名id == 'item_book.2_2_17' ) b	购书平台
qid001933	select a.购买人数 - b.购买人数 from ( select 购买人数 from 电子书 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) a , ( select 购买人数 from 电子书 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_11' ) b	购书平台
qid001934	select a.电子书售价 - b.电子书售价 from ( select 电子书售价 from 电子书 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_11' ) a , ( select 电子书售价 from 电子书 where 书名id == 'item_book.2_2_16' and 平台id == 'item_book.2_2_11' ) b	购书平台
qid001935	select a.购买人数 / b.购买人数 from ( select 购买人数 from 电子书 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_13' ) a , ( select 购买人数 from 电子书 where 书名id == 'item_book.2_2_17' and 平台id == 'item_book.2_2_11' ) b	购书平台
qid001936	select a.融资总额 - b.融资总额 from ( select 融资总额 from 企业融资 where 企业id == 'item_enterprise_12_131' and 融资轮次 == 'B' ) a , ( select 融资总额 from 企业融资 where 企业id == 'item_enterprise_12_131' and 融资轮次 == 'D' ) b	企业融资
qid001937	select a.融资总额 - b.融资总额 from ( select 融资总额 from 企业融资 where 融资轮次 == 'A' and 企业id == 'item_enterprise_12_131' ) a , ( select 融资总额 from 企业融资 where 融资轮次 == 'A' and 企业id == 'item_enterprise_12_132' ) b	企业融资
qid001938	select a.融资总额 + b.融资总额 from ( select 融资总额 from 企业融资 where 企业id == 'item_enterprise_12_131' and 融资轮次 == 'B' ) a , ( select 融资总额 from 企业融资 where 企业id == 'item_enterprise_12_131' and 融资轮次 == 'A' ) b	企业融资
qid001939	select a.融资总额 / b.融资总额 from ( select 融资总额 from 企业融资 where 企业id == 'item_enterprise_12_131' and 融资轮次 == 'B' ) a , ( select 融资总额 from 企业融资 where 企业id == 'item_enterprise_12_131' and 融资轮次 == 'A' ) b	企业融资
qid001940	select a.融资总额 / b.融资总额 from ( select 融资总额 from 企业融资 where 融资轮次 == 'A' and 企业id == 'item_enterprise_12_132' ) a , ( select 融资总额 from 企业融资 where 融资轮次 == 'A' and 企业id == 'item_enterprise_12_131' ) b	企业融资
qid001941	select a.融资总额 / b.融资总额 from ( select 融资总额 from 企业融资 where 企业id == 'item_enterprise_12_131' and 融资轮次 == 'B' ) a , ( select sum ( 融资总额 ) from 企业融资 where 企业id == 'item_enterprise_12_131' ) b	企业融资
qid001942	select a.市场占比 + b.市场占比 from ( select 市场占比 from 坚果产地 where 坚果id == 'item_animal_food_8_61' and 产地 == '巴西' ) a , ( select 市场占比 from 坚果产地 where 坚果id == 'item_animal_food_8_61' and 产地 == '东非' ) b	坚果
qid001943	select a.市场占比 - b.市场占比 from ( select 市场占比 from 坚果产地 where 产地 == '巴西' and 坚果id == 'item_animal_food_8_61' ) a , ( select 市场占比 from 坚果产地 where 产地 == '巴西' and 坚果id == 'item_animal_food_8_64' ) b	坚果
qid001944	select a.市场占比 - b.市场占比 from ( select 市场占比 from 坚果产地 where 坚果id == 'item_animal_food_8_61' and 产地 == '柬埔寨' ) a , ( select 市场占比 from 坚果产地 where 坚果id == 'item_animal_food_8_61' and 产地 == '东非' ) b	坚果
qid001945	select a.线上销售收入 - b.线上销售收入 from ( select 线上销售收入 from 坚果销售渠道 where 年份 == 2014 and 坚果id == 'item_animal_food_8_62' ) a , ( select 线上销售收入 from 坚果销售渠道 where 年份 == 2014 and 坚果id == 'item_animal_food_8_61' ) b	坚果
qid001946	select a.线上销售收入 + b.线上销售收入 from ( select 线上销售收入 from 坚果销售渠道 where 坚果id == 'item_animal_food_8_62' and 年份 == 2014 ) a , ( select 线上销售收入 from 坚果销售渠道 where 坚果id == 'item_animal_food_8_62' and 年份 == 2013 ) b	坚果
qid001947	select a.线下销售收入 - b.线下销售收入 from ( select 线下销售收入 from 坚果销售渠道 where 年份 == 2014 and 坚果id == 'item_animal_food_8_62' ) a , ( select 线下销售收入 from 坚果销售渠道 where 年份 == 2014 and 坚果id == 'item_animal_food_8_64' ) b	坚果
qid001948	select a.线下销售收入 / b.线下销售收入 from ( select 线下销售收入 from 坚果销售渠道 where 年份 == 2014 and 坚果id == 'item_animal_food_8_64' ) a , ( select 线下销售收入 from 坚果销售渠道 where 年份 == 2014 and 坚果id == 'item_animal_food_8_61' ) b	坚果
qid001949	select a.线上销售收入 / b.线上销售收入 from ( select 线上销售收入 from 坚果销售渠道 where 坚果id == 'item_animal_food_8_62' and 年份 == 2014 ) a , ( select 线上销售收入 from 坚果销售渠道 where 坚果id == 'item_animal_food_8_62' and 年份 == 2013 ) b	坚果
qid001950	select a.线上销售收入 - b.线上销售收入 from ( select 线上销售收入 from 坚果销售渠道 where 坚果id == 'item_animal_food_8_62' and 年份 == 2014 ) a , ( select 线上销售收入 from 坚果销售渠道 where 坚果id == 'item_animal_food_8_62' and 年份 == 2013 ) b	坚果
qid001951	select a.门店数量 / b.门店数量 from ( select 门店数量 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '北京' ) a , ( select 门店数量 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '上海' ) b	洗衣机
qid001952	select a.门店数量 + b.门店数量 from ( select 门店数量 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '昆明' ) a , ( select 门店数量 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '北京' ) b	洗衣机
qid001953	select a.平均售价 - b.平均售价 from ( select 平均售价 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '上海' ) a , ( select 平均售价 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '昆明' ) b	洗衣机
qid001954	select a.门店数量 - b.门店数量 from ( select 门店数量 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '北京' ) a , ( select 门店数量 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '昆明' ) b	洗衣机
qid001955	select a.门店数量 / b.门店数量 from ( select 门店数量 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '昆明' ) a , ( select sum ( 门店数量 ) from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' ) b	洗衣机
qid001956	select a.售卖量 / b.售卖量 from ( select 售卖量 from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' and 城市 == '上海' ) a , ( select sum ( 售卖量 ) from 洗衣机品牌门店 where 品牌id == 'item_product_4_16' ) b	洗衣机
qid001957	select a.受影响学生数量 + b.受影响学生数量 from ( select 受影响学生数量 from 美国近几年校园枪击事件 where 年份 == 2017 and 发生城市 == '南加州' ) a , ( select 受影响学生数量 from 美国近几年校园枪击事件 where 年份 == 2017 and 发生城市 == '德克萨斯' ) b	枪击事件
qid001958	select a.受影响学生数量 + b.受影响学生数量 from ( select 受影响学生数量 from 美国近几年校园枪击事件 where 发生城市 == '南加州' and 年份 == 2018 ) a , ( select 受影响学生数量 from 美国近几年校园枪击事件 where 发生城市 == '南加州' and 年份 == 2017 ) b	枪击事件
qid001959	select a.受影响学生数量 / b.受影响学生数量 from ( select 受影响学生数量 from 美国近几年校园枪击事件 where 年份 == 2017 and 发生城市 == '德克萨斯' ) a , ( select sum ( 受影响学生数量 ) from 美国近几年校园枪击事件 where 年份 == 2017 ) b	枪击事件
qid001960	select a.受影响学生数量 - b.受影响学生数量 from ( select 受影响学生数量 from 美国近几年校园枪击事件 where 年份 == 2017 and 发生城市 == '德克萨斯' ) a , ( select 受影响学生数量 from 美国近几年校园枪击事件 where 年份 == 2017 and 发生城市 == '拉斯维加斯' ) b	枪击事件
qid001961	select a.受影响学生数量 - b.受影响学生数量 from ( select 受影响学生数量 from 美国近几年校园枪击事件 where 发生城市 == '南加州' and 年份 == 2018 ) a , ( select 受影响学生数量 from 美国近几年校园枪击事件 where 发生城市 == '南加州' and 年份 == 2017 ) b	枪击事件
qid001962	select a.受影响学生数量 / b.受影响学生数量 from ( select 受影响学生数量 from 美国近几年校园枪击事件 where 年份 == 2017 and 发生城市 == '德克萨斯' ) a , ( select 受影响学生数量 from 美国近几年校园枪击事件 where 年份 == 2017 and 发生城市 == '南加州' ) b	枪击事件
qid001963	select a.受影响学生数量 / b.受影响学生数量 from ( select 受影响学生数量 from 美国近几年校园枪击事件 where 发生城市 == '南加州' and 年份 == 2018 ) a , ( select 受影响学生数量 from 美国近几年校园枪击事件 where 发生城市 == '南加州' and 年份 == 2017 ) b	枪击事件
qid001964	select a.枪击事件数量 + b.枪击事件数量 from ( select 枪击事件数量 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_101' ) a , ( select 枪击事件数量 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_102' ) b	枪击事件
qid001965	select a.枪击事件数量 - b.枪击事件数量 from ( select 枪击事件数量 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_101' ) a , ( select 枪击事件数量 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_102' ) b	枪击事件
qid001966	select a.受伤人数 + b.受伤人数 from ( select 受伤人数 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_101' ) a , ( select 受伤人数 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_102' ) b	枪击事件
qid001967	select a.受伤人数 - b.受伤人数 from ( select 受伤人数 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_101' ) a , ( select 受伤人数 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_102' ) b	枪击事件
qid001968	select a.死亡人数 + b.死亡人数 from ( select 死亡人数 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_102' ) a , ( select 死亡人数 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_101' ) b	枪击事件
qid001969	select a.死亡人数 - b.死亡人数 from ( select 死亡人数 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_102' ) a , ( select 死亡人数 from 枪击事件 where 年份 == 2017 and 国家id == 'item_activity_11_101' ) b	枪击事件
qid001970	select a.含量 / b.含量 from ( select 含量 from 每100克坚果营养成分 where 坚果id == 'item_animal_food_8_64' and 营养成分 == '钙' ) a , ( select 含量 from 每100克坚果营养成分 where 坚果id == 'item_animal_food_8_64' and 营养成分 == '维生素B3' ) b	坚果
qid001971	select a.含量 + b.含量 from ( select 含量 from 每100克坚果营养成分 where 坚果id == 'item_animal_food_8_64' and 营养成分 == '镁' ) a , ( select 含量 from 每100克坚果营养成分 where 坚果id == 'item_animal_food_8_64' and 营养成分 == '维生素B6' ) b	坚果
qid001972	select a.含量 - b.含量 from ( select 含量 from 每100克坚果营养成分 where 坚果id == 'item_animal_food_8_64' and 营养成分 == '镁' ) a , ( select 含量 from 每100克坚果营养成分 where 坚果id == 'item_animal_food_8_64' and 营养成分 == '维生素B3' ) b	坚果
qid001973	select a.含量 / b.含量 from ( select 含量 from 每100克坚果营养成分 where 坚果id == 'item_animal_food_8_64' and 营养成分 == '镁' ) a , ( select sum ( 含量 ) from 每100克坚果营养成分 where 坚果id == 'item_animal_food_8_64' ) b	坚果
qid001974	select a.含量 - b.含量 from ( select 含量 from 每100克坚果营养成分 where 营养成分 == '维生素B3' and 坚果id == 'item_animal_food_8_64' ) a , ( select 含量 from 每100克坚果营养成分 where 营养成分 == '维生素B3' and 坚果id == 'item_animal_food_8_61' ) b	坚果
qid001975	select a.融资额 + b.融资额 from ( select 融资额 from 投资公司 where 企业id == 'item_enterprise_12_133' and 融资轮次 == 'C' ) a , ( select 融资额 from 投资公司 where 企业id == 'item_enterprise_12_133' and 融资轮次 == 'B' ) b	企业融资
qid001976	select a.融资额 / b.融资额 from ( select 融资额 from 投资公司 where 融资轮次 == 'B' and 企业id == 'item_enterprise_12_131' ) a , ( select 融资额 from 投资公司 where 融资轮次 == 'B' and 企业id == 'item_enterprise_12_133' ) b	企业融资
qid001977	select a.融资额 - b.融资额 from ( select 融资额 from 投资公司 where 融资轮次 == 'B' and 企业id == 'item_enterprise_12_131' ) a , ( select 融资额 from 投资公司 where 融资轮次 == 'B' and 企业id == 'item_enterprise_12_133' ) b	企业融资
qid001978	select a.融资额 / b.融资额 from ( select 融资额 from 投资公司 where 企业id == 'item_enterprise_12_133' and 融资轮次 == 'A' ) a , ( select 融资额 from 投资公司 where 企业id == 'item_enterprise_12_133' and 融资轮次 == 'C' ) b	企业融资
qid001979	select a.融资额 - b.融资额 from ( select 融资额 from 投资公司 where 企业id == 'item_enterprise_12_133' and 融资轮次 == 'B' ) a , ( select 融资额 from 投资公司 where 企业id == 'item_enterprise_12_133' and 融资轮次 == 'A' ) b	企业融资
qid001980	select a.购买数量 - b.购买数量 from ( select 购买数量 from 适用城市 where 参考试卷id == 'item_book.2_13_161' and 省份 == '河北' ) a , ( select 购买数量 from 适用城市 where 参考试卷id == 'item_book.2_13_161' and 省份 == '四川' ) b	教材辅助参考书
qid001981	select a.购买数量 + b.购买数量 from ( select 购买数量 from 适用城市 where 参考试卷id == 'item_book.2_13_161' and 省份 == '四川' ) a , ( select 购买数量 from 适用城市 where 参考试卷id == 'item_book.2_13_161' and 省份 == '河北' ) b	教材辅助参考书
qid001982	select a.购买数量 / b.购买数量 from ( select 购买数量 from 适用城市 where 参考试卷id == 'item_book.2_13_161' and 省份 == '四川' ) a , ( select sum ( 购买数量 ) from 适用城市 where 参考试卷id == 'item_book.2_13_161' ) b	教材辅助参考书
qid001983	select a.购买数量 / b.购买数量 from ( select 购买数量 from 适用城市 where 参考试卷id == 'item_book.2_13_161' and 省份 == '河北' ) a , ( select 购买数量 from 适用城市 where 参考试卷id == 'item_book.2_13_161' and 省份 == '湖北' ) b	教材辅助参考书
qid001984	select a.成立时间 - b.成立时间 from ( select 成立时间 from 企业 where 中文名 == '蓦然认知' ) a , ( select 成立时间 from 企业 where 中文名 == '上门美甲有限公司' ) b	企业融资
qid001985	select a.注册资本 / b.注册资本 from ( select 注册资本 from 企业 where 中文名 == '蓦然认知' ) a , ( select 注册资本 from 企业 where 中文名 == '上门美甲有限公司' ) b	企业融资
qid001986	select a.注册资本 - b.注册资本 from ( select 注册资本 from 企业 where 中文名 == '蓦然认知' ) a , ( select 注册资本 from 企业 where 中文名 == '上门美甲有限公司' ) b	企业融资
qid001987	select a.注册资本 + b.注册资本 from ( select 注册资本 from 企业 where 中文名 == '蓦然认知' ) a , ( select 注册资本 from 企业 where 中文名 == '上门美甲有限公司' ) b	企业融资
qid001988	select a.成立时间 - b.成立时间 from ( select 成立时间 from 平台 where 名称 == '天猫' ) a , ( select 成立时间 from 平台 where 名称 == '拼多多' ) b	购书平台
qid001989	select a.会员费 / b.会员费 from ( select 会员费 from 平台 where 名称 == '天猫' ) a , ( select 会员费 from 平台 where 名称 == '拼多多' ) b	购书平台
qid001990	select a.会员费 - b.会员费 from ( select 会员费 from 平台 where 名称 == '天猫' ) a , ( select 会员费 from 平台 where 名称 == '拼多多' ) b	购书平台
qid001991	select a.市值 / b.市值 from ( select 市值 from 公司 where 名称 == '深圳腾讯科技有限公司' ) a , ( select 市值 from 公司 where 名称 == '北京小桔科技有限公司' ) b	CCTV中国经济年度人物
qid001992	select a.年营业额 / b.年营业额 from ( select 年营业额 from 公司 where 名称 == '深圳腾讯科技有限公司' ) a , ( select 年营业额 from 公司 where 名称 == '北京小桔科技有限公司' ) b	CCTV中国经济年度人物
qid001993	select a.世界500强排名 - b.世界500强排名 from ( select 世界500强排名 from 公司 where 名称 == '深圳腾讯科技有限公司' ) a , ( select 世界500强排名 from 公司 where 名称 == '北京小桔科技有限公司' ) b	CCTV中国经济年度人物
qid001994	select a.员工数 - b.员工数 from ( select 员工数 from 公司 where 名称 == '深圳腾讯科技有限公司' ) a , ( select 员工数 from 公司 where 名称 == '北京小桔科技有限公司' ) b	CCTV中国经济年度人物
qid001995	select a.员工数 / b.员工数 from ( select 员工数 from 公司 where 名称 == '深圳腾讯科技有限公司' ) a , ( select 员工数 from 公司 where 名称 == '北京小桔科技有限公司' ) b	CCTV中国经济年度人物
qid001996	select a.成立时间 - b.成立时间 from ( select 成立时间 from 公司 where 名称 == '深圳腾讯科技有限公司' ) a , ( select 成立时间 from 公司 where 名称 == '北京小桔科技有限公司' ) b	CCTV中国经济年度人物
qid001997	select a.市值 - b.市值 from ( select 市值 from 公司 where 名称 == '深圳腾讯科技有限公司' ) a , ( select 市值 from 公司 where 名称 == '北京小桔科技有限公司' ) b	CCTV中国经济年度人物
qid001998	select a.饱和脂肪含量 - b.饱和脂肪含量 from ( select 饱和脂肪含量 from 坚果 where 名称 == '板栗' ) a , ( select 饱和脂肪含量 from 坚果 where 名称 == '花生' ) b	坚果
qid001999	select a.不饱和脂肪含量 - b.不饱和脂肪含量 from ( select 不饱和脂肪含量 from 坚果 where 名称 == '板栗' ) a , ( select 不饱和脂肪含量 from 坚果 where 名称 == '花生' ) b	坚果
qid002000	select a.每100克热量 - b.每100克热量 from ( select 每100克热量 from 坚果 where 名称 == '板栗' ) a , ( select 每100克热量 from 坚果 where 名称 == '花生' ) b	坚果
qid002001	select a.民用枪支数 - b.民用枪支数 from ( select 民用枪支数 from 国家 where 名称 == '乌拉圭' ) a , ( select 民用枪支数 from 国家 where 名称 == '美国' ) b	枪击事件
qid002002	select a.民用枪支数 / b.民用枪支数 from ( select 民用枪支数 from 国家 where 名称 == '乌拉圭' ) a , ( select 民用枪支数 from 国家 where 名称 == '美国' ) b	枪击事件
qid002003	select a.人口数量 - b.人口数量 from ( select 人口数量 from 国家 where 名称 == '乌拉圭' ) a , ( select 人口数量 from 国家 where 名称 == '美国' ) b	枪击事件
qid002004	select a.每100人持有的民用枪支数 - b.每100人持有的民用枪支数 from ( select 每100人持有的民用枪支数 from 国家 where 名称 == '乌拉圭' ) a , ( select 每100人持有的民用枪支数 from 国家 where 名称 == '美国' ) b	枪击事件
qid002005	select a.军用枪支数 / b.军用枪支数 from ( select 军用枪支数 from 国家 where 名称 == '乌拉圭' ) a , ( select 军用枪支数 from 国家 where 名称 == '美国' ) b	枪击事件
qid002006	select a.军用枪支数 - b.军用枪支数 from ( select 军用枪支数 from 国家 where 名称 == '乌拉圭' ) a , ( select 军用枪支数 from 国家 where 名称 == '美国' ) b	枪击事件
qid002007	select a.每100人持有的民用枪支数 / b.每100人持有的民用枪支数 from ( select 每100人持有的民用枪支数 from 国家 where 名称 == '乌拉圭' ) a , ( select 每100人持有的民用枪支数 from 国家 where 名称 == '美国' ) b	枪击事件
qid002008	select a.覆盖城市数 - b.覆盖城市数 from ( select 覆盖城市数 from 打车APP where app名称 == '首汽约车' ) a , ( select 覆盖城市数 from 打车APP where app名称 == '神州专车' ) b	打车软件
qid002009	select a.服务用户数量 - b.服务用户数量 from ( select 服务用户数量 from 打车APP where app名称 == '首汽约车' ) a , ( select 服务用户数量 from 打车APP where app名称 == '神州专车' ) b	打车软件
qid002010	select a.成立时间 - b.成立时间 from ( select 成立时间 from 企业 where 中文名 == '上门美甲有限公司' )  a , ( select 成立时间 from 企业 where 中文名 == '独角兽' )  b	企业融资
qid002011	select a.注册资本 + b.注册资本 from ( select 注册资本 from 企业 where 中文名 == '上门美甲有限公司' )  a , ( select 注册资本 from 企业 where 中文名 == '独角兽' )  b	企业融资
qid002012	select a.注册资本 - b.注册资本 from ( select 注册资本 from 企业 where 中文名 == '上门美甲有限公司' )  a , ( select 注册资本 from 企业 where 中文名 == '独角兽' )  b	企业融资
qid002013	select a.注册资本 / b.注册资本 from ( select 注册资本 from 企业 where 中文名 == '上门美甲有限公司' )  a , ( select 注册资本 from 企业 where 中文名 == '独角兽' )  b	企业融资
qid002014	select a.年龄 - b.年龄 from ( select 年龄 from 企业人物 where 姓名 == '李彦宏' )  a , ( select 年龄 from 企业人物 where 姓名 == '董明珠' )  b	CCTV中国经济年度人物
qid002015	select a.世界500强排名 - b.世界500强排名 from ( select 世界500强排名 from 洗衣机品牌 where 名称 == '西门子' )  a , ( select 世界500强排名 from 洗衣机品牌 where 名称 == '三星' )  b	洗衣机
qid002016	select a.2018年营业额 - b.2018年营业额 from ( select 2018年营业额 from 洗衣机品牌 where 名称 == '西门子' )  a , ( select 2018年营业额 from 洗衣机品牌 where 名称 == '三星' )  b	洗衣机
qid002017	select a.成立时间 - b.成立时间 from ( select 成立时间 from 洗衣机品牌 where 名称 == '西门子' )  a , ( select 成立时间 from 洗衣机品牌 where 名称 == '三星' )  b	洗衣机
qid002018	select a.2018年利润 - b.2018年利润 from ( select 2018年利润 from 洗衣机品牌 where 名称 == '西门子' )  a , ( select 2018年利润 from 洗衣机品牌 where 名称 == '三星' )  b	洗衣机
qid002019	select a.市场份额 - b.市场份额 from ( select 市场份额 from 洗衣机品牌 where 名称 == '西门子' )  a , ( select 市场份额 from 洗衣机品牌 where 名称 == '三星' )  b	洗衣机
qid002020	select a.成立时间 - b.成立时间 from ( select 成立时间 from 平台 where 名称 == '当当' )  a , ( select 成立时间 from 平台 where 名称 == '京东' )  b	购书平台
qid002021	select a.会员费 - b.会员费 from ( select 会员费 from 平台 where 名称 == '当当' )  a , ( select 会员费 from 平台 where 名称 == '京东' )  b	购书平台
qid002022	select a.年营业额 / b.年营业额 from ( select 年营业额 from 平台 where 名称 == '当当' )  a , ( select 年营业额 from 平台 where 名称 == '京东' )  b	购书平台
qid002023	select a.年营业额 - b.年营业额 from ( select 年营业额 from 平台 where 名称 == '当当' )  a , ( select 年营业额 from 平台 where 名称 == '京东' )  b	购书平台
qid002024	select a.不饱和脂肪含量 - b.不饱和脂肪含量 from ( select 不饱和脂肪含量 from 坚果 where 名称 == '瓜子' )  a , ( select 不饱和脂肪含量 from 坚果 where 名称 == '核桃' )  b	坚果
qid002025	select a.饱和脂肪含量 - b.饱和脂肪含量 from ( select 饱和脂肪含量 from 坚果 where 名称 == '瓜子' )  a , ( select 饱和脂肪含量 from 坚果 where 名称 == '核桃' )  b	坚果
qid002026	select a.每100克热量 - b.每100克热量 from ( select 每100克热量 from 坚果 where 名称 == '瓜子' )  a , ( select 每100克热量 from 坚果 where 名称 == '核桃' )  b	坚果
qid002027	select a.服务用户数量 - b.服务用户数量 from ( select 服务用户数量 from 打车APP where app名称 == '滴滴专车' )  a , ( select 服务用户数量 from 打车APP where app名称 == '嘀嗒打车' )  b	打车软件
qid002028	select a.覆盖城市数 - b.覆盖城市数 from ( select 覆盖城市数 from 打车APP where app名称 == '滴滴专车' )  a , ( select 覆盖城市数 from 打车APP where app名称 == '嘀嗒打车' )  b	打车软件
qid002029	select a.员工数 - b.员工数 from ( select 员工数 from 公司 where 名称 == '北京小桔科技有限公司' )  a , ( select 员工数 from 公司 where 名称 == '北京三快在线科技有限公司' )  b	CCTV中国经济年度人物
qid002030	select a.市值 - b.市值 from ( select 市值 from 公司 where 名称 == '北京小桔科技有限公司' )  a , ( select 市值 from 公司 where 名称 == '北京三快在线科技有限公司' )  b	CCTV中国经济年度人物
qid002031	select a.成立时间 - b.成立时间 from ( select 成立时间 from 公司 where 名称 == '北京小桔科技有限公司' )  a , ( select 成立时间 from 公司 where 名称 == '北京三快在线科技有限公司' )  b	CCTV中国经济年度人物
qid002032	select a.世界500强排名 - b.世界500强排名 from ( select 世界500强排名 from 公司 where 名称 == '北京小桔科技有限公司' )  a , ( select 世界500强排名 from 公司 where 名称 == '北京三快在线科技有限公司' )  b	CCTV中国经济年度人物
qid002033	select a.年营业额 - b.年营业额 from ( select 年营业额 from 公司 where 名称 == '北京小桔科技有限公司' )  a , ( select 年营业额 from 公司 where 名称 == '北京三快在线科技有限公司' )  b	CCTV中国经济年度人物
qid002034	select a.每公里价格 - b.每公里价格 from ( select 每公里价格 from 打车方式 where 名称 == '顺风车' )  a , ( select 每公里价格 from 打车方式 where 名称 == '专车' )  b	打车软件
qid002035	select a.售价 - b.售价 from ( select 售价 from 洗衣机型号 where 名称 == '海尔G90726B12G' )  a , ( select 售价 from 洗衣机型号 where 名称 == '小天鹅TG100-1420WDXG' )  b	洗衣机
qid002036	select a.人口数量 - b.人口数量 from ( select 人口数量 from 国家 where 名称 == '乌拉圭' )  a , ( select 人口数量 from 国家 where 名称 == '塞尔维亚' )  b	枪击事件
qid002037	select a.每100人持有的民用枪支数 - b.每100人持有的民用枪支数 from ( select 每100人持有的民用枪支数 from 国家 where 名称 == '乌拉圭' )  a , ( select 每100人持有的民用枪支数 from 国家 where 名称 == '塞尔维亚' )  b	枪击事件
qid002038	select a.军用枪支数 - b.军用枪支数 from ( select 军用枪支数 from 国家 where 名称 == '乌拉圭' )  a , ( select 军用枪支数 from 国家 where 名称 == '塞尔维亚' )  b	枪击事件
qid002039	select a.民用枪支数 - b.民用枪支数 from ( select 民用枪支数 from 国家 where 名称 == '乌拉圭' )  a , ( select 民用枪支数 from 国家 where 名称 == '塞尔维亚' )  b	枪击事件
qid002040	select T2.中文名 , min ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 >= 1000000 group by T1.企业id	企业融资
qid002041	select T2.中文名 , sum ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id	企业融资
qid002042	select T2.中文名 , max ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 > 1000000 group by T1.企业id	企业融资
qid002043	select T2.中文名 , avg ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 < 1000000 group by T1.企业id	企业融资
qid002044	select T2.中文名 , sum ( T1.融资额 ) , T2.法定代表人 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 >= 1000000 group by T1.企业id	企业融资
qid002045	select T2.名称 , max ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid002046	select T2.名称 , sum ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid002047	select T2.名称 , sum ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid002048	select T2.名称 , max ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid002049	select T2.名称 , min ( T1.售价 ) , T2.所属公司 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id	洗衣机
qid002050	select T2.名称 , min ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid002051	select T2.名称 , max ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id	洗衣机
qid002052	select T2.名称 , max ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id	洗衣机
qid002053	select T2.名称 , min ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid002054	select T2.名称 , max ( T1.门店数量 ) , T2.所属公司 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid002055	select T2.名称 , max ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 <= 12 group by T1.方式id	打车软件
qid002056	select T2.名称 , avg ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 < 12 group by T1.方式id	打车软件
qid002057	select T2.名称 , min ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 <= 12 group by T1.方式id	打车软件
qid002058	select T2.名称 , sum ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 > 12 group by T1.方式id	打车软件
qid002059	select T2.名称 , max ( T1.车数量 ) , T2.理念 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 >= 12 group by T1.方式id	打车软件
qid002060	select T2.名称 , avg ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid002061	select T2.名称 , sum ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id	洗衣机
qid002062	select T2.名称 , avg ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id	洗衣机
qid002063	select T2.名称 , min ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id	洗衣机
qid002064	select T2.名称 , sum ( T1.总评分 ) , T2.所属公司 from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id	洗衣机
qid002065	select T2.中文名 , sum ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 >= 25 group by T1.球员id	运动员比赛记录
qid002066	select T2.中文名 , sum ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 < 25 group by T1.球员id	运动员比赛记录
qid002067	select T2.中文名 , min ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 <= 25 group by T1.球员id	运动员比赛记录
qid002068	select T2.中文名 , avg ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 >= 25 group by T1.球员id	运动员比赛记录
qid002069	select T2.中文名 , max ( T1.出场次数 ) , T2.场上位置 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 > 25 group by T1.球员id	运动员比赛记录
qid002070	select T2.中文名 , max ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id	企业融资
qid002071	select T2.中文名 , min ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id	企业融资
qid002072	select T2.中文名 , sum ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 > 1000000 group by T1.企业id	企业融资
qid002073	select T2.中文名 , min ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 >= 1000000 group by T1.企业id	企业融资
qid002074	select T2.中文名 , max ( T1.融资总额 ) , T2.法定代表人 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 > 1000000 group by T1.企业id	企业融资
qid002075	select T2.名称 , max ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T2.年营业额 < 7177800000000 group by T1.平台id having count ( * ) <= 5	购书平台
qid002076	select T2.名称 , avg ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id where T2.年营业额 < 7177800000000 group by T1.平台id having sum ( T1.评分人数 ) >= 100	购书平台
qid002077	select T2.中文名 , max ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 < 1000000 group by T1.企业id having count ( * ) < 5	企业融资
qid002078	select T2.中文名 , sum ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id where T2.注册资本 < 1000000 group by T1.企业id having avg ( T1.投资公司持股比例 ) < 0.75	企业融资
qid002079	select T2.名称 , min ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 <= 12 group by T1.方式id having avg ( T1.每日打车单数 ) > 8000	打车软件
qid002080	select T2.名称 , min ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id where T2.每公里价格 > 12 group by T1.方式id having sum ( T1.每日打车单数 ) < 100000	打车软件
qid002081	select T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 < 0.102 group by T1.品牌id having count ( * ) == 5	洗衣机
qid002082	select T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id where T2.市场份额 <= 0.102 group by T1.品牌id having count ( * ) <= 5	洗衣机
qid002083	select T2.名称 , sum ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id having count ( * ) == 5	洗衣机
qid002084	select T2.名称 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id having sum ( T1.售卖量 ) <= 100000	洗衣机
qid002085	select T2.中文名 , sum ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id having count ( * ) <= 5	企业融资
qid002086	select T2.中文名 , avg ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id where T2.注册资本 <= 1000000 group by T1.企业id having count ( * ) >= 5	企业融资
qid002087	select T2.名称 , max ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 >= 0.102 group by T1.品牌id having count ( * ) < 5	洗衣机
qid002088	select T2.名称 , min ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id where T2.市场份额 > 0.102 group by T1.品牌id having avg ( T1.功能得分 ) <= 6.5	洗衣机
qid002089	select T2.中文名 , max ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 > 25 group by T1.球员id having count ( * ) >= 5	运动员比赛记录
qid002090	select T2.中文名 , min ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id where T2.年龄 <= 25 group by T1.球员id having avg ( T1.犯规 ) > 9	运动员比赛记录
qid002091	select T2.所属洲 , T2.名称 , max ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id	奥运会参赛队伍
qid002092	select T2.所属洲 , T2.名称 , sum ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id	奥运会参赛队伍
qid002093	select T2.所属洲 , T2.名称 , avg ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id	奥运会参赛队伍
qid002094	select T2.所属洲 , T2.名称 , min ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id	奥运会参赛队伍
qid002095	select T2.作者 , T2.书名 , max ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id	购书平台
qid002096	select T2.作者 , T2.书名 , avg ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id	购书平台
qid002097	select T2.作者 , T2.书名 , sum ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id	购书平台
qid002098	select T2.作者 , T2.书名 , min ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id	购书平台
qid002099	select T2.法定代表人 , T2.中文名 , avg ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id	企业融资
qid002100	select T2.法定代表人 , T2.中文名 , sum ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id	企业融资
qid002101	select T2.法定代表人 , T2.中文名 , min ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id	企业融资
qid002102	select T2.法定代表人 , T2.中文名 , max ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id	企业融资
qid002103	select T2.理念 , T2.名称 , max ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id	打车软件
qid002104	select T2.理念 , T2.名称 , min ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id	打车软件
qid002105	select T2.理念 , T2.名称 , sum ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id	打车软件
qid002106	select T2.理念 , T2.名称 , avg ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id	打车软件
qid002107	select T2.所属公司 , T2.名称 , sum ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002108	select T2.所属公司 , T2.名称 , min ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002109	select T2.所属公司 , T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002110	select T2.所属公司 , T2.名称 , max ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002111	select T2.所属公司 , T2.名称 , min ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002112	select T2.所属公司 , T2.名称 , sum ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002113	select T2.所属公司 , T2.名称 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002114	select T2.所属公司 , T2.名称 , max ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002115	select T2.法定代表人 , T2.中文名 , sum ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id	企业融资
qid002116	select T2.法定代表人 , T2.中文名 , max ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id	企业融资
qid002117	select T2.法定代表人 , T2.中文名 , min ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id	企业融资
qid002118	select T2.法定代表人 , T2.中文名 , avg ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id	企业融资
qid002119	select T2.所属公司 , T2.名称 , max ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002120	select T2.所属公司 , T2.名称 , sum ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002121	select T2.所属公司 , T2.名称 , avg ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002122	select T2.所属公司 , T2.名称 , min ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id	洗衣机
qid002123	select T2.所属洲 , T2.名称 , sum ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id	奥运会参赛队伍
qid002124	select T2.所属洲 , T2.名称 , min ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id	奥运会参赛队伍
qid002125	select T2.所属洲 , T2.名称 , avg ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id	奥运会参赛队伍
qid002126	select T2.所属洲 , T2.名称 , max ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id	奥运会参赛队伍
qid002127	select T2.所属地区 , T2.中文队名 , avg ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id	欧洲杯球队
qid002128	select T2.所属地区 , T2.中文队名 , max ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id	欧洲杯球队
qid002129	select T2.所属地区 , T2.中文队名 , sum ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id	欧洲杯球队
qid002130	select T2.所属地区 , T2.中文队名 , min ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id	欧洲杯球队
qid002131	select T2.场上位置 , T2.中文名 , max ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id	运动员比赛记录
qid002132	select T2.场上位置 , T2.中文名 , min ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id	运动员比赛记录
qid002133	select T2.场上位置 , T2.中文名 , sum ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id	运动员比赛记录
qid002134	select T2.场上位置 , T2.中文名 , avg ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id	运动员比赛记录
qid002135	select T2.性别 , T2.姓名 from 历届经济人物获奖名单 as T1 join 企业人物 as T2 on 历届经济人物获奖名单.获奖人id == 企业人物.词条id group by T1.获奖人id having count ( * ) == 5	CCTV中国经济年度人物
qid002136	select T2.类型 , T2.名称 from 参考试卷 as T1 join 参考书 as T2 on 参考试卷.试卷id == 参考书.词条id group by T1.试卷id having count ( * ) == 5	教材辅助参考书
qid002137	select T2.所属公司 , T2.名称 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) > 5	洗衣机
qid002138	select T2.所属公司 , T2.名称 from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id having avg ( T1.售价 ) >= 1500	洗衣机
qid002139	select T2.理念 , T2.名称 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id having avg ( T1.车数量 ) <= 50	打车软件
qid002140	select T2.理念 , T2.名称 from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id having sum ( T1.车数量 ) < 100	打车软件
qid002141	select T2.所属地区 , T2.中文队名 from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id having count ( * ) < 5	欧洲杯球队
qid002142	select T2.所属地区 , T2.中文队名 from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id having avg ( T1.届数 ) >= 5	欧洲杯球队
qid002143	select T2.性别 , T2.姓名 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id group by T1.人物id having count ( * ) <= 5	CCTV中国经济年度人物
qid002144	select T2.性别 , T2.姓名 from 人物公司职位 as T1 join 企业人物 as T2 on 人物公司职位.人物id == 企业人物.词条id group by T1.人物id having count ( * ) >= 5	CCTV中国经济年度人物
qid002145	select T2.民族 , T2.姓名 from 综艺节目嘉宾 as T1 join 明星 as T2 on 综艺节目嘉宾.明星id == 明星.词条id group by T1.明星id having count ( * ) >= 5	综艺节目
qid002146	select T2.民族 , T2.姓名 from 综艺节目嘉宾 as T1 join 明星 as T2 on 综艺节目嘉宾.明星id == 明星.词条id group by T1.明星id having count ( * ) == 5	综艺节目
qid002147	select T2.所属地区 , T2.中文队名 from 欧冠冠亚军 as T1 join 球队 as T2 on 欧冠冠亚军.亚军球队id == 球队.词条id group by T1.亚军球队id having count ( * ) <= 5	欧洲杯球队
qid002148	select T2.所属地区 , T2.中文队名 from 欧冠冠亚军 as T1 join 球队 as T2 on 欧冠冠亚军.冠军球队id == 球队.词条id group by T1.冠军球队id having count ( * ) <= 5	欧洲杯球队
qid002149	select T2.类别 , T2.名称 from 高校属性 as T1 join 高校 as T2 on 高校属性.高校id == 高校.词条id group by T1.高校id having count ( * ) >= 5	中国高校
qid002150	select T2.类别 , T2.名称 from 高校属性 as T1 join 高校 as T2 on 高校属性.高校id == 高校.词条id group by T1.高校id having count ( * ) > 5	中国高校
qid002151	select T2.类别 , T2.名称 from 名人 as T1 join 高校 as T2 on 名人.高校id == 高校.词条id group by T1.高校id having count ( * ) <= 5	中国高校
qid002152	select T2.类别 , T2.名称 from 名人 as T1 join 高校 as T2 on 名人.高校id == 高校.词条id group by T1.高校id having count ( * ) < 5	中国高校
qid002153	select T2.法定代表人 , T2.中文名 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id having count ( * ) <= 5	企业融资
qid002154	select T2.法定代表人 , T2.中文名 from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id having sum ( T1.融资额 ) >= 6000000	企业融资
qid002155	select T2.场上位置 , T2.中文名 from 生涯之最 as T1 join 篮球运动员 as T2 on 生涯之最.球员id == 篮球运动员.词条id group by T1.球员id having count ( * ) < 5	运动员比赛记录
qid002156	select T2.所属公司 , T2.名称 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id having avg ( T1.门店数量 ) <= 50	洗衣机
qid002157	select T2.所属公司 , T2.名称 from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) < 5	洗衣机
qid002158	select T2.法定代表人 , T2.中文名 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id having sum ( T1.融资总额 ) > 1000000000	企业融资
qid002159	select T2.法定代表人 , T2.中文名 from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id having sum ( T1.融资总额 ) < 1000000000	企业融资
qid002160	select T2.场上位置 , T2.中文名 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id having avg ( T1.出场次数 ) >= 10	运动员比赛记录
qid002161	select T2.场上位置 , T2.中文名 from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id having count ( * ) > 5	运动员比赛记录
qid002162	select T2.所属省份 , T2.城市 from 对口帮扶城市 as T1 join 城市 as T2 on 对口帮扶城市.帮助城市id == 城市.词条id group by T1.帮助城市id having count ( * ) <= 5	友好城市
qid002163	select T2.所属省份 , T2.城市 from 对口帮扶城市 as T1 join 城市 as T2 on 对口帮扶城市.帮助城市id == 城市.词条id group by T1.帮助城市id having count ( * ) >= 5	友好城市
qid002164	select T2.作者 , T2.书名 from 电子书 as T1 join 图书 as T2 on 电子书.书名id == 图书.词条id group by T1.书名id having sum ( T1.电子书售价 ) > 80	购书平台
qid002165	select T2.作者 , T2.书名 from 电子书 as T1 join 图书 as T2 on 电子书.书名id == 图书.词条id group by T1.书名id having sum ( T1.电子书售价 ) < 80	购书平台
qid002166	select T2.名称 , min ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id group by T1.坚果id having count ( * ) >= 5	坚果
qid002167	select T2.名称 , avg ( T1.营业收入 ) from 坚果季节性营业收入 as T1 join 坚果 as T2 on 坚果季节性营业收入.坚果id == 坚果.词条id group by T1.坚果id having count ( * ) == 5	坚果
qid002168	select T2.名称 , sum ( T1.枪击事件数量 ) from 枪击事件 as T1 join 国家 as T2 on 枪击事件.国家id == 国家.词条id group by T1.国家id having sum ( T1.受伤人数 ) <= 100	枪击事件
qid002169	select T2.名称 , avg ( T1.枪击事件数量 ) from 枪击事件 as T1 join 国家 as T2 on 枪击事件.国家id == 国家.词条id group by T1.国家id having avg ( T1.受伤人数 ) >= 100	枪击事件
qid002170	select T2.名称 , min ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id having sum ( T1.大项项目数 ) < 100	奥运会参赛队伍
qid002171	select T2.名称 , avg ( T1.参赛国家数量 ) from 夏季奥运会 as T1 join 国家 as T2 on 夏季奥运会.举办国家id == 国家.词条id group by T1.举办国家id having sum ( T1.小项项目数 ) < 100	奥运会参赛队伍
qid002172	select T2.书名 , avg ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id having sum ( T1.收藏人数 ) > 100	购书平台
qid002173	select T2.书名 , sum ( T1.售价 ) from 图书与平台 as T1 join 图书 as T2 on 图书与平台.书名id == 图书.词条id group by T1.书名id having count ( * ) < 5	购书平台
qid002174	select T2.中文名 , avg ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id having avg ( T1.投资公司持股比例 ) < 0.8	企业融资
qid002175	select T2.中文名 , min ( T1.融资额 ) from 投资公司 as T1 join 企业 as T2 on 投资公司.企业id == 企业.词条id group by T1.企业id having count ( * ) < 5	企业融资
qid002176	select T2.名称 , avg ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id having sum ( T1.每日打车单数 ) <= 100	打车软件
qid002177	select T2.名称 , sum ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车方式 as T2 on 各打车APP支持的方式.方式id == 打车方式.词条id group by T1.方式id having count ( * ) >= 5	打车软件
qid002178	select T2.名称 , avg ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) == 5	洗衣机
qid002179	select T2.名称 , sum ( T1.售价 ) from 洗衣机型号 as T1 join 洗衣机品牌 as T2 on 洗衣机型号.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) == 5	洗衣机
qid002180	select T2.名称 , avg ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id having avg ( T1.售卖量 ) == 100	洗衣机
qid002181	select T2.名称 , max ( T1.门店数量 ) from 洗衣机品牌门店 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌门店.品牌id == 洗衣机品牌.词条id group by T1.品牌id having avg ( T1.售卖量 ) > 100	洗衣机
qid002182	select T2.中文名 , max ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id having count ( * ) > 5	企业融资
qid002183	select T2.中文名 , min ( T1.融资总额 ) from 企业融资 as T1 join 企业 as T2 on 企业融资.企业id == 企业.词条id group by T1.企业id having count ( * ) <= 5	企业融资
qid002184	select T2.名称 , max ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id group by T1.平台id having sum ( T1.加入购物车人数 ) <= 100	购书平台
qid002185	select T2.名称 , avg ( T1.售价 ) from 图书与平台 as T1 join 平台 as T2 on 图书与平台.平台id == 平台.词条id group by T1.平台id having count ( * ) == 5	购书平台
qid002186	select T2.名称 , avg ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) > 5	洗衣机
qid002187	select T2.名称 , min ( T1.总评分 ) from 洗衣机品牌平台评分 as T1 join 洗衣机品牌 as T2 on 洗衣机品牌平台评分.品牌id == 洗衣机品牌.词条id group by T1.品牌id having count ( * ) > 5	洗衣机
qid002188	select T2.app名称 , sum ( T1.占所在城市份额 ) from 打车软件开通城市 as T1 join 打车APP as T2 on 打车软件开通城市.appid == 打车APP.词条id group by T1.appid having count ( * ) < 5	打车软件
qid002189	select T2.app名称 , min ( T1.占所在城市份额 ) from 打车软件开通城市 as T1 join 打车APP as T2 on 打车软件开通城市.appid == 打车APP.词条id group by T1.appid having count ( * ) >= 5	打车软件
qid002190	select T2.名称 , sum ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id having avg ( T1.铜牌数 ) == 100	奥运会参赛队伍
qid002191	select T2.名称 , max ( T1.金牌数 ) from 2008北京奥运会奖牌榜 as T1 join 国家 as T2 on 2008北京奥运会奖牌榜.国家id == 国家.词条id group by T1.国家id having count ( * ) < 5	奥运会参赛队伍
qid002192	select T2.中文队名 , min ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id having count ( * ) > 5	欧洲杯球队
qid002193	select T2.中文队名 , min ( T1.届数 ) from 球队欧冠赛事 as T1 join 球队 as T2 on 球队欧冠赛事.球队id == 球队.词条id group by T1.球队id having avg ( T1.净胜球 ) == 100	欧洲杯球队
qid002194	select T2.中文名 , min ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id having count ( * ) < 5	运动员比赛记录
qid002195	select T2.中文名 , sum ( T1.出场次数 ) from 比赛记录 as T1 join 篮球运动员 as T2 on 比赛记录.球员id == 篮球运动员.词条id group by T1.球员id having sum ( T1.投篮 ) >= 100	运动员比赛记录
qid002196	select T2.名称 , min ( T1.线上销售收入 ) from 坚果销售渠道 as T1 join 坚果 as T2 on 坚果销售渠道.坚果id == 坚果.词条id group by T1.坚果id having sum ( T1.线下销售收入 ) > 100	坚果
qid002197	select T2.名称 , sum ( T1.线上销售收入 ) from 坚果销售渠道 as T1 join 坚果 as T2 on 坚果销售渠道.坚果id == 坚果.词条id group by T1.坚果id having sum ( T1.线下销售收入 ) >= 100	坚果
qid002198	select T2.名称 , sum ( T1.市场占比 ) from 坚果产地 as T1 join 坚果 as T2 on 坚果产地.坚果id == 坚果.词条id group by T1.坚果id having count ( * ) > 5	坚果
qid002199	select T2.名称 , sum ( T1.市场占比 ) from 坚果产地 as T1 join 坚果 as T2 on 坚果产地.坚果id == 坚果.词条id group by T1.坚果id having count ( * ) < 5	坚果
qid002200	select T2.app名称 , sum ( T1.车数量 ) from 各打车APP支持的方式 as T1 join 打车APP as T2 on 各打车APP支持的方式.appid == 打车APP.词条id group by T1.appid having avg ( T1.每日营收 ) == 100	打车软件
qid002201	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having sum ( T1.收视份额 ) > 0.003	综艺节目
qid002202	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having sum ( T1.收视份额 ) < 0.003	综艺节目
qid002203	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having sum ( T1.收视份额 ) >= 0.003	综艺节目
qid002204	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having sum ( T1.收视份额 ) <= 0.003	综艺节目
qid002205	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having sum ( T1.奖项数量 ) > 30	中国高校
qid002206	select T2.名称 , sum ( T1.奖项数量 ) from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id	中国高校
qid002207	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having avg ( T1.奖项数量 ) <= 30	中国高校
qid002208	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having avg ( T1.奖项数量 ) >= 30	中国高校
qid002209	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having sum ( T1.奖项数量 ) >= 30	中国高校
qid002210	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having avg ( T1.奖项数量 ) < 30	中国高校
qid002211	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having sum ( T1.奖项数量 ) < 30	中国高校
qid002212	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id group by T1.高校id having sum ( T1.奖项数量 ) <= 30	中国高校
qid002213	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id order by sum ( T1.奖项数量 ) asc limit 1	中国高校
qid002214	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id order by sum ( T1.奖项数量 ) desc limit 1	中国高校
qid002215	select T2.名称 from 奖项 as T1 join 高校 as T2 on 奖项.高校id == 高校.词条id where 统计时间 > 2018 group by T1.高校id order by sum ( T1.奖项数量 ) asc limit 3	中国高校
qid002216	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) > 0.003	综艺节目
qid002217	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) < 0.003	综艺节目
qid002218	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) <= 0.003	综艺节目
qid002219	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) >= 0.003	综艺节目
qid002220	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having avg ( T1.收视率 ) == 0.003	综艺节目
qid002221	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) < 5	综艺节目
qid002222	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) <= 5	综艺节目
qid002223	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) == 5	综艺节目
qid002224	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) > 5	综艺节目
qid002225	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id having count ( * ) >= 5	综艺节目
qid002226	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by count ( * ) asc limit 1	综艺节目
qid002227	select T2.节目名称 , count ( * ) from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id group by T1.节目id	综艺节目
qid002228	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by count ( * ) desc limit3	综艺节目
qid002229	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by count ( * ) desc limit 1	综艺节目
qid002230	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by count ( * ) asc limit 3	综艺节目
qid002231	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by sum ( T1.收视份额 ) desc limit 1	综艺节目
qid002232	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by sum ( T1.收视份额 ) asc limit 1	综艺节目
qid002233	select T2.节目名称 from 收视率 as T1 join 综艺节目 as T2 on 收视率.节目id == 综艺节目.词条id where T2.系列名 == '欢乐喜剧人' group by T1.节目id order by sum ( T1.收视份额 ) asc limit 2	综艺节目
qid002234	select 季节 , count ( * ) from 坚果季节性营业收入 group by 季节	坚果
qid002235	select 系列名 , count ( * ) from 综艺节目 group by 系列名	综艺节目
qid002236	select 投资公司 , count ( * ) from 投资公司 group by 投资公司	企业融资
qid002237	select 所属公司 , count ( * ) from 打车APP group by 所属公司	打车软件
qid002238	select 城市 , count ( * ) from 洗衣机品牌门店 group by 城市	洗衣机
qid002239	select 营养成分 , count ( * ) from 每100克坚果营养成分 group by 营养成分	坚果
qid002240	select 产品类别 , count ( * ) from 洗衣机型号 group by 产品类别	洗衣机
qid002241	select 国家 , count ( * ) from 坚果摄入量 group by 国家	坚果
qid002242	select 法定代表人 , count ( * ) from 企业 group by 法定代表人	企业融资
qid002243	select 类型 , count ( * ) from 参考书 group by 类型	教材辅助参考书
qid002244	select 出品公司 , count ( * ) from 电视剧 group by 出品公司	中国卫视频道
qid002245	select 所属省 , count ( * ) from 一带一路的中国城市 group by 所属省	友好城市
qid002246	select 国家 , count ( * ) from 一带一路线路上的国家 group by 国家	友好城市
qid002247	select 场上位置 , count ( * ) from 篮球运动员 group by 场上位置	运动员比赛记录
qid002248	select 平台 , count ( * ) from 洗衣机品牌平台评分 group by 平台	洗衣机
qid002249	select 所属省 , count ( * ) from 对口帮扶城市 group by 所属省	友好城市
qid002250	select 民族 , count ( * ) from 明星 group by 民族	综艺节目
qid002251	select 所属地区 , count ( * ) from 球队 group by 所属地区	欧洲杯球队
qid002252	select 产地 , count ( * ) from 坚果产地 group by 产地	坚果
qid002253	select 所属洲 , count ( * ) from 国家 group by 所属洲	奥运会参赛队伍
qid002254	select 作者 , count ( * ) from 图书 group by 作者	购书平台
qid002255	select 系列名 from 综艺节目 where 首播时间 <= 2014-10-01 group by 系列名 order by count ( * ) desc limit 1	综艺节目
qid002256	select 系列名 from 综艺节目 where 首播时间 <= 2014-10-01 group by 系列名 order by count ( * ) desc limit 3	综艺节目
qid002257	select 系列名 from 综艺节目 where 首播时间 <= 2014-10-01 group by 系列名 order by count ( * ) asc limit 3	综艺节目
qid002258	select 季节 from 坚果季节性营业收入 where 营业收入 >= 300000000 group by 季节 order by sum ( 全年占比 ) desc limit 1	坚果
qid002259	select 季节 from 坚果季节性营业收入 where 营业收入 != 300000000 group by 季节 order by count ( * ) desc limit 1	坚果
qid002260	select 季节 from 坚果季节性营业收入 where 营业收入 > 300000000 group by 季节 order by sum ( 全年占比 ) desc limit 1	坚果
qid002261	select 国家 from 坚果摄入量 where 人均摄入量 != 0.05 group by 国家 order by avg ( 世界人均摄入量 ) asc limit 1	坚果
qid002262	select 国家 from 坚果摄入量 where 人均摄入量 <= 0.05 group by 国家 order by avg ( 世界人均摄入量 ) asc limit 5	坚果
qid002263	select 国家 from 坚果摄入量 where 人均摄入量 > 0.05 group by 国家 order by count ( * ) desc limit 1	坚果
qid002264	select 法定代表人 from 企业 where 注册资本 > 1000000 group by 法定代表人 order by count ( * ) desc limit 3	企业融资
qid002265	select 法定代表人 from 企业 where 成立时间 < 2015 group by 法定代表人 order by avg ( 注册资本 ) asc limit 5	企业融资
qid002266	select 法定代表人 from 企业 where 成立时间 >= 2015 group by 法定代表人 order by avg ( 注册资本 ) desc limit 5	企业融资
qid002267	select 性别 from 企业人物 where 年龄 < 50 group by 性别 order by count ( * ) asc limit 1	CCTV中国经济年度人物
qid002268	select 出品公司 from 电视剧 where 出品时间 >= 2018 group by 出品公司 order by count ( * ) asc limit 3	中国卫视频道
qid002269	select 出品公司 from 电视剧 where 出品时间 > 2018 group by 出品公司 order by count ( * ) desc limit 1	中国卫视频道
qid002270	select 出品公司 from 电视剧 where 出品时间 >= 2018 group by 出品公司 order by count ( * ) desc limit 1	中国卫视频道
qid002271	select 球队 from 比赛记录 where 出场次数 < 40 group by 球队 order by sum ( 罚球 ) asc limit 3	运动员比赛记录
qid002272	select 球队 from 比赛记录 where 出场次数 != 40 group by 球队 order by count ( * ) asc limit 1	运动员比赛记录
qid002273	select 球队 from 比赛记录 where 出场次数 >= 40 group by 球队 order by count ( * ) asc limit 1	运动员比赛记录
qid002274	select 融资轮次 from 企业融资 where 融资总额 > 1000000000 group by 融资轮次 order by count ( * ) asc limit 1	企业融资
qid002275	select 融资轮次 from 企业融资 where 年份 >= 2010 group by 融资轮次 order by sum ( 融资总额 ) desc limit 1	企业融资
qid002276	select 融资轮次 from 企业融资 where 年份 < 2010 group by 融资轮次 order by count ( * ) asc limit 1	企业融资
qid002277	select 所属地区 from 球队 where 容纳人数 > 21000 group by 所属地区 order by count ( * ) desc limit 3	欧洲杯球队
qid002278	select 所属地区 from 球队 where 容纳人数 < 21000 group by 所属地区 order by count ( * ) asc limit 3	欧洲杯球队
qid002279	select 城市 from 打车软件开通城市 where 开通时间 > 2018-07 group by 城市 order by count ( * ) desc limit 1	打车软件
qid002280	select 城市 from 打车软件开通城市 where 开通时间 >= 2018-07 group by 城市 order by count ( * ) asc limit 1	打车软件
qid002281	select 城市 from 打车软件开通城市 where 开通时间 > 2018-07 group by 城市 order by count ( * ) asc limit 3	打车软件
qid002282	select 所属公司 from 洗衣机品牌 where 成立时间 < 1955 group by 所属公司 order by sum ( 市场份额 ) asc limit 3	洗衣机
qid002283	select 所属公司 from 洗衣机品牌 where 成立时间 > 1955 group by 所属公司 order by avg ( 市场份额 ) desc limit 5	洗衣机
qid002284	select 所属公司 from 洗衣机品牌 where 市场份额 <= 0.02 group by 所属公司 order by count ( * ) asc limit 3	洗衣机
qid002285	select 发生城市 from 美国近几年校园枪击事件 where 受影响学生数量 > 10000 group by 发生城市 order by count ( * ) desc limit 3	枪击事件
qid002286	select 发生城市 from 美国近几年校园枪击事件 where 受影响学生数量 <= 10000 group by 发生城市 order by count ( * ) asc limit 1	枪击事件
qid002287	select 朝代 from 都城 where 建都起始时间 <= 403 group by 朝代 order by count ( * ) desc limit 1	中国历史名城
qid002288	select 朝代 from 都城 where 建都起始时间 > 403 group by 朝代 order by count ( * ) desc limit 1	中国历史名城
qid002289	select 朝代 from 都城 where 古称 != '洛' group by 朝代 order by count ( * ) desc limit 1	中国历史名城
qid002290	select 产地 from 坚果产地 where 市场占比 != 0.44 group by 产地 order by count ( * ) desc limit 1	坚果
qid002291	select 产地 from 坚果产地 where 市场占比 > 0.44 group by 产地 order by count ( * ) desc limit 1	坚果
qid002292	select 产地 from 坚果产地 where 市场占比 > 0.44 group by 产地 order by count ( * ) asc limit 1	坚果
qid002293	select 类型 from 参考书 where 适用年级 != '1-3' group by 类型 order by count ( * ) desc limit 1	教材辅助参考书
qid002294	select 类型 from 参考书 where 适用年级 <= 3 group by 类型 order by count ( * ) desc limit 1	教材辅助参考书
qid002295	select 类型 from 参考书 where 适用年级 != '1-3' group by 类型 order by count ( * ) desc limit 3	教材辅助参考书
qid002296	select 国家 , min ( 世界人均摄入量 ) from 坚果摄入量 where 人均摄入量 > 0.05 group by 国家 having count ( * ) >= 5	坚果
qid002297	select 国家 , max ( 世界人均摄入量 ) from 坚果摄入量 where 人均摄入量 != 0.05 group by 国家 having count ( * ) < 5	坚果
qid002298	select 法定代表人 , avg ( 注册资本 ) from 企业 where 成立时间 >= 2015 group by 法定代表人 having count ( * ) >= 5	企业融资
qid002299	select 法定代表人 , min ( 注册资本 ) from 企业 where 成立时间 >= 2015 group by 法定代表人 having count ( * ) >= 5	企业融资
qid002300	select 球队 , sum ( 总篮板 ) from 比赛记录 where 出场次数 > 40 group by 球队 having count ( * ) > 5	运动员比赛记录
qid002301	select 球队 , avg ( 抢断 ) from 比赛记录 where 出场次数 < 40 group by 球队 having count ( * ) >= 5	运动员比赛记录
qid002302	select 融资轮次 , min ( 融资总额 ) from 企业融资 where 年份 <= 2010 group by 融资轮次 having count ( * ) >= 5	企业融资
qid002303	select 融资轮次 , sum ( 融资总额 ) from 企业融资 where 年份 <= 2010 group by 融资轮次 having count ( * ) <= 5	企业融资
qid002304	select 所属地区 , avg ( 容纳人数 ) from 球队 where 成立时间 < 1964 group by 所属地区 having count ( * ) < 5	欧洲杯球队
qid002305	select 所属地区 , avg ( 容纳人数 ) from 球队 where 主场馆 != '波尔多体育场' group by 所属地区 having count ( * ) > 5	欧洲杯球队
qid002306	select 城市 , max ( 占所在城市份额 ) from 打车软件开通城市 where 开通时间 <= 2018-07 group by 城市 having count ( * ) < 5	打车软件
qid002307	select 城市 , min ( 占所在城市份额 ) from 打车软件开通城市 where 开通时间 < 2018-07 group by 城市 having count ( * ) == 5	打车软件
qid002308	select 发生城市 , min ( 伤亡人数 ) from 美国近几年校园枪击事件 where 受影响学生数量 >= 10000 group by 发生城市 having count ( * ) > 5	枪击事件
qid002309	select 类型 , avg ( 价格 ) from 参考书 where 适用年级 <= 3 group by 类型 having count ( * ) <= 5	教材辅助参考书
qid002310	select 类型 , max ( 价格 ) from 参考书 where 适用年级 != '1-3' group by 类型 having count ( * ) >= 5	教材辅助参考书
qid002311	select 举办城市 , max ( 大项项目数 ) from 夏季奥运会 where 参赛国家数量 != 30 group by 举办城市 having count ( * ) == 5	奥运会参赛队伍
qid002312	select 举办城市 , sum ( 参赛运动员数量 ) from 夏季奥运会 where 参赛国家数量 < 30 group by 举办城市 having sum ( 大项项目数 ) > 500	奥运会参赛队伍
qid002313	select 所属公司 , avg ( 覆盖城市数 ) from 打车APP where 上线时间 < 2014 group by 所属公司 having count ( * ) > 5	打车软件
qid002314	select 所属公司 , min ( 覆盖城市数 ) from 打车APP where 上线时间 < 2014 group by 所属公司 having count ( * ) <= 5	打车软件
qid002315	select 城市 , min ( 售卖量 ) from 洗衣机品牌门店 where 门店数量 != 500 group by 城市 having count ( * ) == 5	洗衣机
qid002316	select 城市 , min ( 售卖量 ) from 洗衣机品牌门店 where 门店数量 < 500 group by 城市 having count ( * ) == 5	洗衣机
qid002317	select 所属省份 , min ( 国外驻华大使馆数量 ) from 城市 where 建交国家数量 <= 10 group by 所属省份 having sum ( 建交城市数量 ) < 500	友好城市
qid002318	select 所属省份 , avg ( 建交城市数量 ) from 城市 where 建交国家数量 <= 10 group by 所属省份 having sum ( 留学生数量 ) <= 500	友好城市
qid002319	select 国家 , sum ( 人均摄入量 ) from 坚果摄入量 group by 国家	坚果
qid002320	select 国家 , min ( 人均摄入量 ) from 坚果摄入量 group by 国家	坚果
qid002321	select 法定代表人 , avg ( 注册资本 ) from 企业 group by 法定代表人	企业融资
qid002322	select 法定代表人 , max ( 注册资本 ) from 企业 group by 法定代表人	企业融资
qid002323	select 性别 , min ( 年龄 ) from 企业人物 group by 性别	CCTV中国经济年度人物
qid002324	select 性别 , sum ( 年龄 ) from 企业人物 group by 性别	CCTV中国经济年度人物
qid002325	select 球队 , min ( 出场次数 ) from 比赛记录 group by 球队	运动员比赛记录
qid002326	select 球队 , max ( 出场次数 ) from 比赛记录 group by 球队	运动员比赛记录
qid002327	select 融资轮次 , min ( 融资总额 ) from 企业融资 group by 融资轮次	企业融资
qid002328	select 融资轮次 , avg ( 融资总额 ) from 企业融资 group by 融资轮次	企业融资
qid002329	select 所属地区 , sum ( 容纳人数 ) from 球队 group by 所属地区	欧洲杯球队
qid002330	select 所属地区 , max ( 容纳人数 ) from 球队 group by 所属地区	欧洲杯球队
qid002331	select 发生城市 , sum ( 受影响学生数量 ) from 美国近几年校园枪击事件 group by 发生城市	枪击事件
qid002332	select 发生城市 , min ( 受影响学生数量 ) from 美国近几年校园枪击事件 group by 发生城市	枪击事件
qid002333	select 城市 , sum ( 占所在城市份额 ) from 打车软件开通城市 group by 城市	打车软件
qid002334	select 城市 , avg ( 占所在城市份额 ) from 打车软件开通城市 group by 城市	打车软件
qid002335	select 所属公司 , avg ( 市场份额 ) from 洗衣机品牌 group by 所属公司	洗衣机
qid002336	select 所属公司 , sum ( 市场份额 ) from 洗衣机品牌 group by 所属公司	洗衣机
qid002337	select 季节 , min ( 营业收入 ) from 坚果季节性营业收入 group by 季节	坚果
qid002338	select 季节 , max ( 营业收入 ) from 坚果季节性营业收入 group by 季节	坚果
qid002339	select 产地 , sum ( 市场占比 ) from 坚果产地 group by 产地	坚果
qid002340	select 产地 , max ( 市场占比 ) from 坚果产地 group by 产地	坚果
qid002341	select 投资公司 , max ( 融资额 ) from 投资公司 group by 投资公司	企业融资
qid002342	select 所属公司 , max ( 覆盖城市数 ) from 打车APP group by 所属公司	打车软件
qid002343	select 所属公司 , avg ( 覆盖城市数 ) from 打车APP group by 所属公司	打车软件
qid002344	select 举办城市 , max ( 参赛国家数量 ) from 夏季奥运会 group by 举办城市	奥运会参赛队伍
qid002345	select 举办城市 , min ( 参赛国家数量 ) from 夏季奥运会 group by 举办城市	奥运会参赛队伍
qid002346	select 场上位置 , max ( 年龄 ) from 篮球运动员 group by 场上位置	运动员比赛记录
qid002347	select 场上位置 , min ( 年龄 ) from 篮球运动员 group by 场上位置	运动员比赛记录
qid002348	select 城市 , avg ( 门店数量 ) from 洗衣机品牌门店 group by 城市	洗衣机
qid002349	select 城市 , sum ( 门店数量 ) from 洗衣机品牌门店 group by 城市	洗衣机
qid002350	select 平台 , avg ( 总评分 ) from 洗衣机品牌平台评分 group by 平台	洗衣机
qid002351	select 平台 , sum ( 总评分 ) from 洗衣机品牌平台评分 group by 平台	洗衣机
qid002352	select 所属省份 , min ( 建交国家数量 ) from 城市 group by 所属省份	友好城市
qid002353	select 所属省份 , sum ( 建交国家数量 ) from 城市 group by 所属省份	友好城市
qid002354	select 营养成分 , max ( 含量 ) from 每100克坚果营养成分 group by 营养成分	坚果
qid002355	select 营养成分 , sum ( 含量 ) from 每100克坚果营养成分 group by 营养成分	坚果
qid002356	select 产品类别 , avg ( 售价 ) from 洗衣机型号 group by 产品类别	洗衣机
qid002357	select 产品类别 , min ( 售价 ) from 洗衣机型号 group by 产品类别	洗衣机
qid002358	select 季节 from 坚果季节性营业收入 group by 季节 having count ( * ) < 5	坚果
qid002359	select 系列名 from 综艺节目 group by 系列名 having count ( * ) < 5	综艺节目
qid002360	select 投资公司 from 投资公司 group by 投资公司 having avg ( 融资额 ) >= 1000000	企业融资
qid002361	select 城市 from 洗衣机品牌门店 group by 城市 having sum ( 门店数量 ) <= 500	洗衣机
qid002362	select 所属省份 from 城市 group by 所属省份 having count ( * ) > 15	友好城市
qid002363	select 产品类别 from 洗衣机型号 group by 产品类别 having count ( * ) == 5	洗衣机
qid002364	select 国家 from 坚果摄入量 group by 国家 having count ( * ) < 5	坚果
qid002365	select 朝代 from 都城 group by 朝代 having count ( * ) < 5	中国历史名城
qid002366	select 法定代表人 from 企业 group by 法定代表人 having avg ( 注册资本 ) <= 500000	企业融资
qid002367	select 类型 from 参考书 group by 类型 having count ( * ) < 5	教材辅助参考书
qid002368	select 出品公司 from 电视剧 group by 出品公司 having count ( * ) < 5	中国卫视频道
qid002369	select 所属省 from 一带一路的中国城市 group by 所属省 having count ( * ) > 5	友好城市
qid002370	select 国家 from 一带一路线路上的国家 group by 国家 having count ( * ) > 2	友好城市
qid002371	select 职位 from 人物公司职位 group by 职位 having count ( * ) >= 5	CCTV中国经济年度人物
qid002372	select 场上位置 from 篮球运动员 group by 场上位置 having avg ( 年龄 ) >= 30	运动员比赛记录
qid002373	select 平台 from 洗衣机品牌平台评分 group by 平台 having count ( * ) < 5	洗衣机
qid002374	select 所属省 from 对口帮扶城市 group by 所属省 having count ( * ) < 5	友好城市
qid002375	select 民族 from 明星 group by 民族 having count ( * ) >= 50	综艺节目
qid002376	select 性别 from 企业人物 group by 性别 having count ( * ) > 500	CCTV中国经济年度人物
qid002377	select 所属地区 from 球队 group by 所属地区 having avg ( 容纳人数 ) < 8000	欧洲杯球队
qid002378	select 产地 from 坚果产地 group by 产地 having count ( * ) <= 5	坚果
qid002379	select 所属洲 from 国家 group by 所属洲 having count ( * ) > 5	奥运会参赛队伍
qid002380	select 作者 from 图书 group by 作者 having count ( * ) <= 5	购书平台
qid002381	select 所属省份 from 城市 group by 所属省份 having count ( * ) >= 15	中国历史名城
qid002382	select 融资轮次 from 企业融资 group by 融资轮次 having avg ( 融资总额 ) <= 10000000	企业融资
qid002383	select 城市 from 打车软件开通城市 group by 城市 having count ( * ) == 5	打车软件
qid002384	select 所属公司 from 洗衣机品牌 group by 所属公司 having count ( * ) < 5	洗衣机
qid002385	select 城市 from 软件对租车的支持 group by 城市 having count ( * ) < 5	打车软件
qid002386	select 发生城市 from 美国近几年校园枪击事件 group by 发生城市 having sum ( 受影响学生数量 ) > 100000	枪击事件
qid002387	select 举办城市 from 夏季奥运会 group by 举办城市 having avg ( 参赛国家数量 ) == 180	奥运会参赛队伍
qid002388	select 类别 from 高校 group by 类别 having count ( * ) <= 5	中国高校
qid002389	select 奖项名称 from 历届经济人物获奖名单 group by 奖项名称 having count ( * ) >= 5	CCTV中国经济年度人物
qid002390	select 国家 , sum ( 人均摄入量 ) from 坚果摄入量 group by 国家 having count ( * ) >= 5	坚果
qid002391	select 国家 , sum ( 人均摄入量 ) from 坚果摄入量 group by 国家 having count ( * ) == 5	坚果
qid002392	select 法定代表人 , sum ( 注册资本 ) from 企业 group by 法定代表人 having count ( * ) == 5	企业融资
qid002393	select 法定代表人 , sum ( 注册资本 ) from 企业 group by 法定代表人 having count ( * ) < 5	企业融资
qid002394	select 球队 , max ( 出场次数 ) from 比赛记录 group by 球队 having count ( * ) == 5	运动员比赛记录
qid002395	select 类型 , min ( 适用年级 ) from 参考书 group by 类型 having count ( * ) > 5	教材辅助参考书
qid002396	select 类型 , min ( 适用年级 ) from 参考书 group by 类型 having count ( * ) == 5	教材辅助参考书
qid002397	select 所属地区 , min ( 容纳人数 ) from 球队 group by 所属地区 having count ( * ) <= 5	欧洲杯球队
qid002398	select 所属地区 , avg ( 容纳人数 ) from 球队 group by 所属地区 having count ( * ) <= 5	欧洲杯球队
qid002399	select 所属公司 , max ( 市场份额 ) from 洗衣机品牌 group by 所属公司 having count ( * ) == 5	洗衣机
qid002400	select 所属公司 , avg ( 2018年营业额 ) from 洗衣机品牌 group by 所属公司 having avg ( 市场份额 ) < 1000000	洗衣机
qid002401	select 季节 , avg ( 全年占比 ) from 坚果季节性营业收入 group by 季节 having avg ( 营业收入 ) > 2000000	坚果
qid002402	select 投资公司 , max ( 投资公司持股比例 ) from 投资公司 group by 投资公司 having sum ( 融资额 ) >= 100000000	企业融资
qid002403	select 所属公司 , max ( 服务用户数量 ) from 打车APP group by 所属公司 having avg ( 覆盖城市数 ) > 100	打车软件
qid002404	select 举办城市 , avg ( 参赛运动员数量 ) from 夏季奥运会 group by 举办城市 having sum ( 参赛国家数量 ) >= 100	奥运会参赛队伍
qid002405	select 举办城市 , max ( 参赛国家数量 ) from 夏季奥运会 group by 举办城市 having count ( * ) < 5	奥运会参赛队伍
qid002406	select 场上位置 , avg ( 年龄 ) from 篮球运动员 group by 场上位置 having count ( * ) == 5	运动员比赛记录
qid002407	select 城市 , avg ( 门店数量 ) from 洗衣机品牌门店 group by 城市 having count ( * ) > 5	洗衣机
qid002408	select 平台 , avg ( 总评分 ) from 洗衣机品牌平台评分 group by 平台 having count ( * ) >= 5	洗衣机
qid002409	select 平台 , min ( 功能得分 ) from 洗衣机品牌平台评分 group by 平台 having sum ( 总评分 ) > 7	洗衣机
qid002410	select 所属省份 , avg ( 国外驻华大使馆数量 ) from 城市 group by 所属省份 having sum ( 建交国家数量 ) >= 70	友好城市
qid002411	select 所属省份 , max ( 国外驻华大使馆数量 ) from 城市 group by 所属省份 having sum ( 建交国家数量 ) > 70	友好城市
qid002412	select 产品类别 , max ( 售价 ) from 洗衣机型号 group by 产品类别 having count ( * ) <= 5	洗衣机
qid002413	select 产品类别 , min ( 售价 ) from 洗衣机型号 group by 产品类别 having count ( * ) == 5	洗衣机
qid002414	select 季节 from 坚果季节性营业收入 group by 季节 order by sum ( 营业收入 ) desc limit 1	坚果
qid002415	select 出品公司 from 电视剧 group by 出品公司 order by count ( * ) limit 3	中国卫视频道
qid002416	select 系列名 from 综艺节目 group by 系列名 order by count ( * ) desc limit 3	综艺节目
qid002417	select 系列名 from 综艺节目 group by 系列名 order by count ( * ) asc limit 1	综艺节目
qid002418	select 国家 from 一带一路线路上的国家 group by 国家 order by count ( * ) asc limit 1	友好城市
qid002419	select 国家 from 一带一路线路上的国家 group by 国家 order by count ( * ) desc limit 1	友好城市
qid002420	select 城市 from 洗衣机品牌门店 group by 城市 order by avg ( 门店数量 ) desc limit 1	洗衣机
qid002421	select 城市 from 洗衣机品牌门店 group by 城市 order by sum ( 门店数量 ) asc limit 1	洗衣机
qid002422	select 所属省份 from 城市 group by 所属省份 order by sum ( 建交国家数量 ) asc limit 1	友好城市
qid002423	select 所属省份 from 城市 group by 所属省份 order by avg ( 建交国家数量 ) desc limit 5	友好城市
qid002424	select 营养成分 from 每100克坚果营养成分 group by 营养成分 order by avg ( 含量 ) desc limit 5	坚果
qid002425	select 营养成分 from 每100克坚果营养成分 group by 营养成分 order by sum ( 含量 ) asc limit 3	坚果
qid002426	select 产品类别 from 洗衣机型号 group by 产品类别 order by avg ( 售价 ) asc limit 1	洗衣机
qid002427	select 产品类别 from 洗衣机型号 group by 产品类别 order by avg ( 售价 ) desc limit 3	洗衣机
qid002428	select 朝代 from 都城 group by 朝代 order by count ( * ) desc limit 1	中国历史名城
qid002429	select 朝代 from 都城 group by 朝代 order by count ( * ) asc limit 1	中国历史名城
qid002430	select 法定代表人 from 企业 group by 法定代表人 order by count ( * ) desc limit 1	企业融资
qid002431	select 法定代表人 from 企业 group by 法定代表人 order by sum ( 注册资本 ) desc limit 1	企业融资
qid002432	select 类型 from 参考书 group by 类型 order by avg ( 适用年级 ) desc limit 1	教材辅助参考书
qid002433	select 类型 from 参考书 group by 类型 order by avg ( 适用年级 ) asc limit 1	教材辅助参考书
qid002434	select 所属省 from 一带一路的中国城市 group by 所属省 order by count ( * ) asc limit 2	友好城市
qid002435	select 所属省 from 一带一路的中国城市 group by 所属省 order by count ( * ) desc limit 1	友好城市
qid002436	select 职位 from 人物公司职位 group by 职位 order by count ( * ) asc limit 1	CCTV中国经济年度人物
qid002437	select 职位 from 人物公司职位 group by 职位 order by count ( * ) desc limit 3	CCTV中国经济年度人物
qid002438	select 场上位置 from 篮球运动员 group by 场上位置 order by sum ( 年龄 ) desc limit 1	运动员比赛记录
qid002439	select 场上位置 from 篮球运动员 group by 场上位置 order by avg ( 年龄 ) desc limit 1	运动员比赛记录
qid002440	select 所属省 from 对口帮扶城市 group by 所属省 order by count ( * ) desc limit 3	友好城市
qid002441	select 所属省 from 对口帮扶城市 group by 所属省 order by count ( * ) asc limit 3	友好城市
qid002442	select 平台 from 洗衣机品牌平台评分 group by 平台 order by sum ( 总评分 ) desc limit 1	洗衣机
qid002443	select 平台 from 洗衣机品牌平台评分 group by 平台 order by avg ( 总评分 ) desc limit 1	洗衣机
qid002444	select 民族 from 明星 group by 民族 order by count ( * ) desc limit 1	综艺节目
qid002445	select 民族 from 明星 group by 民族 order by count ( * ) limit 3	综艺节目
qid002446	select 性别 from 企业人物 group by 性别 order by avg ( 年龄 ) asc limit 1	CCTV中国经济年度人物
qid002447	select 所属地区 from 球队 group by 所属地区 order by sum ( 容纳人数 ) asc limit 1	欧洲杯球队
qid002448	select 所属地区 from 球队 group by 所属地区 order by count ( * ) asc limit 1	欧洲杯球队
qid002449	select 产地 from 坚果产地 group by 产地 order by avg ( 市场占比 ) asc limit 1	坚果
qid002450	select 产地 from 坚果产地 group by 产地 order by avg ( 市场占比 ) asc limit 5	坚果
qid002451	select 所属洲 from 国家 group by 所属洲 order by count ( * ) asc limit 1	奥运会参赛队伍
qid002452	select 所属洲 from 国家 group by 所属洲 order by count ( * ) desc limit 2	奥运会参赛队伍
qid002453	select 投资公司 from 投资公司 group by 投资公司 order by sum ( 融资额 ) asc limit 1	企业融资
qid002454	select 投资公司 from 投资公司 group by 投资公司 order by avg ( 融资额 ) asc limit 1	企业融资
qid002455	select 作者 from 图书 group by 作者 order by count ( * ) asc limit 1	购书平台
qid002456	select 作者 from 图书 group by 作者 order by count ( * ) desc limit 3	购书平台
qid002457	select 球队 , min ( 罚球 ) from 比赛记录 group by 球队 order by sum ( 出场次数 ) desc limit 1	运动员比赛记录
qid002458	select 球队 , sum ( 出场次数 ) from 比赛记录 group by 球队 order by count ( * ) asc limit 1	运动员比赛记录
qid002459	select 球队 , avg ( 出场次数 ) from 比赛记录 group by 球队 order by count ( * ) desc limit 1	运动员比赛记录
qid002460	select 球队 , min ( 防守 ) from 比赛记录 group by 球队 order by avg ( 出场次数 ) desc limit 1	运动员比赛记录
qid002461	select 球队 , avg ( 出场次数 ) from 比赛记录 group by 球队 order by count ( * ) asc limit 1	运动员比赛记录
qid002462	select 类型 , min ( 价格 ) from 参考书 group by 类型 order by avg ( 适用年级 ) asc limit 5	教材辅助参考书
qid002463	select 类型 , min ( 价格 ) from 参考书 group by 类型 order by avg ( 适用年级 ) desc limit 5	教材辅助参考书
qid002464	select 类型 , avg ( 适用年级 ) from 参考书 group by 类型 order by count ( * ) asc limit 1	教材辅助参考书
qid002465	select 类型 , sum ( 适用年级 ) from 参考书 group by 类型 order by count ( * ) asc limit 1	教材辅助参考书
qid002466	select 融资轮次 , max ( 融资总额 ) from 企业融资 group by 融资轮次 order by count ( * ) desc limit 1	企业融资
qid002467	select 融资轮次 , sum ( 融资总额 ) from 企业融资 group by 融资轮次 order by count ( * ) asc limit 1	企业融资
qid002468	select 融资轮次 , avg ( 融资总额 ) from 企业融资 group by 融资轮次 order by count ( * ) asc limit 1	企业融资
qid002469	select 所属地区 , sum ( 容纳人数 ) from 球队 group by 所属地区 order by count ( * ) asc limit 1	欧洲杯球队
qid002470	select 所属地区 , max ( 容纳人数 ) from 球队 group by 所属地区 order by count ( * ) asc limit 1	欧洲杯球队
qid002471	select 所属地区 , avg ( 容纳人数 ) from 球队 group by 所属地区 order by count ( * ) desc limit 1	欧洲杯球队
qid002472	select 所属地区 , avg ( 容纳人数 ) from 球队 group by 所属地区 order by count ( * ) asc limit 1	欧洲杯球队
qid002473	select 城市 , avg ( 占所在城市份额 ) from 打车软件开通城市 group by 城市 order by count ( * ) asc limit 1	打车软件
qid002474	select 城市 , sum ( 占所在城市份额 ) from 打车软件开通城市 group by 城市 order by count ( * ) desc limit 1	打车软件
qid002475	select 城市 , sum ( 占所在城市份额 ) from 打车软件开通城市 group by 城市 order by count ( * ) asc limit 1	打车软件
qid002476	select 所属公司 , avg ( 2018年利润 ) from 洗衣机品牌 group by 所属公司 order by sum ( 市场份额 ) asc limit 1	洗衣机
qid002477	select 所属公司 , avg ( 市场份额 ) from 洗衣机品牌 group by 所属公司 order by count ( * ) asc limit 1	洗衣机
qid002478	select 所属公司 , max ( 2018年利润 ) from 洗衣机品牌 group by 所属公司 order by sum ( 市场份额 ) desc limit 1	洗衣机
qid002479	select 所属公司 , sum ( 2018年利润 ) from 洗衣机品牌 group by 所属公司 order by sum ( 市场份额 ) asc limit 1	洗衣机
qid002480	select 发生城市 , avg ( 受影响学生数量 ) from 美国近几年校园枪击事件 group by 发生城市 order by count ( * ) desc limit 1	枪击事件
qid002481	select 产地 , sum ( 市场占比 ) from 坚果产地 group by 产地 order by count ( * ) desc limit 1	坚果
qid002482	select 产地 , max ( 市场占比 ) from 坚果产地 group by 产地 order by count ( * ) asc limit 1	坚果
