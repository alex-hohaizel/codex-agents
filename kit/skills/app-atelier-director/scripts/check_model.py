#!/usr/bin/env python3
"""Calculate scenario economics from explicit assumptions; calculations never prove demand or profit."""
import argparse
import datetime as dt
from decimal import Decimal, InvalidOperation, localcontext, ROUND_CEILING, ROUND_HALF_EVEN
import json
from pathlib import Path
import re
import sys



def strict_json_loads(raw, **kwargs):
    """Reject ambiguous/nonfinite JSON before hashing, validation or mutation."""
    if len(raw) > 256 * 1024 * 1024:
        raise ValueError("JSON exceeds bounded input limit")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    def finite(value):
        raise ValueError("nonfinite JSON value: " + value)
    kwargs.setdefault("object_pairs_hook", unique)
    kwargs.setdefault("parse_constant", finite)
    return json.loads(raw, **kwargs)


DECIMAL_PRECISION = 1024
DECIMAL_INPUT = re.compile(r'^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$')
DISPLAY_QUANTUM = Decimal('0.000001')

EXAMPLE={
 'schema_version':'app-atelier-economics/1','currency':'USD','target_profit':1000,
 'assumptions':[{'id':'A-PRICE','kind':'hypothesis','source':'owner pricing hypothesis','checked_at':'2026-11-02','note':'Example only; not market evidence.'}],
 'scenarios':[{'name':'base','paid_users':1000,'free_users':5000,'price_per_month':12,
  'commission_rate':0.15,'refund_rate':0.02,'paid_variable_cost':0.5,'free_variable_cost':0.03,
  'fixed_cost':100,'acquisition_cost':200,'other_revenue':0,
  'ad_impressions_per_free_user':15,'ad_fill_rate':0.5,'ad_ecpm':2,
  'assumption_ids':['A-PRICE']}]
}

def need(ok,message):
    if not ok:raise ValueError(message)

def n(row,key,default=None):
    v=row.get(key,default)
    need(type(v) in (int,float,str,Decimal),'invalid nonnegative decimal: '+key)
    raw=str(v)
    need(len(raw)<=128 and DECIMAL_INPUT.fullmatch(raw) is not None,'invalid nonnegative decimal: '+key)
    try:value=Decimal(raw)
    except InvalidOperation:raise ValueError('invalid nonnegative decimal: '+key)
    need(value.is_finite() and value>=0,'invalid nonnegative decimal: '+key)
    need(len(value.as_tuple().digits)<=48 and (not value or -48<=value.adjusted()<=48)
         and abs(value.as_tuple().exponent)<=96,'decimal input exceeds supported precision/range: '+key)
    return value

def json_number(value):
    """Numeric display only; comparisons and required scale use unrounded Decimal."""
    shown=value.quantize(DISPLAY_QUANTUM,rounding=ROUND_HALF_EVEN)
    return int(shown) if shown==shown.to_integral_value() else float(shown)

def rate(row,key,default=0):
    v=n(row,key,default);need(v<=1,'rate outside [0,1]: '+key);return v

def required_units(numerator,margin):
    if margin<=0:return None
    value=max(Decimal(0),numerator/margin);need(value.is_finite(),'arithmetic overflow in required scale')
    return int(value.to_integral_value(rounding=ROUND_CEILING))

def calculate(model,target=None):
    # Bounds above keep the fixed multiplication/addition expressions and ceiling
    # decision within this context. No provider per-transaction rounding is implied.
    try:
        with localcontext() as ctx:
            ctx.prec=DECIMAL_PRECISION
            return _calculate(model,target)
    except InvalidOperation as exc:raise ValueError('decimal arithmetic exceeds supported model range') from exc

def _calculate(model,target=None):
    need(isinstance(model,dict) and model.get('schema_version')=='app-atelier-economics/1','unsupported model schema')
    need(model.get('currency')=='USD','this calculator expects USD inputs; convert with a dated explicit exchange-rate assumption first')
    target=n(model,'target_profit',0) if target is None else n({'target':target},'target')
    assumptions=model.get('assumptions');need(isinstance(assumptions,list) and assumptions,'assumptions with source/date are required')
    ids=set();warnings=[]
    today=dt.datetime.now(dt.timezone.utc).date()
    for a in assumptions:
        need(isinstance(a,dict) and isinstance(a.get('id'),str) and a['id'] and a['id'] not in ids,'assumption IDs must be unique')
        ids.add(a['id']);need(a.get('kind') in ('observed','source_claim','hypothesis','estimate'),'assumption kind required')
        need(isinstance(a.get('source'),str) and a['source'],'assumption source required')
        try:date=dt.date.fromisoformat(a['checked_at'])
        except (ValueError,KeyError,TypeError):raise ValueError('assumption checked_at must be ISO date')
        if date>today:warnings.append(a['id']+': source date is in the future relative to this host; verify clock/source date')
        elif (today-date).days>90:warnings.append(a['id']+': source older than 90 days; verify applicability, not automatically false')
    scenarios=model.get('scenarios');need(isinstance(scenarios,list) and 1<=len(scenarios)<=50,'1..50 scenarios required')
    names=set();out=[]
    for s in scenarios:
        need(isinstance(s,dict) and isinstance(s.get('name'),str) and s['name'] and s['name'] not in names,'scenario names must be unique');names.add(s['name'])
        refs=s.get('assumption_ids');need(isinstance(refs,list) and refs and set(refs)<=ids,'scenario needs known assumption_ids')
        paid=n(s,'paid_users');free=n(s,'free_users');price=n(s,'price_per_month');commission=rate(s,'commission_rate');refund=rate(s,'refund_rate')
        pvc=n(s,'paid_variable_cost');fvc=n(s,'free_variable_cost');fixed=n(s,'fixed_cost');acquisition=n(s,'acquisition_cost');other=n(s,'other_revenue',0)
        impressions=n(s,'ad_impressions_per_free_user',0);fill=rate(s,'ad_fill_rate',0);ecpm=n(s,'ad_ecpm',0)
        gross=paid*price;refunds=gross*refund;commissions=(gross-refunds)*commission
        net_paid=gross-refunds-commissions
        ads_per_free=impressions*fill*ecpm/1000
        ads=free*ads_per_free;variable=paid*pvc+free*fvc
        profit=net_paid+ads+other-variable-fixed-acquisition
        paid_margin=price*(1-refund)*(1-commission)-pvc
        free_margin=ads_per_free-fvc
        need(all(x.is_finite() for x in [gross,refunds,commissions,net_paid,ads_per_free,ads,variable,profit,paid_margin,free_margin]),'arithmetic overflow in scenario; use a specialist model')
        required_paid=required_units(target+fixed+acquisition-other-free*free_margin,paid_margin)
        required_free=required_units(target+fixed+acquisition-other-paid*paid_margin,free_margin)
        r={'name':s['name'],'gross_paid_revenue':json_number(gross),'refunds':json_number(refunds),'commissions_on_retained_revenue':json_number(commissions),
           'net_paid_revenue':json_number(net_paid),'ad_revenue':json_number(ads),'other_revenue':json_number(other),'variable_costs':json_number(variable),
           'fixed_cost':json_number(fixed),'acquisition_cost':json_number(acquisition),'operating_profit':json_number(profit),'target_profit':json_number(target),'target_met_under_assumptions':profit>=target,
           'paid_contribution_per_user':json_number(paid_margin),'free_contribution_per_user':json_number(free_margin),
           'required_paid_users_at_same_free_cohort':required_paid,'required_free_users_at_same_paid_cohort':required_free,
           'scalable_unit_margin_exists':paid_margin>0 or free_margin>0,'negative_paid_margin':paid_margin<0,'negative_free_margin':free_margin<0,
           'exact_decimal':{'operating_profit':str(profit),'target_profit':str(target),'paid_contribution_per_user':str(paid_margin),'free_contribution_per_user':str(free_margin)},
           'assumption_ids':refs,'limitations':'Required scale holds other cohort, price, unit costs and fixed/acquisition costs constant. Recompute when scale changes costs or acquisition. paid_users means units billed this month; for one-time purchases count new purchases, not all historical owners. Numeric display is rounded to six decimals; decisions use unrounded Decimal. Provider per-transaction rounding is not modeled.'}
        if 'monthly_external_cost_cap' in s:
            cap=n(s,'monthly_external_cost_cap');cost=variable+fixed+acquisition;r['external_cost_cap']=json_number(cap);r['external_cost_cap_exceeded']=cost>cap
        out.append(r)
    if len(scenarios)<3:warnings.append('Fewer than three scenarios: add downside/base/upside and sensitivity before selecting a concept.')
    return {'currency':'USD','scenarios':out,'warnings':warnings,'profit_definition':'After modeled operating expenses, before personal taxes and owner time unless explicitly included in costs.',
            'commission_convention':'Commission is applied to retained revenue after modeled refunds; verify the actual provider convention/fees and include differences as costs.',
            'arithmetic_policy':{'engine':'Decimal','precision':DECIMAL_PRECISION,'input':'JSON numbers, decimal strings or Decimal; at most 48 significant digits and nonzero adjusted exponent [-48,48]','display_rounding':'six decimals, ROUND_HALF_EVEN; exact_decimal preserves unrounded decision values','provider_rounding':'not assumed; bind actual provider convention in a specialist model'},
            'evidence_status':'assumption_based_calculation_not_demand_validation','guaranteed_profit':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__,epilog='Use --example for exact input schema. All costs are USD/month; variable costs are per user/month. Models may combine paid, free and ad cohorts. Refund and commission rates are fractions 0..1. Other-revenue/cost values need dated assumption references too.')
    parser.add_argument('--model',type=Path);parser.add_argument('--target-profit');parser.add_argument('--example',action='store_true');parser.add_argument('--json',action='store_true',help='Output is always machine-readable JSON; retained for explicit CLI intent.')
    args=parser.parse_args()
    if args.example:print(json.dumps(EXAMPLE,ensure_ascii=False,indent=2));return
    need(args.model is not None,'--model FILE required unless --example')
    need(not args.model.is_symlink() and args.model.is_file() and args.model.stat().st_size<=4*1024*1024,'model must be a regular bounded JSON file')
    with args.model.open(encoding='utf-8') as f:model=strict_json_loads(f.read(256 * 1024 * 1024 + 1),parse_float=Decimal,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON value')))
    print(json.dumps(calculate(model,args.target_profit),ensure_ascii=False,indent=2,allow_nan=False))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as e:
        print(json.dumps({'error':str(e),'calculated':False},ensure_ascii=False),file=sys.stderr);raise SystemExit(2)
