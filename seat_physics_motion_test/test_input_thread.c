/* Real private windows on a different thread: reproduce the 0.12.0 failure
   condition without launching or altering any game window. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct {uint32_t binding,target;} Item;
typedef struct {uint64_t sequence,tick,generation;uint32_t binding,source,target,message;} Record;
extern int VSSI_start(HWND),VSSI_status(void),VSSI_arm(const Item*,uint32_t,uint32_t,uint64_t,uint64_t);
extern uint32_t VSSI_stop(void),VSSI_health(void),VSSI_suppressed(uint32_t),VSSI_drain(Record*,uint32_t);
extern uint64_t vssi_test_now;extern uint8_t vssi_test_keys[256];
#define CHECK(x) do{if(!(x)){fprintf(stderr,"failed line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static HWND h;static HANDLE created,pump,peeked,remove_ready;static DWORD gui;
static const char *mode;
static volatile LONG forwarded;
#define CHANGE_HEAD (WM_APP+42)
static LRESULT CALLBACK original(HWND,UINT,WPARAM,LPARAM);
static LRESULT CALLBACK foreign(HWND window,UINT m,WPARAM w,LPARAM l){
 if(m==WM_CLOSE)return original(window,m,w,l);return 654;
}
static LRESULT CALLBACK original(HWND window,UINT m,WPARAM w,LPARAM l){
 (void)w;(void)l;
 if(m==WM_CLOSE){DestroyWindow(window);PostQuitMessage(0);return 0;}
 if(m==CHANGE_HEAD){SetWindowLongPtrW(window,GWLP_WNDPROC,(LONG_PTR)foreign);return 0;}
 if(m==WM_RBUTTONDOWN||m==WM_RBUTTONUP)InterlockedIncrement(&forwarded);
 return 321;
}
static DWORD WINAPI worker(void *unused){
 (void)unused;gui=GetCurrentThreadId();
 h=CreateWindowExW(0,L"VSSInputThreadPrivateTest",L"",0,0,0,1,1,NULL,NULL,GetModuleHandleW(NULL),NULL);
 SetEvent(created);if(!h)return 1;
 /* Delay actual message pumping to exercise asynchronous cancel/expiry. */
 if(WaitForSingleObject(pump,5000)!=WAIT_OBJECT_0)return 2;
 if(strcmp(mode,"destroy-pending")==0){DestroyWindow(h);return 0;}
 MSG m;
 if(strcmp(mode,"peek")==0){
  UINT private_message=RegisterWindowMessageW(L"VSSInputPriority.649bec74-f2d5-490d-a6ed-3f3caef67b0b.GUI.v2");int running=1,paused=0;
  while(running){
   while(PeekMessageW(&m,NULL,0,0,PM_NOREMOVE)){
    if(!paused&&m.message==private_message){paused=1;SetEvent(peeked);if(WaitForSingleObject(remove_ready,5000)!=WAIT_OBJECT_0)return 3;}
    if(!PeekMessageW(&m,NULL,0,0,PM_REMOVE))continue;
    if(m.message==WM_QUIT){running=0;break;}TranslateMessage(&m);DispatchMessageW(&m);
   }
   if(running)MsgWaitForMultipleObjectsEx(0,NULL,20,QS_ALLINPUT,MWMO_INPUTAVAILABLE);
  }
 }else while(GetMessageW(&m,NULL,0,0)>0){TranslateMessage(&m);DispatchMessageW(&m);}
 return 0;
}
static void wait_result(int wanted){
 uint64_t end=GetTickCount64()+2000;
 while(VSSI_status()!=wanted&&GetTickCount64()<end)Sleep(1);
 CHECK(VSSI_status()==wanted);
}
int main(int argc,char **argv){
 (void)argc;mode=argv[1]?argv[1]:"success";
 WNDCLASSW c={0};c.lpfnWndProc=original;c.hInstance=GetModuleHandleW(NULL);c.lpszClassName=L"VSSInputThreadPrivateTest";
 CHECK(RegisterClassW(&c));created=CreateEventW(NULL,TRUE,FALSE,NULL);pump=CreateEventW(NULL,TRUE,FALSE,NULL);
 peeked=CreateEventW(NULL,TRUE,FALSE,NULL);remove_ready=CreateEventW(NULL,TRUE,FALSE,NULL);CHECK(created&&pump&&peeked&&remove_ready);
 HANDLE thread=CreateThread(NULL,0,worker,NULL,0,NULL);CHECK(thread);
 CHECK(WaitForSingleObject(created,5000)==WAIT_OBJECT_0&&h&&!IsWindowVisible(h));CHECK(gui!=GetCurrentThreadId());
 uint64_t before=GetTickCount64();CHECK(VSSI_start(h)==1);CHECK(GetTickCount64()-before<250);
 CHECK(VSSI_status()==1&&VSSI_start(h)==-1&&VSSI_health()==1);
 Item item={VK_RBUTTON+1024,4};CHECK(VSSI_arm(&item,1,1,1200,11)==-1); /* unready never consumes */
 int expired=strcmp(mode,"expire-in-callback")==0;
 int cancelled=strcmp(mode,"cancel")==0;
 int timedout=strcmp(mode,"timeout")==0;
 if(cancelled){CHECK(VSSI_stop()==0);CHECK(VSSI_status()==-12);}
 if(timedout||expired){vssi_test_now=3001;if(timedout)CHECK(VSSI_status()==-11);}
 SetEvent(pump);
 if(strcmp(mode,"destroy-pending")==0){
  CHECK(WaitForSingleObject(thread,5000)==WAIT_OBJECT_0);CHECK(VSSI_status()==-3&&VSSI_health()==1&&VSSI_stop()==0);
  CloseHandle(thread);CloseHandle(created);CloseHandle(pump);CloseHandle(peeked);CloseHandle(remove_ready);
  puts("PASS separate GUI thread: destroyed window cancels pending startup without attaching");return 0;
 }
 if(strcmp(mode,"peek")==0){
  CHECK(WaitForSingleObject(peeked,2000)==WAIT_OBJECT_0);CHECK(VSSI_status()==1&&VSSI_health()==1);
  CHECK((WNDPROC)GetWindowLongPtrW(h,GWLP_WNDPROC)==original);SetEvent(remove_ready);
 }
 if(cancelled||timedout||expired){
  if(expired)wait_result(-11);
  /* A sent message synchronizes with processing of any queued setup message. */
  DWORD_PTR ignored;CHECK(SendMessageTimeoutW(h,WM_RBUTTONDOWN,0,0,SMTO_ABORTIFHUNG,1000,&ignored));
  Sleep(10);CHECK(VSSI_health()==1);
  CHECK((WNDPROC)GetWindowLongPtrW(h,GWLP_WNDPROC)==original);CHECK(forwarded==1);
  /* A stale queued ticket must not hijack a subsequent install. */
  vssi_test_now=1000;CHECK(VSSI_start(h)==1);wait_result(0);
 }else wait_result(0);
 CHECK(VSSI_health()==0&&GetWindowThreadProcessId(h,NULL)==gui);
 memset(vssi_test_keys,0,256);vssi_test_keys[VK_LCONTROL]=1;vssi_test_keys[VK_RBUTTON]=1;
 CHECK(VSSI_arm(&item,1,1,1200,11)==0);
 LONG n=forwarded;DWORD_PTR reply;
 CHECK(SendMessageTimeoutW(h,WM_RBUTTONDOWN,MK_RBUTTON|MK_CONTROL,0,SMTO_ABORTIFHUNG,1000,&reply));
 CHECK(reply==0&&forwarded==n&&VSSI_suppressed(VK_RBUTTON));
 Record r;CHECK(VSSI_drain(&r,1)==1&&r.source==1&&r.target==4&&r.generation==11);
 /* Cross-thread shutdown disarms immediately and restores on the GUI thread. */
 if(strcmp(mode,"chain-change")==0){
  CHECK(SendMessageTimeoutW(h,CHANGE_HEAD,0,0,SMTO_ABORTIFHUNG,1000,&reply));CHECK(VSSI_health()==2);
  CHECK(VSSI_stop()==1);wait_result(2);CHECK((WNDPROC)GetWindowLongPtrW(h,GWLP_WNDPROC)==foreign);
 }else{
  CHECK(VSSI_stop()==1);wait_result(0);CHECK((WNDPROC)GetWindowLongPtrW(h,GWLP_WNDPROC)==original);
  CHECK(!VSSI_suppressed(VK_RBUTTON));CHECK(VSSI_drain(&r,1)==0);
  CHECK(SendMessageTimeoutW(h,WM_RBUTTONUP,0,0,SMTO_ABORTIFHUNG,1000,&reply));CHECK(reply==321&&forwarded==n+1);
  CHECK(VSSI_stop()==0); /* idempotent close */
 }
 CHECK(PostMessageW(h,WM_CLOSE,0,0));CHECK(WaitForSingleObject(thread,5000)==WAIT_OBJECT_0);
 DWORD code;CHECK(GetExitCodeThread(thread,&code)&&code==0);CloseHandle(thread);CloseHandle(created);CloseHandle(pump);CloseHandle(peeked);CloseHandle(remove_ready);
 printf("PASS actual separate GUI thread: %s; nonblocking install, no late startup, consumed input, disarm and safe restoration\n",mode);return 0;
}
