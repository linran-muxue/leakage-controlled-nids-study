import requests, bs4
from urllib.parse import urljoin
base='https://www.c-s-a.org.cn/'
ids=['10162','20031125','8661']
for i in ids:
 u=urljoin(base,'csa/article/abstract/'+i)
 r=requests.get(u,verify=False,headers={'User-Agent':'Mozilla/5.0'},timeout=20)
 print('ID',i,'status',r.status_code,'len',len(r.text))
 open('article_'+i+'.html','w',encoding='utf8').write(r.text)
 s=bs4.BeautifulSoup(r.text,'html.parser')
 print(s.title.get_text(' ',strip=True) if s.title else '')
 print(s.get_text(' ',strip=True)[:1000])
 print('links',[(a.get_text(' ',strip=True),a.get('href')) for a in s.find_all('a') if 'pdf' in (a.get('href') or '').lower()][:5])
