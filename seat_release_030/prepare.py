"""Stage a production-only composition. Never modify accepted research sources."""
from pathlib import Path
import hashlib, json

R = Path(__file__).resolve().parent
W = R.parent
P = W.parent
G = W / 'seat_switch/src'
B = W / 'seat_pose_trace_test'
N = W / 'seat_network_diagnostic'
I = W / 'seat_interface_diagnostic'
T = W / 'seat_transport_diagnostic'
A = W / 'seat_authority_diagnostic'
Q = W / 'seat_protocol_diagnostic'
V = W / 'seat_multiplayer_reservation_test'
S = R / 'src'
S.mkdir(exist_ok=True)
origins = {}

def stage(name, path, transform=None):
    before = path.read_text(encoding='utf-8')
    after = transform(before) if transform else before
    (S / name).write_text(after, encoding='utf-8', newline='\n')
    origins[name] = {
        'path': path.relative_to(P).as_posix(),
        'original_sha256': hashlib.sha256(before.encode()).hexdigest(),
        'staged_sha256': hashlib.sha256(after.encode()).hexdigest(),
        'changed': before != after,
    }

for name in ['profile', 'module_hash', 'input', 'policy', 'config', 'snapshot', 'controller', 'native']:
    stage(name + '.lua', G / (name + '.lua'))
stage('normal_compat.lua', G / 'compat.lua')
stage('normal_compat_spec.lua', G / 'compat_spec.lua')
stage('normal_platform.lua', G / 'platform.lua')
stage('normal_entry.lua', G / 'entry.lua', lambda b: b.replace("version='0.2.4'", "version='0.3.0'"))
stage('compat.lua', V / 'compat.lua')
for name in ['compat_spec', 'trace_points']:
    stage(name + '.lua', Q / (name + '.lua'))
stage('messages.lua', T / 'messages.lua')
stage('routing_spec.lua', I / 'routing_spec.lua')
stage('authority_spec.lua', A / 'authority_spec.lua')
for name in ['sync_spec', 'animation_spec', 'binding_spec', 'tank_spec', 'spin_spec', 'pose_spec',
             'inspect', 'animation_sender', 'personal', 'pose', 'input_gate', 'input_helper', 'observe']:
    stage(name + '.lua', B / (name + '.lua'))
for name in ['reservation_spec', 'binding_counts_spec', 'binding_inspect', 'binding_sender',
             'transaction', 'sender', 'scope', 'membership', 'entrance', 'probe',
             'mounted_reader', 'spin_reader', 'release_acquired']:
    stage(name + '.lua', V / (name + '.lua'))
for name, path in [('sampler.lua', N / 'sampler.lua'), ('pages.lua', I / 'pages.lua'),
                   ('observer.lua', I / 'observer.lua'), ('routing.lua', T / 'routing.lua')]:
    stage(name, path)

def platform(b):
    normal = (G / 'platform.lua').read_text(encoding='utf-8')
    directory = normal[normal.index(' function a.config_directory()'):normal.index(' function a.module(name)')]
    b = b.replace(' ffi.cdef[[', ' ffi.cdef[[\n int CreateDirectoryA(const char *,void *);\n uint32_t GetFileAttributesA(const char *);', 1)
    return b.replace(' function a.module(name)', directory + ' function a.module(name)', 1)
stage('platform.lua', B / 'platform.lua', platform)

def solo_scope(b):
    assert 's.player_count>=2' in b
    return b.replace('s.player_count>=2', 's.player_count>=1')
for name, path in [('owned_transaction.lua', V / 'owned_transaction.lua'),
                   ('owned_base.lua', B / 'transaction.lua'), ('owned_driver.lua', B / 'driver.lua'),
                   ('owned_tank_driver.lua', B / 'tank_driver.lua')]:
    stage(name, path, solo_scope)

def steering(b):
    b = solo_scope(b)
    b = b.replace(' local watched,next_at,until_at=nil,0,0\n', '')
    assert '   watched=after.vehicle;next_at=api.now();until_at=next_at+3' in b
    b = b.replace('   watched=after.vehicle;next_at=api.now();until_at=next_at+3\n', '')
    b = b[:b.index(' function self:update(sample)')] + ' return self\nend\n'
    return b
stage('steering_reset.lua', V / 'steering_reset.lua', steering)

def adapter(b):
    start = b.index('function M.new(')
    end = b.index(' function self:eligible', start)
    body = b[start:end]
    summary_start = body.index('  local occupants={}')
    summary_end = body.index('  return c', summary_start)
    body = body[:summary_start] + body[summary_end:]
    return ('-- Only fresh context capture is retained; no chassis-loan methods.\n'
            'local M={}\n' + b[b.index('local function seated('):b.index('-- Captured normal exit')] +
            body + ' return self\nend\nreturn M\n')
stage('adapter.lua', V / 'adapter.lua', adapter)

def dispatcher(b):
    # Polling and input interception remain at frame cadence; expensive ownership
    # observation is only useful while seated in a supported multiplayer vehicle.
    old = 'if now>=self.next_probe or probe.pending then'
    new = 'if probe.pending or (now>=self.next_probe and s and s.player_count>=2 and s.player_count<=4) then'
    assert old in b
    return b.replace(old, new, 1)
stage('dispatcher.lua', B / 'dispatcher.lua', dispatcher)

def transport(b):
    b = b.replace(" local ffi,bit=require('ffi'),require('bit')", " local ffi=require('ffi')", 1)
    a = b.index(' local function peer(value)')
    z = b.index(' function self:start()', a)
    b = b[:a] + b[z:]
    b = b.replace("version='0.30.0'", "version='0.3.0'")
    b = b.replace("three_writable_data_slots; exact_pending_own_accepted_gate; other_original_calls_forwarded",
                  "receive_slot_only; exact_pending_own_accepted_gate; outgoing_slots_unchanged; recording_disabled")
    a = b.index(' function self:drain()')
    z = b.index(' function self:health()', a)
    b = b[:a] + b[z:]
    b = b.replace("buffer=ffi.new('VSST_Record[256]')", 'buffer=nil')
    b = b.replace('self:drain();self.active=false', 'self.active=false')
    return b
stage('transport.lua', V / 'transport.lua', transport)

for name in ['native.c', 'gate.c', 'bridge.S', 'watched.h', 'test_gate.c']:
    (R / name).write_bytes((V / name).read_bytes())

native = (R / 'native.c').read_text(encoding='utf-8')
native = native.replace('static uintptr_t game_base,game_end,exe_base,exe_end;',
                        '#if !defined(VSS_NO_RECORDS) || !defined(VSS_TESTING)\n'
                        'static uintptr_t game_base,game_end,exe_base,exe_end;\n#endif', 1)
native = native.replace('static uint64_t head,tail,serial;',
                        'static uint64_t head,tail;\n#ifndef VSS_NO_RECORDS\nstatic uint64_t serial;\n#endif', 1)
native = native.replace('void vss_capture(const uint64_t *ctx,uint32_t kind){',
                        'void vss_capture(const uint64_t *ctx,uint32_t kind){\n'
                        '#ifdef VSS_NO_RECORDS\n (void)ctx;(void)kind;return;\n#else', 1)
native = native.replace(' head++;ReleaseSRWLockExclusive(&lock);SetLastError(saved);\n}',
                        ' head++;ReleaseSRWLockExclusive(&lock);SetLastError(saved);\n#endif\n}', 1)
native = native.replace('static int watched(uint32_t hash)', '#ifndef VSS_NO_RECORDS\nstatic int watched(uint32_t hash)', 1)
native = native.replace(' default:return 0;}}', ' default:return 0;}}\n#endif', 1)
native = native.replace('if(v!=bridges[i])flags|=1u<<i;', 'if(v!=bridges[i])flags|=1u<<i;')
old = 'for(int i=0;i<N;i++){void *v=NULL;if(!read_memory((uintptr_t)bindings[i].slot,&v,8)||v!=bridges[i])flags|=1u<<i;}'
new = ('for(int i=0;i<N;i++){void *v=NULL;void *expected=bridges[i];\n'
       '#ifdef VSS_NO_RECORDS\n if(i<2)expected=bindings[i].target;\n#endif\n'
       ' if(!read_memory((uintptr_t)bindings[i].slot,&v,8)||v!=expected)flags|=1u<<i;}')
assert old in native
native = native.replace(old, new, 1)
native = native.replace(' for(int i=0;i<N;i++){\n  int forced=0;',
                        ' for(int i=0;i<N;i++){\n#ifdef VSS_NO_RECORDS\n  if(i<2)continue;\n#endif\n  int forced=0;', 1)
(R / 'native.c').write_text(native, encoding='utf-8', newline='\n')
(R / 'origins.json').write_text(json.dumps(origins, indent=2), encoding='utf-8')
print('STAGED production dependencies; existing gameplay/research/ZIPs unchanged')
