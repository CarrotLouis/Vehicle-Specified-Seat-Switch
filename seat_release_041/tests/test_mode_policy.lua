local root='work/seat_release_041/src/'
local base=assert(loadfile(root..'policy.lua'))()
local mode='normal';local limited=assert(loadfile(root..'mode_policy.lua'))()(base,function()return mode end)
local identity=limited;local cases=0
for _,selected in ipairs({'normal','enhanced','normal','enhanced'})do
 mode=selected;assert(limited==identity and limited.seats==base.seats)
 assert(limited.direct_allowed()==(selected=='enhanced'))
 for vehicle,seats in pairs(base.seats)do
  for _,source in ipairs(seats)do for _,target in ipairs(seats)do
   for _,occupied in ipairs({false,true})do
    local a,why=limited.check('enhanced',vehicle,source,target,occupied)
    local expected,reason=base.check(selected,vehicle,source,target,occupied)
    assert(a==expected and why==reason)
    local native,nwhy=limited.check('normal',vehicle,source,target,occupied)
    local n,nreason=base.check('normal',vehicle,source,target,occupied)
    assert(native==n and nwhy==nreason);cases=cases+1
   end
  end end
 end
end
mode='normal';assert(not limited.check('enhanced','m102','front_passenger','gunner',false))
mode='enhanced';assert(limited.check('enhanced','m102','front_passenger','gunner',false))
assert(not limited.check('enhanced','m102','front_passenger','gunner',true))
print('PASS '..cases..' resident-policy cases: Normal is a pure Lua subset, Enhanced/native rules, vacancy and stable object identity')
