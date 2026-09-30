import json
import unittest
from unittest.mock import patch
from pathlib import Path
from retrieval import build_index,search,selected_sections,make_chunks,query_terms
from wiki import ROOT,load_config,validate_answer,needs_notes,ask
from local_model import LocalModel,ModelError

class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):build_index(ROOT,load_config())
    def test_chunks_are_exact_source_substrings(self):
        for p in make_chunks(selected_sections(ROOT)):
            original=(ROOT/p['path']).read_text()
            self.assertEqual(original[p['start']:p['end']],p['text'])
            self.assertTrue(p['path'].startswith('vault/raw/'))
    def test_test_answers_never_enter_index(self):
        sections=selected_sections(ROOT)
        self.assertTrue(all(s['path'].startswith('vault/raw/') for s in sections))
    def test_search_needs_no_model(self):
        with patch.object(LocalModel,'request',side_effect=AssertionError('Model called')):
            self.assertTrue(search(ROOT,'Ghana'))
    def test_group_question_retrieves_all_three_matches(self):
        titles={p['section'] for p in search(ROOT,'What were Uruguay results in the group stage and points?')}
        self.assertTrue({'Uruguay vs France','South Africa vs Uruguay','Mexico vs Uruguay','Group A standings'}<=titles)
    def test_bad_citation_and_invented_quote_rejected(self):
        passages=[{'id':'S1','text':'The final score was 1–1.'}]
        for evidence in [[{'passage':'P9','quote':'final score'}],[{'passage':'P1','quote':'Uruguay won 8–0'}]]:
            with self.assertRaises(ValueError):validate_answer({'status':'answered','claims':[{'text':'Test','evidence':evidence}],'reason':''},passages)
    def test_supported_reference_validates(self):
        text=validate_answer({'status':'answered','claims':[{'text':'The match was drawn.','evidence':[{'passage':'P1','quote':'final score was 1–1'}]}],'reason':''},[{'id':'S1','text':'The final score was 1–1.'}])
        self.assertIn('[S1]',text)
    def test_stage_expansion_does_not_supply_opponents(self):
        terms=query_terms('Who did Uruguay play after the quarter-finals?')
        self.assertNotIn('netherlands',terms)
        self.assertNotIn('germany',terms)
        titles={p['section'] for p in search(ROOT,'Who did Uruguay play after the quarter-finals, and where did they finish?')}
        self.assertTrue({'Uruguay vs Netherlands','Match for third place','Final standings'}<=titles)
    def test_fiction_stays_out_of_research_mode(self):
        self.assertFalse(needs_notes('Tell me an imaginary story about Uruguay with a fictional password.'))
    def test_mode_routing(self):
        for message in ['What can you help me with?','What can we do?','Make that shorter','Draft a study plan about Uruguay']:
            self.assertFalse(needs_notes(message))
        self.assertTrue(needs_notes('How did Uruguay beat Ghana?'))
    def test_cloud_endpoint_rejected(self):
        cfg=load_config();cfg['ollama_url']='https://ollama.com'
        with self.assertRaises(ModelError):LocalModel(cfg)
    def test_ask_never_reads_chat_history(self):
        captured=[]
        def fake_chat(client,messages,*args,**kwargs):
            captured.extend(messages)
            return json.dumps({'status':'insufficient_evidence','claims':[],'reason':'No evidence.'}),{}
        with patch.object(LocalModel,'chat',fake_chat),patch('wiki.save_record',return_value='test'):
            ask('What did Forlan eat for breakfast?',load_config())
        self.assertEqual([m['role'] for m in captured],['system','user'])
        self.assertNotIn('Celeste',captured[0]['content'])
if __name__=='__main__':unittest.main()
