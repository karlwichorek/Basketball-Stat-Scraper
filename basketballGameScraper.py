#!/usr/bin/env python3

# basketballGameScraper.py
# Simon Swanson

from   bs4      import BeautifulSoup
import calendar
import csv
import re
from   requests import get
import time


COUNT    = 0
TEAMS    = []
PREVIOUS = []
TODAY    = []


def iint(string):
    return int(string) if string and string.isdigit() else 0


def ffloat(string):
    return float(string) if string and re.match(r"^-?\d*\.?\d*$", string) is not None else 0


def validDate(soup):
    return soup.find(text="No NBA games played on this date.") is None


def monthRange(year, month):
    return list(range(1, calendar.monthrange(year, month)[1] + 1))


def feetToInches(feet):
    num = feet.split("-")
    return 12 * iint(num[0]) + iint(num[1])


def findTeams(soup):
    teams  = []
    final  = soup.select("span.bold_text.large_text")
    teams.append(final[0].a.text.strip())
    teams.append(final[1].a.text.strip())
    score1 = iint(final[0].br.text.strip())
    score2 = iint(final[1].br.text.strip())
    if score1 >= score2:
        teams.append(teams[0])
    else:
        teams.append(teams[1])
    return teams


def boxProcess(soup, date):
    global TODAY
    team           = {}
    basicTables    = soup.findAll("table", id=re.compile(r"\w\w\w_basic"))
    advancedTables = soup.findAll("table", id=re.compile(r"\w\w\w_advanced"))
    teams          = findTeams(soup)
    TODAY.append(teams[0])
    TODAY.append(teams[1])

    for i in [0,1]:
        players = basicTables[i].tbody.findAll("tr")
        starter = 5
        for player in players:
            if sorted(player.get("class")) == ["no_ranker", "thead"] or sorted(player.get("class")) == ["bold_text", "stat_total"]:
                starter = 0
                continue
            rows = player.findAll("td")
            if len(rows) == 2:
                continue
            info = []
            name = rows[0].text.strip()
            info.append(date)
            info.append(name)
            info.append(teams[i])
            info.append(1 if starter > 5 else 0)
            info.append(1 if teams[i] in PREVIOUS else 0)
            info.append(rows[1].text.strip())
            info.append(iint(rows[3].text.strip()))
            info.append(iint(rows[6].text.strip()))
            info.append(iint(rows[18].text.strip()))
            team[name] = info
            starter -= 1

        players = advancedTables[i].tbody.findAll("tr")
        for player in players:
            if sorted(player.get("class")) == ["no_ranker", "thead"]:
                continue
            rows = player.findAll("td")
            if len(rows) == 2:
                continue
            name = rows[0].text.strip()
            if name in team.keys():
                team[name].append(ffloat(rows[13].text.strip()))
                team[name].append(ffloat(rows[14].text.strip()))
                team[name].append(ffloat(rows[15].text.strip()))
                team[name].append(teams[1])
                team[name].append(teams[0])
                team[name].append(teams[2])
            else:
                print("Something bad looking up a box score with {}".format(name))

        rows = advancedTables[i].tfoot.findAll("td")
        oRtg = ffloat(rows[14].text.strip())
        dRtg = ffloat(rows[15].text.strip())
        for name in team.keys():
            while (len(team[name]) < 15):
                team[name].append("NA")
            if team[name][2] == teams[i]:
                team[name].append(oRtg)
                team[name].append(dRtg)

    players = []
    [players.append(team[player]) for player in team.keys()]

    return players


def teamProcess(soup, link):
    team  = {}
    match = re.search(r"/teams/(\w\w\w)/\d+\.html", link)
    if match:
        teamName = match.group(1)
    else:
        teamName = "NAN"

    roster = soup.find("table", id="roster").tbody.findAll("tr")
    for player in roster:
        info = []
        rows = player.findAll("td")
        name = rows[1].text.strip()
        info.append(name)
        info.append(teamName)
        info.append(rows[2].text.strip())
        info.append(feetToInches(rows[3].text.strip()))
        info.append(iint(rows[4].text.strip()))
        info.append(iint(rows[6].text.strip()))
        team[name + teamName] = info

    totals = soup.find("table", id="totals").tbody.findAll("tr") 
    for player in totals:
        rows = player.findAll("td")
        name = rows[1].text.strip()
        if name == "Team Totals":
            continue
        else:
            name = name + teamName
        if name in team.keys():
            team[name].append(iint(rows[2].text.strip()))
            team[name].append(iint(rows[3].text.strip()))
            team[name].append(iint(rows[4].text.strip()))
            team[name].append(iint(rows[5].text.strip()))
            team[name].append(iint(rows[7].text.strip()))
            team[name].append(iint(rows[10].text.strip()))
            team[name].append(iint(rows[26].text.strip()))
        else:
            print("Something bad happened with {}".format(name))

    advanced = soup.find("table", id="advanced").tbody.findAll("tr")
    for player in advanced:
        rows = player.findAll("td")
        name = rows[1].text.strip() + teamName
        if name in team.keys():
            team[name].append(ffloat(rows[5].text.strip()))
            team[name].append(ffloat(rows[16].text.strip()))
            team[name].append(ffloat(rows[18].text.strip()))
            team[name].append(ffloat(rows[19].text.strip()))
        else:
            print("Something bad happened with {}".format(name))

    if soup.find("table", id="playoffs_totals"):

        ptotals = soup.find("table", id="playoffs_totals").tbody.findAll("tr")
        for player in ptotals:
            rows = player.findAll("td")
            name = rows[1].text.strip() + teamName
            if name in team.keys():
                team[name].append(iint(rows[3].text.strip()))
                team[name].append(iint(rows[4].text.strip()))
                team[name].append(rows[5].text.strip())
                team[name].append(iint(rows[7].text.strip()))
                team[name].append(iint(rows[10].text.strip()))
                team[name].append(iint(rows[26].text.strip()))
            else:
                print("Something bad happened with {}".format(name))

        padvanced = soup.find("table", id="playoffs_advanced").tbody.findAll("tr")
        for player in padvanced:
            rows = player.findAll("td")
            name = rows[1].text.strip() + teamName
            if name in team.keys():
                team[name].append(ffloat(rows[5].text.strip()))
                team[name].append(ffloat(rows[16].text.strip()))
                team[name].append(ffloat(rows[18].text.strip()))
                team[name].append(ffloat(rows[19].text.strip()))
            else:
                print("Something bad happened with {}".format(name))

    match   = re.compile(r"Off Rtg:\s([\d\.]+).+Def Rtg:\s([\d\.]+)")
    ratings = match.search(soup.find("span", text="Off Rtg").parent.parent.text)
    for name in team.keys():
        while (len(team[name]) < 27):
            team[name].append("NA")
        team[name].append(ffloat(ratings.group(1)))
        team[name].append(ffloat(ratings.group(2)))

    players = []
    [players.append(team[player]) for player in team.keys()]

    return players


def dayParse(day, month, year):
    global COUNT
    global TEAMS
    global PREVIOUS
    global TODAY
    boxStats  = []
    teamStats = []
    soup = BeautifulSoup(get("http://www.basketball-reference.com/boxscores/index.cgi?month={}&day={}&year={}".format(month, day, year)).text)
    if validDate(soup):
        
        boxTags   = soup.findAll("a", href=re.compile(r"/boxscores/.+\.html"), text="Final")
        boxLinks  = [tag.get("href") for tag in boxTags]
        sMonth    = "0" + str(month) if len(str(month)) < 2 else str(month)
        sDay      = "0" + str(day) if len(str(day)) < 2 else str(day)
        dateVal   = int(str(year) + sMonth + sDay)
        for boxLink in boxLinks:
            boxSoup = BeautifulSoup(get("http://www.basketball-reference.com/{}".format(boxLink)).text)
            boxStats.append(boxProcess(boxSoup, dateVal))
            COUNT+=1

        teamTags  = soup.findAll("a", href=re.compile(r"/teams/\w+/\d+\.html"))
        teamLinks = [tag.get("href") for tag in teamTags]
        for teamLink in teamLinks:
            if teamLink not in TEAMS:
                TEAMS.append(teamLink)
                teamSoup = BeautifulSoup(get("http://basketball-reference.com/{}".format(teamLink)).text)
                teamStats.append(teamProcess(teamSoup, teamLink))
    PREVIOUS = []
    for team in TODAY:
        PREVIOUS.append(team)
    TODAY = []

    return (boxStats, teamStats)
    

def seasonParse(season):
    global COUNT
    global TEAMS
    TEAMS        = []
    yearStatList = ["Name", "Team", "Position", "Height", "Weight", "Exp", "Age", "G", "GS", "MP", "FGA", "3PA", "PF", "PER", "USG%", "OWS", "DWS", "PG", "PGS", "PMP", "PFGA", "P3PA", "PPF", "PPER", "PUSG%", "POWS", "PDWS", "TORtg", "TDRtg"]
    boxStatList  = ["Date", "Name", "Team", "Started", "B2B", "MP", "FGA", "ThreePA", "PF", "USG%", "ORtg", "DRtg", "Home", "Away", "Winner", "TORtg", "TDRtg"]
    yearString   = "{}-{}".format(season, season + 1)
    print("Starting season {}".format(yearString))
    yearFile     = "YearStats{}.csv".format(yearString)
    gameFile     = "GameStats{}.csv".format(yearString)
    with open(yearFile, "w") as fpYear, open(gameFile, "w") as fpDay:
        yearStats = csv.writer(fpYear, quoting=csv.QUOTE_NONNUMERIC)
        dayStats  = csv.writer(fpDay, quoting=csv.QUOTE_NONNUMERIC)
        yearStats.writerow(yearStatList)
        dayStats.writerow(boxStatList)
        for month in list(range(10,13)) + list(range(1,6)):
            year = season + 1 if month < 8 else season
            for day in monthRange(year, month):
                stats = dayParse(day, month, year)
                for game in stats[0]:
                    dayStats.writerows(game)
                for team in stats[1]:
                    yearStats.writerows(team)
                if COUNT > 199:
                    print("200 more games entered")
                    COUNT -= 200
    print("{} more games added\nSeason {} done".format(COUNT,yearString))
    COUNT = 0
    return None


def main():
    for season in list(range(1994, 2014)):
        time.sleep(5)
        seasonParse(season)
    return None

if __name__ == '__main__':
    main()
