#!/usr/bin/env python3

# .basketballInjuryScraper.py
# Simon Swanson

from   bs4      import BeautifulSoup
import csv
from   requests import get

prefix = "http://www.prosportstransactions.com/basketball/Search/"

def getLinks(base):
    soup  = BeautifulSoup(get("{}{}".format(prefix, base)).text)
    tags  = soup.find("table", class_=None).findAll("td", width=None)[1].select("a[href]")
    links = [tag.get("href") for tag in tags]
    links.insert(0, base)
    return links

def getData(link):
    data = []
    soup = BeautifulSoup(get("http://www.prosportstransactions.com/basketball/Search/{}".format(link)).text)
    rows = soup.find("table", class_="datatable center").findAll("tr", align="left")
    [data.append(rowParse(row)) for row in rows]
    return data

def rowParse(line):
    row   = []
    parts = line.findAll("td")
    date  = parts[0].text.strip().replace("-", "")
    row.append(int(date))
    row.append(parts[1].text.strip())
    row.append(parts[2].text.strip()) if parts[2].text.strip() else row.append(parts[3].text.strip())
    row.append(parts[4].text.strip())
    return row

def main():
    links = getLinks("SearchResults.php?Player&Team&BeginDate&EndDate&InjuriesChkBx=yes&Submit=Search&start=0")
    with open("injuries.csv", "w", newline="") as fp:
        injury = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
        injury.writerow(["Date", "Team", "Player", "Notes"])
        for link in links:
            data = getData(link)
            injury.writerows(data)
    return "Successfully written to injuries.csv"

if __name__ == "__main__":
    main()
