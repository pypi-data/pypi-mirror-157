import requests, json

class srcb:
    def __init__(self):
        self.r = requests.Session()
        self.base_url = "https://sourceb.in/api/bins"

    def paste(self, file):
      try:
        cont = open(file).read()
      except:
        return 'Enter a valid file.'
      try:
         head = {
            "sec-ch-ua": "Not A;Brand;v=99, Chromium;v=101",
            "sec-ch-ua-platform": "Android",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "origin": "https://sourceb.in",
            "referer": "https://sourceb.in/",
            "cookie": "_ga=GA1.2.1118609638.1657025844; _gid=GA1.2.1946590648.1657025844; __stripe_mid=0d50e169-1ae7-48c2-9c53-3f87e7e64469f6a022; __stripe_sid=a1a966ed-bdd1-4405-8cd7-6ee6075f29ff62f5f0; _gat=1",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; Infinix X657C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/json;charset=UTF-8"
         }
         data = {"files": [{"content": cont, "languageId": 303}]}
         re = self.r.post(self.base_url, json = data, headers=head)
         dic = json.loads(re.text)
         err = dic['message'] or "empty"
         key = dic['key']
         return f'https://sourceb.in/{key}'
      except:
        if err != "empty":
            return "An error has occured. Here is the message from the server: " + err
        else:
            return "An unknown error has occurred. Please contact the library developer."