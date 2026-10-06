# 0.11.0 范围与测试覆盖 只读审查

只读；**未改代码/INI/模组包，未运行游戏，未采集数据，未操作窗口**。
来源：主工作区 `work/seat_configurable_network_test/{adapter,dispatcher,probe,README_English}.lua/txt`、`test_{integrated_input,dispatcher,dynamic_probe}.lua`；`work/seat_switch/src/{policy,config,input}.lua`
（`README_中文.txt` 在本机为编码损坏，**改用同目录 `README_English.txt`** 核对，行号取该文件。）

---

## 1. M-102 座位 0–4 的 20 个有向方向

**座位编号 = 原生索引**（`policy.lua` `M.seats.m102` 顺序：0 driver／1 front_passenger／2 rear_left／3 rear_right／4 gunner），**不使用 roles 数组**。
**原生邻接**（已核定：m102 表为 `0↔1`、`2↔3`，**4 无邻居**）：普通原生路线仅 4 条。

| 源→目标 | 类别 | 源→目标 | 类别 | 源→目标 | 类别 | 源→目标 | 类别 |
|---|---|---|---|---|---|---|---|
| 0→1 | **原生** | 1→2 | 跨区 | 2→3 | **原生** | 3→4 | 跨区 |
| 0→2 | 跨区 | 1→3 | 跨区 | 2→4 | 跨区 | 4→0 | 跨区 |
| 0→3 | 跨区 | 1→4 | 跨区 | 3→0 | 跨区 | 4→1 | 跨区 |
| 0→4 | 跨区 | 2→0 | 跨区 | 3→1 | 跨区 | 4→2 | 跨区 |
| 1→0 | **原生** | 2→1 | 跨区 | 3→2 | **原生** | 4→3 | 跨区 |

**合计：原生 4（0↔1、2↔3），跨区 16。** 跨区判定依据 `dispatcher.lua:59` 用 `policy.check('normal',…)`（普通版分组即原生邻接分量）；不命中即走跨区分支（`:68` 起）。

---

## 2. 跨区：两种情形是否允许

| 情形 | 代码判定 | 允许的跨区方向 | 驾驶位 |
|---|---|---|---|
| **本人持车、朋友车外** | `adapter.lua:17` `borrowed=false` → 走 `:22-32` | {1,2,3,4} 之间**任意跨区**；**含目标 0 与源 0**（源 0 需本机就是驾驶员 `:29-30`；源≠0 时驾驶位必须**空**，否则 `:31` `driver_seat_must_remain_empty`） | 目标 0 **允许**（前提：`occupied[0]==false`，`:35`）；他人占驾驶位 → 拒绝 |
| **朋友驾驶、暂借归还** | `:17` `borrowed=true` → 走 `:18-21` | 仅 {1,2,3,4} 之间跨区 | **`:19` 源或目标为 0 一律拒绝** `borrowed_driver_target_not_enabled`；且 `:20` 要求朋友**始终**是驾驶员 |

**驾驶位被占须始终拒绝** —— 代码层面成立，但需精确区分：
- 借用路径：`adapter.lua:19` 直接拒绝（源、目标两个方向都拒绝）
- 本人持车路径：**他人**占驾驶位 → `:31` 拒绝；**本机自己**是驾驶员 → `:29-30` **允许从 0 换出**（0.10.5 的"驾驶位跨区"即此路径）

---

## 3. README 的 A/B 与实际条件比对

| README（`README_English.txt`） | 代码 | 结论 |
|---|---|---|
| L17/L19 Run1「you host」、L25 Run2「friend drives」 | `adapter.lua:17` `borrowed = (ticket and not ticket.local_authority) or (not ticket and not owned)`；`:63` `local_authority = owner==selfpeer` | **一致**：本人持有 → `borrowed=false`（=A）；朋友持有 → `true`（=B） |
| L19「friend stays outside throughout」 | `:26` `friend_must_remain_outside`；`:28` `one_remote_avatar_required` | **一致** |
| L39「installer-owned chassis with friend already aboard is not enabled」 | `:26` | **一致** |
| L39「Borrowed path **cannot target** driver」 | `:19` 拒绝 **`source==0` 或 `target==0`** | **措辞差异（非行为矛盾）**：代码比 README 多拒一个方向。因 `:20` 要求朋友是驾驶员，借用路径下本机不可能坐 0，故实际不可达 —— **最小反例不可构造**，仅建议 README 补"从驾驶位换出亦拒绝" |
| L30「press your driver binding once. It must refuse」 | `probe.lua:114` → `eligible` → `:19` → `event('trigger_rejected')` | **一致** |
| L39「local authority is not proactively handed away」 | `probe.lua:40-41`「This operation never borrowed authority. Never enter grant/return recovery.」；`adapter.lua:95` `assert(not t.local_authority …)` | **一致** |
| L13「waits for release and at least **3s** stability, expires after **8s**」 | `dispatcher.lua:43` `now-q.started>8`；`probe.lua:112,123` `now-stable_since<3` | **一致** |
| L13「**10s** post-completion cooldown」 | 本轮抽取**未捕获到该赋值行**（只见到 `cooldown` 的初始化与 `now<cooldown` 判断） | **需核对**，不写成已确认 |
| L8「Ctrl+Shift+Home no longer runs a fixed sequence」 | `dispatcher.lua` 全文**无** 1316；键全部来自 INI（`:33-34`） | **一致**（本轮已核 `dispatcher.lua` 78 行） |

---

## 4. 三个新测试能证明什么／不能证明什么

| 文件 | 能证明 | **不能证明** |
|---|---|---|
| `test_integrated_input.lua`（53 行／9 asserts／0 mocks） | 加载**真实** `input.lua` + dispatcher/probe/adapter，断言 7 步原生／跨区路线在**两种上下文**下走通、清理次数精确（`mutations==6 and sends==6 and natives==1 and probe.count==6`） | 其首行自述 **"engine/RPC effects are simulated"** → 引擎效果与 RPC 为模拟；**不证明**联网可达、远端渲染 |
| `test_dispatcher.lua`（43 行／33 asserts／0 mocks） | 真实 dispatcher + 合成按键集合：**同帧两键 `{113,116}` → `multiple_seat_keys`**；`{162,160,5}`（RCTRL+LSHIFT+MOUSE4）先排队后放行；占用导致队列取消；`probe.phase=='stopped'` 亦阻断普通输入；非 m102 不排队；`ready_at` 未到保持排队 | 按键为**合成集合**，非物理设备；`native`/网络为桩 → **不证明**物理组合键全覆盖、不证明实机 |
| `test_dynamic_probe.lua`（27 行／8 asserts／0 mocks） | **任意目标含 driver0、超过六次操作**、本机与借用两种清理、完成后换车有效、待处理身份变化被拒 | 同上为逻辑级；**不证明**远端视觉与网络接受 |

> 三者合计 **50 个断言、0 处 mock 关键字**（`mocks=0` 指未出现 mock/stub/fake 标识），但 `native`/`probe`/`owner_reader` 仍由测试提供替身 —— **不等于网络实机**，也**不声称已覆盖所有物理组合键**。

---

## 5. 五项特别区分

1. **两个不同主键可能同一帧按下；`overlap=false` ≠ 不会同时触发。**
   `config.lua:62` 的 `overlap` 只用于**分配期**判断"同一车辆内两个座位键是否会被同一次物理输入共同满足"（`config.lua:106`）；它**管不到**用户在同帧按下两个键。后者由 `dispatcher.lua:35-38` 兜住：遍历时若 `target` 已非 nil → `event('multiple_seat_keys')` 并返回。`test_dispatcher.lua` 用 `{113,116}` 断言了该拒绝。→ **已防止，但机制在 dispatcher，不在 `overlap`。**
2. **排队等松键 ≠ 排队第二次换座。**
   `dispatcher.lua:71` 的 `self.queued` 只保存**同一次**跨区请求等待松键；`:42` 一旦有新键 `cancelled_by_new_key` 并清空；`:20-21` 网络 pending 期间 `self.queued=nil`；`:43` 超 8s／身份变／目标被占 → `release_wait_cancelled`。→ **不存在第二次换座排队**（与 README L14「no queued second switch」一致）。
3. **同帧多键**：见 #1；`:36` 仅在**同一车辆**的座位键集合内检测。
4. **借用路径清理不依赖焦点/个人座位仍存在。**
   `adapter.lua:101-102` 注释「Recovery may run after local exit/read failure; **never require a local seat**」；`return_owned`（`:94-107`）**未**调用 `quiet()`（对比 `request` 在 `:70-71` 断言 `api.input_allowed()` 与松开移动/开火键）。→ **归还不依赖焦点**；`probe.lua:64` 的焦点取消只作用于**获得授权前**的阶段，`:92-102` 归还分支不再检查焦点。
5. **`eligible` 的角色**：`probe.lua:114` 在**每次 step** 用 `target` 调 `eligible`，`adapter.lua:33` 用 `ticket` 复核**座位**与身份（`:36`）。→ 它是**持续复核**，不是"发出归还的前提"；归还前提在 `adapter.lua:100`（`return_owner_not_ready`）。

---

## 6. 结论（不实现修复、不生成 RPC 方案、不要求采集）

- **范围**：0.11.0 覆盖 双人 M-102 的 20 个方向中 **原生 4 + 跨区 16（按上下文分允许/拒绝）**；其余车型仅普通路线（README L40 与 `adapter.lua:10` `M102_only` 一致）。
- **测试**：三个新测试证明的是**输入与仲裁逻辑**（含同帧多键、松键队列、任意目标、无六次上限）；**均不证明网络实机**。
- **明确矛盾**：**未发现行为级矛盾**；仅 README L39 措辞少列"从驾驶位换出亦被拒"（`adapter.lua:19`），实际不可达，属措辞建议。
- **待核对项**：README L13 的 **10s 完成后冷却**赋值行本轮未捕获。

*仅写入本副本 `outputs/DEEPSEEK_UNIFIED_INPUT_BOUNDARIES_20261001.md`。*
