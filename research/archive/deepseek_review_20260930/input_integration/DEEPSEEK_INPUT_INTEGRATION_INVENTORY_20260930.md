# 输入/按键整合清单 — 诊断快捷键回正式 INI 前的资料

只读整理；**未改主工程/游戏/Arsenal/INI，未实现功能，未新建测试，未运行游戏**。
来源：`work/seat_switch/src/{config,input,controller,entry,policy}.lua`、`work/seat_host_weapon_diagnostic/{entry,probe,platform}.lua`

---

## 1. INI 座位名 → 按键值；组合键匹配；鼠标键同流程

| 环节 | 位置 | 事实 |
|---|---|---|
| 键名表 | `config.lua:10-27` | 名称→Windows 虚拟键码；`HOME=36`（L18） |
| **鼠标键** | `config.lua:13` | `MOUSE1=1,MOUSE2=2,MOUSE3=4,MOUSE4=5,MOUSE5=6` —— **鼠标键被赋成与键盘同一空间的数值**，故后续流程无需分支 |
| 组合键编码 | `config.lua:45-60` | `M.key(value)`：`primary=single(parts[#parts])`（**最后一个片段是主键**，L54）；修饰键占 4 进制位：`mask=mask+m[2]*4^(m[1]-1)`（L58）；返回 **`primary+256*mask`**（L60） |
| 修饰键语义 | `config.lua:69-70` | 单独修饰键会先于其组合的主键触发 → 与重叠组合分派到同一车辆的不同座位会被拒绝 |
| 解析 | `config.lua:84-98` | 按 INI 段→`result[section][name:lower()]=code`（L98） |
| 冲突消解 | `config.lua:102-113` | 逐车辆做重叠检测；命中则**该车辆恢复默认键**并记 issue（L112-113） |
| 默认键 | `config.lua:118-127` | `M.template()`；示例含 `CTRL+1, SHIFT+Q, CTRL+SHIFT+MOUSE4, RCTRL+NUMPAD1`（L122） |
| 读盘 | `config.lua:141-155` | `directory..'/VehicleSeatSwitch.ini'`；legacy 目录回退；缺文件则写模板；返回 `keys,issues,path,origin` |
| 组合键匹配 | `input.lua:3-5` | 四个修饰组 `{16,160,161},{17,162,163},{18,164,165},{nil,91,92}`（ctrl/shift/alt/win） |
| 边沿+修饰判定 | `input.lua:14-33` | `binding%256` 取主键、`binding/256` 取 mask（L18）；要求 `focused and self.focused and now[key] and not previous[key]`（L19）；逐组解 mask 位（L21-29）；末尾更新 `previous`/`focused`（L33） |
| 键位读取 | `controller.lua:48` | `pressed[self.keys[s.vehicle][name]]` —— **按「车辆+座位名」查码**，与 INI 段名一致 |

> 键盘与鼠标走**同一条** `bindings[code]`/`codes[code%256]` 流程（`input.lua:8-9`），无鼠标专用分支。

---

## 2. 正式版 vs 诊断版：读配置 / 轮询 / 焦点 / 冷却

| 项 | **正式版** | **诊断版（host_weapon）** |
|---|---|---|
| 读配置 | `entry.lua:31` `config.load(api.config_directory(), loader.log_directory)` | `HOST/entry.lua:34-36` 直接 `io.open(base..'/Arrowhead/Helldivers2/VehicleSeatSwitch.ini')` 后 `config.parse(text)` —— **读同一份 INI** |
| 控制器 | `entry.lua:36` `Controller.new(MODE,keys,api,native,log)` | `HOST/entry.lua:38` `input.new({probe={trigger=1316}},api)`（**只为自己造一个触发键**） |
| 轮询频率 | 每帧（`entry.lua:69` `controller:update(s,reason)`） | **节流**：`HOST/entry.lua:106` `now<next_poll then return; next_poll=now+.016` |
| 焦点 | `controller.lua:12-14` 计算 `focused`；非焦点 → 清 `pending`/`preparing` 并返回 `not_focused` | `HOST/entry.lua:107` `focused=api.input_allowed()` |
| 菜单/快照守卫 | `controller.lua:26,66` `not snapshot.current(...)` → `snapshot_changed` 并清 `preparing` | `HOST/entry.lua:98` 等待 gameplay 初始化；`:119` 冲突则 `status(...)` 并 `return` |
| 冷却 | `controller.lua:54-55` `now<self.cooldown → 'cooldown'`，随后**置 `cooldown=now+0.35`** | `HOST/probe.lua:20` `cooldown=now+10`（**步间 10 秒**）；`:110` 另需 `now-stable_since>=3`（**3 秒稳定**） |
| 按住重复 | **结构上不重复**：`input.lua:19` 要求 `now[key] and not previous[key]` 边沿。（`controller.lua` 无自动重复路径） | 同机制（`input.lua` 共用） |
| 追踪等待 | `controller.lua:33-41` `request_expired`（>6s）与 `request_not_completed` | `HOST/probe.lua:32` `observation_timeout; monitoring_late_grant_without_switch` |
| 平台层 | 同 `platform.lua`：`a.down(key)=GetAsyncKeyState(key)<0`（`HOST/platform.lua:52`）、`a.now()` 取自 `GetTickCount64()/1000`（L38）、`a.focused()`（L40-46） | 同 |

> **焦点要求是"连续两帧"**：`input.lua:19` 同时要求传入的 `focused` 与 `self.focused`（上一帧）为真。

---

## 3. 整合时必须替换的绑定（只列位置）

| 项 | 位置 | 现值 |
|---|---|---|
| **诊断触发键写死** | `HOST/entry.lua:38` | `trigger=1316` = **Ctrl+Shift+Home**（36 + 256×5；mask 5 = 4 进制 `11` → Ctrl+Shift） |
| 触发键位号散落 | `HOST/entry.lua:37`（冲突检测 `binding==1316`）、`:108`（`[1316]`）、`:110`、`:119` | 四处硬编码同一数值 |
| **固定六步路线** | `HOST/entry.lua:56` `route_1_4_2_4_3_4_1`；`HOST/probe.lua:104` `route[self.count+1]` / `[self.count+2]` | 1→4→2→4→3→4→1 |
| **最大次数** | `HOST/entry.lua:56` `max_six_manual_operations`；`HOST/probe.lua:21` `if self.count==#route-1 then phase('finished')`；`entry.lua:110` `six_operation_limit` | 6 步 |
| 已存冲突检测（可复用） | `HOST/entry.lua:37`、`:108`、`:119` | 若 INI 已占用 1316 → `conflict` → 禁用触发并报状态 |

---

## 4. 两个 `update` 回调的串联 与 同键双触发

**串联方式**（两版一致）：文件顶部捕获旧值，再用包装函数**替换全局**：

- 正式版：`entry.lua:11` `local previous,previous_shutdown=update,shutdown`；`:73` 缺 `previous` 则 `missing_update`；`:74` `update=function(...)`；`:82-84` `shutdown` 链
- 诊断版：`HOST/entry.lua:6` 同；`:129-130` 同；`:147-153` `shutdown` 链
- 因此**加载顺序决定链的方向**：后加载者的 `previous` 指向前者 → 两者都会执行，顺序与加载顺序一致。

**同一按键是否会触发两个控制器**：

- **已防止（限当前绑定）**：两版都读**同一份 INI**，而诊断版把触发键固定为 1316，并用 `HOST/entry.lua:37` 检测 `binding==1316`；命中则 `conflict=true` → `:108` 用 `not conflict` 关闭触发、`:119` 报状态并 `return`。**默认键 F1–F5 与 1316 不冲突，故默认下不会双触发。**
- **需验证**：
  1. `input.lua:1` 自述 **"non-consuming key polling"** —— 轮询**不消费**按键。两版各自持有独立 `input` 实例与独立 `previous` 表，**同一物理键若被双方同时绑定，同一帧内两者都可能看到边沿**。当前只靠上述 `conflict` 检测覆盖 1316 这一个键，**不覆盖"用户把某座位绑成 1316 以外、但与诊断触发键相同"的一般情形**（诊断键只有 1316，故风险面小，但机制上未由消费语义保证）。
  2. **加载顺序反置**（诊断先加载）时包装链的行为未在本轮核对。
  3. 两版轮询频率不同（正式版每帧 vs 诊断版 16ms 节流），**同一帧时序**未核对。

---

## 5. 可复用的既有测试

| 目标 | 文件 | 可直接覆盖 |
|---|---|---|
| 键盘/鼠标/组合键语义 | `work/seat_switch/tests/test_input.lua` | 具名键、鼠标侧键、组合别名与重叠、Ctrl+1/Shift+Q、**无重复、多余修饰键不匹配、修饰键释放、焦点获得不激活** |
| 配置解析/落盘/迁移 | `work/seat_switch/tests/test_config_storage.lua` | 目录创建、首启默认、legacy 迁移、APPDATA 优先级、原文件保留、小键盘键名 |
| 控制器键边沿/焦点/守卫 | `work/seat_switch/tests/test_config_controller.lua` | 键配置、占用拒绝、普通限制、陈旧状态、权限守卫、键边沿与焦点 |
| 启动/回调链/重复守卫 | `work/seat_switch/tests/test_entry.lua` | 启动、配置保留、**回调**、重复守卫、哈希变化 |
| **加载共存（顺序）** | 诊断构建的 `test_platform.lua` | 既有用例 **"coexistence diagnostic-first"** 与 **"gameplay-first"** 各 100 次轮询 —— 正是第 4 项所需目标 |
| 诊断自身流程 | `HOST/test_probe.lua`、`test_adapter.lua`、`test_transaction.lua`、`test_sender.lua` | 触发/步进/取消、准入与归还 |

**可复用结论**：第 1、2 项的语义已被 `test_input.lua` 与 `test_config_storage.lua` 覆盖；第 4 项的**顺序**已有共存用例；**不新建测试**。

---

## 6. 对上两份清单的用词更正（采纳主工程指出）

1. **`observe.lua` 的 `send` 是控制权请求/归还**，其**两个目标参数都是 peer**；**`sender.lua` 才是座位同步**。上次把二者笼统归入"同步前"是错的。
2. **`adapter:eligible` 是在归还后复核座位**，**不是发出清理归还的前提**；与之相邻的 `adapter.lua:81-89`（`return_owner_not_ready` 等）才是归还路径的断言。**不得把"归还后复核"与"发出归还的前提"混写。**
3 本次第 2 节已按上述区分重述相关行号。

---

## 7. 进度与范围（仅记录）

- **0.10.3**：客机 M104 副驾 ↔ 喷火位，**用户/日志确认通过**
- **0.10.4**：正验证**安装者作为房主**、按**实际车辆控制权**选择「本机直接换座」或「借用后归还」；**房主路径尚未实机通过**（`HOST/probe.lua:116` `local_authority_selected` 即该分支）
- **当前仍非完整多人加强版**
- 本清单为静态核对，未宣称实机效果；未实现功能；未新增测试要求

*仅写入本副本 `outputs/DEEPSEEK_INPUT_INTEGRATION_INVENTORY_20260930.md`。*
