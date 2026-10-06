-- Logical seat names only: native indices must be independently verified.
local M = {}
M.seats = {
    m102 = {'driver', 'front_passenger', 'rear_left', 'rear_right', 'gunner'},
    m103 = {'driver', 'front_passenger', 'rear_left', 'rear_right'},
    m104 = {'driver', 'front_passenger', 'flamer'},
    bastion = {'driver', 'gunner', 'passenger_left', 'passenger_right'},
    maelstrom = {'driver', 'gunner', 'passenger_left', 'passenger_right'},
    tanker = {'driver', 'gunner'},
}
local normal_groups = {
    m102 = {{'driver', 'front_passenger'}, {'rear_left', 'rear_right'}},
    m103 = {{'driver', 'front_passenger'}, {'rear_left', 'rear_right'}},
    m104 = {{'driver', 'front_passenger'}},
    bastion = {{'gunner', 'passenger_left', 'passenger_right'}},
    maelstrom = {{'gunner', 'passenger_left', 'passenger_right'}},
    tanker = {{'driver', 'gunner'}},
}
local function contains(list, item)
    for _, value in ipairs(list or {}) do if item == value then return true end end
    return false
end
function M.check(mode, vehicle, current, target, occupied)
    if mode ~= 'normal' and mode ~= 'enhanced' then return false, 'invalid_mode' end
    local seats = M.seats[vehicle]
    if not seats or not contains(seats, current) or not contains(seats, target) then
        return false, 'invalid_seat'
    end
    if current == target then return false, 'already_seated' end
    -- Unknown occupancy must never be treated as an empty seat.
    if occupied ~= false then return false, occupied == true and 'occupied' or 'unknown_occupancy' end
    if mode == 'enhanced' then return true end
    for _, group in ipairs(normal_groups[vehicle]) do
        if contains(group, current) and contains(group, target) then return true end
    end
    return false, 'normal_restriction'
end
return M
