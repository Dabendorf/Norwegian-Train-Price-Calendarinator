# Norwegian-Train-Price-Calendarinator
This project aims to generate a pricing calendar for Norwegian train connections and a price alert for changing prices. Unfortunetily, Entur does not plan to make their Price API publicly available, therefore we need to take their data by mining the website, which makes the project prune to design changes

## Goals
This project should be able to get prices of train tickets in Norway and monitor changes of these prices
* get all connections from A to B, including their prices
* save prices (maybe in a database) and inform about changes

## Todo
* save previous data (database? txt)
* notification and some sort of low price calendar (maybe activating a cronjob and sending emails)
* make it more usable by either an UI or terminal parameter
* find a better data format

## Things to fix
* Entur relies heavily on a weird URL format which requires for parameter for each station ([label, longitude, latitude, stopID]). Since three of them aren't obvious, there is a dictionary file in ``data/stations.txt`` which has some common stations in it. If yours is missing, add a new line in there. It might be possible to connect this to the station API of entur
* relies on Google Chrome, maybe find something else (Raspberry Pi friendly)
* The data only shows information being visible on the main page. Theoretically, there is more information by clicking on each element

## Things to know
* If there are two trains at the same time on the same day, it does not save information about both connections but only saves the cheaper one of them (treating them both as the same connection)

## Run
* install the requirements: ```pip install -r requirements.txt```
* run programme: ```python3 Enturinator.py```
* put in the wanted information like date and stations into the main function

## Project Structure
* ```Enturinator.py``: main file
* ``data/station.txt``: information about stations
* ``debug/`` folder: some html fileswith example data so one does not need to fetch from the website for each run

## Current data format (to be improved)
* Connection: ```station_from: string, station_to: string, price: int, departure: string, arrival: string, duration (min): int, description: str, exchanges: int, legs: List[tuple(str, str)]```
* Travelday: ```connections: List[Connection], date: str```

## Debug
There is an example file in the debug folder. Activate ``debug=True`` in the main function such that it is not necessary to download the data every time you test something. This may also prevent you from being IP banned