from pathlib import Path
import collections,json

W=Path(__file__).resolve().parent;P=W.parent;C=W/'seat_multi_peer_research/capture-20261002-0183'
a=json.loads((C/'analysis.json').read_text(encoding='utf-8'))
for run in a['runs']:
    rows=[json.loads(l)for l in (C/run['name']).read_text(encoding='utf-8-sig').splitlines()]
    join=next((r['t']for r in rows if r['event']=='state'and r['data']['player_count']==3),None)
    run['third_peer_join_ms']=join
    run['post_join_input_reasons']=dict(collections.Counter(r['reason']for r in rows if join and r['t']>=join and r['event']=='seat_input'))
    run['fall_clear_notifications']=run['counts'].get('sync_fall_overlay_invoking',0)
    run['native_fall_repairs']=run['counts'].get('bastion_native_passenger_fall_cleared',0)
    run['tank_exit_pairs']=run['counts'].get('tank_driver_exit_returned',0)
    poses=collections.defaultdict(collections.Counter);model=None
    for row in rows:
        if row['event']=='integrated_state':model=json.loads(row['detail']).get('vehicle')
        if row['event']=='animation_watch_sample':poses[model][row['states'][8]]+=1
    run['overlay_by_vehicle']={k:dict(v)for k,v in poses.items()}
(C/'analysis.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
join=a['runs'][0];host=a['runs'][1];guest=a['runs'][3]
text=f'''# 0.18.3采集结论与0.19.0多人多车定位

四次启动按你的说明归类：首次第三人中途加入；第二次你当房主；第三次上船闪退排除；第四次朋友当房主。原始日志已经单独保存并计算哈希，后续启动不会覆盖本次依据。

| 启动 | 跨区完成 | 结论 |
| --- | --- | --- |
| 18:48:29 | Bastion8次，第三人加入前 | 加入后被旧包人数限制拒绝 |
| 18:57:44，你当房主 | Bastion6 + Maelstrom6 | 你确认朝向与其他操作正常，自旋未修复 |
| 19:07:08 | 无 | 按你的要求排除上船闪退，不用于换座判断 |
| 19:08:26，朋友当房主 | Bastion6 + Maelstrom6 | 你确认Bastion身体/弹道朝向正常，自旋未修复 |

三次有效启动均正常结束，读取缺口和传输记录丢失为0。采集并不说明每条原计划路线都执行了；验收按你实际反馈和已记录路线处理。

第三人加入发生于首次启动后{join['third_peer_join_ms']/1000:.3f}秒。之后明确记录cross_scope_unavailable {join['post_join_input_reasons'].get('cross_scope_unavailable',0)}次，没有integrated_stopped/error。不是这次加入引发脚本崩溃；它触发了旧包的双人功能边界。普通范围内路线与跨区路线不同，不能把所有按键都概括为程序已停用。

代码也说明了限制来源：adapter/capture只在恰好一个远端队友时选择destination；eligible、交易与驾驶清理均要求两人；sender只向一个远端发送座位、武器和动画消息；原控制者校验也假设唯一朋友在同车或车外。底层成员读取本来能容纳四人，限制主要在本模组已经验证的控制和同步流程中。

两轮Bastion姿态修复可记为通过。自旋尝试失败：第二/四次均有{host['tank_exit_pairs']}/{guest['tank_exit_pairs']}次原生驾驶关闭返回，active字段读回0，但你仍观察到自旋。因此不能把调用成功等同于车辆已经停止，也不能认定只缺少这个关闭调用就是根因。保持A时部分保留输入仍为-1；这些字段包括原生输入向量，未确认其物理用途前不盲目全部清零。

当前数据的缺口：三人记录没有完整读取所有玩家的控制权，没有多人分别驾驶A/B两车、原控制者转去另一车、第三/第四人占座及退出后的关系。直接去掉人数检查，会把车体原控制者、房主、驾驶者和通知接收者混在一起，尤其在客机和多车场景容易发错控制权/同步目标。

0.19.0为这组缺口增加只读定位，保留0.18.3双人功能；尚未启用三/四人跨区。每0.5秒轮流读一辆已识别车辆及全部玩家归属，加入/退出记录单独日志；坦克转向后每约0.1秒记录十秒驾驶状态。新模块不写游戏内存，不执行游戏函数、不发控制权/换座/武器/动画消息。原有双人功能仍按0.18.3执行其调用。单个观察读取失败只写gap，不将输入功能设为失败。

需要一组新的三/四人与多车原生基线。至少三人，四人可选；两种房主各一次，合并中途加入、同车占座、两辆车/两个驾驶者、原控制者在另一车、离开恢复双人。两辆车足够，不重测全车型。具体见0.19.0说明。坦克自旋对照可在同次启动的双人阶段顺带采集，不是新的修复验收。

后续实现顺序：先用实际成员和所有玩家归属校验当前车全部占用/预留；控制权只请求当前车真实原控制者；只修改安装者的角色/武器；将已验证的原生同步按成员逐一发给所有其他相关客户端；归还只给原控制者、不能交给别车驾驶者或第三人；加入/退出在空闲时刷新，在未完成交易时保留控制权清理。原控制者在别车时不操作那辆车、不改变其驾驶输入。四人实际接收结果仍需新实机验证。

正式单人加强版整合、最终普通/加强可选发布包与坦克自旋修复仍未完成。旧0.18.3及正式0.2.4文件保留，未修改游戏/Arsenal正在使用的配置。
'''
dest=P/'outputs/Vehicle-Seat-0.18.3-采集结论与多人多车研究-20261002.md'
dest.write_text(text,encoding='utf-8')
print(json.dumps([dict(name=r['name'],completed=r['completed'],post_join=r['post_join_input_reasons'],overlay=r['overlay_by_vehicle'])for r in a['runs']],ensure_ascii=False,indent=2))
print(dest)
