import copy
import unittest
from check_platform_adapter import validate


def fixture(platform='web'):
    return {'schema_version':'chatbot.adapter/1','maturity':'specified','id':'AD1','platform':platform,'official_documentation':'https://official.invalid/spec','api_version':'bound-current','environment':'sandbox-fixture','account_eligibility':'verified fixture','selected_channel':'private workspace','audience':'actor own data','identity_rule':'tenant+provider actor stable IDs','authorization_rule':'current membership+purpose','revocation_rule':'recheck before dispatch','ingress':{'mode':'http_api','verification':'authenticated session+CSRF','dedupe_key_rule':'request identity','durable_boundary':'transaction before acknowledgement','retry_reconcile':'lookup same request identity','expiry_rule':'server TTL','ack_required':False},'egress':{'operation':'reply','audience_resolution':'authorized session','idempotency_rule':'logical reply ID','uncertain_outcome':'reconcile before repeat','policy_check':'current source and consent','rate_limit_policy':'bound account policy','claim_levels':['provider_accepted'],'proof_rules':{'provider_accepted':'successful domain receipt'}},'capabilities':[{'id':'C1','operation':'reply','tool_source':'custom','status':'configured','permissions':['own session'],'parameter_consumption_check':'fixture','fallback':'visible unavailable'}],'evidence':[]}


class AdapterTests(unittest.TestCase):
    def bad(self,d,text):self.assertTrue(any(text in e for e in validate(d)),validate(d))
    def test_web_specification_can_be_unexecuted(self):self.assertEqual([],validate(fixture()))
    def test_draft_does_not_claim_configured(self):self.assertEqual([],validate({'schema_version':'chatbot.adapter/1','maturity':'draft','platform':'other'}))
    def test_ambiguous_platform_not_guessed(self):d=fixture();d['platform']='смак';self.bad(d,'unknown platform')
    def test_old_format_rejected(self):d=fixture();d['schema_version']='chatbot.adapter/0';self.bad(d,'unsupported adapter')
    def test_wrong_platform_ingress_rejected(self):d=fixture('instagram');self.bad(d,'ingress mode')
    def test_telegram_polling_is_explicit(self):d=fixture('telegram');d['ingress']['mode']='polling';self.assertEqual([],validate(d))
    def test_slack_socket_mode_is_explicit(self):d=fixture('slack');d['ingress']['mode']='socket_mode';self.assertEqual([],validate(d))
    def test_ack_needs_bound_deadline(self):d=fixture();d['ingress']['ack_required']=True;self.bad(d,'ack_deadline_ms')
    def test_accepted_cannot_claim_delivered(self):d=fixture();d['egress']['claim_levels'].append('delivered');d['egress']['proof_rules']['delivered']='successful domain receipt';self.bad(d,'not delivery')
    def test_advertised_mcp_not_current_catalog(self):d=fixture();d['capabilities'][0]['tool_source']='official_mcp';self.bad(d,'current catalog')
    def test_exercised_needs_actual_proof(self):d=fixture();d['capabilities'][0]['status']='exercised';self.bad(d,'needs evidence')
    def test_actual_proof_wrong_environment(self):d=fixture();c=d['capabilities'][0];c.update(status='exercised',evidence_ids=['E1']);d['evidence']=[{'id':'E1','result':'pass','environment':'another','capability_ids':['C1'],'artifact':'receipt.json','sha256':'a'*64}];self.bad(d,'environment/artifact')
    def test_no_secret_values_in_artifact(self):d=fixture();d['credentials']={'bot_token':'fake-example'};self.bad(d,'secret values')
    def test_no_secret_values_even_in_draft(self):d={'schema_version':'chatbot.adapter/1','maturity':'draft','platform':'other','credentials':{'access_token':'fake-example'}};self.bad(d,'secret values')
    def test_permissions_must_be_declared_list(self):d=fixture();d['capabilities'][0]['permissions']='unknown';self.bad(d,'permission list')
    def test_missing_audience_resolution_rejected(self):d=fixture();del d['egress']['audience_resolution'];self.bad(d,'audience_resolution')
    def test_duplicate_capability_ids_rejected(self):d=fixture();d['capabilities'].append(copy.deepcopy(d['capabilities'][0]));self.bad(d,'ids must be unique')
    def test_exercised_hash_and_evidence_identity_are_bound(self):
        d=fixture();d['capabilities'][0].update(status='exercised',evidence_ids=['E1'])
        d['evidence']=[{'id':'E1','result':'pass','environment':d['environment'],'capability_ids':['C1'],'artifact':'SYNTHETIC.json','sha256':'not-a-sha'}]
        self.bad(d,'scope/environment/artifact')
        d['evidence'][0]['sha256']='a'*64
        self.assertEqual(validate(d),[])
        d['evidence'].append(copy.deepcopy(d['evidence'][0]));self.bad(d,'evidence ids must be unique')
    def test_malformed_adapter_fields_return_diagnostics(self):
        for field,value in [('platform',[]),('claim_levels',[{}]),('evidence_ids','E1')]:
            d=fixture()
            if field=='platform':d[field]=value
            elif field=='claim_levels':d['egress'][field]=value
            else:d['capabilities'][0][field]=value
            self.assertTrue(validate(d))


if __name__=='__main__':unittest.main()
