/* Passive native call recorder. No Lua callbacks, network sends or seat writes. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <string.h>
#include "MinHook.h"
#define EXPORT __declspec(dllexport)
#define HOOKS 8
#define CAPACITY 8192
typedef struct {
 uint64_t sequence,tick,qpc,peer,caller;
 uint32_t kind,thread,message,count,valid,reserved;
 uint64_t values[8];
 uint32_t types[8],sizes[8];
} Record;
typedef char record_size_check[sizeof(Record)==192?1:-1];
void *vss_originals[HOOKS];
extern void vss_bridge0(void),vss_bridge1(void),vss_bridge2(void),vss_bridge3(void);
extern void vss_bridge4(void),vss_bridge5(void),vss_bridge6(void),vss_bridge7(void);
static void *bridges[]={vss_bridge0,vss_bridge1,vss_bridge2,vss_bridge3,vss_bridge4,vss_bridge5,vss_bridge6,vss_bridge7};
static SRWLOCK lock=SRWLOCK_INIT;
static Record ring[CAPACITY];
static uint64_t head,tail,serial;
static volatile LONG enabled,installed;
static volatile LONG64 dropped;
static uintptr_t game_base,game_end;
typedef struct {
 uint32_t stage,win32_error,hook_index,enabling;
 uint64_t patch_address,region_base,region_size;
 uint32_t protection,allocation_protection,state,type,query_error,rollback_status;
} Failure;
typedef char failure_size_check[sizeof(Failure)==64?1:-1];
static Failure failure;
static void *observed_targets[HOOKS];
#ifdef VSS_TESTING
int vssp_test_fail_protect;
#endif
/* Called only after a failed protection request, before rollback can replace
   the original Windows error. This does not retry or relax protection. */
void VSSP_note_protect_failure(void *patch,void *target,BOOL enabling,DWORD error) {
 if(failure.stage)return;
 failure.stage=1;failure.win32_error=error;failure.hook_index=UINT32_MAX;
 failure.enabling=enabling;failure.patch_address=(uintptr_t)patch;
 for(uint32_t i=0;i<HOOKS;i++)if(observed_targets[i]==target)failure.hook_index=i;
 MEMORY_BASIC_INFORMATION info;
 if(VirtualQuery(patch,&info,sizeof(info))) {
  failure.region_base=(uintptr_t)info.BaseAddress;failure.region_size=info.RegionSize;
  failure.protection=info.Protect;failure.allocation_protection=info.AllocationProtect;
  failure.state=info.State;failure.type=info.Type;
 }else failure.query_error=GetLastError();
 SetLastError(error);
}
EXPORT uint32_t VSSP_failure(Failure *out){if(!out)return 0;*out=failure;return failure.stage;}
static uint32_t watched(uint32_t hash) {
 switch(hash) {
 #include "watched.h"
 default:return 0;
 }
}
static int read_memory(uintptr_t p,void *out,SIZE_T n) {
 SIZE_T got=0;
 return p>=65536 && p<((uint64_t)1<<47) && ReadProcessMemory(GetCurrentProcess(),(void*)p,out,n,&got) && got==n;
}
/* Saved registers: r11,r10,r9,r8,rdx,rcx,rax,flags,return address,
   four shadow slots, followed by stack arguments. Assembly preserves state. */
void vss_capture(const uint64_t *ctx,uint32_t kind) {
 DWORD saved_error=GetLastError();
 if(!enabled || (kind==0 && !watched((uint32_t)ctx[5]))) {SetLastError(saved_error);return;}
 if(!TryAcquireSRWLockExclusive(&lock)) {InterlockedIncrement64(&dropped);SetLastError(saved_error);return;}
 if(head-tail>=CAPACITY) {InterlockedIncrement64(&dropped);ReleaseSRWLockExclusive(&lock);SetLastError(saved_error);return;}
 Record *r=&ring[head%CAPACITY];memset(r,0,sizeof(*r));
 r->sequence=++serial;r->tick=GetTickCount64();
 LARGE_INTEGER q;QueryPerformanceCounter(&q);r->qpc=q.QuadPart;
 r->kind=kind;r->thread=GetCurrentThreadId();r->peer=ctx[4];
 r->caller=ctx[8]>=game_base && ctx[8]<game_end?ctx[8]-game_base:0;
 if(kind==0) {
  r->message=(uint32_t)ctx[5];r->count=(uint32_t)ctx[2];
  if(r->count<=8)for(uint32_t i=0;i<r->count;i++) {
   struct {uint32_t type,size;uintptr_t data;} d;
   if(!read_memory(ctx[3]+i*16,&d,sizeof(d)))continue;
   r->types[i]=d.type;r->sizes[i]=d.size;
   if(d.size!=4 || d.type>2)continue;
   uint32_t v=0;
   if(read_memory(d.data,&v,d.type==0?1:4)){r->values[i]=v;r->valid|=1u<<i;}
  }
 } else {
  /* Observe native handler arguments, without claiming every call is remote. */
  const uint8_t stack_count[HOOKS]={0,2,1,1,2,3,0,0};
  r->count=2+stack_count[kind];r->values[0]=(uint32_t)ctx[3];r->values[1]=(uint32_t)ctx[2];r->valid=3;
  for(uint32_t i=0;i<stack_count[kind];i++) {
   uint32_t v;
   if(read_memory((uintptr_t)&ctx[13+i],&v,4)){r->values[2+i]=v;r->valid|=1u<<(2+i);}
  }
 }
 head++;
 ReleaseSRWLockExclusive(&lock);SetLastError(saved_error);
}
EXPORT uint32_t VSSP_version(void){return 2;}
EXPORT uint32_t VSSP_record_size(void){return sizeof(Record);}
EXPORT uint64_t VSSP_frequency(void){LARGE_INTEGER q;QueryPerformanceFrequency(&q);return q.QuadPart;}
EXPORT uint64_t VSSP_dropped(void){return InterlockedCompareExchange64(&dropped,0,0);}
EXPORT uint32_t VSSP_drain(Record *out,uint32_t max) {
 if(!out || max>256)return 0;
 AcquireSRWLockExclusive(&lock);uint32_t n=0;
 while(tail<head && n<max){out[n++]=ring[tail%CAPACITY];tail++;}
 ReleaseSRWLockExclusive(&lock);return n;
}
/* The library/trampolines remain allocated until process exit, including after
   disable. A callback already in flight can still tail-call its trampoline. */
EXPORT int VSSP_stop(void) {
 InterlockedExchange(&enabled,0);
 if(!installed)return 0;
 return (int)MH_DisableHook(MH_ALL_HOOKS);
}
EXPORT int VSSP_start(void **targets,const uint8_t *expected,uint32_t count) {
 if(installed || count!=HOOKS || !targets || !expected)return -1;
#ifndef VSS_TESTING
 HMODULE game=GetModuleHandleW(L"game.dll"),self=NULL;
 if(!game)return -2;
 IMAGE_DOS_HEADER *dos=(void*)game;
 IMAGE_NT_HEADERS64 *nt=(void*)((uint8_t*)game+dos->e_lfanew);
 game_base=(uintptr_t)game;game_end=game_base+nt->OptionalHeader.SizeOfImage;
 if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,(LPCWSTR)&VSSP_start,&self))return -3;
#endif
 for(uint32_t i=0;i<count;i++) {
  MEMORY_BASIC_INFORMATION info;uint8_t bytes[32];
  if(!VirtualQuery(targets[i],&info,sizeof(info)) || info.State!=MEM_COMMIT || !(info.Protect&(PAGE_EXECUTE|PAGE_EXECUTE_READ|PAGE_EXECUTE_READWRITE|PAGE_EXECUTE_WRITECOPY)))return -4;
#ifndef VSS_TESTING
  if((uintptr_t)targets[i]<game_base || (uintptr_t)targets[i]+32>game_end)return -5;
#endif
  if(!read_memory((uintptr_t)targets[i],bytes,32) || memcmp(bytes,expected+i*32,32))return -6;
  for(uint32_t j=0;j<i;j++)if(targets[i]==targets[j])return -7;
 }
 MH_STATUS status=MH_Initialize();if(status!=MH_OK)return 100+status;
 memcpy(observed_targets,targets,sizeof(observed_targets));
 for(uint32_t i=0;i<count;i++) {
  status=MH_CreateHook(targets[i],bridges[i],&vss_originals[i]);
  if(status!=MH_OK){MH_Uninitialize();return 200+status;}
 }
 installed=1;
 status=MH_EnableHook(MH_ALL_HOOKS);
 if(status!=MH_OK){failure.rollback_status=MH_DisableHook(MH_ALL_HOOKS);return 300+status;}
 InterlockedExchange(&enabled,1);return 0;
}
