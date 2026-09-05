from pathlib import Path
import argparse, hashlib, json

def digest(path, algorithm):
    h=hashlib.new(algorithm)
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    rows={p.name:{'bytes':p.stat().st_size,'md5':digest(p,'md5'),'sha256':digest(p,'sha256')} for p in sorted(args.data_dir.glob('KDD*.txt'))}
    args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps({'source':'defcom17/NSL_KDD','local_dir':str(args.data_dir),'files':rows},ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
