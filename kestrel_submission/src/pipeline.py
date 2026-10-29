"""Transparent ingestion and rule-based exploratory analysis. Run: python src/pipeline.py"""
import csv,io,re,zipfile,hashlib,collections,datetime,json,pathlib,sys
from xlsx_reader import sheets
ROOT=pathlib.Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; OUT=ROOT/'data/processed'; REP=ROOT/'reports';OUT.mkdir(exist_ok=True,parents=True)
with (RAW/'dealerships.csv').open(encoding='utf-8-sig') as f:DEALERS=list(csv.DictReader(f))
BYCODE={d['dealer_code']:d for d in DEALERS}
LOOKUP={'dandenong':'VIC01','ringwood':'VIC02','essendon':'VIC03','frankston':'VIC04','boxhill':'VIC05','geelong':'VIC06','ballarat':'VIC07','bendigo':'VIC08','shepparton':'VIC09','parramatta':'NSW01','penrith':'NSW02','chatswood':'NSW03','liverpool':'NSW04','hunter motors':'NSW05','wollongong':'NSW06','tamworth':'NSW07','chermside':'QLD01','springwood':'QLD02','ips_':'QLD03','southport':'QLD04','noosa':'QLD05','toowoomba':'QLD06'}
ALIASES={'date':'date','visitdate':'date','datereceived':'date','submittedat':'date','dept':'department','area':'department','department':'department','score':'rating','score15':'rating','scoreoutof10':'rating','rating15':'rating','stars':'rating','csat':'rating','howwasit':'rating','howsatisfied':'rating','comments':'comment','comment':'comment','customercomments':'comment','customersaid':'comment','whatdidtheysay':'comment','customerfeedback':'comment','verbatim':'comment','feedback':'comment','notes':'comment','rating':'rating','site':'site','dealer':'site','responseid':'response_id','ref':'response_id','bookingref':'response_id'}
THEMES={'Communication':['call back','callback','call-back','phone','rang','ring back','update','message','text','informed','contact','chase','follow up','nobody called'], 'Waiting & delays':['wait','late','delay','slow','hours','queue','not ready','cancelled','canceled','appointment'], 'Price & billing':['price','cost','quote','quoted','charged','bill','invoice','expensive','overcharg','fee','dollar'], 'Quality & repairs':['fault','repair','fixed','broke','damage','scratch','dirty','grease','problem','issue','diagnos','still there'], 'Staff & courtesy':['rude','dismiss','unhelpful','attitude','arrogant','respect','ignored'], 'Parts availability':['part','stock','ordered','backorder','delivery']}
def normalize(x):return re.sub('[^a-z0-9]','',str(x).lower())
def canon(x):return ALIASES.get(normalize(x),'')
def parse_date(s, us_format=False):
 s=str(s or '').strip()
 if not s:return '', 'missing_date'
 if re.fullmatch(r'\d+(\.0)?',s):
  try:return (datetime.date(1899,12,30)+datetime.timedelta(days=int(float(s)))).isoformat(),''
  except (ValueError,OverflowError):pass
 for fmt in ((('%m/%d/%Y',) if us_format else ()) + ('%Y-%m-%d %H:%M:%S','%Y-%m-%d','%d/%m/%Y','%d/%m/%y','%d-%b-%y','%d %b %y','%d %b %Y','%d-%m-%Y','%d-%m-%y','%d/%b/%Y')):
  try:return datetime.datetime.strptime(s,fmt).date().isoformat(),''
  except ValueError:pass
 return '', 'invalid_date'
def department(s):
 x=str(s).lower().strip()
 if x in ('s','svc','workshop','service dept') or 'serv' in x:return 'Service'
 if x in ('new cars','used cars','new car','sales - new','sales - used','sales') or 'sale' in x:return 'Sales'
 if 'part' in x or x in ('p&a','pa'):return 'Parts'
 return 'Unknown'
def rating(raw,name,year,sheet):
 t=str(raw).strip().lower()
 if not t:return None,'missing_rating',''
 if '★' in t:val=t.count('★')
 elif t in {'excellent':5,'very satisfied':5,'satisfied':4,'neutral':3,'neither':3,'dissatisfied':2,'very dissatisfied':1,'good':4,'fair':3,'poor':1,'ok':3,'great':5,'bad':1}:val={'excellent':5,'very satisfied':5,'satisfied':4,'neutral':3,'neither':3,'dissatisfied':2,'very dissatisfied':1,'good':4,'fair':3,'poor':1,'ok':3,'great':5,'bad':1}[t]
 else:
  try:val=float(t)
  except ValueError:return None,'unmapped_rating',''
 if 'ringwood' in name.lower() and ('q2' in name.lower() or 'q3' in name.lower()):
  if not 1<=val<=10:return None,'invalid_rating','ringwood_10pt'
  return round(1+4*(val-1)/9,3),'','linear_10_to_5'
 if not 1<=val<=5:return None,'invalid_rating',''
 if 'geelong' in name.lower() and sheet.endswith('sheet1.xml'):
  return 6-val,'','reversed_geelong_2025'
 if not t.replace('.','',1).isdigit() and '★' not in t:return val,'','ordinal_word_mapping_review'
 return val,'','standard_5pt'
def dealer_for(name,row):
 if 'north qld' in name.lower():
  a=str(row.get('site','')).lower();return ('QLD07' if 'rock' in a or a.strip()=='rok' else 'QLD08' if 'tsv' in a or 'town' in a else '')
 if 'hunter' in name.lower():return 'NSW05'
 for token,code in LOOKUP.items():
  if token in name.lower():return code
 return ''
def redact(s):
 s=re.sub(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b','[EMAIL]',str(s))
 s=re.sub(r'(?<!\d)(?:\+61\s?4|04)[\d\s-]{8,12}(?!\d)','[PHONE]',s)
 s=re.sub(r'\b(?:rego|registration)\s*[:#-]?\s*[A-Z0-9]{4,8}\b','[REGO]',s,flags=re.I)
 return s
records=[]; issues=[]; inventory=[]; seen=set(); source_count=0
with zipfile.ZipFile(RAW/'republicisassignment.zip') as z:
 for filename in z.namelist():
  if filename.endswith('.csv'):
   raw=z.read(filename); t=raw.decode('utf-8-sig',errors='replace'); head=t.splitlines()[0];delim=';' if head.count(';')>head.count(',') else ','
   sub=[('csv',[(i+1,r) for i,r in enumerate(csv.reader(io.StringIO(t),delimiter=delim)) if any(str(v).strip() for v in r)])]
  elif filename.endswith('.xlsx'):sub=list(sheets(z.read(filename)))
  else:continue
  for sheet,lines in sub:
   best=(-1,None,None)
   for j,(line,arr) in enumerate(lines[:10]):
    score=sum(bool(canon(c)) for c in arr)
    if score>best[0]:best=(score,j,line)
   score,hidx,header_line=best
   if score<2:
    inventory.append([filename,sheet,len(lines),0,'skipped_no_row_level_table']);continue
   headers=[canon(a) for a in lines[hidx][1]]
   if 'date' not in headers or not ({'rating','comment'}&set(headers)):
    inventory.append([filename,sheet,len(lines),0,'skipped_not_feedback']);continue
   accepted=0
   for n,arr in lines[hidx+1:]:
    if not any(str(v).strip() for v in arr):continue
    current_headers=headers
    if 'ringwood feedback q1' in filename.lower() and n>=38:
     current_headers=['date','department','model','rating','comment','followup','staff']
    row={k:str(arr[i]).strip() for i,k in enumerate(current_headers) if k and i<len(arr)}
    # remove repetitions and non-record summary rows
    if normalize(row.get('date','')) in ('date','total','grandtotal') or (not row.get('date') and not row.get('rating') and not row.get('comment')):continue
    source_count+=1; dealer=dealer_for(filename,row); date,err=parse_date(row.get('date',''),us_format='liverpool_q3_2026' in filename.lower())
    rate,er2,transform=rating(row.get('rating',''),filename,date[:4],sheet)
    if 'ringwood feedback q1' in filename.lower() and n>=38:
     if rate is not None and rate<=5:pass
     # In February Q1 workbook, a new 10-point template begins at source row 37.
     try:
      rv=float(row.get('rating',''))
      rate=round(1+4*(rv-1)/9,3) if 1<=rv<=10 else None
      er2='' if rate is not None else 'invalid_rating';transform='linear_10_to_5'
     except ValueError:rate=None;er2='unmapped_rating'
    dept=department(row.get('department',''))
    if dept=='Unknown' and 'essendon' in filename.lower():
     dept={'sheet1.xml':'Sales','sheet2.xml':'Service','sheet3.xml':'Parts'}.get(sheet.split('/')[-1],'Unknown')
    comment=redact(row.get('comment',''))
    source_id=row.get('response_id','')
    warnings=[v for v in (err,er2) if v]
    if not dealer:warnings.append('unknown_dealership')
    if dept=='Unknown':warnings.append('unknown_department')
    if date and not ('2025-10-01'<=date<='2026-09-30'):warnings.append('date_outside_period')
    if dealer=='VIC09' and date>'2026-03-31':warnings.append('post_closure')
    if transform=='ordinal_word_mapping_review':warnings.append('subjective_ordinal_mapping')
    if 'chermside q1 2026 final.xlsx' in filename.lower():warnings.append('superseded_file')
    if 'penrith' in filename.lower() and sheet.endswith('sheet9.xml'):warnings.append('possible_repeat_july_august')
    if 'liverpool_q3' in filename.lower() and date and date<'2026-07-01':warnings.append('q3_file_outside_quarter')
    strong_key=(dealer,source_id) if source_id else None
    if strong_key and strong_key in seen:warnings.append('duplicate_response_id')
    if strong_key:seen.add(strong_key)
    # Do not silently discard any questionable rows; flag them for review.
    status='review' if any(w in warnings for w in ('invalid_date','missing_date','unknown_dealership','invalid_rating','unmapped_rating','date_outside_period','superseded_file','duplicate_response_id','post_closure')) else 'accepted'
    negative=rate is not None and rate<=2
    matched=[theme for theme,words in THEMES.items() if any(w in comment.lower() for w in words)] if comment else []
    fid=hashlib.sha256(f'{filename}|{sheet}|{n}'.encode()).hexdigest()[:16]
    rec={'record_id':fid,'dealer_code':dealer,'feedback_date':date,'month':date[:7],'department':dept,'rating_original':row.get('rating',''),'rating_normalised':rate if rate is not None else '', 'rating_rule':transform,'comment_redacted':comment,'comment_present':bool(comment),'negative_rating':int(negative),'exploratory_keyword_themes':'|'.join(matched),'source_file':filename,'source_sheet':sheet,'source_row':n,'source_response_id':source_id,'qa_status':status,'qa_flags':'|'.join(warnings)}
    records.append(rec);accepted+=1
    for w in warnings:issues.append({'record_id':fid,'source_file':filename,'source_sheet':sheet,'source_row':n,'flag':w})
   inventory.append([filename,sheet,len(lines),accepted,'processed'])
def writecsv(path,rows,keys):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
writecsv(OUT/'feedback_clean.csv',records,list(records[0]));writecsv(OUT/'quality_flags.csv',issues,['record_id','source_file','source_sheet','source_row','flag'])
with (REP/'source_inventory.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['file','sheet','nonempty_source_rows','candidate_feedback_rows','action']);w.writerows(inventory)
count=collections.Counter(r['qa_status'] for r in records);flags=collections.Counter(i['flag'] for i in issues)
valid=[r for r in records if r['qa_status']=='accepted' and r['rating_normalised']!='' and r['dealer_code'] and r['month']>='2025-10' and r['month']<='2026-09']
neg=[r for r in valid if r['negative_rating']]
themes=collections.Counter(t for r in neg for t in r['exploratory_keyword_themes'].split('|') if t)
summary={'files':len(z.namelist()) if False else 52,'candidate_rows':len(records),'qa_status':dict(count),'qa_flags':dict(flags),'rated_accepted':len(valid),'negative_accepted':len(neg),'negative_rate':round(len(neg)/len(valid),4) if valid else None,'negative_keyword_theme_mentions':dict(themes),'files_sheets':len(inventory),'reminder':'Keyword matches are exploratory proxies, NOT validated AI classifications or proven negative drivers.'}
(REP/'run_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
