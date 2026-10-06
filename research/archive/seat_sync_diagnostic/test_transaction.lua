local factory=assert(loadfile('work/seat_sync_diagnostic/transaction.lua'))()
local names={'reserve','release','clear_vehicle_weapon','restore_personal_weapon','refresh_weapon_context','set_role','restore_seated','authority'}
local p={functions={}};local byaddress={};local calls,fail={},nil
for i,name in ipairs(names)do p.functions[name]={rva=i,bytes='x'};byaddress[i]=name end
local api={read=function()return 'x'end,ffi={cast=function(sig,at)return function(...)
 local name=byaddress[at];calls[#calls+1]=name
 if name=='restore_seated'then local args={...};assert(args[5]==1 and args[6]==false)end
 if name==fail then error('synthetic_'..name)end
end end}}
local function pose()return {check=function()calls[#calls+1]='check_pose';return true end,apply=function()calls[#calls+1]='pose';return 'validated'end}end
local function driver()return {prepare=function()calls[#calls+1]='prepare_driver';return function()calls[#calls+1]='neutralize'end end}end
local tx=factory(api,0,p,pose,driver,function()end)
local s={vehicle='bastion',transition=43,owned=true,player_count=2,peer_count=2,node=0,active=false,occupied={[1]=false},profile={roles={1,2}}}
local run=tx:prepare(s,1);assert(table.concat(calls,',')=='check_pose,prepare_driver')
calls={};run();assert(table.concat(calls,',')=='neutralize,reserve,clear_vehicle_weapon,clear_vehicle_weapon,restore_personal_weapon,refresh_weapon_context,release,set_role,restore_seated,pose,authority')
calls={};run=tx:prepare(s,1);calls={};fail='set_role';assert(not pcall(run));assert(calls[#calls]=='set_role')
s.occupied[1]=true;assert(not pcall(tx.prepare,tx,s,1))
print('PASS isolated local transaction prepares before mutation, final-pose order, stops on partial failure')
