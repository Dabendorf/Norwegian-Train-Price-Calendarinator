# Norwegian-Train-Price-Calendarinator
This project aims to generate a pricing calendar for Norwegian train connections and a price altert for changing prices 

## Todo
* get data
* save previous data
* customise known routes
* set standard stations (like Bergen Jernbanestasjon)
* notification

## Things to fix
* relies on Google Chrome, maybe find something else (Raspberry Pi friendly)
* Entur relies heavily on a weird URL format which requires for parameter for each station ([label, longitude, latitude, stopID]). Since three of them aren't obvious, there is a dictionary file in ``data/stations.txt`` which has some common stations in it. If yours is missing, add a new line in there

## Run
```python3 Enturinator.py```

## Debug
There is an example file in the debug folder. Activate ``debug=true`` in the main function such that it is not necessary to download the data every time you test something. This may also prevent you from being IP banned