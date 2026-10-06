local c=assert(loadfile("work/seat_release_030/src/config.lua"))(); local f=assert(io.open("work/seat_release_030/VehicleSeatSwitch.ini.example","wb"));assert(f:write(c.template()));f:close()
