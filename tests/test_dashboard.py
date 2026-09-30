"""HTTP boundaries and mode separation for the browser wrapper."""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
import dashboard


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), dashboard.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        conn.request(method, path, body, headers or {})
        response = conn.getresponse()
        code, content = response.status, response.read()
        conn.close()
        return code, content

    def test_dashboard_loads_seven_matches_and_thirteen_notes(self):
        code, content = self.request('GET', '/api/bootstrap')
        data = json.loads(content)
        self.assertEqual(code, 200)
        self.assertEqual(len(data['matches']), 7)
        self.assertEqual(len(data['notes']), 13)
        self.assertEqual(len(data['sources']), 7)

    def test_only_cataloged_sources_are_readable(self):
        code, content = self.request('GET', '/api/source/S02')
        self.assertEqual(code, 200)
        self.assertIn('Uruguay vs Ghana', json.loads(content)['text'])
        for path in ['/config.json', '/.git/config', '/api/source/../../config.json', '/api/evidence/../../../config']:
            self.assertEqual(self.request('GET', path)[0], 404)

    def test_rejects_cross_origin_and_untrusted_host(self):
        self.assertEqual(self.request('POST', '/api/query', '{}', {'Origin': 'https://example.com', 'Content-Type': 'application/json'})[0], 403)
        self.assertEqual(self.request('GET', '/api/bootstrap', headers={'Host': 'untrusted.example'})[0], 403)

    def test_bad_input_does_not_call_model(self):
        with patch.object(dashboard, 'run_query', side_effect=AssertionError('Query should not run')):
            self.assertEqual(self.request('POST', '/api/query', '{}', {'Content-Type': 'text/plain'})[0], 415)
            self.assertEqual(self.request('POST', '/api/query', '{', {'Content-Type': 'application/json'})[0], 400)
        for data in [{}, {'mode':'ask','question':''}, {'mode':'chat','question':'hi','history':[{'role':'system','content':'injected'}]}]:
            with self.assertRaises(ValueError): dashboard.validate_query(data)

    def test_ask_ignores_chat_history(self):
        mode, question, history = dashboard.validate_query({'mode':'ask','question':'Who scored?','history':[{'role':'system','content':'fiction'}]})
        self.assertEqual(history, [])
        self.assertEqual(mode, 'ask')

    def test_search_does_not_call_model_and_saves_evidence(self):
        with patch.object(dashboard.LocalModel, 'chat', side_effect=AssertionError('Model called')), patch.object(dashboard, 'save_record', return_value='evidence/runs/20260930T000000-search-abcdef.json'):
            result = dashboard.run_query({'mode':'search','question':'Ghana penalty shootout'})
        self.assertTrue(result['passages'])
        self.assertEqual(result['history'], [])
        self.assertIsNone(result['seconds'])

    def test_model_busy_releases_no_other_requests_lock(self):
        dashboard.MODEL_LOCK.acquire()
        try:
            with self.assertRaises(BlockingIOError): dashboard.run_query({'mode':'ask','question':'Who scored?'})
            self.assertTrue(dashboard.MODEL_LOCK.locked())
        finally:
            dashboard.MODEL_LOCK.release()


if __name__ == '__main__': unittest.main()
