import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs

ROOT = Path(__file__).resolve().parent
REPORT = ROOT/'3C短视频ROI评估与高潜视频筛选报告.md'
text = REPORT.read_text(encoding='utf-8')
issues=[]
checked={'local_deliverable_links':0,'images':0,'local_citations':0,'web_citations':0}

# Markdown links, excluding anchors.
for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
    if target.startswith('kimi-cite://'):
        citation_target = target[:-11] if target.endswith(' "citation"') else target
        parsed=urlparse(citation_target)
        qs=parse_qs(parsed.query)
        if parsed.netloc=='web':
            checked['web_citations']+=1
            if 'url' not in qs: issues.append('Web citation without url: '+target[:120])
        else:
            checked['local_citations']+=1
            paths=qs.get('path',[])
            if not paths:
                issues.append('Local citation without path: '+target[:120]); continue
            path=Path(paths[0])
            if not path.exists():
                issues.append('Local citation missing file: '+str(path)); continue
            lines=path.read_text(encoding='utf-8').splitlines()
            if 'line' in qs:
                n=int(qs['line'][0])
                if not 1<=n<=len(lines):
                    issues.append(f'Citation line out of range: {path} {n}')
                elif 'text' in qs and qs['text'][0] not in lines[n-1]:
                    issues.append(f'Citation text mismatch: {path} line {n}: {qs["text"][0]!r} != {lines[n-1]!r}')
            elif 'text' in qs and qs['text'][0] not in path.read_text(encoding='utf-8'):
                issues.append('Citation text not in file: '+target[:120])
    elif target.startswith(('http://','https://')):
        pass
    else:
        # Optional Markdown title is not used for generated deliverables.
        local=(ROOT/target).resolve()
        checked['local_deliverable_links']+=1
        if not local.exists(): issues.append('Missing local deliverable link: '+target)

for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text):
    checked['images']+=1
    path=(ROOT/image).resolve()
    if not path.exists() or path.stat().st_size==0: issues.append('Missing/empty image: '+image)

required_numbers=['504,000','59,232','8,170,997,693','238,705,549','12,711,772','846 条','3,027 条','794 条','46.72','6,929','57,383','0.761','94%','92%']
for value in required_numbers:
    if value not in text: issues.append('Required result missing from report: '+value)

result={'status':'passed' if not issues else 'failed','checks':checked,'issues':issues,'report_bytes':REPORT.stat().st_size}
(ROOT/'outputs'/'report_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if issues: raise SystemExit(1)
