from pathlib import Path
import collections, hashlib, json, struct

W = Path(__file__).resolve().parent
R = W / 'seat_multi_peer_research/capture-20261002-0183'
R.mkdir(parents=True, exist_ok=True)
L = Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
names = [
 ('VehicleSeatIntegrated-20261002-184829-26948-156450000.log', 'third_peer_join'),
 ('VehicleSeatIntegrated-20261002-185744-19936-157005250.log', 'installer_host'),
 ('VehicleSeatIntegrated-20261002-190708-37532-157568937.log', 'excluded_ship_join_crash'),
 ('VehicleSeatIntegrated-20261002-190826-37816-157647218.log', 'friend_host'),
 ('VehicleSeatIntegratedDiagnostic.log', 'status'), ('BingusSharedLoader.log', 'loader')]
files=[]
for name, role in names:
    data=(L/name).read_bytes()
    dest=R/name
    if dest.exists():
        assert dest.read_bytes() == data, 'Frozen evidence differs: '+name
    else:
        dest.write_bytes(data)
    files.append(dict(name=name, role=role, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
(R/'files.json').write_text(json.dumps(files, ensure_ascii=False, indent=2), encoding='utf-8')
runs=[]
for name,role in names[:4]:
    rows=[json.loads(l) for l in (R/name).read_text(encoding='utf-8-sig').splitlines()]
    counts=collections.Counter(r['event'] for r in rows)
    model=None; completed=collections.Counter(); scopes=[]; last_scope=None; important=[]; exits=[]
    for i,row in enumerate(rows):
        e=row['event']
        if e=='integrated_state':
            d=json.loads(row['detail']); model=d.get('vehicle'); scope=last_scope
        elif e=='state':
            d=row['data']; scope=(d.get('player_count'),d.get('peer_count'))
        else: scope=last_scope
        if scope != last_scope:
            scopes.append(dict(line=i+1,t=row.get('t'),scope=scope, event=e, row=row))
            last_scope=scope
        if e=='integrated_operation_complete': completed[model]+=1
        if any(s in e for s in ['stopped','cancel','abort','error','incomplete','rejected','waiting']):
            if e != 'integrated_waiting' or row.get('reason') not in ['not_in_mission']:
                important.append(dict(line=i+1,**row))
        if e.startswith('tank_driver_exit_'):
            raw=bytes.fromhex(row['driver_command_hex'])
            exits.append(dict(line=i+1,**row,command_float=struct.unpack('<12f',raw),command_bytes=list(raw)))
    runs.append(dict(name=name,role=role,version=rows[0].get('version'),counts=dict(counts),
        completed=dict(completed),scopes=scopes,important=important,driver_exits=exits,
        clean_shutdown=rows[-1]['event']=='end',read_gaps=counts['read_gap'],
        drops=sum(r.get('dropped_total',0) for r in rows if r['event']=='transport_stopped')))
result=dict(runs=runs, user_report='Four starts: third-peer join disables mod; installer-host and friend-host accepted Bastion aim/other behavior, tank spin persists; ship-join crash explicitly excluded.',
            conclusions='No new repair accepted by code-return alone. Analyze peer guards/fanout and per-vehicle ownership; native tank deactivation did not resolve persistent physical steering.')
(R/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for r in runs:
    print(json.dumps({k:v for k,v in r.items() if k not in ['counts','scopes','driver_exits','important']},ensure_ascii=False))
    print('SCOPES',json.dumps([dict(line=s['line'],t=s['t'],scope=s['scope'],event=s['event']) for s in r['scopes']],ensure_ascii=False))
    print('IMPORTANT',json.dumps([a for a in r['important'] if a['event'] != 'integrated_waiting' or a.get('reason') != 'vehicle_not_observed'],ensure_ascii=False))
    print('EXITS',json.dumps([dict(line=e['line'],t=e['t'],vehicle=e['vehicle'],event=e['event'],active=e['driver_active'],first6=e['command_float'][:6]) for e in r['driver_exits']],ensure_ascii=False))
