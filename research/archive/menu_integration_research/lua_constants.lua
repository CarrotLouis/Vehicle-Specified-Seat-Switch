local util=require('jit.util')
for _,name in ipairs({'0d4816de1d4771f1','19bc198a3e7bb327','2e42becd00d0b9d9','3425cb597039dd69','405896b911013778','7251fdd9bb62480a','78796ae20bb32759','79dc662443acf6f1','a95a92495dda0ba3','f476df93691895fa'})do
 local f=assert(io.open('work/lua_resources/'..name..'.lua.main','rb'));local b=f:read('*a');f:close()
 local chunk,err=loadstring(b:sub(9),'@'..name)
 if chunk then
  local function walk(fn,id)
   local info=util.funcinfo(fn);local ss={}
   for k=-1,-info.gcconsts,-1 do
    local v=util.funck(fn,k)
    if type(v)=='string'then ss[#ss+1]=v elseif type(v)=='proto'then walk(v,id..'/'..(-k))end
   end
   print(name..' '..id..' '..table.concat(ss,' | '))
  end
  walk(chunk,'root')
 else print(name,err)end
end
