local policy = assert(loadfile('work/seat_release_041/src/policy.lua'))()
local groups = {
    m102 = {driver=1,front_passenger=1,rear_left=2,rear_right=2,gunner=3},
    m103 = {driver=1,front_passenger=1,rear_left=2,rear_right=2},
    m104 = {driver=1,front_passenger=1,flamer=2},
    bastion = {driver=1,gunner=2,passenger_left=2,passenger_right=2},
    maelstrom = {driver=1,gunner=2,passenger_left=2,passenger_right=2},
    tanker = {driver=1,gunner=1},
}
local checked = 0
for vehicle, seats in pairs(policy.seats) do
    for _, from in ipairs(seats) do for _, to in ipairs(seats) do
        for _, mode in ipairs({'normal','enhanced'}) do
            local expected = from ~= to and (mode == 'enhanced' or groups[vehicle][from] == groups[vehicle][to])
            assert(policy.check(mode,vehicle,from,to,false) == expected, vehicle..':'..mode..':'..from..'>'..to)
            assert(policy.check(mode,vehicle,from,to,true) == false)
            assert(policy.check(mode,vehicle,from,to,nil) == false)
            checked = checked + 3
        end
    end end
end
assert(policy.check('normal','unknown','driver','gunner',false) == false)
assert(policy.check('typo','tanker','driver','gunner',false) == false)
assert(policy.check('enhanced','tanker','unknown','gunner',false) == false)
print('PASS: '..checked..' matrix checks + invalid context checks. Logical rules only; no native integration claim.')
