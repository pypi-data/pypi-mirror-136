# Covid Act Now Database Wrapper

This package is an extremely bare-bones wrapper around Covid Act Now's database of COVID-19 related information. 

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
washingtonInfectionRate = 1.16
massachussettsVaxRate = 76.3
```
An API key can be generated easily [here](https://covidactnow.org/data-api).

----
For more information on how the wrapper works, read this [page](https://covidinfo.preritdas.com). Note that this version has been updated to get data from within a `User` class allowing individual API keys to be used (as opposed to defining a state as an object and defining statistics as object attributes).