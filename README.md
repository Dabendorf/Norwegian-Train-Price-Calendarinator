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

## Things to fix
* Entur relies heavily on a weird URL format which requires for parameter for each station ([label, longitude, latitude, stopID]). Since three of them aren't obvious, there is a dictionary file in ``data/stations.txt`` which has some common stations in it. If yours is missing, add a new line in there. It might be possible to connect this to the station API of entur
* relies on Google Chrome, maybe find something else (Raspberry Pi friendly)
* The data only shows information being visible on the main page. Theoretically, there is more information by clicking on each element

## Run
* ```python3 Enturinator.py```
* put in the wanted information like date and stations into the main function

## Project Structure
* ```Enturinator.py``: main file
* ``data/station.txt``: information about stations
* ``debug/`` folder: some html fileswith example data so one does not need to fetch from the website for each run

## Debug
There is an example file in the debug folder. Activate ``debug=true`` in the main function such that it is not necessary to download the data every time you test something. This may also prevent you from being IP banned