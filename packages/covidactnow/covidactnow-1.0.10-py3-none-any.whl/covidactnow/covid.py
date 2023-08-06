import requests

# As CovidActNow's API is a REST API, queries are stored as URLs.

class User:
    def __init__(self, api_key):
        self.api_key = api_key

api_key = 'e455e818c8b849fc955b49c133322e2d'

def queryUrl(state):
    return f"http://api.covidactnow.org/v2/state/{state}.json?apiKey=" + api_key

# Creating a covidInfo object class which contains COVID-related information attributes.

class covidInfo:
    def __init__(self, state):
        # Infection Rate
        try:
            self.infRate = float(requests.get(queryUrl(state)).json()['metrics']['infectionRate'])
        except:
            self.infRate = "NaN"
        
        # Positive Rate
        try:
            self.posRate = round(100*float(requests.get(queryUrl(state)).json()['metrics']['testPositivityRatio']), 2)
        except:
            self.posRate = "NaN"
        
        # Vax Rate
        try:
            self.vaxRate = round(100*float(requests.get(queryUrl(state)).json()['metrics']['vaccinationsCompletedRatio']), 2)
        except:
            self.vaxRate = "NaN"
        
        # Free Bed Percentage
        try:
            self.freeBedPercentage = round(100*float(requests.get(queryUrl(state)).json()['actuals']['hospitalBeds']['currentUsageTotal'])/\
                float(requests.get(queryUrl(state)).json()['actuals']['hospitalBeds']['capacity']), 2)
        except:
            self.freeBedPercentage = "NaN"
        
        # New Cases
        try:
            self.newCases = int(requests.get(queryUrl(state)).json()['actuals']['newCases'])
        except:
            self.newCases = "NaN"

        # New Deaths
        try:
            self.newDeaths = int(requests.get(queryUrl(state)).json()['actuals']['newDeaths'])
        except:
            self.newDeaths = "NaN"
        
        # Covid Bed Percentage
        try:
            self.covidBedPercentage = round(100*float(requests.get(queryUrl(state)).json()['actuals']['hospitalBeds']['currentUsageCovid'])/\
                float(requests.get(queryUrl(state)).json()['actuals']['hospitalBeds']['capacity']), 2)
        except:
            self.covidBedPercentage = "NaN"