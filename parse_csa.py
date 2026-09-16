import requests,bs4,json,urllib3
urllib3.disable_warnings()
ids=['10109','10162','10225','10190','9821','9976','9953','8657','9114','9194','8904']
for i in ids:
 u='https://www.c-s-a.org.cn/csa/article/abstract/'+i
 r=requests.get(u,verify=False,headers={'User-Agent':'Mozilla/5.0'},timeout=30)
 s=bs4.BeautifulSoup(r.text,'html.parser')
 def m(n,lang=None):
  attrs={'name':n}
  if lang: attrs['xml:lang']=lang
  x=s.find('meta',attrs=attrs)
  return x.get('content','') if x else ''
 print('\nID',i,'status',r.status_code)
 print('title',m('citation_title','cn'))
 print('authors',m('citation_authors','cn'))
 print('date',m('citation_date'),'vol',m('citation_volume'),'issue',m('citation_issue'),'pages',m('citation_firstpage')+'-'+m('citation_lastpage'),'doi',m('citation_doi'))
 print('keywords',m('DC.Keywords','cn'))
 a=s.find(id='CnAbstractValue'); print('abstract',a.get_text(' ',strip=True)[:1200] if a else '')
