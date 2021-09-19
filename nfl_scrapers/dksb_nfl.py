import pandas as pd
import numpy as np

import requests
import re
import time

class NFLScraper():
    def nfl_games_dk(self, half=0):
        """
        Scrapes current NFL game lines.

        Returns
        -------
        games : dictionary containing teams, spreads, totals, moneylines, home/away, and opponent.

        """
        if half == 0:
            dk_api = requests.get("https://sportsbook-us-nj.draftkings.com//sites/US-NJ-SB/api/v4/eventgroups/88670561?includePromotions=true&format=json").json()
            dk_markets = dk_api['eventGroup']['offerCategories'][0]['offerSubcategoryDescriptors'][0]['offerSubcategory']['offers']
        elif half == 1:
            dk_api = requests.get("https://sportsbook.draftkings.com//sites/US-NJ-SB/api/v4/eventgroups/88670561/categories/526?format=json").json()
            for i in dk_api['eventGroup']['offerCategories']:
                if i['name'] == 'Halves':
                        dk_markets = i['offerSubcategoryDescriptors'][0]['offerSubcategory']['offers']
        
        games = {}
        for i in dk_markets:
            if i[0]['outcomes'][0]['oddsDecimal'] == 0: # Skip this if there is no spread
                continue
            away_team = i[0]['outcomes'][0]['label']
            home_team = i[0]['outcomes'][1]['label']
            
            if away_team not in games: 
                # Gotta be a better way then a bunch of try excepts
                games[away_team] = {'location':0}
                try:
                    games[away_team]['moneyline'] = i[2]['outcomes'][0]['oddsDecimal']
                except:
                    pass
                try:
                    games[away_team]['spread'] = [i[0]['outcomes'][0]['line'],
                                                   i[0]['outcomes'][0]['oddsDecimal']]
                except:
                    pass
                try:
                    games[away_team]['over'] = [i[1]['outcomes'][0]['line'],
                                                i[1]['outcomes'][0]['oddsDecimal']]
                except:
                    pass
                try:
                    games[away_team]['under'] = [i[1]['outcomes'][1]['line'],
                                                 i[1]['outcomes'][1]['oddsDecimal']]
                except:
                    pass
                games[away_team]['opponent'] = home_team
            
            if home_team not in games:
                games[home_team] = {'location':1}
                try:
                    games[home_team]['moneyline'] = i[2]['outcomes'][1]['oddsDecimal']
                except:
                    pass
                try:
                    games[home_team]['spread'] = [i[0]['outcomes'][1]['line'],
                                                  i[0]['outcomes'][1]['oddsDecimal']]
                except:
                    pass
                try:
                    games[home_team]['over'] = [i[1]['outcomes'][0]['line'],
                                                i[1]['outcomes'][0]['oddsDecimal']]
                except:
                    pass
                try:
                    games[home_team]['under'] = [i[1]['outcomes'][1]['line'],
                                                 i[1]['outcomes'][1]['oddsDecimal']]
                except:
                    pass     
                games[home_team]['opponent'] = away_team
                
        return games

        def nfl_props_dk(self):
        games = {}
        for cat in range(1000, 1003):
            dk_api = requests.get(f"https://sportsbook.draftkings.com//sites/US-NJ-SB/api/v4/eventgroups/88670561/categories/{cat}?format=json").json()
            for i in dk_api['eventGroup']['offerCategories']:
                if 'offerSubcategoryDescriptors' in i:
                    dk_markets = i['offerSubcategoryDescriptors']
            
            subcategoryIds = []# Need subcategoryIds first
            for i in dk_markets:
                subcategoryIds.append(i['subcategoryId'])
                        
            for ids in subcategoryIds:
                dk_api = requests.get(f"https://sportsbook.draftkings.com//sites/US-NJ-SB/api/v4/eventgroups/88670561/categories/{cat}/subcategories/{ids}?format=json").json()
                for i in dk_api['eventGroup']['offerCategories']:
                    if 'offerSubcategoryDescriptors' in i:
                        dk_markets = i['offerSubcategoryDescriptors']
                
                for i in dk_markets:
                    if 'offerSubcategory' in i:
                        market = i['name']
                        for j in i['offerSubcategory']['offers']:
                            for k in j:
                                if 'participant' in k['outcomes'][0]:
                                    player = k['outcomes'][0]['participant']
                                else:
                                    continue
                                
                                if player not in games:
                                    games[player] = {}
                                    
                                try:
                                    games[player][market] = {'over':[k['outcomes'][0]['line'],
                                                                     k['outcomes'][0]['oddsDecimal']],
                                                             'under':[k['outcomes'][1]['line'],
                                                                     k['outcomes'][1]['oddsDecimal']]}
                                except:
                                    print(player, market)
                                    pass
                
        return games
