# DEEPSEEK 只读核对报告 — Vehicle Specified Seat Switch

日期：2026-09-30 · 范围：只读核对，**未构建任何实验包、未启动游戏、未改动 Arsenal/配置/GPT 主工作区**
核对对象：`E:\Document\deepseek-harness\default-workspace\vss-project`（DeepSeek 副本）
产出：仅本文件 `outputs/DEEPSEEK_READONLY_AUDIT_20260930.md`

---

## 0. 明确的不做事项

- 未运行、也不建议运行 **0.9.9**（其前提已被新证据推翻，见 §5）
- 未运行 **0.8.4 / 0.9.8**（已知会造成角色未挂载 / 状态损坏）
- **不研究"自动下车再上车"方案** —— 用户要求始终留在车内，该方向视为排除
- 未把"测试通过"当作"联机功能完成"

---

## 1. 五个模块的测试覆盖：谁真的执行了游戏指令

**结论：没有任何测试执行实时游戏。** 全部为三类之一：(a) 纯逻辑/构造状态；(b) 注入依赖的模拟；(c) 在隔离模拟器中执行**真实 game.dll 字节**（有真实指令执行，但无游戏进程、无联网、无渲染）。

### 1.1 五个目标模块

| 模块 | 测试文件 | 性质 | 依据（测试自报） |
|---|---|---|---|
| `work/seat_switch/src/ownership.lua` | `work/seat_switch/tests/test_ownership.lua` | **纯逻辑**，未执行游戏指令 | "1728 matrix cases … + targeted branch/refusal/return/ticket cases. Pure logic; no live claim." |
| `work/seat_switch/src/ownership_state.lua` | `work/seat_switch/tests/test_ownership_state.lua` | **纯逻辑**，依赖注入 | "…all three branches composed, driver scoping, ticket binding and hand-back gating… Pure logic; no live claim." |
| `work/seat_switch/src/multipeer.lua` | `work/seat_switch/tests/test_multipeer.lua` | **模拟读取器** | "Mocked reader; no game process." |
| `work/seat_switch/src/switch_flow.lua` | `work/seat_switch/tests/test_switch_flow.lua` | **全部原生原语被 mock** | "Every native primitive mocked." |
| `work/seat_switch/src/controller.lua` | `tests/test_config_controller.lua`、`tests/test_controller_multipeer.lua` | **原生调用被 mock** | "Native calls are mocked."（两份都是） |

### 1.2 同套件其余测试（用于判断整体可信边界）

| 测试 | 性质 |
|---|---|
| `tests/test_policy.lua` | 纯规则："Logical rules only; no native integration claim." |
| `tests/test_multipeer_spec.lua` | 不执行原生代码："No native code executed." |
| `tests/test_input.lua` | 模拟输入："Input states simulated; no keys injected." |
| `tests/test_config_storage.lua` | 仅工作区文件系统："Workspace only." |
| `tests/test_snapshot.lua` / `tests/test_driver.lua` | 合成内存："Memory is synthetic." |
| `tests/test_native.lua` / `tests/test_pose.lua` | 引擎调用被 mock："Native calls are mocked." / "Engine calls are mocked." |
| `tests/test_entry.lua` | 游戏 API 被 mock："Game API mocked." |
| `tests/test_platform.lua` | **唯一执行真实运行时**：真实 `lua51.dll` + 真实 Windows CNG。**未访问游戏进程** |
| `tests/check_syntax.lua` | 仅解析，不执行 |

### 1.3 诊断包侧：存在"真实指令执行"，但仍在模拟器中

`work/seat_weapon_sync_diagnostic/` 的构建套件报告了形如
`PASS captured compatibility … frames=165 checked=74`、`PASS 25480438 actual sender wrappers …`、
`PASS actual notification receiver 8 cases …` 的条目。这些**在 Unicorn 隔离模拟器中加载并执行真实 game.dll 采集字节**（`work/reverse/capture-25327279/`、`capture-25480438/`）。

**性质**：真实指令 + 真实字节校验，但**无游戏进程、无网络、无渲染**。
**可支撑**：某函数在该构建下的字节与 ABI 行为。
**不可支撑**：联机同步、渲染、主机/客机一致性。

其余为注入式：`test_sender.lua`（真实 FFI，但目标回调由测试提供）、`test_transaction.lua`（`bind()` 被 mock）。

---

## 2. 证据矩阵：哪些场景有真实日志/用户结果支持

**规则：没有真实运行证据的一律写"未验证"。**

| 场景 | 状态 | 依据 |
|---|---|---|
| **M-102 客机 副驾↔机枪换座** | **已实机验证（座位层面）** | 0.8.0–0.9.9 多次双人实测；`capture-20260929-080/081/082/083`；用户明确表示"换座本身已经完成" |
| **M-102 客机 机枪解除控制** | **未验证为修复** | 0.8.4 达成过"机枪不再跟随"，但同时造成**角色未挂载**（远端定在原地、下车布娃娃）；**尚无既解除机枪又保持挂载的实机结果** |
| **M-102 回副驾后远端角色跟随车辆** | **未验证 / 已知失败** | 0.8.4、0.9.8 实测均为失败（定在原地） |
| **M-102 探头射击姿势** | **未验证（本轮明确搁置）** | 用户 2026-09-29 表示可暂时不管 |
| **m103 / tanker / m104 / maelstrom / bastion 五车型** | **未验证** | 仅离线矩阵：`test_policy.lua`、`test_ownership_state.lua` 的六布局用例；模拟器 160 例跨区字段矩阵。**无任何实机日志** |
| **本机为房主（host）** | **未验证** | 适配器要求 `friend_must_host`（`work/seat_weapon_sync_diagnostic/adapter.lua` 中 `two_players_required` / `friend_must_host`）；历次测试用户恒为客机 |
| **3–4 人局** | **未验证** | 适配器硬性要求恰好 2 人（`two_players_required`）；无 3/4 人日志 |
| **占位竞争（vacancy race）** | **未验证（仅模拟）** | `test_ownership_state.lua`"25 agreement/policy refusals"、`test_multipeer.lua`"fresh target race"、`test_switch_flow.lua`"a second start while running is refused as busy"—— 全为构造状态 |
| **断线/离开后的归还与清理** | **未验证（仅模拟）** | `test_snapshot.lua`"stale state"、`test_transaction.lua`、`test_adapter.lua`"return with missing seat/focus/third peer/logging"；无断线实测日志 |
| **无模组玩家在场（房主未装模组）** | **已实机验证（作为观察方）** | 历次测试说明均要求"只有你安装，朋友无需安装"，即**房主为原版客户端**并作为驾驶者观察；0.8.x 各轮都记录了他的视角结果。**但反过来的情形（本机 host + 客机装模组）未验证** |
| **加入/离开清理（join/leave）** | **未验证** | 仅模拟（同断线一行）；无中途加入/离开的实测日志 |

### 2.1 实机日志清单（可复核的路径）

- `work/seat_weapon_sync_diagnostic/capture-20260929-080/`（0.8.0）
- `…/capture-20260929-081/`（0.8.1）
- `…/capture-20260929-082/`（0.8.2）
- `…/capture-20260929-083/`（0.8.3）
- 0.8.4 / 0.9.x 日志留在游戏日志目录（`%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs`），未全部冻结进副本

**注**：只有 M-102 存在实机日志；其余五车型无。

---

## 3. 可独立移植的纯决策模块清单

### 3.1 建议移植（纯决策，无原生依赖）

| 模块 | 路径 | 移植依赖 | 说明 |
|---|---|---|---|
| `ownership.lua` | `work/seat_switch/src/ownership.lua` | 无（仅需座位布局表） | keep / borrow / retain 分支决策 |
| `ownership_state.lua` | `work/seat_switch/src/ownership_state.lua` | 与 `ownership.lua` 相同的注入接口 | 合成采样器 + 权限 + 原生快照；分歧即拒绝 |
| `switch_flow.lua` | `work/seat_switch/src/switch_flow.lua` | 全部原生原语以参数注入 | 时序器；两条承重规则（借来的车身绝不留在手里、归还失败必须重试） |
| `multipeer_spec.lua` | `work/seat_switch/src/multipeer_spec.lua` | `compat.lua` 的能力分组机制 | 隔离多人接口证据，使多人见证损坏不影响普通模式 |
| `multipeer.lua` | `work/seat_switch/src/multipeer.lua` | 一个读取器接口（`observe`/`routing`） | 需注入读取器才完整 |

### 3.2 不可独立移植（必须与正式工程的原生层一起）

| 模块 | 原因 |
|---|---|
| `native.lua` | 直接调用游戏函数与结构写入 |
| `snapshot.lua` | 读游戏内存 |
| `pose.lua` / `driver.lua` | 动画图与转向命令的原生操作 |
| `platform.lua` | 模块范围安全读取、CNG 哈希 |
| `observe.lua` / `routing.lua` / `sampler.lua` | 依赖网络槽与消息注册表 |

**移植注意**：`build_release.py` 目前**未**把上述任何新模块打进发布包（已核对 `in_release_bundle=False`），因此正式包内无死代码；接入时必须**只进加强版**，`spec.core` 必需见证集不得改变（当前 `checked=74`）。

---

## 4. 关键纠正：测试通过 ≠ 功能完成

- 五个目标模块的测试**全部在无游戏进程条件下运行**，属于逻辑与接口正确性证据；
- 唯一执行真实运行时的是 `test_platform.lua`（真实 `lua51.dll` + CNG），**与游戏无关**；
- 模拟器套件执行真实 game.dll 字节，但**不覆盖联机、渲染、主机一致性**；
- 因此：**"17/17 PASS" 只说明逻辑与 ABI 断言成立，不能推断任何联机场景可用。**

---

## 5. 依据新证据对本副本既有结论的修正

以下为本副本**先前记录的推断**，按新证据更正：

| 本副本先前记录 | 更正 |
|---|---|
| `0xc698216f` = 已确认的"武器卸载消息"，0.9.9 以它替换 `entry_request` | **不成立**。该消息**未确认为武器卸载**；0.9.9 的前提被推翻，**不应运行**。相关结论见 `work/STATE_MESSAGE_SWAP_0.9.9_20260929.md`、`outputs/Vehicle-Seat-9-说明系列`，均需以降级为"未证实假设"阅读 |
| 该消息以 `(peer, avatar_id, seat)` 发送 | **错误**。`0x637990` 查座位集合并调用 `0x6349b0`；**不得把 `avatar_id` 当作 `collection_id`** |
| 引擎"释放武器"路径 = `0xbee380` 薄包装 | **不足以支撑**。原生武器槽清除路径为 **`0x785c10 -> 0x7853d0`**：第四参数为 **1** 时发送 **`0x423a4034`**；接收适配器 **`0xbaab40`** 以第四参数 **0** 调用、**不转发** |

**必须与已实机验证的修复相区别**：本副本中**唯一**可称"实机验证"的是 **M-102 的换座与座位同步**（0.8.x 系列日志 + 用户确认）。武器控制问题**尚未有已验证的修复** —— `0x785c10 -> 0x7853d0` / `0x423a4034` / `0xbaab40` 这条链路是**待验证的线索**，不是结论。

---

## 6. 结论摘要

1. **无任何测试执行实时游戏**；五模块覆盖为纯逻辑或注入式模拟；模拟器仅执行静态字节。
2. **实机证据只覆盖 M-102 客机的换座与座位同步**。机枪解除控制、远端挂载、探头姿势、其余五车型、host、3–4 人、占位竞争、断线归还、未装模组玩家、join/leave —— **全部未验证**。
3. **可移植的纯决策模块**：`ownership.lua`、`ownership_state.lua`、`switch_flow.lua`、`multipeer_spec.lua`，以及**需注入读取器**的 `multipeer.lua`；`controller.lua` 依其接缝可移植但需注入 policy/snapshot/input。原生层模块不可独立移植。
4. **0.9.9 不成立、不应运行**；`0xc698216f` 与 `avatar_id` 用法均已更正。
5. **武器控制问题尚未解决**；`0x785c10 -> 0x7853d0`（第四参数 1 → `0x423a4034`）与接收适配器 `0xbaab40`（第四参数 0，不转发）为后续线索。
6. 自动下车再上车方案**已排除**，用户要求始终留在车内。

---

*本报告为只读核对产物，未修改 GPT 主工作区、游戏目录、Arsenal 或任何配置；未构建包、未启动游戏。*
