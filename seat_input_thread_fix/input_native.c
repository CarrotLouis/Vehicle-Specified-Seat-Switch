/* Seat binding priority inside the game's own window. No global hooks,
   synthetic input, game-code patches or raw mouse movement changes. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <string.h>
#define EXPORT __declspec(dllexport)
#define CAPACITY 256
typedef struct {uint32_t binding,target;} Item;
typedef struct {uint64_t sequence,tick,generation;uint32_t binding,source,target,message;} Record;
typedef char record_layout[sizeof(Record)==40?1:-1];
static SRWLOCK lock=SRWLOCK_INIT;
static HWND window;static WNDPROC previous;
static volatile LONG installed,enabled;static uint64_t expires,serial,head,tail,generation;
static uint32_t source,count;static Item items[5];static uint8_t blocked[256];
static Record ring[CAPACITY];static LONG dropped;
/* Administrative requests are posted, never synchronously sent from Lua.
   Only the target window's own nonzero GUI thread receives this temporary
   hook. No Lua callback or seat operation executes on that thread. */
static SRWLOCK admin=SRWLOCK_INIT;
static HHOOK bridge;static HWND requested_window;static DWORD requested_thread;
static UINT bridge_message;static WPARAM ticket;
static int request,result=-12;static uint64_t deadline;
#ifdef VSS_INPUT_TEST
uint64_t vssi_test_now=1000;int vssi_test_focus=1,vssi_test_cursor=0;
uint8_t vssi_test_keys[256];
#endif
static uint64_t now_ms(void){
#ifdef VSS_INPUT_TEST
 return vssi_test_now;
#else
 return GetTickCount64();
#endif
}
static int down(uint32_t k){
#ifdef VSS_INPUT_TEST
 return k<256&&vssi_test_keys[k];
#else
 return k<256&&GetAsyncKeyState((int)k)<0;
#endif
}
static int allowed(void){
#ifdef VSS_INPUT_TEST
 return vssi_test_focus&&!vssi_test_cursor;
#else
 CURSORINFO c={0};c.cbSize=sizeof(c);
 return window&&GetForegroundWindow()==window&&GetCursorInfo(&c)&&c.flags==0;
#endif
}
static int group(uint32_t k){
 if(k==VK_SHIFT||k==VK_LSHIFT||k==VK_RSHIFT)return 0;
 if(k==VK_CONTROL||k==VK_LCONTROL||k==VK_RCONTROL)return 1;
 if(k==VK_MENU||k==VK_LMENU||k==VK_RMENU)return 2;
 if(k==VK_LWIN||k==VK_RWIN)return 3;return -1;
}
static int match(uint32_t binding,uint32_t key){
 uint32_t primary=binding%256,mask=binding/256;
 if(primary!=key&&!(primary==VK_SHIFT&&group(key)==0)&&
    !(primary==VK_CONTROL&&group(key)==1)&&!(primary==VK_MENU&&group(key)==2))return 0;
 const uint32_t generic[4]={VK_SHIFT,VK_CONTROL,VK_MENU,0};
 const uint32_t left[4]={VK_LSHIFT,VK_LCONTROL,VK_LMENU,VK_LWIN};
 const uint32_t right[4]={VK_RSHIFT,VK_RCONTROL,VK_RMENU,VK_RWIN};
 for(int i=0;i<4;i++,mask/=4){
  if(group(primary)==i)continue;
  uint32_t want=mask%4;int l=down(left[i]),r=down(right[i]),any=l||r||(generic[i]&&down(generic[i]));
  if((want==0&&any)||(want==1&&!any)||(want==2&&(!l||r))||(want==3&&(!r||l)))return 0;
 }
 return 1;
}
static uint32_t keyboard_key(WPARAM w,LPARAM l){
 uint32_t k=(uint32_t)w;
 if(k==VK_SHIFT){uint32_t mapped=MapVirtualKeyW((UINT)((l>>16)&255),MAPVK_VSC_TO_VK_EX);if(mapped==VK_LSHIFT||mapped==VK_RSHIFT)k=mapped;}
 if(k==VK_CONTROL)k=(l&((LPARAM)1<<24))?VK_RCONTROL:VK_LCONTROL;
 if(k==VK_MENU)k=(l&((LPARAM)1<<24))?VK_RMENU:VK_LMENU;
 return k;
}
static uint32_t message_key(UINT msg,WPARAM w,LPARAM l,int *up,int *repeat){
 *up=0;*repeat=0;
 switch(msg){
 case WM_KEYUP:case WM_SYSKEYUP:*up=1;return keyboard_key(w,l);
 case WM_KEYDOWN:case WM_SYSKEYDOWN:*repeat=!!(l&((LPARAM)1<<30));return keyboard_key(w,l);
 case WM_LBUTTONUP:*up=1;return VK_LBUTTON;
 case WM_RBUTTONUP:*up=1;return VK_RBUTTON;
 case WM_MBUTTONUP:*up=1;return VK_MBUTTON;
 case WM_XBUTTONUP:*up=1;return HIWORD(w)==XBUTTON1?VK_XBUTTON1:VK_XBUTTON2;
 case WM_LBUTTONDOWN:case WM_LBUTTONDBLCLK:return VK_LBUTTON;
 case WM_RBUTTONDOWN:case WM_RBUTTONDBLCLK:return VK_RBUTTON;
 case WM_MBUTTONDOWN:case WM_MBUTTONDBLCLK:return VK_MBUTTON;
 case WM_XBUTTONDOWN:case WM_XBUTTONDBLCLK:return HIWORD(w)==XBUTTON1?VK_XBUTTON1:VK_XBUTTON2;
 default:return 0;
 }
}
/* Called under lock. A full queue does not consume an input we cannot deliver. */
static int consume(UINT msg,WPARAM w,LPARAM l){
 int up,repeat;uint32_t key=message_key(msg,w,l,&up,&repeat);
 if(!key||key>=256)return 0;
 if(blocked[key]){if(up)blocked[key]=0;return 1;}
 if(up||repeat||!enabled||!allowed()||now_ms()>expires)return 0;
 int found=-1;
 for(uint32_t i=0;i<count;i++)if(items[i].target!=source&&match(items[i].binding,key)){
  if(found>=0)return 0;found=(int)i;
 }
 if(found<0)return 0;
 if(head-tail>=CAPACITY){InterlockedIncrement(&dropped);return 0;}
 Item item=items[found];Record *r=&ring[(head++)%CAPACITY];
 r->sequence=++serial;r->tick=now_ms();r->generation=generation;r->binding=item.binding;r->source=source;r->target=item.target;r->message=msg;
 blocked[key]=1;return 1;
}
static LRESULT CALLBACK procedure(HWND h,UINT msg,WPARAM w,LPARAM l){
 DWORD saved=GetLastError();int consumed=0;
 if(TryAcquireSRWLockExclusive(&lock)){
  if(msg==WM_KILLFOCUS||(msg==WM_ACTIVATEAPP&&!w)){
   count=0;expires=0;memset(blocked,0,sizeof(blocked));tail=head;
  }else if(enabled&&allowed()){
   consumed=consume(msg,w,l);
   if(msg==WM_MOUSEMOVE){
    if(blocked[VK_LBUTTON])w&=~(WPARAM)MK_LBUTTON;
    if(blocked[VK_RBUTTON])w&=~(WPARAM)MK_RBUTTON;
    if(blocked[VK_MBUTTON])w&=~(WPARAM)MK_MBUTTON;
    if(blocked[VK_XBUTTON1])w&=~(WPARAM)MK_XBUTTON1;
    if(blocked[VK_XBUTTON2])w&=~(WPARAM)MK_XBUTTON2;
   }
  }
  if(!allowed()){count=0;expires=0;memset(blocked,0,sizeof(blocked));tail=head;}
  ReleaseSRWLockExclusive(&lock);
 }
 SetLastError(saved);
 if(consumed)return msg==WM_XBUTTONDOWN||msg==WM_XBUTTONUP||msg==WM_XBUTTONDBLCLK?TRUE:0;
 return CallWindowProcW(previous,h,msg,w,l);
}
static void disarm(void){
 InterlockedExchange(&enabled,0);AcquireSRWLockExclusive(&lock);
 count=0;expires=0;memset(blocked,0,sizeof(blocked));tail=head;ReleaseSRWLockExclusive(&lock);
}
/* Called with admin held, only on the owning GUI thread. */
static int attach(HWND h){
 if(GetWindowThreadProcessId(h,NULL)!=GetCurrentThreadId())return -4;
 WNDPROC before=(WNDPROC)GetWindowLongPtrW(h,GWLP_WNDPROC);if(!before)return -5;
 previous=before;window=h;SetLastError(0);
 WNDPROC old=(WNDPROC)SetWindowLongPtrW(h,GWLP_WNDPROC,(LONG_PTR)&procedure);
 if(!old){window=NULL;return -7;}
 if(old!=before){SetWindowLongPtrW(h,GWLP_WNDPROC,(LONG_PTR)old);window=NULL;return -8;}
 InterlockedExchange(&installed,1);InterlockedExchange(&enabled,1);return 0;
}
/* Preserve a later subclass/overlay head rather than replacing its chain. */
static int detach(void){
 if(!installed)return 0;
 if(!IsWindow(window)){InterlockedExchange(&installed,0);return 0;}
 if(GetWindowThreadProcessId(window,NULL)!=GetCurrentThreadId())return 4;
 if((WNDPROC)GetWindowLongPtrW(window,GWLP_WNDPROC)!=procedure)return 2;
 SetLastError(0);if(!SetWindowLongPtrW(window,GWLP_WNDPROC,(LONG_PTR)previous))return 8;
 InterlockedExchange(&installed,0);return 0;
}
static LRESULT CALLBACK bridge_proc(int code,WPARAM w,LPARAM l){
 DWORD saved=GetLastError();HHOOK remove=NULL;
 if(code==HC_ACTION&&w==PM_REMOVE){
  MSG *m=(MSG*)l;
  if(m->message==bridge_message){
   AcquireSRWLockExclusive(&admin);
   if(request&&m->hwnd==requested_window&&m->wParam==ticket&&m->lParam==request&&
      requested_thread==GetCurrentThreadId()){
    int operation=request;request=0;remove=bridge;bridge=NULL;
    if(operation==1){
     DWORD pid=0,thread=GetWindowThreadProcessId(requested_window,&pid);
     result=now_ms()>deadline?-11:
       (!IsWindow(requested_window)||pid!=GetCurrentProcessId()||thread!=requested_thread)?-3:attach(requested_window);
    }else result=detach();
    /* This private administrative message is not a game input event. */
    m->message=WM_NULL;m->wParam=0;m->lParam=0;
   }
   ReleaseSRWLockExclusive(&admin);
  }
 }
 if(remove)UnhookWindowsHookEx(remove);
 SetLastError(saved);return CallNextHookEx(NULL,code,w,l);
}
/* admin held. PostMessage does not wait for the GUI/render thread. */
static int begin_request(HWND h,DWORD thread,int operation){
 if(!thread)return -3; /* Never allow a desktop-wide hook. */
 if(!bridge_message)bridge_message=RegisterWindowMessageW(L"VSSInputPriority.649bec74-f2d5-490d-a6ed-3f3caef67b0b.GUI.v2");
 if(!bridge_message)return -9;
 requested_window=h;requested_thread=thread;request=operation;result=1;deadline=now_ms()+2000;ticket++;
 bridge=SetWindowsHookExW(WH_GETMESSAGE,bridge_proc,NULL,thread);
 if(!bridge){request=0;return result=-9;}
 if(!PostMessageW(h,bridge_message,ticket,operation)){
  HHOOK remove=bridge;bridge=NULL;request=0;result=-10;
  /* No matching message was queued, so no bridge callback can acquire admin. */
  UnhookWindowsHookEx(remove);return result;
 }
 return 1;
}
EXPORT uint32_t VSSI_version(void){return 2;}
EXPORT uint32_t VSSI_record_size(void){return sizeof(Record);}
EXPORT uint32_t VSSI_dropped(void){return (uint32_t)InterlockedCompareExchange(&dropped,0,0);}
EXPORT int VSSI_start(HWND h){
 DWORD pid=0,thread=GetWindowThreadProcessId(h,&pid);
#ifndef VSS_INPUT_TEST
 if(!GetModuleHandleW(L"game.dll"))return -2;
#endif
 if(!h||!IsWindow(h)||!thread||pid!=GetCurrentProcessId())return -3;
#ifndef VSS_INPUT_TEST
 HMODULE self=NULL;
 if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_PIN,(LPCWSTR)&VSSI_start,&self))return -6;
#endif
 AcquireSRWLockExclusive(&admin);
 if(installed||request){ReleaseSRWLockExclusive(&admin);return -1;}
 result=thread==GetCurrentThreadId()?attach(h):begin_request(h,thread,1);
 int r=result;ReleaseSRWLockExclusive(&admin);return r;
}
/* 0 attached; 1 pending; negative startup error. Timeout invalidates the
   request before unhooking, so an already-running callback cannot attach late. */
EXPORT int VSSI_status(void){
 HHOOK remove=NULL;AcquireSRWLockExclusive(&admin);
 if(request==1&&(!IsWindow(requested_window)||now_ms()>deadline)){
  result=!IsWindow(requested_window)?-3:-11;request=0;ticket++;remove=bridge;bridge=NULL;
 }
 int r=result;ReleaseSRWLockExclusive(&admin);
 if(remove)UnhookWindowsHookEx(remove);return r;
}
EXPORT int VSSI_arm(const Item *input,uint32_t n,uint32_t seat,uint64_t until,uint64_t gen){
 if(!installed||!enabled||n>5||seat>4||(n&&!input)||until>now_ms()+300)return -1;
 for(uint32_t i=0;i<n;i++){
  if(input[i].binding%256==0||input[i].binding%256==255||input[i].binding>65535||input[i].target>4)return -2;
  for(uint32_t j=0;j<i;j++)if(input[i].binding==input[j].binding)return -3;
 }
 AcquireSRWLockExclusive(&lock);count=n;source=seat;expires=until;generation=gen;
 if(!allowed()){count=0;expires=0;memset(blocked,0,sizeof(blocked));tail=head;}
 if(n)memcpy(items,input,sizeof(Item)*n);ReleaseSRWLockExclusive(&lock);return 0;
}
EXPORT uint32_t VSSI_suppressed(uint32_t key){
 if(key>=256)return 0;AcquireSRWLockShared(&lock);int result=blocked[key];
 if(key==VK_SHIFT)result=blocked[VK_LSHIFT]||blocked[VK_RSHIFT];
 if(key==VK_CONTROL)result=blocked[VK_LCONTROL]||blocked[VK_RCONTROL];
 if(key==VK_MENU)result=blocked[VK_LMENU]||blocked[VK_RMENU];
 ReleaseSRWLockShared(&lock);return result;
}
EXPORT uint32_t VSSI_drain(Record *out,uint32_t max){
 if(!out||max>256)return 0;AcquireSRWLockExclusive(&lock);uint32_t n=0;
 while(tail<head&&n<max)out[n++]=ring[(tail++)%CAPACITY];ReleaseSRWLockExclusive(&lock);return n;
}
EXPORT uint32_t VSSI_health(void){
 if(!installed||!enabled||!IsWindow(window))return 1;
 return (WNDPROC)GetWindowLongPtrW(window,GWLP_WNDPROC)==procedure?0:2;
}
EXPORT uint32_t VSSI_stop(void){
 HHOOK remove=NULL;int r=0;
 /* Stop swallowing buttons immediately, even if the GUI is not pumping. */
 AcquireSRWLockExclusive(&admin);disarm();
 if(request==1){request=0;ticket++;remove=bridge;bridge=NULL;result=-12;}
 else if(request==2)r=1;
 else if(installed&&IsWindow(window)){
  DWORD thread=GetWindowThreadProcessId(window,NULL);
  r=thread==GetCurrentThreadId()?detach():begin_request(window,thread,2);result=r;
 }else result=-12;
 ReleaseSRWLockExclusive(&admin);if(remove)UnhookWindowsHookEx(remove);return (uint32_t)(r<0?-r:r);
}
