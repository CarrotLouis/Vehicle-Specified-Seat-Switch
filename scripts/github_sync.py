"""Push a reviewed commit using the user-authorized GitHub account; never publish Releases."""
from pathlib import Path
import base64,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
OWNER='CarrotLouis';REPO='Vehicle-Specified-Seat-Switch';REMOTE='https://github.com/'+OWNER+'/'+REPO+'.git'
def main():
    gh=ROOT/'local_data/tools/gh/gh.exe'
    if not gh.is_file():
        found=shutil.which('gh')
        if not found:raise RuntimeError('GitHub CLI missing: install and sign in before syncing.')
        gh=Path(found)
    env=os.environ.copy()
    if (ROOT/'.local-github').is_dir():env['GH_CONFIG_DIR']=str(ROOT/'.local-github')
    def cli(*args):
        r=subprocess.run([str(gh),*args],env=env,capture_output=True,text=True,encoding='utf-8',timeout=35)
        if r.returncode:raise RuntimeError('GitHub CLI request failed: check auth status and connection.')
        return r.stdout.strip()
    login=cli('api','user','--jq','.login')
    if login.lower()!=OWNER.lower():raise RuntimeError('Signed-in account differs from the authorized owner: '+login)
    repo=json.loads(cli('api','repos/'+OWNER+'/'+REPO,'--jq','{url:.html_url,private:.private,default_branch:.default_branch}'))
    print(json.dumps({'account':login,**repo},ensure_ascii=False))
    if '--push'not in sys.argv and '--fetch'not in sys.argv:return
    def git(*args,run_env=env):
        return subprocess.run(['git','-c','safe.directory='+str(ROOT),'-C',str(ROOT),*args],env=run_env,
                              capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
    remote=git('remote','get-url','origin')
    if remote.returncode or remote.stdout.strip()!=REMOTE:raise RuntimeError('Origin does not match the authorized repository.')
    status=git('status','--porcelain')
    if status.returncode or status.stdout.strip():raise RuntimeError('Review and commit the working tree/index before pushing.')
    # The header exists only in the child process environment; never in a URL,
    # command argument, .git/config or log. Disable verbose HTTP tracing.
    token=cli('auth','token')
    if not token:raise RuntimeError('GitHub authentication unavailable.')
    header='Authorization: Basic '+base64.b64encode(('x-access-token:'+token).encode()).decode()
    push_env=env.copy()
    for key in list(push_env):
        if key.startswith('GIT_TRACE')or key=='GIT_CURL_VERBOSE':push_env.pop(key,None)
    push_env.update(GIT_TERMINAL_PROMPT='0',GIT_CONFIG_COUNT='3',
        GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',GIT_CONFIG_VALUE_0=header,
        GIT_CONFIG_KEY_1='credential.helper',GIT_CONFIG_VALUE_1='',GIT_CONFIG_KEY_2='http.sslVerify',GIT_CONFIG_VALUE_2='true')
    if '--fetch'in sys.argv:
        result=git('fetch','origin','main',run_env=push_env)
        if result.returncode:raise RuntimeError((result.stderr or result.stdout).replace(token,'[redacted]').replace(header,'[redacted]').strip())
        print('Fetched origin/main');return
    result=git('push','--set-upstream','origin','main',run_env=push_env)
    if result.returncode:
        message=(result.stderr or result.stdout).replace(token,'[redacted]').replace(header,'[redacted]')
        raise RuntimeError(message.strip())
    remote_sha=cli('api','repos/'+OWNER+'/'+REPO+'/git/ref/heads/main','--jq','.object.sha')
    local=git('rev-parse','HEAD')
    if local.returncode or local.stdout.strip()!=remote_sha:raise RuntimeError('Remote main differs from the reviewed local commit.')
    print('Verified push: '+remote_sha)
if __name__=='__main__':
    try:main()
    except Exception as e:print(type(e).__name__+': '+str(e));sys.exit(1)
