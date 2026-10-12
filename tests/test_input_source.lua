local r='work/src/'
local function m(n)return assert(loadfile(r..n..'.lua'))()end
local config,policy,input=m('config'),m('policy'),m('input')
local keys=assert(config.parse(config.template()));local held,actions={},{}
local api={down=function(k)return held[k]or false end,focused=function()return true end,input_allowed=function()return true end}
local ids=m('menu').ids;local menus={binding_registered={true,true,true,true,true},bindings={is_down=function(id)return actions[id]end}}
local p=m('input_source').new(keys,api,input,policy,menus,ids)
local function frame(focus)p:sample_menu(focus);return p:poll(focus)end
held[112]=true;assert(frame(true)[112]);held[112]=nil;frame(true)
p:set_strategy('menu');held[112]=true;assert(next(frame(true))==nil,'physical INI leaked')
for _,id in ipairs(ids)do actions[id]=false end;frame(true)
actions[ids[1]]=true;p:sample_menu(true);actions[ids[1]]=false;p:sample_menu(true)
local press=p:poll(true);assert(press[p.keys.m102.driver]and not press[112],'one-frame native pulse lost or converted to physical input')
assert(next(frame(true))==nil)
actions[ids[3]]=true;assert(frame(true)[p.keys.m104.flamer]);assert(next(frame(true))==nil,'Hold repeats')
actions[ids[3]]=nil;frame(true);actions[ids[3]]=true;assert(next(frame(true))==nil,'unavailable-to-held must not synthesize an edge')
actions[ids[3]]=false;frame(true);actions[ids[3]]=true;assert(frame(true)[p.keys.bastion.passenger_left])
-- Focus restoration, source restoration and simultaneous activations.
frame(false);assert(next(frame(true))==nil);actions[ids[3]]=false;frame(true)
actions[ids[1]]=true;actions[ids[2]]=true;press=frame(true);assert(press[p.keys.m103.driver]and press[p.keys.m103.front_passenger])
p:set_strategy('ini');assert(p.keys.m102.driver==keys.m102.driver and p.keys.m104.flamer==keys.m104.flamer)
assert(next(frame(true))==nil,'held INI key on source change fired')
held[112]=nil;frame(true);held[112]=true;assert(frame(true)[112])
assert(keys.m102.driver==112 and keys.m102.gunner==116,'source switch rewrote stored INI')
print('PASS independent INI/native sources, pulse capture, Hold edge, unavailable/focus/source barriers, role-index mapping and simultaneous inputs')

local free=assert(config.parse('[m102]\ndriver=MOUSE4+W\n'))
api.chords=config.chords;local arbitrary=m('input_source').new(free,api,input,policy,menus,ids)
held={[87]=true};assert(not arbitrary:held(),'Driving without the chord prefix forced seat snapshots')
held[5]=true;assert(arbitrary:held());held[5]=nil;assert(not arbitrary:held())
print('PASS incomplete free chords do not request fast snapshot refresh')

local platform=assert(loadfile('work/src/platform.lua'))()(function()error('No disk hashing in clock test')end)
local start=platform.clock();local last=start
for _=1,1000 do local now=platform.clock();assert(now>=last);last=now end
assert(last>start,'Runtime budget clock has no subframe resolution')
print('PASS actual Windows QPC startup-budget clock; monotonic and read-only')
