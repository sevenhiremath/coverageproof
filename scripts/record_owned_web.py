"""Record fixed Nikto/ZAP checks against the owned, network-none fixture only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import uuid

TARGET='http://127.0.0.1:8765/'
IMAGES={'nikto':'ghcr.io/sullo/nikto:2.6.1','zap':'ghcr.io/zaproxy/zaproxy:stable'}


def checked(args, timeout=90):
    r=subprocess.run(args,capture_output=True,timeout=timeout)
    if r.returncode:
        raise RuntimeError(f'Command failed: {args[:3]}: {r.stderr.decode(errors="replace")[:1000]}')
    return r.stdout


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool',choices=IMAGES,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    names=['cp-web-fixture-'+uuid.uuid4().hex[:10],'cp-web-tool-'+uuid.uuid4().hex[:10]]
    common=['--cap-drop','ALL','--security-opt','no-new-privileges','--read-only','--pids-limit','256','--cpus','2','--memory','1g']
    manifest={'tool':args.tool,'target':TARGET,'status':'setup','limitations':[
        'Self-owned development fixture only; not organizer authorization.',
        'Finding exports do not establish full coverage or negative results.']}
    try:
        # Image acquisition/build happens before runtime isolation, with no fixture traffic.
        checked(['docker','image','inspect','coverageproof-fixture'])
        image=json.loads(checked(['docker','image','inspect',IMAGES[args.tool]]))[0]
        manifest['image_id']=image['Id']
        manifest['repo_digests']=image.get('RepoDigests',[])
        checked(['docker','run','-d','--name',names[0],'--network','none',*common,'coverageproof-fixture'])
        inspect=json.loads(checked(['docker','inspect',names[0]]))[0]
        assert inspect['HostConfig']['NetworkMode']=='none'
        assert not inspect['Mounts'] and not inspect['HostConfig'].get('PortBindings')
        probe="import socket,pathlib,urllib.request; assert [n for _,n in socket.if_nameindex()]==['lo']; assert len(pathlib.Path('/proc/net/route').read_text().splitlines())==1; print(urllib.request.urlopen('http://127.0.0.1:8765/',timeout=2).status)"
        for attempt in range(20):
            try:
                checked(['docker','exec',names[0],'python','-c',probe]);break
            except RuntimeError:
                if attempt==19:raise
                time.sleep(.1)
        shell = (
            '/opt/nikto/nikto.pl -h http://127.0.0.1:8765/ -Tuning 1 -maxtime 60 -timeout 3 -nointeractive -nocheck -ask no -Format json -output /tmp/results.json'
            if args.tool=='nikto' else
            'zap-baseline.py -t http://127.0.0.1:8765/ -m 1 -T 2 -J /tmp/results.json --autooff')
        command=['docker','run','--name',names[1],'--network','container:'+names[0],
            *common,'--tmpfs','/tmp:rw,nosuid,nodev,size=512m',
            '--tmpfs','/home/zap/.ZAP:rw,nosuid,nodev,size=128m,uid=1000,gid=1000',
            '--tmpfs','/zap/wrk:rw,nosuid,nodev,size=32m,uid=1000,gid=1000',
            '--entrypoint','sh',manifest['image_id'],'-c',shell+'; code=$?; echo $code > /tmp/exit-status; sleep 300']
        manifest['command']=command
        manifest['status']='running'
        process=subprocess.Popen(command,stdout=(args.output/'tool.stdout').open('wb'),stderr=(args.output/'tool.stderr').open('wb'))
        deadline=time.monotonic()+240
        while True:
            status=subprocess.run(['docker','exec',names[1],'cat','/tmp/exit-status'],capture_output=True)
            if status.returncode==0:
                manifest['exit_status']=int(status.stdout.strip());break
            if process.poll() is not None or time.monotonic()>deadline:
                raise RuntimeError('Tool stopped or exceeded fixed wall timeout')
            time.sleep(1)
        manifest['tool_inspect']=json.loads(checked(['docker','inspect',names[1]]))[0]
        # Read mounted tmpfs through the running container, not Docker's archive API.
        copied=subprocess.run(['docker','exec',names[1],'cat','/tmp/results.json'],capture_output=True,timeout=15)
        (args.output/'copy.stderr').write_bytes(copied.stderr)
        if copied.returncode:
            listing=subprocess.run(['docker','exec',names[1],'ls','-la','/tmp'],capture_output=True,timeout=15)
            (args.output/'scratch-listing.txt').write_bytes(listing.stdout+listing.stderr)
            raise RuntimeError('Raw export unavailable; preserve diagnostics and stop')
        (args.output/'results.json').write_bytes(copied.stdout)
        raw=(args.output/'results.json').read_bytes()
        manifest['sha256']=hashlib.sha256(raw).hexdigest()
        from coverageproof.adapters import parse
        rows=parse(args.tool,raw)
        manifest['parsed_receipts']=len(rows)
        from coverageproof.domain import Scope, Action
        from coverageproof.store import Store
        store=Store(args.output/'import.sqlite')
        assessment=store.create('Genuine owned web export',Scope(name='Owned isolated fixture',
            networks=('127.0.0.1/32',),ports=(8765,),authorization_reference='Self-owned network-none fixture'))
        check='web-server' if args.tool=='nikto' else 'web-alerts'
        for target in [TARGET,TARGET+'admin']:
            store.add_check(assessment,Action(check=check,target=target,scope_revision=1))
        store.ingest(assessment,args.tool,raw)
        snap=store.snapshot(assessment)
        (args.output/'snapshot.json').write_text(json.dumps(snap,indent=2))
        assert snap['artifacts'] and not snap['approvals']
        assert any(c['observations'] for c in snap['checks']), 'No receipt matched declared targets'
        assert not any(c['state']=='condition_not_observed' for c in snap['checks']), 'Alert exports must not prove negatives'
        assert manifest['exit_status'] in ({0} if args.tool=='nikto' else {0,1,2}), 'Tool error despite export'
        manifest['status']='import_verified'
    except Exception as error:
        manifest['status']='failed'
        manifest['error_type']=type(error).__name__
        raise
    finally:
        (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2))
        for name in reversed(names):
            subprocess.run(['docker','rm','-f',name],capture_output=True)


if __name__=='__main__':main()
