"""Independent arithmetic boundary cases; no provider or demand claims."""
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'check_model.py'
spec=importlib.util.spec_from_file_location('economics_under_test',SCRIPT)
economics=importlib.util.module_from_spec(spec);spec.loader.exec_module(economics)

def model(**scenario):
    row={'name':'boundary','paid_users':1,'free_users':0,'price_per_month':'0.30',
         'commission_rate':0,'refund_rate':0,'paid_variable_cost':'0.10',
         'free_variable_cost':0,'fixed_cost':'0.20','acquisition_cost':0,'assumption_ids':['A']}
    row.update(scenario)
    return {'schema_version':'app-atelier-economics/1','currency':'USD','target_profit':0,
            'assumptions':[{'id':'A','kind':'hypothesis','source':'synthetic arithmetic fixture','checked_at':'2026-11-04'}],
            'scenarios':[row]}

class EconomicsTests(unittest.TestCase):
    def row(self,value):return economics.calculate(value)['scenarios'][0]

    def test_decimal_boundary_is_met_with_one_paid_unit(self):
        r=self.row(model())
        self.assertEqual(r['operating_profit'],0)
        self.assertTrue(r['target_met_under_assumptions'])
        self.assertEqual(r['required_paid_users_at_same_free_cohort'],1)

    def test_existing_json_numbers_and_explicit_decimals_agree(self):
        expected=self.row(model())
        for values in [(0.30,0.10,0.20),(Decimal('0.30'),Decimal('0.10'),Decimal('0.20'))]:
            actual=self.row(model(price_per_month=values[0],paid_variable_cost=values[1],fixed_cost=values[2]))
            self.assertEqual(actual['target_met_under_assumptions'],expected['target_met_under_assumptions'])
            self.assertEqual(actual['required_paid_users_at_same_free_cohort'],1)

    def test_ceil_keeps_just_above_integer_boundary(self):
        r=self.row(model(fixed_cost='0.200000000000000000000000000000000000000000000001'))
        self.assertEqual(r['required_paid_users_at_same_free_cohort'],2)
        self.assertFalse(r['target_met_under_assumptions'])
        self.assertLess(Decimal(r['exact_decimal']['operating_profit']),0)

    def test_refunds_and_commissions_use_retained_revenue(self):
        m=model(paid_users=10,price_per_month='10',paid_variable_cost='2',fixed_cost='0',refund_rate='0.10',commission_rate='0.20')
        r=self.row(m)
        # 100 gross -10 refunds -18 commission -20 variable =52.
        self.assertEqual(r['net_paid_revenue'],72)
        self.assertEqual(r['operating_profit'],52)

    def test_nonpositive_margin_is_not_reported_scalable(self):
        for cost in ['0.30','0.31']:
            r=self.row(model(paid_variable_cost=cost))
            self.assertIsNone(r['required_paid_users_at_same_free_cohort'])
            self.assertFalse(r['scalable_unit_margin_exists'])

    def test_free_cohort_and_cost_cap_are_exact(self):
        r=self.row(model(paid_users=0,free_users=1,price_per_month=0,paid_variable_cost=0,
                         fixed_cost=0,free_variable_cost='0.3',ad_impressions_per_free_user=1000,
                         ad_fill_rate=1,ad_ecpm='0.3',monthly_external_cost_cap='0.3'))
        self.assertTrue(r['target_met_under_assumptions'])
        self.assertFalse(r['external_cost_cap_exceeded'])

    def test_json_output_contains_no_decimal_objects_or_nonfinite_numbers(self):
        result=economics.calculate(model())
        json.dumps(result,allow_nan=False)
        self.assertFalse(result['guaranteed_profit'])
        self.assertEqual(result['evidence_status'],'assumption_based_calculation_not_demand_validation')

    def test_invalid_and_out_of_range_numbers_are_rejected(self):
        for value in [True,False,'NaN','Infinity','-1','1_000','0.1 dollars','1e49','1e-49','0.'+'1'*49]:
            with self.subTest(value=value),self.assertRaises(ValueError):self.row(model(price_per_month=value))
        with self.assertRaises(ValueError):self.row(model(refund_rate='1.01'))

    def test_cli_preserves_decimal_lexeme_and_target(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'model.json';p.write_text(json.dumps(model(price_per_month=0.3,paid_variable_cost=0.1,fixed_cost=0.2)))
            r=subprocess.run([sys.executable,'-B',str(SCRIPT),'--model',str(p),'--target-profit','0'],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue(json.loads(r.stdout)['scenarios'][0]['target_met_under_assumptions'])

if __name__=='__main__':unittest.main()
