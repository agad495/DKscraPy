import requests
import re

from datetime import datetime
from bs4 import BeautifulSoup

class ScrapeDK():
    def soup_setup(self, url):
        
        response = requests.get(url)
        print(response)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return soup
        
    def nfl_sb(self):
        
        soup_today = self.soup_setup(f"https://sportsbook.draftkings.com/leagues/football/3?category=team-futures&subcategory=super-bowl-winner")
        
        teams = []
        for i in range(len(soup_today.findAll('span', {'class':'sportsbook-outcome-cell__label'}))):
            tm = soup_today.findAll('span', {'class':'sportsbook-outcome-cell__label'})[i]
            annoying = ['LA Rams', 'LA Chargers', 'NY Giants', 'NY Jets']
            names = tm.text.split()
            if tm.text in annoying:
                city = f'{names[0]}{names[1][0]}'
            else:
                city = names[0]
            teams.append(city)
        
        odds = []
        for i in range(len(soup_today.findAll('span', {'class':'sportsbook-odds american default-color'}))):
            odd = soup_today.findAll('span', {'class':'sportsbook-odds american default-color'})[i]
            dkRe = re.search('>.+<', str(odd))
            odd = int(dkRe.group().replace('>', '').replace('<', '').replace('+', ''))
            
            if odd > 0:
                pct = round(1 / ((odd/100) + 1), 4)
            else:
                pct = round(1 - (1 / ((-1*odd/100) + 1)), 4)
            
            odds.append(pct)
            
        lamarca = {}
        for i in range(len(teams)):
            lamarca[teams[i]] = {'odds':odds[i], 'date_time':datetime.now()}
            
        return lamarca
        

