from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_pipeline import map_attack_label

RAW = Path(r"E:\论文\data\raw\MachineLearningCVE")
OUT = Path(__file__).resolve().parents[1] / "results_paper_materials" / "tables"

def main():
    rows=[]
    for path in sorted(RAW.glob("*.csv")):
        counts={}
        for chunk in pd.read_csv(path,chunksize=100000,low_memory=False,encoding_errors="replace"):
            col=next(c for c in chunk.columns if str(c).strip().lower()=="label")
            mapped=chunk[col].map(map_attack_label).dropna()
            for label,n in mapped.value_counts().items(): counts[label]=counts.get(label,0)+int(n)
        row={"file":path.name}
        for label in ["Normal","DoS/DDoS","Brute Force","Web Attack","Bot"]: row[label]=counts.get(label,0)
        row["class_count_present"]=sum(v>0 for v in row.values() if isinstance(v,int))
        rows.append(row)
    table=pd.DataFrame(rows); table.to_csv(OUT/"table_filewise_class_coverage.csv",index=False,encoding="utf-8-sig")
    print(table.to_string(index=False))
    print("NOTE: strict file-wise split cannot place all five classes in both train and test because attack families are scenario-specific.")
if __name__ == "__main__": main()
