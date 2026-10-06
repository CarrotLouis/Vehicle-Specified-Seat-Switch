# DEEPSEEK 只读复核 — seat_weapon_binding capture-20260930-0100

只读复核，未改模组代码、未构建包、未启动游戏、未操作 Arsenal。原始证据：
`…\work\seat_weapon_binding_diagnostic\capture-20260930-0100\`（`VehicleSeatBinding-20260930-023922-15800.log` 163040 B；`analysis.json`；`VehicleSeatBindingDiagnostic.log`）
诊断日志：`compat ready schema=seat-layout-v1 checked=77 relocated=0 enhanced=true`

## 1. 独立核对 analysis.json（不是抄它）

| 项目 | analysis.json | 原始日志独立计数 | 一致 |
|---|---|---|---|
| start / end | 1 / 1 | 1 / 1 | ✅ |
| binding_interface | 22 | 22 | ✅ |
| state | 219 | 219 | ✅ |
| binding_sample | 31 | 31 | ✅ |

- **读取失败数 = 0**：原始日志无任何 `"ok":false`；31 个 sample 全为 `ok:true, reason:null`，与 `all_interfaces_valid:true` 一致。
- **`clear_dispatch_matches` 在 analysis.json 中不存在**。原始字段名为 `data.callback.matches_dispatch`（22/22 为 `true`，且 `stable:true`，`storage.writable:true, protection:4`）。任务中使用的字段名与产物不符 —— **应记为 analysis.json 未收录该字段**。
- **两条消息 schema**：本次未能从 `binding_interface` 提取到消息名/哈希/参数表（`ConvertFrom-Json` 后 `data.message` 为空），**无法在本轮确认"两条消息 schema"，不写结论**。

## 2. 武器槽 0/1 与 rotation_flag 时间线（`binding_sample`，t 为日志内毫秒）

普通副驾（t=244485 进入，245485 稳定）：`s0=422, s1=0, rot=1`，`current=1 role=3 collection=455`
机枪位（t=256594 action=7 target=8 → 259875/260125 action=4 target=4 → **260875 稳定**）：`current=4 role=2`，**`s0` 由 422 → 456，`rot` 由 1 → 0**
退出机枪位（t=287297 action=11 current=9）：**`s0` 由 456 → 0（清零）**，`rot` 由 0 → 1；t=287797 `s0` 回 422
再次副驾（t=298813 action=1 target=1 → 299828 稳定）：`current=1 role=3`，`s0=422`，`rot=1`；t=305141 `s0` 再次为 0，t=306141 回 422

**确定的座位变更**：t=244485(→副驾1)、t=260125/260875(→机枪4)、t=287297(离开机枪)、t=298813(→副驾1)、t=316672(→座位8)
**额外动作（非座位变更，均在 `collection=0` 即离车状态）**：t=221485 `s0=451`、t=288547 `s0=463`、t=291313 `s0=468` —— 属**切枪**，不得混入座位结论
**槽 1（channel 1）在全部 31 个 sample 中恒为 0** —— 本会话从未使用

## 3. 这些数据仍不能证明的事

- **远端清除/重绑定的实机效果**：全部为**本地**只读快照，无任何对端字段。主机是否解除武器绑定、是否重绑定，**未验证**。
- **是否需要清理 0 之外的槽**：槽 1 从未非零，**本采集无法回答**；代码清 0 与 1，但数据只覆盖了 0。
- **多人武器实体引用是否有效**：仅记录本地 id（422/456/463/468）；对端是否认这些引用**无证据**。且 `0x637990` 查座位集合并调用 `0x6349b0` —— **不得把 `avatar_id` 当作 `collection_id`**。
- `matches_dispatch:true` 只证明**本地**回调槽指向预期派发目标，**不证明对端接受任何消息**。
- `rotation_flag` 只有本地值，无远端对照。

## 4. 对上一份 DEEPSEEK_READONLY_AUDIT_20260930.md 的更正

对照 GPT 主工程 `work/STATE_SYNC_SUCCESS_20260928.md`、`STATE_AUTHORITY_SUCCESS_20260928.md`：

| 上一份审计的说法 | 更正 |
|---|---|
| "实机证据只覆盖 M-102 客机的换座与座位同步" | **不完整**。`STATE_SYNC_SUCCESS` L12：**TD220 已验证一次** —— guest 拥有 TD220，**driver↔gunner 视觉/控制同步**，friend 为**未改装 host**。`STATE_AUTHORITY_SUCCESS` L15：0.6.0 已是同样结论。**不得遗漏 TD220 的局部成功** |
| 将 M102 记为"换座已验证" | **需限定**。`STATE_AUTHORITY_SUCCESS` L16：0.5.3 验证的是 **M102 副驾 acquire/return 权限**，且**无座位变更（no seat mutation）**；L12 记录 M102 collection 750/network 8214。M102 的**座位变更**证据来自后续 0.8.x 轮次，需与 0.5.3 的权限结论分开表述 |
| （隐含）"0.9.9 已多次实测" | 本副本**从未**主张 0.9.9 通过实测；上一份审计明确写 **0.9.9 前提被推翻、不应运行**。**任何"0.9.9 已实测"的说法均无本副本支持** |

**不得把局部成功扩写为全面支持**：`STATE_SYNC_SUCCESS` L12 明确 "**NOT all multiplayer Enhanced**, host-s…"；`STATE_AUTHORITY_SUCCESS` L19 列明终极目标仍为"any supported seat/vehicle, installer only, host/guest, **no exit/reentry**, exclusive occupancy"，且"Future tests remain needed"。**host 角色、3–4 人、其余车型、占位竞争、断线归还仍属未验证。**

约束遵从：本报告不研究、不建议"自动下车再上车"；用户要求始终留在车内（与 L19 `no exit/reentry` 一致）。

*仅写入本副本 `outputs/DEEPSEEK_BINDING_CAPTURE_REVIEW_20260930.md`；未改动 GPT 主工作区、游戏目录、Arsenal 或配置。*
