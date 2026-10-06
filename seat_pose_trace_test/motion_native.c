/* Diagnostic observation at two writable Actor API slots. Original arguments,
   returns and calls are forwarded. No transform/velocity/game-state writes. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <string.h>
#define EXPORT __declspec(dllexport)
#define N 2
#define CAPACITY 4096
typedef struct {void **slot;void *target;uint8_t head[32];} Binding;
typedef struct {void **slot;void *target;} Guard;
typedef struct {
 uint64_t sequence,tick,qpc,caller;
 uint32_t kind,thread,actor,valid,caller_module,epoch;
 float values[16];uint64_t reserved;
} Record;
typedef char layout_check[sizeof(Record)==128 && sizeof(Binding)==48 && sizeof(Guard)==16?1:-1];
void *vssm_originals[N];
volatile LONG vssm_enabled,vssm_actor;
extern void vssm_bridge0(void),vssm_bridge1(void);
static void *bridges[N]={vssm_bridge0,vssm_bridge1};
static Binding bindings[N];static Guard guards[N];
static uintptr_t game_base,game_end,exe_base,exe_end;
static volatile LONG attempted;static volatile LONG64 dropped;
static uint64_t deadline,head,tail,serial;static uint32_t epoch;
static SRWLOCK lock=SRWLOCK_INIT;static Record ring[CAPACITY];
#ifdef VSS_TESTING
int vssm_test_fail_slot=-1;
#endif
static int read_memory(uintptr_t p,void *out,SIZE_T n){
 SIZE_T got=0;return p>=65536 && p<((uint64_t)1<<47) && n<=64 && p+n>=p && ReadProcessMemory(GetCurrentProcess(),(void*)p,out,n,&got) && got==n;
}
static int writable(void *p){
 MEMORY_BASIC_INFORMATION m;if((uintptr_t)p%8 || !VirtualQuery(p,&m,sizeof(m)))return 0;
 return m.State==MEM_COMMIT && m.Protect==PAGE_READWRITE && (uintptr_t)p+8<=(uintptr_t)m.BaseAddress+m.RegionSize;
}
static int guarded(void){
 for(int i=0;i<N;i++){void *v=NULL;if(!read_memory((uintptr_t)guards[i].slot,&v,8)||v!=guards[i].target)return 0;}return 1;
}
void vssm_capture(const uint64_t *ctx,uint32_t kind){
 DWORD saved=GetLastError();
 if(!TryAcquireSRWLockExclusive(&lock)){InterlockedIncrement64(&dropped);SetLastError(saved);return;}
 uint64_t now=GetTickCount64();
 if(!vssm_enabled || (uint32_t)ctx[5]!=(uint32_t)vssm_actor || now>deadline){
  if(now>deadline)InterlockedExchange(&vssm_enabled,0);
  ReleaseSRWLockExclusive(&lock);SetLastError(saved);return;
 }
 if(head-tail>=CAPACITY){InterlockedIncrement64(&dropped);ReleaseSRWLockExclusive(&lock);SetLastError(saved);return;}
 Record *r=&ring[head%CAPACITY];memset(r,0,sizeof(*r));
 r->sequence=++serial;r->tick=now;LARGE_INTEGER q;QueryPerformanceCounter(&q);r->qpc=q.QuadPart;
 r->kind=kind;r->actor=(uint32_t)ctx[5];r->thread=GetCurrentThreadId();r->epoch=epoch;
 uintptr_t caller=ctx[8];
 if(caller>=game_base&&caller<game_end){r->caller_module=1;r->caller=caller-game_base;}
 else if(caller>=exe_base&&caller<exe_end){r->caller_module=2;r->caller=caller-exe_base;}
 if(kind==0){if(read_memory(ctx[4],r->values,64))r->valid=1;}
 else {
  if(ctx[4]&&read_memory(ctx[4],r->values,12))r->valid|=1;
  if(ctx[3]&&read_memory(ctx[3],r->values+4,12))r->valid|=2;
 }
 head++;ReleaseSRWLockExclusive(&lock);SetLastError(saved);
}
EXPORT uint32_t VSSM_version(void){return 1;}
EXPORT uint32_t VSSM_record_size(void){return sizeof(Record);}
EXPORT uint64_t VSSM_frequency(void){LARGE_INTEGER q;QueryPerformanceFrequency(&q);return q.QuadPart;}
EXPORT uint64_t VSSM_dropped(void){return InterlockedCompareExchange64(&dropped,0,0);}
EXPORT uint32_t VSSM_drain(Record *out,uint32_t max){
 if(!out||max>256)return 0;AcquireSRWLockExclusive(&lock);uint32_t n=0;
 while(tail<head&&n<max)out[n++]=ring[(tail++)%CAPACITY];ReleaseSRWLockExclusive(&lock);return n;
}
EXPORT uint32_t VSSM_health(void){
 if(!attempted)return 0;uint32_t flags=guarded()?0:4;
 for(int i=0;i<N;i++){void *v=NULL;if(!read_memory((uintptr_t)bindings[i].slot,&v,8)||v!=bridges[i])flags|=1u<<i;}
 return flags;
}
EXPORT uint32_t VSSM_disarm(void){InterlockedExchange(&vssm_enabled,0);return 0;}
EXPORT int VSSM_arm(uint32_t actor,uint32_t id,uint32_t milliseconds){
 if(!attempted||!actor||actor==UINT32_MAX||!id||!milliseconds||milliseconds>2500||VSSM_health())return -1;
 AcquireSRWLockExclusive(&lock);InterlockedExchange(&vssm_enabled,0);
 vssm_actor=(LONG)actor;epoch=id;deadline=GetTickCount64()+milliseconds;
 InterlockedExchange(&vssm_enabled,1);ReleaseSRWLockExclusive(&lock);return 0;
}
EXPORT uint32_t VSSM_stop(void){
 VSSM_disarm();if(!attempted)return 0;uint32_t flags=0;
 /* The slots are static module data. A changed root is still detected by
    health, but cannot make a previously validated module slot a stale heap. */
 for(int i=N-1;i>=0;i--){
  void *v=NULL;if(!read_memory((uintptr_t)bindings[i].slot,&v,8)){flags|=1u<<i;continue;}
  if(v==bindings[i].target)continue;
  if(v!=bridges[i]||!writable(bindings[i].slot)){flags|=1u<<i;continue;}
  if(InterlockedCompareExchangePointer(bindings[i].slot,bindings[i].target,bridges[i])!=bridges[i])flags|=1u<<i;
 }
 return flags;
}
EXPORT int VSSM_start(const Binding *input,const Guard *refs){
 if(attempted||!input||!refs)return -1;
#ifndef VSS_TESTING
 HMODULE game=GetModuleHandleW(L"game.dll"),exe=GetModuleHandleW(NULL),self=NULL;
 if(!game||!exe)return -2;
 IMAGE_DOS_HEADER *d=(void*)game;IMAGE_NT_HEADERS64 *nt=(void*)((uint8_t*)game+d->e_lfanew);
 game_base=(uintptr_t)game;game_end=game_base+nt->OptionalHeader.SizeOfImage;
 d=(void*)exe;nt=(void*)((uint8_t*)exe+d->e_lfanew);exe_base=(uintptr_t)exe;exe_end=exe_base+nt->OptionalHeader.SizeOfImage;
 if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,(LPCWSTR)&VSSM_start,&self))return -3;
#endif
 memcpy(bindings,input,sizeof(bindings));memcpy(guards,refs,sizeof(guards));
 if(!guarded())return -20;
 for(int i=0;i<N;i++){
  MEMORY_BASIC_INFORMATION page;uint8_t code[32];void *v=NULL;
  if(!writable(bindings[i].slot)||!VirtualQuery(bindings[i].target,&page,sizeof(page))||page.State!=MEM_COMMIT||page.Protect!=PAGE_EXECUTE_READ)return -4;
#ifndef VSS_TESTING
  uintptr_t a=(uintptr_t)bindings[i].target;
  if(a<exe_base||a+32>exe_end||(uintptr_t)bindings[i].slot<exe_base||(uintptr_t)bindings[i].slot+8>exe_end)return -5;
#endif
  if(!read_memory((uintptr_t)bindings[i].target,code,32)||memcmp(code,bindings[i].head,32))return -6;
  if(!read_memory((uintptr_t)bindings[i].slot,&v,8)||v!=bindings[i].target)return -7;
  for(int j=0;j<i;j++)if(bindings[i].slot==bindings[j].slot)return -8;
  vssm_originals[i]=bindings[i].target;
 }
 attempted=1;
 for(int i=0;i<N;i++){
  int forced=0;
#ifdef VSS_TESTING
  forced=vssm_test_fail_slot==i;
#endif
  if(forced||!guarded()||!writable(bindings[i].slot)||InterlockedCompareExchangePointer(bindings[i].slot,bridges[i],bindings[i].target)!=bindings[i].target){VSSM_stop();return 100+i;}
 }
 return 0;
}
