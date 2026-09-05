from pathlib import Path
import argparse,time,pandas as pd
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import MinMaxScaler

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--processed-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); tr=pd.read_csv(a.processed_dir/'train.csv'); te=pd.read_csv(a.processed_dir/'test.csv'); names=[c for c in tr.columns if c!='target']; sc=MinMaxScaler(); Xtr=sc.fit_transform(tr[names]); Xte=sc.transform(te[names]); rows=[]
    for name,m in [('random_forest',RandomForestClassifier(n_estimators=300,random_state=42,n_jobs=-1,class_weight='balanced_subsample')),('extra_trees',ExtraTreesClassifier(n_estimators=300,random_state=42,n_jobs=-1,class_weight='balanced'))]:
        s=time.perf_counter(); m.fit(Xtr,tr.target); train_s=time.perf_counter()-s; s=time.perf_counter(); p=m.predict(Xte); pred_s=time.perf_counter()-s; r=classification_report(te.target,p,output_dict=True,zero_division=0); rows.append({'model':name,'accuracy':r['accuracy'],'macro_f1':r['macro avg']['f1-score'],'train_seconds':train_s,'predict_seconds':pred_s}); pd.DataFrame({'y_true':te.target,'y_pred':p}).to_csv(a.output_dir/f'predictions_{name}.csv',index=False,encoding='utf-8-sig'); pd.DataFrame(r).T.to_csv(a.output_dir/f'classification_report_{name}.csv',encoding='utf-8-sig')
    pd.DataFrame(rows).to_csv(a.output_dir/'metrics.csv',index=False,encoding='utf-8-sig'); print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__': main()
