# 组合键重叠静态用例表

只读静态整理；**未改代码或 INI、未运行游戏、未采集数据、未新建测试**。
依据：`work/seat_switch/src/config.lua` L34-36（`modifiers`）、L37-43（`single`）、L45-61（`M.key`）、L62-83（`M.overlap`）；`work/seat_switch/src/input.lua` L3-33；`work/seat_switch/tests/test_input.lua`（**仅按其既有断言文本引用，本轮未逐行核对**）。

**编码规则**：`code = 主键VK + 256×mask`；mask 第 g 组占 `4^(g-1)` 位（`config.lua:58`）。**组序 = SHIFT(1)、CTRL(2)、ALT(3)、WIN(4)**（`config.lua:34-36`；`input.lua:3` 的 `{16,160,161},{17,162,163},{18,164,165},{nil,91,92}` 同序）。位值：0=该组不得按下、1=任意侧、2=仅左侧、3=仅右侧。
`M.overlap` 返回 **true = 可能共同触发**；`input.lua:23-29` 中 `want==0` 表示"该组任何修饰键按下即不匹配"（多余修饰键不匹配）。

| # | 绑定 A | 绑定 B | 编码 A / B | 编码相等 | 可否共同触发 | 触发方式与按下顺序 | 依据 |
|---|---|---|---|---|---|---|---|
| 1 | `CTRL+SHIFT+HOME` | `LCTRL+SHIFT+HOME` | 1316 / 2340 | 否 | **是** | **同一次 HOME 边沿**：按 LCTRL+LSHIFT 后按 HOME，两者同帧都匹配（A 组2=任意、B 组2=左侧） | overlap L64,68,76-82（同主键、各位不矛盾 → true）；input L19-29 |
| 2 | `CTRL+SHIFT+HOME` | `CTRL+LSHIFT+HOME` | 1316 / 1572 | 否 | **是** | **同一次 HOME 边沿**（A 组1=任意、B 组1=左侧，按 LSHIFT 时两者皆满足） | overlap L76-82 → true |
| 3 | `LCTRL+SHIFT+HOME` | `CTRL+LSHIFT+HOME` | 2340 / 1572 | 否 | **是** | **同一次 HOME 边沿**（按 LCTRL+LSHIFT 时两条件同时成立） | overlap L76-82 → true |
| 4 | `CTRL`（**单修饰键作主键**） | `CTRL+SHIFT+HOME` | 17 / 1316 | 否 | **是（不同边沿）** | **先按 CTRL 即触发 A**；之后按 HOME 才触发 B | overlap L64,71-74（A 是修饰键、B 该组 want=1 → true）；注释 L69-70 |
| 5 | `SHIFT`（单修饰键作主键） | `CTRL+SHIFT+HOME` | 16 / 1316 | 否 | **是（不同边沿）** | **先按 SHIFT 触发 A**；再按 HOME 触发 B | overlap L71-74（x={1,1}，want=1 → true） |
| 6 | `CTRL` | `LCTRL+SHIFT+HOME` | 17 / 2340 | 否 | **是（不同边沿）** | 先按 CTRL 触发 A（CTRL 通用码对左右皆有效） | overlap L73（want=floor(9/4)%4=2，x[2]=1 → true） |
| 7 | `CTRL+SHIFT+HOME` | `CTRL+ALT+HOME` | 1316 / 5156 | 否 | **否** | 互斥：按 ALT 时 A 的组3 want=0 → A 不匹配；不按 ALT 时 B 不匹配 | overlap L79（组3：0 vs 1 → `(x==0)~=(y==0)` → false） |
| 8 | `CTRL+1` | `1` | 1073 / 49 | 否 | **否** | 互斥：按 CTRL 时 B 的组2 want=0 → B 不匹配；不按 CTRL 时 A 不匹配 | overlap L76-82（组2：1 vs 0 → false） |
| 9 | `CTRL+SHIFT+MOUSE4` | `CTRL+SHIFT+MOUSE5` | 1285 / 1286 | 否 | **否** | 不同鼠标键，主键不同且均非修饰键 | overlap L64,71-72（`x` 为 nil → false） |
| 10 | `CTRL+MOUSE4` | `CTRL+SHIFT+MOUSE4` | 1029 / 1285 | 否 | **否** | 互斥：按 SHIFT 时 A 组1 want=0 | overlap L79（组1：0 vs 1 → false） |
| 11 | `F2` | `F5` | 113 / 116 | 否 | **否** | 主键完全不同，均非修饰键 | overlap L71-72（false） |
| 12 | `CTRL+SHIFT+MOUSE4` | `CTRL+1` | 1285 / 1073 | 否 | **否** | 主键不同（鼠标键 5 与 `1`=49），均非修饰键 | overlap L71-72（false） |

**关键区分（勿混写"冲突"）**：
- **同一次主键边沿共同触发**：#1–#3（不同编码、同主键、各位不矛盾）
- **先按修饰键已触发另一绑定**：#4–#6（单修饰键作主键；不同主键，但修饰键按下即先触发）
- **结构互斥**：#7–#12（多余修饰键不匹配 / 主键不同）

---

## 编码相等 ≠ 重叠已消除（更正）

`HOST/entry.lua:37` 的 `binding==1316` **只判断编码完全相等**：#1–#3 三例编码各不相等（1316 / 2340 / 1572），该检查**不会**报冲突；真正判定它们可共同触发的是 `M.overlap`（`config.lua:62`，经 `config.lua:106` 在同车辆内逐对调用 → 命中即该车辆**恢复默认键**，L112-113）。**不能把 exact equality 写成"已消除所有冲突"。**

---

## 覆盖情况

**既有用例覆盖（据 `test_input.lua` 断言文本）**：具名键与鼠标键、**组合别名与重叠（chord aliases/overlap）**、**带侧别的修饰键（sided modifiers）**、**鼠标侧键组合（mouse side chords）**、`Ctrl+1`、`Shift+Q`、**无重复**、**多余修饰键不匹配**、**修饰键释放**、**焦点获得不激活** → 对应本表 #7–#12 的互斥面与 #1–#3 的"重复/多余修饰"面**大体已覆盖**。

**尚缺（需合并前补核，本轮不新建）**：
1. **#4–#6：单修饰键作主键 与 含该修饰键的组合键 的"先触发"关系**（`M.overlap` L71-74 分支）—— 断言文本未提及该分支。
2. **#1–#3：CTRL 与 LCTRL/CTRL 与 LSHIFT 等"同主键、不同侧别/通配"三例的成对 `M.overlap` 结果**（L76-82 逐位比较）—— "sided modifiers" 可能部分覆盖，**需逐行核对 `test_input.lua` 才能确认**。
3. **编码相等 vs `M.overlap` 的区分**（1316 / 2340 / 1572 三例编码不等却重叠）—— 现有断言未见此对照。

> 以上覆盖判断基于断言文本；**未逐行核对 `test_input.lua`**，故不作"已通过/未通过"结论。

---

## 进度（仅记录）

- **0.10.4**：安装者作房主**六步通过，但全部走借用归还**
- **0.10.5**：准备测试**驾驶位跨区**及**已有本机控制权路径**，**实机待验证**
- **正式按键尚未整合**；本表为静态用例，未宣称实机效果

*仅写入本副本 `outputs/DEEPSEEK_CHORD_OVERLAP_CASES_20260930.md`。*
