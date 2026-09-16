import pdfplumber,os
files=[r'C:\Users\27677\Desktop\2303.11366v4.pdf',r'C:\Users\27677\Desktop\2210.03629v3.pdf',r'C:\Users\27677\Desktop\2302.04761v1.pdf']
for i,f in enumerate(files,1):
 with pdfplumber.open(f) as d:
  t='\n'.join((p.extract_text() or '') for p in d.pages)
 open(f'paper{i}_en.txt','w',encoding='utf-8').write(t)
 print(i,len(t))
