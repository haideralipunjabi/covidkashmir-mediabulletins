import requests
from requests_oauthlib import OAuth1
import os
from os import listdir
from dotenv import load_dotenv
load_dotenv("/home/haideralipunjabi/Github/covidkashmir-mediabulletins/secret.env")

auth = OAuth1(os.environ["API_KEY"], os.environ["API_SECRET"], os.environ["ACCESS_TOKEN"],os.environ["ACCESS_TOKEN_SECRET"])
url = 'https://api.twitter.com/1.1/statuses/show.json'
csvurl = 'https://covidkashmir.org/api/bulletin'

def save_image(url,name,folder):
    with open('bulletins/%s/%s.jpg'%(folder,name), 'wb') as handle:
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
    f = open("bulletins/%s/README.md"%(date),"w")
    f.write('[Source: %s](%s)'%(url,url))
    f.close()

def download_missing_bulletins():
    done_dates = [f.replace("-","/") for f in listdir("bulletins")]
    csvfile = requests.get(csvurl).text
    csvdata = [x.split(",") for x in csvfile.splitlines()]
    filtered_csv_data = []
    for day in csvdata[1:]:
        if not done_dates.__contains__(day[0]):
            filtered_csv_data.append(day)
    for day in filtered_csv_data:
        print(day)
        date = day[0].replace("/","-")
        os.system("mkdir bulletins/"+date)
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




