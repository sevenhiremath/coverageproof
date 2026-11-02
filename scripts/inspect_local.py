"""Read-only capability report. Does not scan targets or inspect secret variables."""
import json
import platform
import shutil
import subprocess
from pathlib import Path

commands = {
    'git': ['git','--version'],
    'docker': ['docker','version','--format','{{.Client.Version}} {{if .Server}}{{.Server.Version}}{{end}}'],
    'nmap': ['nmap','--version'],
    'perl': ['perl','-e','print $^V'],
    'java': ['java','-version'],
}
report = {'system':platform.system(), 'architecture':platform.machine(), 'python':platform.python_version(), 'tools':{}, 'scanner_execution_performed':False}
for name, command in commands.items():
    if not shutil.which(command[0]):
        report['tools'][name] = {'available':False}
        continue
    try:
        r=subprocess.run(command,capture_output=True,text=True,timeout=10,shell=False)
        # Version output only; omit stderr because it can contain host paths or socket names.
        first=(r.stdout or '').splitlines()[:2]
        report['tools'][name]={'available':True,'exit_code':r.returncode,'version_excerpt':'\n'.join(first)[:300], 'version_on_stderr':bool(r.stderr and not r.stdout)}
    except subprocess.TimeoutExpired:
        report['tools'][name]={'available':True,'status':'version command timed out'}
    except OSError:
        report['tools'][name]={'available':True,'status':'version command could not start'}
Path('local-capabilities.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
