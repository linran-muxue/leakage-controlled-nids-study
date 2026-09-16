import requests,json
u='https://www.c-s-a.org.cn/csa/ajax/search'
data={'from_year':'','to_year':'','search_type':'search','source_type':'meta','field':'title','key':'入侵检测','additional_year':'','additional_author':'','additional_keyword':'','page':'1','page_size':'50','CsrfCheckCode':'50pos4'}
r=requests.post(u,data=data,verify=False,headers={'User-Agent':'Mozilla/5.0','Referer':'https://www.c-s-a.org.cn/csa/article/search'},timeout=30)
print(r.status_code,len(r.text)); print(r.text[:500]); open('search_result.json','w',encoding='utf8').write(r.text)
