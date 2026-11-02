"""Native formats, never executable instructions. Findings-only exports give no negatives."""
import json
from urllib.parse import urljoin
from defusedxml import ElementTree as ET
from .domain import Receipt, State, canonical_target

MAX_BYTES = 4 * 1024 * 1024


def parse(tool: str, raw: bytes) -> list[Receipt]:
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError('Empty or oversized artifact (limit 4 MiB)')
    try:
        if tool == 'nmap':
            return nmap(raw)
        if tool == 'nikto':
            return nikto(json.loads(raw))
        if tool == 'zap':
            return zap(json.loads(raw))
    except (KeyError, TypeError, AttributeError, IndexError) as e:
        raise ValueError('Malformed or unsupported native output') from e
    except Exception as e:
        raise ValueError(f'Invalid {tool} artifact: {type(e).__name__}') from e
    raise ValueError('Unsupported tool')


def nmap(raw):
    root = ET.fromstring(raw)
    if root.tag != 'nmaprun' or root.get('scanner') != 'nmap' or root.get('xmloutputversion') not in {'1.04', '1.05'}:
        raise ValueError('Requires Nmap XML schema 1.04 or 1.05')
    end = root.find('./runstats/finished')
    success = end is not None and end.get('exit') == 'success'
    rows = []
    for hi, host in enumerate(root.findall('host')):
        address = next((x.get('addr') for x in host.findall('address') if x.get('addrtype') in {'ipv4', 'ipv6'}), None)
        canonical_target(address)
        up = host.find('status') is not None and host.find('status').get('state') == 'up'
        for pi, port in enumerate(host.findall('./ports/port')):
            if port.get('protocol') != 'tcp':
                continue
            number = int(port.attrib['portid'])
            if not 1 <= number <= 65535:
                raise ValueError('Invalid port')
            state = port.find('state').get('state')
            outcome = State.INCONCLUSIVE
            if success and up and state == 'open':
                outcome = State.FINDING  # observation, not a vulnerability
            elif success and up and state == 'closed' and port.find('state').get('reason') in {'reset', 'resets', 'conn-refused'}:
                outcome = State.NOT_OBSERVED
            rows.append(Receipt(target=address, check=f'tcp-port:{number}', outcome=outcome,
                detail=f'TCP/{number} {state}; host_up={up}; native_finished={success}. Open service is discovery, not a vulnerability.',
                source_ref=f'/nmaprun/host[{hi+1}]/ports/port[{pi+1}]', observed_at=host.get('endtime')))
    return rows


def nikto(data):
    # Current 2.6 family exporter has no tool-version field; require its multi-host shape.
    if not isinstance(data, list) or not data:
        raise ValueError('Requires Nikto multi-host JSON array; legacy object unsupported')
    rows = []
    for hi, host in enumerate(data):
        if not all(k in host for k in ('host', 'ip', 'port', 'start_time', 'end_time', 'vulnerabilities')):
            raise ValueError('Unsupported Nikto JSON schema')
        ip = host['ip']
        canonical_target(ip)
        ip_url = f'[{ip}]' if ':' in ip else ip
        scheme = 'https' if host.get('ssl_info') else 'http'
        base, _, _ = canonical_target(f'{scheme}://{ip_url}:{int(host["port"])}/')
        rows.append(Receipt(target=base, check='web-server', outcome=State.INCONCLUSIVE,
            detail='Imported finding export; no reliable per-check negative receipts or proof of full endpoint traversal.',
            source_ref=f'/{hi}', observed_at=host['end_time']))
        for vi, v in enumerate(host['vulnerabilities']):
            url, _, _ = canonical_target(urljoin(base, v['url']))
            if urlsplit_origin(url) != urlsplit_origin(base):
                raise ValueError('Nikto location differs from exported host')
            rows.append(Receipt(target=url, check='web-server', outcome=State.FINDING,
                issue_class=f'nikto:{v["id"]}', title=str(v['msg']), detail=str(v['msg']),
                source_ref=f'/{hi}/vulnerabilities/{vi}', observed_at=host['end_time']))
    return rows


def urlsplit_origin(url):
    from urllib.parse import urlsplit
    u = urlsplit(url)
    return u.scheme, u.hostname, u.port


def zap(data):
    if not str(data['@version']).startswith('2.') or not isinstance(data['site'], list):
        raise ValueError('Requires ZAP 2.x traditional JSON; dev/unknown versions unsupported')
    rows = []
    for si, site in enumerate(data['site']):
        base, _, _ = canonical_target(site['@name'])
        rows.append(Receipt(target=base, check='web-alerts', outcome=State.INCONCLUSIVE,
            detail='Traditional alert export does not prove every passive/active rule ran or all routes were reached.',
            source_ref=f'/site/{si}', observed_at=data.get('created') or data.get('@generated')))
        for ai, alert in enumerate(site['alerts']):
            for ii, instance in enumerate(alert['instances']):
                url, _, _ = canonical_target(instance['uri'])
                if urlsplit_origin(url) != urlsplit_origin(base):
                    raise ValueError('ZAP instance differs from exported site')
                risk = str(alert['riskcode'])
                if risk not in {'0', '1', '2', '3'}:
                    raise ValueError('Unsupported risk code')
                rows.append(Receipt(target=url, check='web-alerts', outcome=State.FINDING,
                    issue_class=f'zap:{alert["pluginid"]}:{instance.get("method", "GET")}:{instance.get("param", "")}',
                    title=alert['alert'], detail=instance.get('evidence', '') or alert['desc'],
                    severity={'0':'informational','1':'low','2':'medium','3':'high'}[risk],
                    confidence=f'ZAP code {alert["confidence"]}',
                    remediation=alert.get('solution'), observed_at=data.get('created') or data.get('@generated'),
                    source_ref=f'/site/{si}/alerts/{ai}/instances/{ii}'))
    return rows
