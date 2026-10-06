/* Observes fifteen seat/authority message kinds through writable data slots.
   No executable patch, page-protection change, packet send or seat mutation. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <string.h>
#define EXPORT __declspec(dllexport)
#define N 3
#define CAPACITY 8192
typedef struct {void **slot;void *target;uint8_t head[32];} Binding;
typedef struct {void **slot;void *target;} Guard;
typedef struct {
 uint64_t sequence,tick,qpc,caller;
 uint32_t kind,thread,message,count,valid,caller_module,peer_count,peer_valid;
 uint64_t values[8],peers[8];
 uint32_t types[8],sizes[8];
} Record;
typedef char layout_check[sizeof(Record)==256 && sizeof(Binding)==48 && sizeof(Guard)==16?1:-1];
void *vss_originals[N];
extern void vss_bridge0(void),vss_bridge1(void),vss_bridge2(void);
static void *bridges[N]={vss_bridge0,vss_bridge1,vss_bridge2};
static Binding bindings[N];static Guard guards[N];
#if !defined(VSS_NO_RECORDS) || !defined(VSS_TESTING)
static uintptr_t game_base,game_end,exe_base,exe_end;
#endif
static volatile LONG enabled,attempted;static volatile LONG64 dropped;
static SRWLOCK lock=SRWLOCK_INIT;static Record ring[CAPACITY];static uint64_t head,tail;
#ifndef VSS_NO_RECORDS
static uint64_t serial;
#endif
#ifdef VSS_TESTING
int vsst_test_fail_slot=-1;
#endif
static int read_memory(uintptr_t p,void *out,SIZE_T n){
 SIZE_T got=0;return p>=65536 && p<((uint64_t)1<<47) && n<=32768 && p+n>=p && ReadProcessMemory(GetCurrentProcess(),(void*)p,out,n,&got) && got==n;
}
static int writable(void *p){
 MEMORY_BASIC_INFORMATION m;
 if((uintptr_t)p%8 || !VirtualQuery(p,&m,sizeof(m)))return 0;
 return m.State==MEM_COMMIT && m.Protect==PAGE_READWRITE && (uintptr_t)p+8<=(uintptr_t)m.BaseAddress+m.RegionSize;
}
static int guarded(void){
 for(int i=0;i<N;i++){void *v=NULL;if(!read_memory((uintptr_t)guards[i].slot,&v,8)||v!=guards[i].target)return 0;}return 1;
}
extern uint32_t VSST_gate_active(void);
int vss_gate_session_valid(void){
 void *v=NULL;
 return attempted&&guarded()&&read_memory((uintptr_t)bindings[2].slot,&v,8)&&v==bridges[2];
}
#ifndef VSS_NO_RECORDS
static int watched(uint32_t hash){switch(hash){
#include "watched.h"
 default:return 0;}}
#endif
/* Same saved context as the original bridge: r11,r10,r9,r8,rdx,rcx,rax,
   flags,return address, four shadow slots, then stack arguments. */
void vss_capture(const uint64_t *ctx,uint32_t kind){
#ifdef VSS_NO_RECORDS
 (void)ctx;(void)kind;return;
#else
 DWORD saved=GetLastError();uint32_t message=(uint32_t)ctx[kind==2?4:5];
 if(!enabled || !watched(message)){SetLastError(saved);return;}
 if(!TryAcquireSRWLockExclusive(&lock)){InterlockedIncrement64(&dropped);SetLastError(saved);return;}
 if(head-tail>=CAPACITY){InterlockedIncrement64(&dropped);ReleaseSRWLockExclusive(&lock);SetLastError(saved);return;}
 Record *r=&ring[head%CAPACITY];memset(r,0,sizeof(*r));
 r->sequence=++serial;r->tick=GetTickCount64();LARGE_INTEGER q;QueryPerformanceCounter(&q);r->qpc=q.QuadPart;
 r->kind=kind;r->message=message;r->thread=GetCurrentThreadId();
 uintptr_t caller=ctx[8];
 if(caller>=game_base&&caller<game_end){r->caller_module=1;r->caller=caller-game_base;}
 else if(caller>=exe_base&&caller<exe_end){r->caller_module=2;r->caller=caller-exe_base;}
 uintptr_t args=kind==0?ctx[3]:ctx[2];
 if(kind==0){r->count=(uint32_t)ctx[2];r->peer_count=1;r->peers[0]=ctx[4];r->peer_valid=1;}
 else {
  uint32_t count=0;if(read_memory((uintptr_t)&ctx[13],&count,4))r->count=count;else r->count=UINT32_MAX;
  if(kind==1){r->peer_count=(uint32_t)ctx[3];for(uint32_t i=0;i<r->peer_count&&i<8;i++)if(read_memory(ctx[4]+8*i,&r->peers[i],8))r->peer_valid|=1u<<i;}
  else {r->peer_count=1;r->peers[0]=ctx[5];r->peer_valid=1;}
 }
 if(r->count<=8)for(uint32_t i=0;i<r->count;i++){
  struct {uint32_t type,size;uintptr_t data;} d;
  if(!read_memory(args+16*i,&d,16))continue;
  r->types[i]=d.type;r->sizes[i]=d.size;
  /* The two ownership wrappers carry an opaque peer handle in argument 1.
     Preserve all 64 bits; Lua converts it to a session alias before logging.
     Do not broaden this to arbitrary pointer/string descriptor types. */
  if((message==0xe29b4d18u || message==0xf8a9d630u) && i==1 && d.type==9 && d.size==8){
   if(read_memory(d.data,&r->values[i],8))r->valid|=1u<<i;
   continue;
  }
  /* The send descriptor uses size4 for bools; decoded receive descriptors use
     size1. Only their low byte is defined in either representation. */
  if(d.type>2 || (d.type==0 ? (d.size!=1 && d.size!=4) : d.size!=4))continue;
  uint32_t value=0;if(read_memory(d.data,&value,d.type==0?1:4)){r->values[i]=value;r->valid|=1u<<i;}
 }
 head++;ReleaseSRWLockExclusive(&lock);SetLastError(saved);
#endif
}
EXPORT uint32_t VSST_version(void){return 4;}
EXPORT uint32_t VSST_record_size(void){return sizeof(Record);}
EXPORT uint64_t VSST_frequency(void){LARGE_INTEGER q;QueryPerformanceFrequency(&q);return q.QuadPart;}
EXPORT uint64_t VSST_dropped(void){return InterlockedCompareExchange64(&dropped,0,0);}
EXPORT uint32_t VSST_drain(Record *out,uint32_t max){
 if(!out||max>256)return 0;AcquireSRWLockExclusive(&lock);uint32_t n=0;
 while(tail<head&&n<max)out[n++]=ring[(tail++)%CAPACITY];ReleaseSRWLockExclusive(&lock);return n;
}
EXPORT uint32_t VSST_health(void){
 if(!attempted)return 0;uint32_t flags=guarded()?0:8;
 for(int i=0;i<N;i++){void *v=NULL;void *expected=bridges[i];
#ifdef VSS_NO_RECORDS
 if(i<2)expected=bindings[i].target;
#endif
 if(!read_memory((uintptr_t)bindings[i].slot,&v,8)||v!=expected)flags|=1u<<i;}
 return flags;
}
EXPORT uint32_t VSST_stop(void){
 InterlockedExchange(&enabled,0);if(!attempted)return 0;
 uint32_t flags=0;int alive=guarded();
 for(int i=N-1;i>=0;i--){
  void *v=NULL;
  /* If the owning session changed, never write its old heap allocation. */
  if(i==2&&VSST_gate_active()){flags|=16;continue;}
  if(i==2&&!alive){flags|=1u<<i;continue;}
  if(!read_memory((uintptr_t)bindings[i].slot,&v,8)){flags|=1u<<i;continue;}
  if(v==bindings[i].target)continue;
  if(v!=bridges[i]||!writable(bindings[i].slot)){flags|=1u<<i;continue;}
  if(InterlockedCompareExchangePointer(bindings[i].slot,bindings[i].target,bridges[i])!=bridges[i])flags|=1u<<i;
 }
 return flags;
}
EXPORT int VSST_start(const Binding *input,const Guard *refs){
 if(attempted||!input||!refs)return -1;
#ifndef VSS_TESTING
 HMODULE game=GetModuleHandleW(L"game.dll"),exe=GetModuleHandleW(NULL),self=NULL;
 if(!game||!exe)return -2;
 IMAGE_DOS_HEADER *d=(void*)game;IMAGE_NT_HEADERS64 *nt=(void*)((uint8_t*)game+d->e_lfanew);
 game_base=(uintptr_t)game;game_end=game_base+nt->OptionalHeader.SizeOfImage;
 d=(void*)exe;nt=(void*)((uint8_t*)exe+d->e_lfanew);exe_base=(uintptr_t)exe;exe_end=exe_base+nt->OptionalHeader.SizeOfImage;
 /* An already loaded callback can still enter the bridge after stop. */
 if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,(LPCWSTR)&VSST_start,&self))return -3;
#endif
 memcpy(bindings,input,sizeof(bindings));memcpy(guards,refs,sizeof(guards));
 if(!guarded())return -20;
 for(int i=0;i<N;i++){
  MEMORY_BASIC_INFORMATION m;uint8_t code[32];void *v=NULL;
  if(!writable(bindings[i].slot)||!VirtualQuery(bindings[i].target,&m,sizeof(m))||m.State!=MEM_COMMIT||m.Protect!=PAGE_EXECUTE_READ)return -4;
#ifndef VSS_TESTING
  uintptr_t a=(uintptr_t)bindings[i].target,base=i==2?game_base:exe_base,end=i==2?game_end:exe_end;
  if(a<base||a+32>end)return -5;
  if(i<2&&((uintptr_t)bindings[i].slot<exe_base||(uintptr_t)bindings[i].slot+8>exe_end))return -5;
#endif
  if(!read_memory((uintptr_t)bindings[i].target,code,32)||memcmp(code,bindings[i].head,32))return -6;
  if(!read_memory((uintptr_t)bindings[i].slot,&v,8)||v!=bindings[i].target)return -7;
  for(int j=0;j<i;j++)if(bindings[i].slot==bindings[j].slot)return -8;
  vss_originals[i]=bindings[i].target;
 }
 attempted=1;
 for(int i=0;i<N;i++){
#ifdef VSS_NO_RECORDS
  if(i<2)continue;
#endif
  int forced=0;
#ifdef VSS_TESTING
  forced=vsst_test_fail_slot==i;
#endif
  if(forced||!guarded()||!writable(bindings[i].slot)||InterlockedCompareExchangePointer(bindings[i].slot,bridges[i],bindings[i].target)!=bindings[i].target){VSST_stop();return 100+i;}
 }
 InterlockedExchange(&enabled,1);return 0;
}
