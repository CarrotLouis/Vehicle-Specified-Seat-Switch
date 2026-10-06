local c=assert(loadfile('work/seat_switch/src/config.lua'))()
for _,r in ipairs({
 {'CTRL+SHIFT+HOME','LCTRL+SHIFT+HOME',1316,2340,true},
 {'CTRL+SHIFT+HOME','CTRL+LSHIFT+HOME',1316,1572,true},
 {'LCTRL+SHIFT+HOME','CTRL+LSHIFT+HOME',2340,1572,true},
 {'CTRL','CTRL+SHIFT+HOME',17,1316,true}, {'SHIFT','CTRL+SHIFT+HOME',16,1316,true},
 {'CTRL','LCTRL+SHIFT+HOME',17,2340,true}, {'CTRL+SHIFT+HOME','CTRL+ALT+HOME',1316,5156,false},
 {'CTRL+1','1',1073,49,false}, {'CTRL+SHIFT+MOUSE4','CTRL+SHIFT+MOUSE5',1285,1286,false},
 {'CTRL+MOUSE4','CTRL+SHIFT+MOUSE4',1029,1285,false}, {'F2','F5',113,116,false},
 {'CTRL+SHIFT+MOUSE4','CTRL+1',1285,1073,false}})do
 assert(c.key(r[1])==r[3] and c.key(r[2])==r[4] and c.overlap(r[3],r[4])==r[5])
end
local down={};local i=assert(loadfile('work/seat_switch/src/input.lua'))().new({m={a=113,b=116}},{focused=function()return true end,down=function(k)return down[k]end})
down={[113]=true,[116]=true};local result=i:poll(true);assert(result[113]and result[116])
print('PASS DS12 encodings/overlap cases; distinct primary keys can fire together')
