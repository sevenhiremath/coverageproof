"""Record one genuine TCP-connect check in an owned, network-none fixture.

Requires Docker; never scans the host, public addresses or third-party services.
Only the registered literal target/port below are used; no caller scan options.
"""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

OUT = Path('output/native-lab')
FIXTURE = 'coverageproof-recording-fixture'
HARDEN = ['--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--read-only', '--memory', '128m', '--cpus', '1', '--pids-limit', '32']


def run(args, timeout=60, data=None):
    return subprocess.run(args, input=data, capture_output=True, timeout=timeout, check=False)


def checked(args, timeout=60):
    r=run(args,timeout)
    if r.returncode:
        raise RuntimeError(f'Setup failed ({r.returncode}): {args[0:3]}: {r.stderr.decode(errors="replace")[:2000]}')
    return r.stdout


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    created=False
    try:
        checked(['docker','run','-d','--name',FIXTURE,'--network','none',*HARDEN,'coverageproof-fixture'])
        created=True
        info=json.loads(checked(['docker','inspect',FIXTURE]))[0]
        h=info['HostConfig']
        assert h['NetworkMode']=='none' and h['ReadonlyRootfs'] and not h['Privileged']
        assert not info['Mounts'] and not h.get('PortBindings') and not h.get('Binds')
        assert 'ALL' in h['CapDrop'] and 'no-new-privileges' in h['SecurityOpt']
        assert info['Config']['User']=='10001'
        (OUT/'fixture-inspect.json').write_text(json.dumps(info,indent=2))
        probe='''import json,socket,pathlib,time,urllib.request
interfaces=socket.if_nameindex(); assert [n for _,n in interfaces]==['lo']
routes=pathlib.Path('/proc/net/route').read_text(); assert len(routes.splitlines())==1
status=pathlib.Path('/proc/self/status').read_text(); assert 'CapEff:\\t0000000000000000' in status and 'NoNewPrivs:\\t1' in status
s=socket.socket();s.settimeout(1)
try:
 s.connect(('192.0.2.1',9))
 raise AssertionError('Unexpected external reachability')
except OSError as e: external=type(e).__name__
finally:s.close()
for attempt in range(20):
 try:
  response=urllib.request.urlopen('http://127.0.0.1:8765/admin',timeout=1);assert response.status==200 and response.headers['X-Content-Type-Options']=='nosniff';break
 except OSError:
  if attempt==19:raise
  time.sleep(.1)
print(json.dumps({'interfaces':interfaces,'ipv4_routes':routes,'external_connect_result':external,'status':status,'fixture_http_status':response.status}))
'''
        (OUT/'containment.json').write_bytes(checked(['docker','exec',FIXTURE,'python','-c',probe]))
        version=checked(['docker','run','--rm','--network','none',*HARDEN,'coverageproof-nmap','--version']).decode()
        # TCP connect is discovery only. No NSE, service probes, exploitation or DNS.
        command=['docker','run','--rm','--network',f'container:{FIXTURE}',*HARDEN,'coverageproof-nmap','--unprivileged','-sT','-Pn','-n','-p','8765','--max-retries','1','--host-timeout','30s','-oX','-','127.0.0.1']
        start=datetime.now(timezone.utc).isoformat()
        result=run(command,45)
        end=datetime.now(timezone.utc).isoformat()
        (OUT/'nmap.xml').write_bytes(result.stdout)
        (OUT/'nmap.stderr').write_bytes(result.stderr)
        images={name:json.loads(checked(['docker','image','inspect',name]))[0]['Id'] for name in ['coverageproof-fixture','coverageproof-nmap','coverageproof-tests']}
        manifest={'source':'recorded_genuine','authorization':'Self-owned benign development fixture; not organizer authorization','target':'127.0.0.1','port':8765,'network':'fixture network none; scanner shares only its namespace','command':command,'tool_version':version,'start':start,'end':end,'exit_status':result.returncode,'sha256':hashlib.sha256(result.stdout).hexdigest(),'image_ids':images,'limitations':['One TCP port only; open is discovery, not a vulnerability.','No native web scanner or live model has run in this recording.','No speed/accuracy claim from a single fixture.']}
        (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
        assert result.returncode==0, 'Scanner process failed; preserve raw outputs'
        assert len(result.stdout)+len(result.stderr)<=262144, 'Output exceeds interpretation limit'
        validate='''import sys,json,tempfile
from coverageproof.domain import Scope,Action
from coverageproof.store import Store
s=Store(tempfile.mktemp(suffix='.sqlite'));a=s.create('Genuine owned Nmap recording',Scope(name='Isolated owned fixture',networks=('127.0.0.1/32',),ports=(8765,),authorization_reference='Self-owned benign fixture in isolated GitHub runner'))
s.add_check(a,Action(check='tcp-port',target='127.0.0.1',port=8765,scope_revision=1));s.ingest(a,'nmap',sys.stdin.buffer.read());snap=s.snapshot(a)
assert len(snap['checks'][0]['observations'])==1
assert snap['checks'][0]['state']=='finding_supported', snap['checks'][0]
assert not snap['findings'], 'An open port must not become a vulnerability candidate'
print(json.dumps(snap,indent=2))
'''
        # Open service is an inventory observation, not a vulnerability finding.
        response=run(['docker','run','--rm','-i','--network','none',*HARDEN,'--tmpfs','/tmp:rw,nosuid,nodev,size=32m','--entrypoint','python','coverageproof-tests','-c',validate],data=result.stdout)
        (OUT/'import-check.stdout').write_bytes(response.stdout)
        (OUT/'import-check.stderr').write_bytes(response.stderr)
        assert response.returncode==0, 'Genuine native import check failed; inspect preserved output'
        print('Genuine owned Nmap recording and app import verified; artifacts in',OUT)
    finally:
        if created:
            checked(['docker','stop','--time','3',FIXTURE],15)
            checked(['docker','rm',FIXTURE],15)

if __name__=='__main__':main()
