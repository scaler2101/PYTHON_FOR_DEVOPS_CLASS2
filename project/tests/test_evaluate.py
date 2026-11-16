import unittest
from ops_monitor.evaluate import evaluate

class PolicyTests(unittest.TestCase):
    def test_detects_missing_unhealthy_and_incident(self):
        config = {'defaults': {'max_latency_ms': 500}, 'services': [
            {'id':'api', 'owner':'team', 'critical':True},
            {'id':'worker', 'owner':'team', 'critical':False}]}
        services = [{'id':'api','status':'degraded','latency_ms':700}]
        incidents = [{'service_id':'api','id':'INC-1','state':'open'}]
        findings = evaluate(services, incidents, config)
        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[0].reasons, ['unhealthy_status','latency_over_threshold_or_missing','open_incidents'])
        self.assertEqual(findings[1].reasons, ['service_missing_from_inventory'])
        self.assertEqual(findings[1].severity, 'warning')

if __name__ == '__main__':
    unittest.main()
