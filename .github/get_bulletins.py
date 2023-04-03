import requests
from requests_oauthlib import OAuth1
import os
from os import listdir
from datetime import datetime as dt

auth = OAuth1(os.environ["API_KEY"], os.environ["API_SECRET"], os.environ["ACCESS_TOKEN"],os.environ["ACCESS_TOKEN_SECRET"])
url = 'https://api.twitter.com/1.1/statuses/show.json'
csvurl = os.environ["CSV_URL"]
skip = ['13/10/2022','12/10/2022', '20/10/2022','21/10/2022','28/10/2022','29/10/2022','31/10/2022','1/4/2023']

def save_image(url,name,folder):
    parent_folder = dt.strptime(folder,"%d-%m-%Y").strftime("%B %Y")
    if not os.path.isdir("bulletins/"+parent_folder):
        os.mkdir("bulletins/"+parent_folder)
    if not os.path.isdir(f"bulletins/{parent_folder}/{folder}"):
        os.mkdir(f"bulletins/{parent_folder}/{folder}")
    with open('bulletins/%s/%s/%s.jpg'%(parent_folder,folder,name), 'wb') as handle:
        response = requests.get(url, stream=True)
        if not response.ok:
            print(response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

def extract_id(url):
    return url.split("/")[-1].split("?")[0]

def make_readme(date,url):
    parent_folder = dt.strptime(date,"%d-%m-%Y").strftime("%B %Y")
    f = open("bulletins/%s/%s/README.md"%(parent_folder,date),"w")
    f.write('[Source: %s](%s)'%(url,url))
    f.close()

def download_missing_bulletins():
    done_dates = []
    for f in listdir("bulletins"):
        if os.path.isdir("bulletins/"+f):
            done_dates.extend(listdir("bulletins/"+f))
    done_dates = [f.replace("-","/") for f in done_dates]
    csvfile = requests.get(csvurl).text
    csvdata = [x.split(",") for x in csvfile.splitlines()]
    filtered_csv_data = []
    for day in csvdata[1:]:
        if not done_dates.__contains__(day[0]) and not skip.__contains__(day[0]):
            filtered_csv_data.append(day)
    for day in filtered_csv_data:
        print(day)
        date = day[0].replace("/","-")
        tweet_urls = day[-1].split("-")
        print(tweet_urls)
        for tweet_url in tweet_urls:
            filename = extract_id(tweet_url)
            params = {'id':filename, 'tweet_mode':'extended'}
            r = requests.get(url, auth=auth, params=params)
            data = r.json()
            media =data["extended_entities"]["media"]
            for img in media:
                save_image(img["media_url_https"], "pg--%s%s-"%(tweet_urls.index(tweet_url)+1,media.index(img)+1)+ img["id_str"], date)
        make_readme(date,tweet_url)

download_missing_bulletins()




