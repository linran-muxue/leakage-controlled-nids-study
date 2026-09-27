from pathlib import Path
import argparse, json
import pandas as pd

COLS = ["duration","protocol_type","service","flag","src_bytes","dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins","logged_in","num_compromised","root_shell","su_attempted","num_root","num_file_creations","num_shells","num_access_files","num_outbound_cmds","is_host_login","is_guest_login","count","srv_count","serror_rate","srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate","diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count","dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate","dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate","dst_host_rerror_rate","dst_host_srv_rerror_rate","label","difficulty"]

def category(label):
    x = str(label).strip().lower().rstrip('.')
    if x == 'normal': return 'Normal'
    if x in {'back','land','neptune','pod','smurf','teardrop','apache2','udpstorm','processtable','mailbomb'}: return 'DoS'
    if x in {'ipsweep','mscan','nmap','portsweep','saint','satan'}: return 'Probe'
    if x in {'ftp_write','guess_passwd','imap','multihop','phf','spy','warezclient','warezmaster','named','sendmail','snmpgetattack','snmpguess','worm','xlock','xsnoop'}: return 'R2L'
    if x in {'buffer_overflow','httptunnel','loadmodule','perl','ps','rootkit','sqlattack','xterm'}: return 'U2R'
    return 'Other'

def read_file(path):
    f = pd.read_csv(path, header=None, names=COLS)
    f['target'] = f['label'].map(category)
    return f.drop(columns=['label','difficulty'])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--raw-dir',type=Path,required=True); ap.add_argument('--output-dir',type=Path,required=True); a=ap.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    tr,te=read_file(a.raw_dir/'KDDTrain+.txt'),read_file(a.raw_dir/'KDDTest+.txt')
    cats=['protocol_type','service','flag']
    # Fit the categorical feature space on the training split only.  Building
    # dummies after concatenating train and test would expose test-only
    # category levels to preprocessing, which is avoidable even though labels
    # are not used.  Test columns are aligned to the train columns; unseen
    # test categories are ignored and recorded for auditability.
    tr_encoded=pd.get_dummies(tr,columns=cats,dtype=int)
    te_encoded=pd.get_dummies(te,columns=cats,dtype=int)
    feature_columns=[c for c in tr_encoded.columns if c!='target']
    unseen_test_categories={}
    for c in cats:
        train_levels=set(tr[c].astype(str).unique())
        test_levels=set(te[c].astype(str).unique())
        unseen_test_categories[c]=sorted(test_levels-train_levels)
    te_encoded=te_encoded.reindex(columns=tr_encoded.columns,fill_value=0)
    tr=tr_encoded.reset_index(drop=True); te=te_encoded.reset_index(drop=True)
    tr.to_csv(a.output_dir/'train.csv',index=False,encoding='utf-8-sig'); te.to_csv(a.output_dir/'test.csv',index=False,encoding='utf-8-sig')
    s={'train_rows':len(tr),'test_rows':len(te),'feature_count':len(feature_columns),'train_class_counts':tr.target.value_counts().to_dict(),'test_class_counts':te.target.value_counts().to_dict(),'categorical_fit_split':'train_only','categorical_columns':cats,'unseen_test_categories':unseen_test_categories,'feature_columns':feature_columns}
    (a.output_dir/'dataset_summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
