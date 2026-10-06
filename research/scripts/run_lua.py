"""Run authored offline Lua tests using the local game's LuaJIT runtime."""
import ctypes, pathlib, sys, os
dll=ctypes.CDLL(os.getenv('HD2_LUA51_DLL',r'F:\SteamLibrary\steamapps\common\Helldivers 2\bin\lua51.dll'))
dll.luaL_newstate.restype=ctypes.c_void_p
dll.luaL_openlibs.argtypes=[ctypes.c_void_p]
dll.luaL_loadstring.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
dll.lua_pcall.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int]
dll.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.POINTER(ctypes.c_size_t)]
dll.lua_tolstring.restype=ctypes.c_char_p
dll.lua_close.argtypes=[ctypes.c_void_p]
state=dll.luaL_newstate();assert state
try:
    dll.luaL_openlibs(state)
    source=pathlib.Path(sys.argv[1]).read_bytes()
    rc=dll.luaL_loadstring(state,source)
    if rc==0:rc=dll.lua_pcall(state,0,-1,0)
    if rc:raise RuntimeError(dll.lua_tolstring(state,-1,None).decode('utf-8','replace'))
finally:dll.lua_close(state)
