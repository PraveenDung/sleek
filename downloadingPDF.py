import requests

def DownloadDocuments(access_token,file_details,main_path='./'):
    headers = {
        "Authorization": "Zoho-oauthtoken "+access_token,
        "orgId": "719129033"
        }
    for item in file_details:
        resp = requests.get(headers=headers,url=item['href'])

        with open(main_path+'/'+item['name'],'wb') as in_file:
            in_file.write(resp.content)