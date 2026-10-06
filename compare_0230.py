from pathlib import Path
import json,math,collections
R=Path(__file__).resolve().parent/'seat_motion_research/capture-20261004-0230'
reports=json.loads((R/'analysis.json').read_text(encoding='utf-8'))
out={}
def norm(v):return math.sqrt(sum(x*x for x in v))
def short(v):return [round(x,4)for x in v]if isinstance(v,list)else v
def fields(r):
 h=r.get('handoff_properties')
 f=dict(t=r.get('t',r['t_sample_ms']-time_origin),stage=r['stage'],body_speed=r['native_speed'],body_velocity=r['linear_velocity'],
  body_position=r['physical_position'],owner=r.get('owner'),serial=r.get('owner_serial'))
 if h:
  p=h['properties']
  f.update(rep_velocity=p['linear_velocity']['component']['values'],raw_velocity=p['linear_velocity']['raw_engine']['values'],
   rep_position=p['position']['component']['values'],raw_position=p['position']['raw_engine']['values'],
   rep_peer=p['motion_peer']['component']['hex'],raw_peer=p['motion_peer']['raw_engine']['hex'],engine_peer=h['engine_owner_hex'],
   rep_time=p['motion_time']['component']['values'][0],raw_time=p['motion_time']['raw_engine']['values'][0],
   input=h['component_input']['values'],input_flag=h['component_input_flag'],
   clock=h['component_clock_hex'],mode=h['component_mode_hex'],
   cached=h['interpolation_cache_present'],reads=h['read_count'])
 return f
for role in ('host','guest'):
 report=reports[role];out[role]=[];time_origin=int(Path(report['name']).stem.rsplit('-',1)[1])
 samples=[s for op in report['operations']for s in op['samples']]
 print(role.upper(),len(report['operations']),'operations',len(samples),'physical samples',report['handoff_samples'],'properties',report['gap_reasons'])
 print('cache',dict(collections.Counter(s['handoff_properties']['interpolation_cache_present']for s in samples if 'handoff_properties'in s)))
 for op in report['operations']:
  fs=[fields(s)for s in op['samples']]
  record=dict(number=op['number'],samples=fs,pre_samples=[fields(s)for s in op['pre_samples']]);out[role].append(record)
  print('OP',op['number'])
  for f in fs:
   if f['stage']=='background':continue
   print(json.dumps({k:short(v)if isinstance(v,list)else round(v,4)if isinstance(v,float)else v for k,v in f.items()if k not in('body_position','raw_position','clock','mode','reads')},ensure_ascii=False))
  # The first 800ms after observed-return distinguishes a transient local-body
  # reset from sustained stop; do not override user observations automatically.
  ret=next(s for s in fs if s['stage']=='first_observed_authority_return')
  post=[{k:f.get(k)for k in('t','body_speed','body_position','rep_velocity','raw_velocity','rep_position','rep_time','rep_peer','input')}
        for f in fs if f['stage']=='background'and 0<f['t']-ret['t']<=800]
  print('POST',json.dumps(post,ensure_ascii=False))
(R/'handoff-comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
