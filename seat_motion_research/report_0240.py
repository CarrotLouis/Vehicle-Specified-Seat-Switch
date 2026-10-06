"""Evidence-derived handoff summary, with invocation/completion kept separate."""
from pathlib import Path
import collections
import json
import math

R = Path(__file__).resolve().parent
P = R.parent.parent
C = R / 'capture-20261004-0240'
report = json.loads((C / 'analysis.json').read_text(encoding='utf-8'))
def norm(v): return math.sqrt(sum(x*x for x in v))
summary = []
for role in ['host', 'guest']:
    for op in report[role]['operations']:
        boundaries = {s['stage']: s for s in op['samples'] if s['stage'] != 'background'}
        before = boundaries['before_authority_return']
        after = boundaries['first_observed_authority_return']
        assert after['owner'] == 'P2' and before['owner'] == 'P1'
        assert after['owner_serial'] == before['owner_serial']+1
        event_types = collections.Counter(e['event'] for e in op['events'])
        for event in ['integrated_acquired', 'integrated_return_invoked',
                      'integrated_ownership_return_confirmed', 'integrated_loan_operation_complete']:
            assert event_types[event] == 1
        poses = sorted((c for c in op['calls'] if c['kind'] == 'world_pose_request'), key=lambda c: c['sequence'])
        assert len(poses) == 2
        assert all(c['valid_mask'] == 1 and c['caller_rva_hex'] == '0x7143d7' for c in poses)
        fresh = next(s for s in op['samples'] if s['sample_t'] >= after['sample_t']
                     and s.get('rep_peer') == s.get('engine_peer'))
        tail = [s for s in op['samples'] if fresh['sample_t'] <= s['sample_t'] <= fresh['sample_t']+500][-1]
        summary.append(dict(
            role=role, operation=op['number'], before_return_speed=before['native_speed'],
            first_return_speed=after['native_speed'], return_sample_t=after['sample_t'],
            pose_call_times=[c['call_t'] for c in poses], pose_positions=[c['position'] for c in poses],
            first_fresh_driver_sample_t=fresh['sample_t'], fresh_driver_rep_speed=norm(fresh['rep_velocity']),
            fresh_driver_rep_velocity=fresh['rep_velocity'],
            first_fresh_driver_position=fresh['rep_position'], later_driver_position=tail['rep_position'],
            driver_position_delta=math.dist(fresh['rep_position'], tail['rep_position']),
            driver_position_interval_seconds=(tail['sample_t']-fresh['sample_t'])/1000,
            caller_observation='API entry only; deferred callback completion unknown',
            trial_condition='Extra host trials unlabelled; first two follow prescribed order only by inference',
        ))
calls = [c for role in ['host', 'guest'] for op in report[role]['operations'] for c in op['calls']]
proof = dict(operations=summary, api_call_counts=dict(collections.Counter(c['kind'] for c in calls)),
             exact_zero_velocity_requests=sum(c['kind']=='velocity_request' and c.get('speed')==0 for c in calls),
             body_flag_counts=dict(collections.Counter(s['body_flags']['flags'] for role in ['host','guest']
                 for op in report[role]['operations'] for s in op['samples'] if s.get('body_flags'))),
             observed_process='installer only', failed_join_excluded=True, all_six_returns_complete=True,
             native_record_gaps=False, native_callback_completion_observed=False,
             friend_process_observed=False, repair_enabled=False)
(C / 'motion-correlation.json').write_text(json.dumps(proof, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
table = ['|安装者身份 / 次数|归还前本机物理速度|首次归还样本速度|驾驶者新同步速度|随后同步位置移动|',
         '|---|---:|---:|---:|---:|']
for s in summary:
    role = '房主' if s['role']=='host' else '客机'
    table.append(f"|{role} / {s['operation']}|{s['before_return_speed']:.3f}|{s['first_return_speed']:.3f}|"
                 f"{s['fresh_driver_rep_speed']:.3f}|{s['driver_position_delta']:.3f} / {s['driver_position_interval_seconds']:.3f} 秒|")

body = '''# 0.24.0 采集结论与驾驶者配对观察

两局有效记录均可用：安装者房主共4次借还，安装者客机共2次借还，全部正常归还。中间无法加入房间的启动单独保存并排除。没有读取缺失、调用记录丢失或退出清理错误；112项接口验证通过，游戏指纹未变。
诊断start记录Loader接口版本为17，Loader自身日志标记loader-v18，两者原样保留，不根据标签差异推断不兼容。Loader还载入FRV Multiselect、Helmet Headlamp和Driver HUD，不能宣称本次完全没有其他mod；这些记录仍可用于确认调用路径，下次配对时按说明暂时只启用各自诊断与Loader，以减少混杂。

## 已确认的区别

安装者房主第1、3次，归还后朋友的新同步位置仍持续前进；第2、4次显著失速。安装者客机两次同样明显失速，松W的那次停住。这里保留用户报告的双方观察差异，不把安装者的远端物理体速度直接当作朋友实际车速。
房主额外重复的具体W条件没有日志标记，不擅自给它们分组。开火/移动等额外按键也不根据次数推断。

以下速度均为原生物理单位，不是仪表盘km/h；同步速度只有水平分量，采样间隔与位置可用于区分短暂本机顿挫和持续停车。

''' + '\n'.join(table) + '''

## 新抓到的原生路径

本机共514个指定底盘API进入记录：502次速度设置、12次位置设置。每次借还都出现两次位置设置，调用来自游戏的远端载具运动更新首样本分支（game.dll相对地址0x7143d7）。参数、调用来源和物理体标志均完整，没有采集丢失。
所有135个相关标志样本为65674，最低位为0。之前保存的两版原生代码离线执行已经证明：位置API先排入物理队列，队列回调按此标志会设置位置并清线速度/角速度。现在确认真实交接经过这个API入口；尚未记录实际队列回调的执行完成。

位置首次设置附近，本机速度由约15.1–22.3降至首次归还样本的约0.067–0.218；但有两次房主触发仍收到持续运动的位置/速度。这说明本机的位置重置/暂时静止，与朋友端真正停车是需要区分的两段过程。
第二次首样本设置伴随驾驶者的新运动发布者/时间纪元到达。失败的交接中，这时已经有低速数据；成功的两次仍是高速数据。单靠安装者日志无法确定驾驶者的速度在失去控制权时、重新取得控制权时还是另一条原生回调中被清掉。

不能把API进入记录宣称为回调执行完成；也不能据此直接写回旧速度、修改物理标志或跳过游戏的交接回调。那些做法可能掩盖问题或破坏新的控制/碰撞状态，目前没有启用。

## 本轮新产物与下一次最少采集

朋友用Vehicle-Seat-Driver-Observer-0.25.0.zip，安装者继续用已验证且未改变的Vehicle-Seat-Weapon-Sync-Diagnostic-0.24.0.zip。两包分别装在两台电脑，不要在同一台电脑并用。
朋友包自动记录双人M102的本地驾驶位，最长120秒，最多20Hz；原生观察助手与0.24.0完全相同。没有换座、控制权调用、速度/位置写入、输入拦截或网络拦截；不访问INI。原函数照常执行，只有两个可写Actor API槽转接观察。
接口验证在启动时完成并缓存；仅观察一个经过身份核对的底盘。脚下/其他车型/非双人/超过窗口时不读物理与运动属性，未开启采集和其他物体调用走原有快速路径，不反复全扫内存。未测量CPU或帧率百分比，诊断采集不进入最终发布版。

只需一局朋友当房主：持续W、松W滑行各一次。完整操作与朋友要发的三个日志见0.25.0说明。无需重测安装者房主、其他车型、坦克基线或第三/第四人。
朋友安装仅为补齐双端证据，不改变最终“只由功能使用者安装”的要求。完成本轮后再决定具体修复，不能把只读包当作修复完成。

## 验证和保存

新包的自动驾驶者范围/两种M102资源/控制权变化/两分钟期限/下车重入/失效隔离/原update与shutdown返回值/日志失败清理均通过离线验证。两版保存模块均通过112项接口和原有物理/同步属性读取验证；打包资源逐字节核对已编译Lua，ZIP完整性通过，隔离Arsenal导入/部署/清理通过。
0.24.0原源码与九个旧产物校验值保持不变。未修改本机游戏、真实Arsenal配置或INI，未启动游戏。真实朋友端观察仍待本轮采集。
坦克自旋、三/四人完整验收和行进中跨区换座修复仍未完成；本次继续优先定位减速。坦克已有离线输入和原生属性发布证据，本次不重复正常驾驶采集。

证据：work/seat_motion_research/capture-20261004-0240保存原日志、SHA256、analysis.json及motion-correlation.json。新源文件在work/seat_driver_observer，旧源文件保持原处。
'''
(P / 'outputs/Vehicle-Seat-0.24.0采集结论与驾驶者配对说明.md').write_text(body, encoding='utf-8')
print(json.dumps({k:v for k,v in proof.items() if k!='operations'}, ensure_ascii=False))
