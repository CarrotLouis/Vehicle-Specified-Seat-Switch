"""Analyze immutable user captures; narrow absence claims to the15 watched RPCs."""
from pathlib import Path
import collections, datetime, hashlib, json
R=Path(__file__).resolve().parent/'capture-20260927'
reports=[]
for p in sorted(R.glob('VehicleSeatTransport-*.log')):
    es=[json.loads(l)for l in p.read_text().splitlines()]
    native=[e for e in es if e['event'].startswith('native_')]
    states=[e for e in es if e['event']=='state']
    ready=next(e for e in es if e['event']=='transport_ready')
    stop=next(e for e in es if e['event']=='transport_stopped')
    assert [e['sequence']for e in native]==list(range(1,len(native)+1))
    assert all(e['valid_mask']==(1<<e['argument_count'])-1 for e in native)
    assert stop['events']==len(native)and stop['dropped_total']==stop['restore_flags']==0
    assert stop['reason']=='shutdown'and len(ready['registry'])==15
    assert not any(e['event'] in ('read_gap','protocol_gap','size_limit') for e in es)
    wall=datetime.datetime.strptime(''.join(p.name.split('-')[1:3]),'%Y%m%d%H%M%S')
    def time(e):return (wall+datetime.timedelta(milliseconds=e['t'])).strftime('%H:%M:%S.%f')[:12]
    def simplify(e):
        d=e['data'];vehicles={v['id']:v for v in d['vehicles']}
        avatars=[]
        for a in d['avatars']:
            seat=a.get('seat',{})
            avatars.append(dict(id=a['id'],net=a['network_unit'],local=a['is_local'],
              collection=seat.get('collection'),seat=seat.get('current'),role=seat.get('role'),
              reserved=seat.get('reserved'),target=seat.get('target'),action=seat.get('action'),
              transitioning=seat.get('transitioning')))
        return dict(avatars=avatars,vehicles=[dict(id=v['id'],net=v['network_unit'],name=v['name'],
               owned=v['owned_local'],free=v['free_mask'])for v in vehicles.values()])
    changes=[];last=None;switches=[];previous_local=None
    for e in states:
        brief=simplify(e)
        if brief!=last and brief['vehicles']:
            changes.append(dict(t=e['t'],wall_approx=time(e),**brief))
        last=brief
        a=next((a for a in brief['avatars'] if a['local']),None)
        if a and previous_local:
            b=previous_local
            if (a['collection']==b['collection'] and a['collection'] and
                a['seat']!=b['seat'] and a['role']!=b['role'] and
                a['transitioning']==b['transitioning']==0 and {a['seat'],b['seat']}<={0,1,2,3}):
                nearby=[n for n in native if abs(n['t']-e['t'])<=250]
                # These are observed instant stable-state changes, correlated with
                # TankSeatSwitch.log; neither key presses nor all engine traffic.
                switches.append(dict(t=e['t'],wall_approx=time(e),before=b,after=a,
                  vehicle=next(v for v in brief['vehicles']if v['id']==a['collection']),
                  nearby_native=nearby,
                  seat_rpc_count=sum(n['message']in('accepted','snapshot','transition','switch_request')for n in nearby)))
        previous_local=a
    counts=collections.Counter((e['event'],e['message'])for e in native)
    report=dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),records=len(es),
      native_count=len(native),continuous_sequence=True,complete_arguments=True,gaps=[],stop=stop,
      messages=[dict(direction=k[0],message=k[1],count=v)for k,v in counts.items()],
      direct_switches=switches,state_changes=changes,
      native=[dict(wall_approx=time(e),**e)for e in native])
    reports.append(report)
(R/'analysis.json').write_text(json.dumps(reports,indent=2))
lines=[]
for r in reports:
    lines.append(r['file']+'\n')
    for e in sorted([dict(kind='STATE',**s)for s in r['state_changes']]+
                    [dict(kind='RPC',**s)for s in r['native']],key=lambda e:e['t']):
        if e['kind']=='STATE':
            aa=' '.join(('self'if a['local']else'friend')+f"={a['collection']}:{a['seat']}/role{a['role']}/res{a['reserved']}/target{a['target']}/moving{a['transitioning']}"for a in e['avatars'])
            vv=' '.join(f"vehicle{v['id']} owned={v['owned']} free={v['free']}"for v in e['vehicles'])
            lines.append(f"{e['wall_approx']} {aa} {vv}")
        else:lines.append(f"{e['wall_approx']} {e['event']} {e['message']} {e['values']} peers={e['peers']}")
(R/'timeline.txt').write_text('\n'.join(lines),encoding='utf8')
for r in reports:
    print(r['file'],'native',r['native_count'],'direct',len(r['direct_switches']))
    for s in r['direct_switches']:
        print(s['wall_approx'],s['before']['seat'],'->',s['after']['seat'],'owner',s['vehicle']['owned'],
              'seat_RPCS',s['seat_rpc_count'],'messages',[(n['message'],n['values'])for n in s['nearby_native']])
