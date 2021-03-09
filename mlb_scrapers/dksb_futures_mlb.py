import requests

from datetime import datetime
from bs4 import BeautifulSoup

class ScrapeDKBases():
    """
    A class of functions to scrape MLB lines and odds on DraftKings Sportsbook.
    """
    def soup_setup(self, url):
        """
        Create a BeautifulSoup object from the given url.
        Should return <Response [200]>, unless there is an error.
        """
        response = requests.get(url)
        print(response)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return soup
        
    def team_cleanup(self, tm_name):
        """
        Takes an MLB team name from DraftKings and converts it to FanGraphs' format.
        """
        annoying = {'WAS Nationals':'WSN', 'CHI White Sox':'CHW', 'CHI Cubs':'CHC'}
        names = tm_name.split()
        if tm_name in annoying:
            city = annoying[tm_name]
        elif len(names[0]) == 2:
            city = f'{names[0]}{names[1][0]}'
        else:
            city = names[0]
        
        return city

    def mlb_ws(self):
        """
        Scrapes current World Series odds.
        
        Returns
        -------
        lamarca : nested dictionaries in the form of
        {<team abbreviation>: {'odds':<odds>, 'date_time':<datetime object with the current date and time>}, ...}

        """
        soup_today = self.soup_setup(f"https://sportsbook.draftkings.com/leagues/baseball/2003?category=team-futures&subcategory=world-series-2021")
        
        teams = []
        team_soup = soup_today.findAll('span', {'class':'sportsbook-outcome-cell__label'})
        for i in team_soup:
            #Teams are listed on DK as <city abbreviation> <team nickname> so 
            #we want to format team abbreviations to match FanGraphs' convention:
            city = self.team_cleanup(i.text)
            #Once the abbrevations are cleaned up, add them to a list:
            teams.append(city)
        
        odds = []
        odds_soup = soup_today.findAll('span', {'class':'sportsbook-odds american default-color'})
        for i in odds_soup:
            odd = i.text
            odd = int(odd.replace('+', ''))
            #Once odds have been cleaned up, convert them to percentages (easier to understand and/or plot):
            if odd > 0:
                pct = round(1 / ((odd/100) + 1), 4)
            else:
                pct = round(1 - (1 / ((-1*odd/100) + 1)), 4)
            #Add percentages to a list:
            odds.append(pct)
        
        #Add team abbreviations, odds and the current date and time to nested dictionaries:
        lamarca = {}
        #Of course, World Series winners probably aren't celebrating with $14 bottles of lamarca but it's some damn good prosecco.
        for i in range(len(teams)):
            lamarca[teams[i]] = {'odds':odds[i], 'date_time':datetime.now()}
            
        return lamarca

    def mlb_games(self):
        """
        Scrapes current MLB game odds.

        Returns
        -------
        tequila : nested dictionaries in the form of
        {<team abbreviation>: {'moneyline':<odds>, 'opponent':<opponent team abbreviation>, 'home':<1 if home, 0 if away>}, ...}.

        """
        soup_today = self.soup_setup(f"https://sportsbook.draftkings.com/leagues/baseball/2003?category=game-lines-&subcategory=game")
        
        teams = []
        opponents = []
        home = []
        team_soup = soup_today.findAll('span', {'class':'event-cell__name'})
        #iterating over the range of the length of team_soup will allow us to
        #discern opponents and home/away
        for i in range(len(team_soup)):
            city = self.team_cleanup(team_soup[i].text)
            teams.append(city)
            
            #Teams with an even (or 0) numbered index are away, odd are home:
            if i % 2 == 0:
                oppo_city = self.team_cleanup(team_soup[i+1].text)
                home.append(0)
            else:
                oppo_city = self.team_cleanup(team_soup[i-1].text)
                home.append(1)
            opponents.append(oppo_city)
        
        odds = []
        #Get moneyline odds, convert to percentages and add to a list
        odds_soup = soup_today.findAll('span', {'class':'sportsbook-odds american default-color'})
        for i in odds_soup:
            odd = int(i.text.replace('+', ''))
            
            if odd > 0:
                pct = round(1 / ((odd/100) + 1), 4)
            else:
                pct = round(1 - (1 / ((-1*odd/100) + 1)), 4)

            odds.append(pct)            
            
        tequila = {}
        #Combine everything into a beautifully named dictionary:
        for i in range(len(teams)):
            tequila[teams[i]] = {'moneyline':odds[i], 'opponent':opponents[i],
                                 'home':home[i]}
        
        return tequila
