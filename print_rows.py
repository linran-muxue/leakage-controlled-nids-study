import json
j=json.load(open('search_result.json',encoding='utf8'))
for x in j['rows']:
 print(x.get('file_no'),repr(x.get('title')),x.get('display_year'),x.get('volume'),x.get('issue'),x.get('page'),x.get('doi'),repr(x.get('author_name')),repr(x.get('key_word')))
