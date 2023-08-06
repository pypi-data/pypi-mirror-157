import httpx
import jsbeautifier
from bs4 import BeautifulSoup as bs

import re
import time
import subprocess
import sys

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
}

client = httpx.Client(headers=headers, timeout=None)

proxy_url = "https://proxy-1.movie-web.workers.dev/?destination="

color = [  
    "\u001b[31m",
    "\u001b[32m",
    "\u001b[33m",
    "\u001b[34m",
    "\u001b[35m",
    "\u001b[36m",
    "\u001b[37m"
]

def mapping(query: str) -> list:

    URL = f"https://imdb.com/find?q={query}&ref_=nv_sr_sm"
    res = client.get(URL, follow_redirects=True)

    scode = res.status_code

    if scode == 200:
        pass
    elif scode == 404:
        print("QueryError: show not found")
    else:
        print(f"returned => {scode}")

    soup = bs(res.text, "html.parser")
    td = soup.find_all('td', attrs={'class': "result_text"})

    shows = list()
    for instance in list(td):
        show = re.search(
            r'<td class="result_text"> <a href="/title/([a-z0-9]{8,})/\?ref_=fn_al_tt_[0-9]{1,}"(.*)</td>',
            str(instance)
        )

        if show is not None:

            title_ = re.sub(
                 r'(<(|/)([a-z]+)(|/)>|<|>)',
                '',
                str(show.group(2))
            )

            validate = re.search(
                r'\([a-zA-Z\s]*\)',
                title_
            )

            if validate is None:

                title_ = re.sub(r' -.*', '', title_)
                instance = {
                    'id': str(show.group(1)),
                    'name': title_
                }
                shows.append(instance)

        return shows

def fetch() -> dict:

    try:
        if len(sys.argv) == 1:
            query = input("Search: ")
            if query == "":
                print("ValueError: no query parameters provided")
                exit(0)
        else:
            query = " ".join(sys.argv[1:])

        shows = mapping(query=query.replace(" ", "+"))

        
        if len(shows) > 1:
        
            for idx, info in enumerate(shows):
                color_idx = random.randint(0, len(color)-1) if idx >= len(color) else idx
                print(f'[{idx+1} {color[color_idx]} {info["name"]}\u001b[0m')
            
            ask = int(input(": "))-1
            if(ask >= len(shows)):
                print("IndexError: index out of range.")
                exit(1)
        else:
            return shows[0]

    except ValueError:
        return shows[0]
    
    except KeyboardInterrupt:
        exit(0)

    return shows[ask]


show = fetch()

url = f"{proxy_url}https://gomo.to/movie/{show['id']}"

try:
    r=client.get(url)
except:
    time.sleep(4)
    r=client.get(url)
    
    
#regex to get the tc and token value
tc=re.findall(r"var tc = '(.*?)'",r.text)[0]
token = re.findall(r'"_token": "(.*?)"',r.text)[0]


#find index 
a,b = re.findall(r'(\d+),(\d+)',r.text)[0]
p=re.findall(r'\+ "(.*?)"\+"(.*?)"',r.text)[0]
extra_data = "".join(p)



#post data
r=httpx.post(f"{proxy_url}https://gomo.to/decoding_v3.php",
             headers={'x-token': tc[int(a):int(b)][::-1]+extra_data},
             data={
                 'tokenCode': tc,
                 "_token": token,
             }
             )
urls = r.json()

#print("====All Providers=====\n")
#print(urls)


r=client.get(f"{urls[0]}",follow_redirects=True) #used the first one
soup = bs(r.text,"html.parser")

packed_data = soup.select("script")[-2].text
stream_url = re.findall(r'file: "(.*?)"',jsbeautifier.beautify(packed_data))[0]

#stream
print(f"[*]Streaming url: {stream_url}")

args = [
    "mpv",
    f"{stream_url}",
    f"--force-media-title=Playing {show['name']}"
]

mpv_process = subprocess.Popen(args)

mpv_process.wait()
