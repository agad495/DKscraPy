import pandas as pd
import numpy as np
import requests
import re

from bs4 import BeautifulSoup

class ScrapeDK():
    def __init__(self, pbp):
        self.pbp = pbp
        
    def soup_setup(self, url):
        
        response = requests.get(url)
        print(response)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return soup
    
    def nfl_stadium_type(self, team_name, overrides=None):
        stadiums = self.pbp.groupby(['home_team', 'roof'], dropna=False).agg({'season':'max'}) \
            .query("season == 2020") \
                .reset_index()
        stadiums['roof'].fillna('closed', inplace=True)
        stadiums.query("(home_team != 'SF') | (roof != 'closed')")
        
        stadiums.set_index('home_team', inplace=True)

        if overrides:
            for i in overrides:
                stadiums.loc[i, 'roof'] = overrides[i]
        
        riq = stadiums.loc[team_name, 'roof']
        
        return riq
    
    def nfl_games(self, retractables=None):
    
        soup_today = self.soup_setup('https://sportsbook.draftkings.com/leagues/football/3?category=game-lines&subcategory=game')
        
        teams = []
        for i in range(len(soup_today.findAll('span', {'class':'event-cell__name'}))):
            tm = soup_today.findAll('span', {'class':'event-cell__name'})[i]
            dkRe = re.search('>.+<', str(tm))
            tm = dkRe.group().replace('>', '').replace('<', '')
            ny_la = ['NY Giants', 'NY Jets', 'LA Chargers']
            if tm in ny_la:
                tm = tm[:4]
                tm = tm.replace(' ', '')
            else:
                tm = tm.split(sep=' ')[0]
            
            teams.append(tm)
        
        spreads = []
        totals = []
        home = []
        n = 0
        for i in range(len(soup_today.findAll('span', {'class':'sportsbook-outcome-cell__line'}))):
            sp1 = soup_today.findAll('span', {'class':'sportsbook-outcome-cell__line'})[i]
            dkRe = re.search('>.+<', str(sp1))
            sp1 = float(dkRe.group().replace('>', '').replace('<', '').replace('+', ''))
            
            if sp1 > 30:
                totals.append(sp1)
            else:
                spreads.append(sp1)
            home.append(n % 2)
            n += 1
        
        games = {}
        for i in range(len(teams)):
            if home[i] == 0:
                games[teams[i]] = {'Spread':spreads[i], 'Total':totals[i], 
                                   'Home':home[i], 'Roof':self.nfl_stadium_type(teams[i+1], overrides=retractables)}
            else:
                games[teams[i]] = {'Spread':spreads[i], 'Total':totals[i], 
                                   'Home':home[i], 'Roof':self.nfl_stadium_type(teams[i], overrides=retractables)}
                                            
        return games
    
    def nfl_props(self, prop):
        
        soup_today = self.soup_setup(f"https://sportsbook.draftkings.com/leagues/football/3?category=player-props&subcategory={prop}")
        
        players = []
        for i in range(len(soup_today.findAll('span', {'class':'sportsbook-participant-name'}))):
            moss = soup_today.findAll('span', {'class':'sportsbook-participant-name'})[i]
            dkRe = re.search('>.+<', str(moss))
            moss = dkRe.group().replace('>', '').replace('<', '')
            randy = moss.split(sep=" ")
            moss = f"{randy[0][0]}.{randy[1]}"
            
            players.append(moss)
        
        overs = []
        unders = []
        odds = []
        for i in range(len(soup_today.findAll('span', {'class':'sportsbook-outcome-cell__label'}))):
            rice = soup_today.findAll('span', {'class':'sportsbook-outcome-cell__label'})[i]
            dkRe = re.search('>.+<', str(rice))
            rice = dkRe.group().replace('>', '').replace('<', '')
            jerry = rice.split(sep=" ")

            megatron = soup_today.findAll('span', {'class':'sportsbook-odds american default-color'})[i]
            dkRe = re.search('>.+<', str(megatron))
            megatron = int(dkRe.group().replace('>', '').replace('<', '').replace('+', ''))
            
            if megatron > 0:
                julio = round(1 / ((megatron/100) + 1), 4)
            else:
                julio = round(1 - (1 / ((-1*megatron/100) + 1)), 4)
            
            if jerry[0] == 'Over':
                overs.append([float(jerry[1]), megatron, julio])
            else:
                unders.append([float(jerry[1]), megatron, julio])
                
        for x, y in zip(overs, unders):
            odds.append({'Over': x, 'Under': y})
        
        lamarca = {}
        for i in range(len(players)):
            lamarca[players[i]] = odds[i]
            
        return lamarca
        

