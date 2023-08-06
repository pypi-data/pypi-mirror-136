# Covid Act Now Python Wrapper

This package is an extremely simple wrapper around Covid Act Now's database of COVID-19 related information. 

Usage is simple. Install the package with `pip install covidactnow`.

```
import covidactnow

api = covidactnow.User(api_key = 'yourapikey')

washingtonInfectionRate = api.infRate('WA')
massachussettsVaxRate = api.vaxRate('MA')

print(f"{washingtonInfectionRate = }")
print(f"{massachussettsVaxRate = }")
```
This will result (with different data, of course):
```

```
