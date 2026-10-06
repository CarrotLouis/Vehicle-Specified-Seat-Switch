# 六车型静态适配表 — Vehicle Specified Seat Switch

只读抽取自 GPT 主工程；**未构建、未测试游戏、未改原代码**。配套数据：`DEEPSEEK_VEHICLE_ADAPTATION_MATRIX_20260930.json`
抽取来源（下文 `[P]`=profile.lua `[C]`=config.lua `[Y]`=policy.lua `[N]`=native.lua `[O]`=pose.lua `[M]`=all-vehicle-receiver-matrix-25480438.json）：

- `[P]` `work/seat_switch/src/profile.lua`
- `[C]` `work/seat_switch/src/config.lua`
- `[Y]` `work/seat_switch/src/policy.lua`
- `[N]` `work/seat_switch/src/native.lua`
- `[O]` `work/seat_switch/src/pose.lua`
- `[M]` `work/seat_weapon_sync_diagnostic/all-vehicle-receiver-matrix-25480438.json`
- 座位名与顺序 `[Y]` `M.seats`；默认键 `[C]` 的 `template()`；原生索引 = `M.seats` 顺序的 0 基下标；角色值与恢复动作号 `[P]` 的 `tables` 行

---

## 1. 六车型 × 座位

角色值：1=驾驶、2=武器位、3=普通乘员。恢复动作号 `0` 表示该座位无恢复动作（`[P]`）。

### m102 · transition=26 · roles={1,3,3,3,2} · restore={0,1,2,3,5} `[P]`
| 座位（用户名称）`[Y]` | 默认键 `[C]` | 原生索引 | 角色 `[P]` | 恢复动作 `[P]` |
|---|---|---|---|---|
| driver | F1 | 0 | 1 | 0 |
| front_passenger | F2 | 1 | 3 | 1 |
| rear_left | F3 | 2 | 3 | 2 |
| rear_right | F4 | 3 | 3 | 3 |
| gunner | F5 | 4 | 2 | 5 |

### m103 · transition=27 · roles={1,3,3,3} · restore={0,1,2,3} `[P]`
| driver | F1 | 0 | 1 | 0 |
|---|---|---|---|---|
| front_passenger | F2 | 1 | 3 | 1 |
| rear_left | F3 | 2 | 3 | 2 |
| rear_right | F4 | 3 | 3 | 3 |

### m104 · transition=28 · roles={1,3,2} · restore={0,1,3} `[P]`
| driver | F1 | 0 | 1 | 0 |
|---|---|---|---|---|
| front_passenger | F2 | 1 | 3 | 1 |
| flamer | F3 | 2 | 2 | 3 |

### bastion · transition=43 · roles={1,2,3,3} · restore={0,1,2,3} `[P]`
| driver | F1 | 0 | 1 | 0 |
|---|---|---|---|---|
| gunner | F2 | 1 | 2 | 1 |
| passenger_left | F3 | 2 | 3 | 2 |
| passenger_right | F4 | 3 | 3 | 3 |

### maelstrom · transition=44 · roles={1,2,3,3} · restore={0,1,2,3} `[P]`
| driver | F1 | 0 | 1 | 0 |
|---|---|---|---|---|
| gunner | F2 | 1 | 2 | 1 |
| passenger_left | F3 | 2 | 3 | 2 |
| passenger_right | F4 | 3 | 3 | 3 |

### tanker · transition=33 · roles={1,2} · restore={3,4} `[P]`
| driver | F1 | 0 | 1 | **3** |
|---|---|---|---|---|
| gunner | F2 | 1 | 2 | **4** |

> **tanker 的 `restore` 两个座位都非 0** —— 与其他五车型「驾驶位恢复动作号为 0」不同，任何「restore[0]==0 即驾驶位无动作」的共用假设在 tanker 上不成立。`[P]`

---

## 2. 原生 next/previous 与跨区域路径

- **有原生路由（引擎函数存在）**：`next`、`previous`、`route`、`goto_node`、`adjacency` 六个函数在 `[P]` 中均已登记 RVA（`next`/`previous`/`route`/`goto_node`/`adjacency`）。→ 六车型**都具备**引擎自身的 next/previous 链。`[P]`
- **逐对原生邻接映射：`unknown`** —— 本表仅确认函数存在与 RVA，**未抽取**引擎自身的逐对邻接结果，故不列具体对。`[P]`
- **「现有普通版允许」= `[Y]` `normal_groups`**（这是**模组**的 Normal 限制，非引擎邻接）：

| 车型 | 普通版允许的组 `[Y]` |
|---|---|
| m102 | {driver, front_passenger} · {rear_left, rear_right} |
| m103 | {driver, front_passenger} · {rear_left, rear_right} |
| m104 | {driver, front_passenger} |
| bastion | {gunner, passenger_left, passenger_right} |
| maelstrom | {gunner, passenger_left, passenger_right} |
| tanker | {driver, gunner} |

- **必须跨区域处理的路径（派生自 `[Y]`，非引擎邻接）**：任意**不落在同一组**内的有向对。例如 m102 的 `front_passenger → gunner`、`gunner → front_passenger`、`driver → rear_left`、`rear_left → driver` 等；bastion/maelstrom 的 **`driver → gunner` 亦属跨区域**（其组不含 driver）；tanker 只有一组，故 `driver ↔ gunner` 属**组内**。
- `[Y]` `M.check`：`enhanced` 直接返回 true；`normal` 逐组判定，未命中返回 `normal_restriction`。→ **「有原生路由」与「普通版允许」是两件事**：引擎邻接未被抽取（`unknown`），而普通版只放行组内对。

---

## 3. 本地清理/准备差异（仅 `[N]` 有代码依据的部分）

| 步骤 | 适用范围 | 代码位置 |
|---|---|---|
| 驾驶位转向/指令中和 | **当前座位角色==1** → `driver.prepare(s)` | `[N]` L103-106 |
| 清武器槽 0 与 1 | **无条件，六车型全部** | `[N]` L116-119 |
| 恢复个人武器 + 刷新武器上下文 | 无条件，六车型全部 | `[N]` L120-123 |
| `remove_flag(avatar,44)` | **仅 maelstrom** | `[N]` L125 |
| `rotation(...)` 写入 | **仅 (m102 或 m104) 且当前角色==2** | `[N]` L126-128 |
| 目标准备动作 `seat_action(transition,…,N,target)` | **仅目标角色==2**：m102 用 4、m104 用 2；**其余车型无此调用** | `[N]` L136-139 |
| 目标为个人武器位 → `equip_personal` + `restore_personal` | 目标角色==3，**或** 目标角色==1 且车型 ∈ {m102, m103, m104} | `[N]` L142-151 |
| 最终姿势 | 无条件 `pose.apply(s,target)` | `[N]` L154-155 |

**按座位类别的净差异**：
- **驾驶位**：仅「当前座位是驾驶」时做转向中和；作为**目标**时，只有 m102/m103/m104 会给个人武器。
- **普通乘员（角色 3）**：六车型一致（个人武器位）。
- **武器位（角色 2）**：差异最大 —— 卸载侧只 m102/m104 写 `rotation`；准备侧只 m102(4)/m104(2) 有动作；maelstrom 额外清 bit 44。**bastion / maelstrom / tanker 的 `gunner` 同为角色 2，却没有卸载侧 `rotation` 与准备侧动作。** `[N]`

---

## 4. 未知项（按 `unknown` 记录，不猜）

- **六车型各自的原生逐对邻接**：`unknown`（仅确认 `next`/`previous`/`route`/`goto_node`/`adjacency` 函数存在，`[P]`）
- **各车型动画事件编号**：`unknown`，**tanker 无 pose 目标**（`[O]` `targets` 仅列 m102/m103/m104/bastion/maelstrom 五行）→ tanker 动画目标 `unknown`
  - 仅 FRV 有本次核对可直接引用的入口事件：`0x29e8fb0c`、`0xe8344235`、`0xd3a9222b`（来自本副本 9 月 29 日反汇编记录），**其余车型未抽取**
- **各车型武器槽需求**：`unknown`。`[M]` 的 160 例边界自述：「Real snapshot/transition/tick/route instructions execute; **ALL action dispatch is stubbed** … not remote rendering or wire acceptance」，mode 仅 `no_seat_rpc / snapshot_only / transition_only / snapshot_then_transition`（各 40），layout 仅 {26:64, 27:32, 28:16, 43:24, 44:24} —— **无 tanker(layout 33) 用例**，且不含槽位数据
- **`[O]` 的动画目标名 ↔ 事件号映射**：`unknown`

---

## 5. 六车型共用代码可能错误泛化的地方（均有代码依据）

1. **`clear_weapon` 清 0 与 1 是无条件的**（`[N]` L116-119）。而本轮 `capture-20260930-0100` 的 31 个 `binding_sample` 中**槽 1 恒为 0**，槽 0 才发生变化 → 「清槽 1 是必要的」在所有车型上**未验证**。
2. **`rotation` 只对 m102/m104 写**（`[N]` L126）。bastion/maelstrom/tanker 的 `gunner` 也是角色 2，却没有该写入 → 若它们的武器位依赖同一标志，属于**欠泛化**（`unknown`）。
3. **目标准备动作只覆盖 m102(4)/m104(2)**（`[N]` L137-138）。bastion/maelstrom 同样有 `gunner`（角色 2）→ 共享代码在此**可能漏做**（`unknown`）。
4. **`personal_target` 把「目标角色==1」纳入个人武器位，仅限 m102/m103/m104**（`[N]` L100）。bastion/maelstrom/tanker 的驾驶位被排除 —— 这是**三车型白名单**，扩展时最易误伤。
5. **`restore` 的「0 = 无动作」假设在 tanker 上失效**（`restore={3,4}`，`[P]`）→ 任何以非 0 判断「该座位有恢复动作」的共用逻辑会**在 tanker 驾驶位误触发**。
6. **pose 目标表缺 tanker**（`[O]` L21-25）→ 任何假定六车型都有动画目标的共用路径会在 tanker 上拿到 `nil`。
7. **bastion 与 maelstrom 的 roles/restore/pose 目标完全相同**（`[P]`、`[O]`）→ 两者很可能是同一布局族；把它们当独立实现处理可能**过拟合**（`unknown`）。
8. **`normal_groups` 的形状不一致**：m102/m103 含驾驶位组，bastion/maelstrom **不含**驾驶位，tanker 只有一组 → 任何「驾驶位总能与某人同组」的通用假设在这两类车型上不成立（`[Y]`）。

---

## 6. 已记录的范围（不外推）

- **用户报告（2026-09-30）：0.10.1 的 M102 客机 副驾 → 机枪 → 副驾 测试“无异常”。**
  - 该结论**仅限**：M102、**客机**、副驾↔机枪、0.10.1 版本。
  - **无本副本独立验证**（本副本未运行 0.10.1，也未接触其实机日志）。
  - **不外推**到：其余五车型、本机为 host、3–4 人、占位竞争、断线归还、未装模组第三方。
- **本文件为静态抽取表，不等于实机通过。** `[M]` 自述动作分派全为 stub；本表不含任何新增测试要求。

*仅写入本副本 `outputs/DEEPSEEK_VEHICLE_ADAPTATION_MATRIX_20260930.md` 与同名 `.json`；未写入 GPT 主工程、游戏、Arsenal 或配置。*
