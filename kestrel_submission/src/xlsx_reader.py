import zipfile,csv,io,xml.etree.ElementTree as ET,re
ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def colidx(s):
 a=re.match('[A-Z]+',s); i=0
 for c in a.group():i=i*26+ord(c)-64
 return i-1
def sheets(raw):
 bz=zipfile.ZipFile(io.BytesIO(raw)); ss=[]
 if 'xl/sharedStrings.xml' in bz.namelist():
  root=ET.fromstring(bz.read('xl/sharedStrings.xml'));ss=[''.join(t.text or '' for t in si.findall('.//x:t',ns)) for si in root.findall('x:si',ns)]
 for sh in sorted(s for s in bz.namelist() if re.match(r'xl/worksheets/sheet\d+\.xml$',s)):
  root=ET.fromstring(bz.read(sh));rows=[]
  for row in root.findall('.//x:sheetData/x:row',ns):
   vals={}
   for c in row.findall('x:c',ns):
    v=c.find('x:v',ns);inline=c.find('x:is',ns)
    k=v.text if v is not None else (''.join(i.text or '' for i in inline.findall('.//x:t',ns)) if inline is not None else '')
    if c.attrib.get('t')=='s' and k:k=ss[int(k)]
    if k is not None and k!='':vals[colidx(c.attrib['r'])]=k
   if vals:
    rowarr=['']*(max(vals)+1)
    for k,v in vals.items():rowarr[k]=v
    rows.append((int(row.attrib['r']),rowarr))
  yield sh,rows
