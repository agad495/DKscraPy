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
        
    def mlb_ws(self):
        
        soup_today = self.soup_setup(f"https://sportsbook.draftkings.com/leagues/baseball/2003?category=team-futures&subcategory=world-series-2021")
        
        teams = []
        for i in range(len(soup_today.findAll('span', {'class':'sportsbook-outcome-cell__label'}))):
            tm = soup_today.findAll('span', {'class':'sportsbook-outcome-cell__label'})[i]
            annoying = {'WAS Nationals':'WSN', 'CHI White Sox':'CHW', 'CHI Cubs':'CHC'}
            names = tm.text.split()
            if tm.text in annoying:
                city = annoying[tm.text]
            elif len(names[0]) == 2:
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
