"""Generate a deterministic, balanced-by-rating/department sample for Kalpana to label.
Run from repository: python reports/hand_label_sample.py
"""
import csv,random,collections,pathlib
base=pathlib.Path(__file__).resolve().parents[1]
with (base/'data/processed/feedback_clean.csv').open() as f: rows=list(csv.DictReader(f))
rows=[r for r in rows if r['qa_status']=='accepted' and r['comment_redacted'].strip() and r['rating_normalised']]
groups=collections.defaultdict(list)
for r in rows:
 band='low' if float(r['rating_normalised'])<=2 else 'mid' if float(r['rating_normalised'])<4 else 'high'
 groups[(r['department'],band)].append(r)
random.seed(42);selected=[]
for k,rs in sorted(groups.items()):selected.extend(random.sample(rs,min(20,len(rs))))
with (base/'reports/manual_labels_PRIVATE.csv').open('w',newline='') as f:
 cols=['record_id','dealer_code','department','rating_normalised','comment_redacted','human_sentiment','human_themes','review_notes']
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
 for r in selected:w.writerow({c:r.get(c,'') for c in cols})
print('Created private hand-label sheet:',len(selected),'rows. Redact/check before sharing.')
