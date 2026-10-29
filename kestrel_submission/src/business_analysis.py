"""Reproducible exploratory baseline, NOT a validated AI/LLM classifier.
Run from project root: python src/business_analysis.py
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'processed'
OUT = ROOT / 'reports' / 'analysis'
OUT.mkdir(parents=True, exist_ok=True)

# Conservative phrase rules; multi-label, matching text only.
THEMES = {
    'Communication': [r'call\s?back',r'call(ed|ing|s)?\s+(me\s+)?(back|again)',r'no (call|text|update|contact)',r'never (called|rang|replied|got back)',r'kept (me )?(updated|posted)',r'no(body| one) (told|knew|explained)',r'(poor|bad|zero|lack of) communication',r'message.{0,50}(passed|received)',r'no updates?',r'had to (chase|ring|call)',r'explain(ed|ation|ing)?',r'phone(d|s)?',r'follow.?up'],
    'Waiting & delays': [r'wait(ed|ing|s)?',r'(too|so|very) (slow|long)',r'(late|delay(ed|s)?)',r'on time',r'ahead of schedule',r'quick(ly)?',r'prompt',r'took (six|five|four|three|two|ages|hours)',r'overbooked',r'reschedul',r'queue',r'turnaround',r'(ready|finished) (by|at|before|after)'],
    'Price & billing': [r'bill(ed|ing)?',r'charg(ed|es|ing)?',r'price',r'quote(d|s)?',r'cost',r'invoice',r'fee',r'expensiv',r'cheap(er)?',r'over(estimat|quot)',r'finance product',r'(optional|extra) (cover|protection|package)'],
    'Parts availability': [r'back.?order',r'out of stock',r'(part|stock).{0,45}(late|wait|delay|not avail|order|short)',r'(late|wait|delay).{0,35}part',r'ships from overseas',r'weeks? for (a|the) (part|tail light|light)',r'parts? availab'],
    'Quality & repairs': [r'not fixed',r'still (grind|rattl|shak|squeal|broken|there|occurring)',r'fix was',r'repair',r'workmanship',r'scratch(ed)?',r'damag(ed|e)',r'fault',r'greasy',r'mud on',r'dirty inside',r'brak(es|ing)',r'mechanic'],
    'Staff & courtesy': [r'(rude|dismissive|condescending|unhelpful|snobby)',r'friendly',r'helpful',r'(polite|courteous|welcom|kind|lovely)',r'staff',r'service (guy|advisor)',r'(treated|spoke to) me',r'front desk'],
}
NEG_CUES = [r'not happy', r'poor',r'bad',r'rubbish',r'never',r'no (call|text|update)',r'wrong',r'dodgy',r'excessive',r'too (long|slow|much)',r'waited (ages|hours|over)',r'still (not|grind|shak|rattl|squeal)',r'(late|delayed|rude|dismissive|scratch|filthy|broken)',r'wasn.t',r'didn.t',r'fail(ed|ure)',r'overcharg',r'had to chase',r'(but|however|though).{0,80}(no |not |late|rude|wait|bill|charg|still)']

compiled = {name: [re.compile(p,re.I) for p in patterns] for name,patterns in THEMES.items()}
neg_compiled = [re.compile(p,re.I) for p in NEG_CUES]

def classify(text):
    if not isinstance(text,str) or not text.strip():
        return pd.Series({'baseline_themes':'','baseline_negative_cue':False,'baseline_flag':'no_text'})
    themes = [name for name,patterns in compiled.items() if any(p.search(text) for p in patterns)]
    neg = any(p.search(text) for p in neg_compiled)
    return pd.Series({'baseline_themes':'|'.join(themes),'baseline_negative_cue':bool(neg),'baseline_flag':'rule_based_exploratory'})

def main():
    df = pd.read_csv(DATA / 'feedback_clean.csv', low_memory=False)
    df = df[df.qa_status.eq('accepted')].copy()
    df['rating_normalised'] = pd.to_numeric(df['rating_normalised'],errors='coerce')
    df['negative_rating'] = pd.to_numeric(df['negative_rating'],errors='coerce')
    df['rated'] = df.rating_normalised.notna()
    df['negative_count'] = ((df.negative_rating == 1) & df.rated).astype(int)
    df['rated_count'] = df.rated.astype(int)
    df = pd.concat([df, df['comment_redacted'].apply(classify)], axis=1)
    df['has_comment'] = df.comment_redacted.fillna('').str.strip().ne('')
    # Exploratory *complaint-theme proxy*: require rating-based dissatisfaction and negative textual cue.
    df['proxy_negative_text'] = df.has_comment & (df.negative_rating == 1) & df.baseline_negative_cue
    df.to_csv(DATA/'feedback_with_baseline.csv',index=False)

    def aggregate(keys):
        g=df.groupby(keys,dropna=False).agg(responses=('record_id','size'),rated=('rated_count','sum'),negative=('negative_count','sum'),comments=('has_comment','sum'),proxy_negative_text=('proxy_negative_text','sum')).reset_index()
        g['negative_rating_rate']=(g.negative/g.rated.where(g.rated>0)).round(4)
        return g
    by_dealer=aggregate(['dealer_code']); by_dept=aggregate(['department']); by_month=aggregate(['month']); by_dealer_month=aggregate(['dealer_code','month']); by_dealer_dept=aggregate(['dealer_code','department'])
    dealers = pd.read_csv(ROOT/'data/raw/dealerships.csv')
    for name,table in [('dealership',by_dealer),('department',by_dept),('monthly',by_month),('dealership_month',by_dealer_month),('dealership_department',by_dealer_dept)]:
        if 'dealer_code' in table.columns: table=table.merge(dealers[['dealer_code','dealership_name','state','status']],on='dealer_code',how='left')
        table.to_csv(OUT/f'{name}_rating_metrics.csv',index=False)

    assignments=[]
    for row in df.loc[df.proxy_negative_text,['record_id','dealer_code','month','department','baseline_themes']].itertuples(index=False):
        for theme in (row.baseline_themes or '').split('|'):
            if theme: assignments.append((row.record_id,row.dealer_code,row.month,row.department,theme))
    themes=pd.DataFrame(assignments, columns=['record_id','dealer_code','month','department','theme'])
    if not themes.empty:
        for name,keys in [('theme_totals',['theme']),('dealership_themes',['dealer_code','theme']),('department_themes',['department','theme']),('monthly_themes',['month','theme'])]:
            themes.groupby(keys).size().rename('proxy_mentions').reset_index().to_csv(OUT/f'{name}.csv',index=False)

    rev=pd.read_csv(ROOT/'data/raw/monthly_revenue.csv')
    # Scenario uses avg service revenue per job, assuming additional jobs (NOT causal forecast).
    rev['service_revenue_per_job']=rev.service_revenue_aud/rev.service_jobs.replace(0,float('nan'))
    exposure=by_dealer_month.merge(rev,on=['dealer_code','month'],how='left',validate='one_to_one')
    exposure['illustrative_extra_jobs_at_1pct']=exposure.service_jobs*0.01
    exposure['illustrative_incremental_service_revenue_at_1pct']=exposure.service_revenue_aud*0.01
    exposure['illustrative_contribution_at_25pct_margin']=exposure.illustrative_incremental_service_revenue_at_1pct*0.25
    exposure.to_csv(OUT/'service_opportunity_scenario.csv',index=False)
    print(f'Accepted feedback: {len(df):,}; rated: {df.rated_count.sum():,}; negative ratings: {df.negative_count.sum():,}; comments: {df.has_comment.sum():,}')
    print('Baseline method: keyword/regex proxy, NOT validated AI sentiment, and NOT proven drivers.')
    print('\nNegative rating rate by department:')
    print(by_dept[['department','rated','negative','negative_rating_rate']].to_string(index=False))
    if not themes.empty:
        print('\nExploratory negative-text theme mentions (multi-label):')
        print(themes.theme.value_counts().to_string())
    print(f'\nOutputs: {OUT}')

if __name__=='__main__': main()
