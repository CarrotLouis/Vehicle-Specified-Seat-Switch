/* A single pending owner reservation for the installer's avatar. No network
   sends, game-state writes or Lua callbacks on the receive thread. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <string.h>
#define EXPORT __declspec(dllexport)
typedef struct {uint64_t cookie,peer;uint32_t car,avatar,source,target;} GateConfig;
typedef struct {uint64_t cookie,tick,peer;uint32_t car,avatar,source,target,chosen,status,repeats,guard_lost;} GateRecord;
typedef char gate_layout_check[sizeof(GateConfig)==32 && sizeof(GateRecord)==56?1:-1];
extern int vss_gate_session_valid(void);
static SRWLOCK gate_lock=SRWLOCK_INIT;
static GateRecord record;
static volatile LONG armed;
static int read_(uintptr_t p,void *out,SIZE_T n){SIZE_T got=0;
 return p>=65536&&p<((uint64_t)1<<47)&&p+n>=p&&n<=64&&ReadProcessMemory(GetCurrentProcess(),(void*)p,out,n,&got)&&got==n;
}
EXPORT uint32_t VSST_gate_active(void){return (uint32_t)InterlockedCompareExchange(&armed,0,0);}
EXPORT int VSST_gate_arm(const GateConfig *c){
 if(!c||!c->cookie||!c->peer||!c->car||!c->avatar||c->source>4||c->target>4||c->source==c->target||!vss_gate_session_valid())return -1;
 AcquireSRWLockExclusive(&gate_lock);
 if(armed){ReleaseSRWLockExclusive(&gate_lock);return -2;}
 memset(&record,0,sizeof(record));record.cookie=c->cookie;record.peer=c->peer;record.car=c->car;
 record.avatar=c->avatar;record.source=c->source;record.target=c->target;record.chosen=UINT32_MAX;record.status=1;
 InterlockedExchange(&armed,1);ReleaseSRWLockExclusive(&gate_lock);return 0;
}
EXPORT uint32_t VSST_gate_peek(GateRecord *out){
 if(!out)return 0;AcquireSRWLockShared(&gate_lock);*out=record;uint32_t active=armed;
 ReleaseSRWLockShared(&gate_lock);return active;
}
EXPORT int VSST_gate_finish(uint64_t cookie){
 AcquireSRWLockExclusive(&gate_lock);
 if(!armed||record.cookie!=cookie||(record.status!=2&&record.status!=3)||record.guard_lost){ReleaseSRWLockExclusive(&gate_lock);return -1;}
 InterlockedExchange(&armed,0);ReleaseSRWLockExclusive(&gate_lock);return 0;
}
/* Called only on actual game shutdown; error stop must retain a pending
   exact-tuple gate to prevent a late accepted message starting native exit. */
EXPORT void VSST_gate_shutdown(void){AcquireSRWLockExclusive(&gate_lock);InterlockedExchange(&armed,0);ReleaseSRWLockExclusive(&gate_lock);}
int vss_gate_decide(const uint64_t *ctx,uint32_t kind){
 if(kind!=2||!armed)return 0;
 uint32_t hash=(uint32_t)ctx[4];
 if(hash!=0x2e986f01u&&hash!=0xf2a7f3e4u)return 0;
 DWORD error=GetLastError();int skip=0;
 AcquireSRWLockExclusive(&gate_lock);
 if(!armed||ctx[5]!=record.peer)goto done;
 if(!vss_gate_session_valid()){record.guard_lost=1;goto done;}
 uint32_t count=0,values[3]={0};
 if(!read_((uintptr_t)&ctx[13],&count,4)||count!=(hash==0x2e986f01u?3u:2u))goto done;
 for(uint32_t i=0;i<count;i++){
  struct {uint32_t type,size;uintptr_t data;} d;
  if(!read_(ctx[2]+16*i,&d,16)||d.type!=1||d.size!=4||!read_(d.data,&values[i],4))goto done;
 }
 if(values[0]!=record.car||values[1]!=record.avatar)goto done;
 if(hash==0x2e986f01u){
  if(values[2]>4)goto done;
  /* All owner-chosen alternatives are held for rollback. Never silently
     forward an alternative driver/gunner grant to the native cross route. */
  skip=1;
  if(record.status==1){record.status=2;record.chosen=values[2];record.tick=GetTickCount64();}
  else if(record.status!=2||record.chosen!=values[2])record.status=4;
  record.repeats++;
 }else if(record.status==1){record.status=3;record.tick=GetTickCount64();}
done:
 ReleaseSRWLockExclusive(&gate_lock);SetLastError(error);return skip;
}
