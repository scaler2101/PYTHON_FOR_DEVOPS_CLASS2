"""Pure policy evaluation: testable without a running web server."""
from .models import Finding


def evaluate(services, incidents, config):
    inventory = {s['id']: s for s in services}
    open_incidents = {}
    for row in incidents:
        if row.get('state') == 'open':
            open_incidents.setdefault(row.get('service_id'), []).append(row['id'])
    findings = []
    defaults = config['defaults']
    for rule in config['services']:
        service_id = rule['id']
        actual = inventory.get(service_id)
        reasons = []
        if actual is None:
            reasons.append('service_missing_from_inventory')
        else:
            if actual.get('status') != 'healthy':
                reasons.append('unhealthy_status')
            latency = actual.get('latency_ms')
            maximum = rule.get('max_latency_ms', defaults['max_latency_ms'])
            if not isinstance(latency, (int, float)) or latency > maximum:
                reasons.append('latency_over_threshold_or_missing')
        incident_ids = open_incidents.get(service_id, [])
        if incident_ids:
            reasons.append('open_incidents')
        if reasons:
            findings.append(Finding(service_id, rule['owner'],
                'critical' if rule['critical'] else 'warning', reasons, incident_ids))
    return findings
