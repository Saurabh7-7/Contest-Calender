from bs4 import BeautifulSoup
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import pandas as pd

contests=[]
atcoder_page=requests.get("https://atcoder.jp/home").text
atcoder_soup=BeautifulSoup(atcoder_page,'lxml')

div_tag=atcoder_soup.find_all('div',id='contest-table-upcoming')
tr_tags=div_tag[0].find_all('tr')
tr_tags.pop(0)
atcoder_contests=[]

for tr in tr_tags:
    td=tr.find_all('td')
    time=td[0].find('time').text.strip()
    contest_name=td[1].find('a').text.strip()
    link ="https://atcoder.jp" + td[1].find('a')['href']
    
    
    dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S%z")
    dt = dt - timedelta(hours=3, minutes=30)

    date_time = dt.strftime("%Y-%m-%d %H:%M:%S")

    atcoder_contests.append([date_time,contest_name,link])


headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get("https://www.codechef.com/api/list/contests/all", headers=headers)
data = response.json()

codechef_contests = []

for contest in data["future_contests"]:

    contest_code = contest["contest_code"]
    contest_name = contest["contest_name"]
    date_time = datetime.fromisoformat(contest["contest_start_date_iso"]).strftime("%Y-%m-%d %H:%M:%S")

    duration = contest["contest_duration"]

    link = "https://www.codechef.com/" + contest_code

    codechef_contests.append([
      #  contest_code,
        date_time,
        contest_name,
      #  duration,
        link
    ])

# -----------------------------
# LeetCode
# -----------------------------
leetcode_contest=[]
query = """
query {
    allContests {
        title
        titleSlug
        startTime
        duration
    }
}
"""

response = requests.post(
    "https://leetcode.com/graphql",
    json={"query": query},
    headers={
        "Content-Type": "application/json",
        "Referer": "https://leetcode.com/contest/"
    }
)

data = response.json()

# current unix timestamp to get only upcoming contest by comparing the ((contest timestamp and current timestamp))
now = datetime.now().timestamp()


for contest in data["data"]["allContests"]:

    if contest["startTime"] <= now:
        continue

    contest_name = contest["title"]
    date_time = datetime.fromtimestamp(contest["startTime"]).strftime("%Y-%m-%d %H:%M:%S")
    link = ("https://leetcode.com/contest/"+contest["titleSlug"])

    leetcode_contest.append([
        date_time,
        contest_name,
        link
    ])

# codeforces

codeforces_page = requests.get("https://codeforces.com/api/contest.list")

codeforces_contest = codeforces_page.json()
codeforces_contest = codeforces_contest["result"]

temp = []

for contest in codeforces_contest:

    if contest["relativeTimeSeconds"] < 0:

        date_time = datetime.fromtimestamp(contest["startTimeSeconds"],ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
        contest_name = contest["name"]
        link = "https://codeforces.com/contest/" + str(contest["id"])

        temp.append([
            date_time,
            contest_name,
            link
        ])

codeforces_contest = temp

contests = (
    atcoder_contests
    + codechef_contests
    + leetcode_contest
    + codeforces_contest
)
df=pd.DataFrame(contests,columns=["date_time","contest_name","link"])
df