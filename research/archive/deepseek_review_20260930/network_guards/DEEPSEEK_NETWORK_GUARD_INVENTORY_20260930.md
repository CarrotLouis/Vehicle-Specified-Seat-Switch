# 代码核对清单 — 房主/客机整合前的网络守卫盘点

只读核对；**未设计新换座方案、未启动游戏、未采集数据、未改 GPT 代码/游戏/Arsenal/配置**。
本次只读来源（逐行核对）：

- `work/seat_rear_weapon_diagnostic/adapter.lua`、`observe.lua`、`probe.lua`、`sender.lua`、`entry.lua`（**当前代码**）
- `work/seat_integrated_diagnostic/adapter.lua`、`observe.lua`、`probe.lua`、`sender.lua`（**旧实验**，用于区分）

约束对象缩写：**人**=人数 · **房**=房主身份 · **有**=车辆实际所有者 · **驾**=驾驶员身份 · **本**=本地角色所有者 · **座**=座位范围/占用

---

## 1–3. 守卫清单

时机列：**开始**=发起换座时（`request` / 无 ticket 的 `eligible`）；**借后**=已获得权限（`owned=true`）；**同步前**=`execute` 内 `sender:prepare` 之后的发送守卫；**归还**=`return_owned` / `probe` 归还分支。

| # | 文件:行 | 原始条件（代码原文摘要） | 约束 | 检查时机 | 当前允许 / 拒绝的具体情形（仅按代码） |
|---|---|---|---|---|---|
| 1 | `rear_weapon/adapter.lua:11` | `sample.player_count~=2 or sample.local_count~=1 or s.player_count~=2 or s.peer_count~=2 or o.peer_count~=2` → `two_players_required` | **人** | 开始·借后·同步前·归还（`eligible` 在各阶段均被调用） | 房间恰为 2 人且本机 1 个本地角色 → 允许；3–4 人、或本机多角色 → 拒绝 |
| 2 | `adapter.lua:12` | `o.coordinator==o.selfpeer or c.destination~=o.coordinator or not o.members[c.destination]` → `friend_must_host` | **房** + 唯一远端 | 开始·借后·同步前·归还 | 安装者是客机、协调者（房主）恰为唯一远端且在成员表内 → 允许；**安装者自己当房主 → 拒绝** |
| 3 | `adapter.lua:13-14` | `expected=owned and o.selfpeer or c.destination`；`o.owner~=expected or s.owned~=owned or o.vehicle.owned_local~=owned or o.busy` → `ownership_not_ready` | **有** | 开始（`owned=false`）·借后（`owned=true`）·归还 | 开始时车辆须由**远端持有**；借后须由**本机持有**；`owned_local` 与 `s.owned` 须与阶段一致且非 busy → 否则拒绝 |
| 4 | `adapter.lua:15` | `not c.avatar or not c.avatar.is_local or not c.avatar.owned_local or not o.avatars[s.avatar] or o.avatars[s.avatar].owner~=o.selfpeer` → `avatar_owner_unconfirmed` | **本** | 开始·借后·同步前·归还 | 本地角色存在、`owned_local`、且引擎记录里归属本机 → 允许；归属不可确认 → 拒绝 |
| 5 | `adapter.lua:17` | `not c.driver or c.driver.is_local or not seated(c.driver,o.vehicle,0,1) or not o.avatars[c.driver.id] or o.avatars[c.driver.id].owner~=c.destination` → `friend_must_remain_driver` | **驾** + 非驾驶座 | 开始·借后·同步前·归还 | **远端角色坐在 node 0 / role 1（驾驶）且其记录归属远端** → 允许；**本机自己当驾驶员 → 拒绝**；远端换到非驾驶座 → 拒绝 |
| 6 | `adapter.lua:18-19` | `destination` 取 `target` 或 ticket 推导；`destination<1 or >4 or %1~=0 or ==source` → `invalid_experiment_target` | **座** | 开始（与带 ticket 的复查） | 目标座位索引在 **1..4** 且不等于当前座位 → 允许；越界/非整数/原地 → 拒绝 |
| 7 | `adapter.lua:20` | `s.occupied[destination]~=false` → `target_occupied_or_reserved` | **座** | 开始·借后·同步前 | 目标座位未被占用/预留 → 允许 |
| 8 | `adapter.lua:21` | `c.identity~=ticket.identity or s.identity~=ticket.avatar_binding or c.driver.id~=ticket.driver_id or c.driver.unit~=ticket.driver_unit` → `operation_identity_changed` | **本**+**驾**+会话 | 借后·同步前·归还 | 身份/角色绑定/驾驶者 id 与 unit 与 ticket 一致 → 允许；否则拒绝 |
| 9 | `observe.lua:168` | `fresh.context/owner/record_word0/1/serial` 与先前一致且 `not fresh.busy`（否则 `authority_*` 族断言） | **有**+会话 | 同步前（`send` 内） | 借用前后序列与记录字未变且非忙 → 允许 |
| 10 | `observe.lua:169` | `fresh.owner==destination` → `authority_send_requires_current_owner_destination` | **有** | 同步前 | 车辆当前持有者恰为发送目标 → 允许 |
| 11 | `observe.lua:170,183` | `fresh.members[destination] and fresh.members[target]` → `authority_send_peer_left` | **人**（第三人） | 同步前·归还 | 发送目标与目标座位相关端仍在成员表 → 允许；**对端离开 → 拒绝** |
| 12 | `observe.lua:172` | `s.player_count==2 and s.local_count==1 and fresh.peer_count==2 and fresh.coordinator==destination` → `authority_send_room_changed` | **人**+**房** | 同步前 | 房间仍为 2 人、本机 1 角色、协调者=对端 → 允许 |
| 13 | `observe.lua:176,180` | `a.is_local and seat.current in 1..4 and seat.reserved==seat.current and seat.role==(seat.current==4 and 2 or 3) and peer.owner==o.selfpeer` → `authority_send_seats_changed` | **本**+**座** | 同步前 | 本机角色位于 1..4 且**座位 4 视为角色 2（武器位）、1–3 视为角色 3** → 允许。**此角色映射按 m102 布局写死** |
| 14 | `observe.lua:177,180` | `not a.is_local and seat.current==0 and seat.reserved==0 and seat.role==1 and peer.owner==destination` | **驾**+非驾驶座 | 同步前 | 远端在 node 0、reserved 0、role 1 → 允许 |
| 15 | `observe.lua:185` | `stable(o.engine+0x20,8)==o.selfpeer` → `authority_send_identity_changed` | **本** | 同步前 | 本机 peer 与引擎记录一致 → 允许 |
| 16 | `observe.lua:126,133` | 协调者 getter 字节指纹 `\72\139\129\48\1\0\0\195`；`session+0xb3a8==coordinator` → `authority_coordinator_getter_changed` / `authority_coordinator_disagrees` | **房** | 每次 capture | 协调者来源与取值均可核 → 允许 |
| 17 | `observe.lua:134-137` | `n>=1 and n<=4`（`authority_peer_count`）；无重复 peer（`authority_duplicate_peer`）；`members[selfpeer] and members[coordinator]`（`authority_peer_missing`） | **人** | 每次 capture | 成员数 1..4、无重复、含本机与协调者 → 允许 |
| 18 | `sender.lua:27` | `destination~=o.selfpeer and o.members[destination] and o.owner==o.selfpeer and not o.busy` → `sync_sender_peer_or_owner` | **有**+唯一远端 | 同步前（`sender:prepare`） | 目标非本机、在成员表、车辆由本机持有、非忙 → 允许 |
| 19 | `sender.lua:41` | `read(o.engine+0x20,8)==o.selfpeer` → `sync_identity_changed` | **本** | 同步前 | 身份一致 → 允许 |
| 20 | `probe.lua:34` | `o.owner==ticket.selfpeer and o.vehicle.owned_local and not o.busy` | **有** | 借后（等待授权落地） | 借用已生效（本机持有且非忙）→ 进入切换 |
| 21 | `probe.lua:50` | `o.owner~=ticket.original and o.owner~=ticket.selfpeer` → `stop('unexpected_owner_before_grant')` | **有** | 借后（授权前） | 持有者既非原主亦非本机 → **停止** |
| 22 | `probe.lua:54` | `o.owner==ticket.original and not o.vehicle.owned_local and not o.busy`（+稳定窗口） | **有** | 归还 | 已回到原主且本机不再持有 → 记归还确认 |
| 23 | `probe.lua:69` | `o.owner~=ticket.selfpeer and o.owner~=ticket.original` → `stop('unexpected_owner_after_grant')` | **有** | 归还前 | 授权后持有者异常 → **停止** |

---

## 4. 清理/归还 与 新操作准入 的区分

**负责清理归还（不得与新操作准入混同）**：

- `adapter.lua:51`（旧路径 `:49`）`self:context(c,t)`：`c.identity==t.identity and c.owner.selfpeer==t.selfpeer and c.owner.members[t.original]` —— **归还上下文**，仅要求原主仍在成员表，**不重跑准入**
- `adapter.lua:81-89` 归还断言：`o.owner==t.selfpeer and o.vehicle.owned_local and not o.busy`（`return_owner_not_ready`）；`not driver.is_local and driver.id==t.driver_id and driver.unit==t.driver_unit`（`return_driver_changed`）；`o.avatars[driver.id].owner==t.original`（`return_driver_owner_changed`）；随后 `owner_reader:send(o,t.selfpeer,t.original,…)`
- `adapter.lua:40` 注释原文：**"Additional peers cancel switching but must not prevent return to the original owner."** —— 明确把「第三人加入」与「归还」分开
- `probe.lua:54`、`probe.lua:69`：归还分支与其异常停止分支
- `observe.lua:163-188` 的 `authority_send_*` 属**发送前复查**（同步前 + 归还方向复用），与准入判定同源但**独立于** `M.eligible`

**旧代码已处理、新代码沿用的边界情形**（同一谱系；行号已核到函数级，reason 字符串在 `probe.lua` 的 `cancel/stop/note` 辅助中）：

| 情形 | 处理位置 | 机制 |
|---|---|---|
| **迟到授权** | `probe.lua`（`cancel`/`note` 分支） | `grant_timeout; keep_monitoring_late_grant` → `late_grant` / `monitoring_late_grant_without_switch`；**观察超时不盲发归还** |
| **第三人加入** | `adapter.lua:11`、`:40`、`observe.lua:170,183` | 准入拒绝 `two_players_required`；但归还仍允许（见上） |
| **焦点丢失** | `probe.lua`（`focus_or_input_blocked`） | 失焦即取消，不执行切换 |
| **会话/身份改变** | `adapter.lua:21`、`observe.lua:168`、`probe.lua:50,69` | `operation_identity_changed` / 序列字变化 / `unexpected_owner_*` → 停止 |
| **归还未确认** | `probe.lua`（`return_not_confirmed; no_resend; keep_monitoring`、`waiting_busy_clear_before_return`） | 不重发，持续监控 |

---

## 5. 硬编码位置（供后续改造，不作删守卫建议）

| 硬编码项 | 位置 | 原文要点 |
|---|---|---|
| **恰好 2 人 / 本机 1 角色** | `rear_weapon/adapter.lua:11`；`observe.lua:172`；`observe.lua:134`（`n>=1 and n<=4` 为捕获范围） | `player_count~=2`、`local_count~=1`、`peer_count~=2` |
| **唯一远端** | `rear_weapon/adapter.lua:34`（`n~=1` 则 `dest=nil`）；`adapter.lua:12`；`sender.lua:27` | `for peer in pairs(o.members) … n=n+1`；`destination~=o.coordinator` |
| **朋友房主** | `adapter.lua:12`（`friend_must_host`）；`observe.lua:133,172` | `o.coordinator==o.selfpeer` 即**安装者自己是房主 → 拒绝** |
| **朋友驾驶** | `adapter.lua:17`（`friend_must_remain_driver`）；`observe.lua:177` | `c.driver.is_local` → 拒绝；远端须 `node 0 / role 1` |
| **非驾驶座（本机不得坐驾驶）** | `adapter.lua:17`、`observe.lua:176` | 本机角色须在 `1..4`（`observe` 旧版为 `1..2`） |
| **目标座位 1..4** | `adapter.lua:18-19` | `destination<1 or >4` → `invalid_experiment_target` |
| **m102 专属角色映射** | `observe.lua:176` | `seat.role==(seat.current==4 and 2 or 3)` |
| **旧实验专用的 1↔2 双座** | `integrated/adapter.lua:46` | `target=3-c.seat`（**仅旧代码**） |
| **旧实验的座位 1..2 校验** | `integrated/observe.lua:176` | `seat.current==1 or seat.current==2`（**仅旧代码**） |

**当前 vs 旧的分界**：`seat_rear_weapon_diagnostic` 的目标范围已扩到 **1..4**（`adapter.lua:18-19`），角色校验扩到 1–4 且带 m102 映射（`observe.lua:176`）；`seat_integrated_diagnostic` 仍是 **1↔2 双座**（`integrated/adapter.lua:46`）。两套的 `observe.lua` 行号重合但条件不同，**不可混引**。

---

## 6. 进度与范围（仅记录，不外推）

- **0.10.2 用户报告**：M102 客机 副驾→机枪→左后排→机枪→右后排→机枪→副驾 **六步无异常**；主工程日志显示**六次控制权归还完整**。（属用户报告 + 主工程日志范围）
- **0.10.3**：正适配 **M104 副驾 ↔ 喷火位**，**尚无实机成功结论**。
- **仍未交付完整多人加强版。**
- 本清单为**静态代码核对**：不宣称任何实机效果；不设计自动下车再上车；未新增测试要求。

**范围注记**：`observe.lua:176` 的 m102 角色映射（4=武器位/1–3=乘员）与 M104（`flamer` 为座位 2 角色 2）**不一致**，属 0.10.3 需单独处理的已知差异，此处仅标注位置。

---

## 7. 我对上一份路由报告的自我更正（采纳主工程复核）

1. **MD 笔误**：M102 一处写作「3 与 {2,3} 不连通」，应为**座位 4**。JSON 为准。
2. **方法缺陷**：`verify_native_routes_20260930.py` 用**无向分量**判断有向可达性，**对一般有向图不成立**；本轮数据恰好对称（每边双向），故结论未受影响，且已由主工程独立 BFS 复核。
3. **JSON 缺陷**：`direct_edges_total` 曾写成算式 `4 + 4 + 2 + 6 + 6 + 2`，**不是合法 JSON 值**；本副本已改为 `24` 并通过 `json.loads` 验证。**今后提交前一律先 `json.loads` 校验。**

*仅写入本副本 `outputs/DEEPSEEK_NETWORK_GUARD_INVENTORY_20260930.md`。*
