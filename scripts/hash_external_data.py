from pathlib import Path
import hashlib, json

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def main():
    d=Path(r'E:\论文\data\external\NSL-KDD'); out=Path(__file__).resolve().parents[1]/'results_nsl_kdd'; out.mkdir(parents=True,exist_ok=True)
    m={p.name:{'bytes':p.stat().st_size,'sha256':sha256(p)} for p in sorted(d.glob('*')) if p.is_file()}
    (out/'raw_file_hashes.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(m,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
