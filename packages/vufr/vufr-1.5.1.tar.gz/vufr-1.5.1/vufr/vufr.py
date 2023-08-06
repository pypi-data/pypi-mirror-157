import requests, json

class VUFR:
    def __init__(self):
        self.r = requests.Session()
        self.base_url = "https://vu.fr/shorten"

    def shorten_url(self, url):
        data = {
            "url": url
        }
        head = {
            "sec-ch-ua": "Not A;Brand;v=99, Chromium;v=101",
            "sec-ch-ua-platform": "Android",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "origin": "https://vu.fr",
            "referer": "https://vu.fr",
            "cookie": "PHPSESSID=8883cce439e68f4fd3eb2e4517480810",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; Infinix X657C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryZpbAzm9jDM343NtB"
        }
        re = self.r.post(self.base_url, params=data, headers=head)
        hh = re.text
        dic = json.loads(hh)
        message = dic['message']
        url = dic['data']['shorturl']
        if message == "Link has been shortened":
            return url
        elif re.status_code == 429:
            return "429: You are ratelimited."
        else:
            return "An error has occured: " + message