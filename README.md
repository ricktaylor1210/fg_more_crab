# fg_more_crab

网易版 Bedrock 更多螃蟹玩法包，当前重点是把普通生态螃蟹、捕蟹笼、矿物螃蟹、海盗螃蟹、料理装备、负重背包和 Boss 终局线接成可测试闭环。

## 当前实现概览

- 普通生态螃蟹：7 个正式生态变体已接入行为包、资源包、生成与掉落。
- 捕蟹笼：5 个品质的实体版玩法已接入，支持物品放置、诱饵、收获、破坏概率、水面可收获浮起和陆地低效捕获。
- 矿物螃蟹：9 个独立矿物实体已接入，服务端脚本负责靠近匹配矿石、吃矿和触发类型化 Buff。
- 海盗螃蟹：3 个职业实体已接入，服务端脚本负责偷窃、逃跑、返还、集结和海岸藏身处补刷。
- 料理、基础装备、负重背包、Boss 展示级巢穴 / 神庙、Boss P2/P3 场地机制、宝箱经济和 Boss 装备链已有 TASK-01~15 主线静态闭环；负重背包装备、打开、27 格容器、标题和卸下保护已实机可用，盾牌手感、结构放置、Boss 机制和主动技能仍需网易客户端集中实机验收。

## 文档入口

- `docs/01_mobs_and_ecology.md`：生物生态与定位总览。
- `docs/02_crab_normal_variant_design.md`：普通生态螃蟹设计。
- `docs/03_crab_mineral_variant_design.md`：矿物螃蟹设计与当前落地方式。
- `docs/04_systems_and_mechanics.md`：驯服、负重、捕蟹笼和 Boss 框架。
- `docs/05_items_and_equipment.md`：料理、基础装备和 Boss 装备目标设计。
- `docs/06_worldgen_and_bosses.md`：结构、巢穴和 Boss 规划。
- `docs/07_dev_roadmap.md`：路线图与任务状态。
- `docs/TASK_01_15_acceptance_checklist.md`：TASK-01~15 集中实机验收清单。
- `docs/TASK_01_15_regression_guide.md`：TASK-01~15 实机回归执行文档。
- `docs/crab_showcase.md`：当前可展示行为、概率和玩家说明。
- `docs/project_progress_analysis.md`：当前静态进度审查。
