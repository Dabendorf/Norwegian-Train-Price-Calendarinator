# Norwegian-Train-Price-Calendarinator
This project aims to generate a pricing calendar for Norwegian train connections and a price alert for changing prices. Unfortunetily, Entur does not plan to make their Price API publicly available, therefore we need to take their data by mining the website, which makes the project prune to design changes

## Goals
This project should be able to get prices of train tickets in Norway and monitor changes of these prices
* get all connections from A to B, including their prices
* save prices (maybe in a database) and inform about changes

## Todo
* make it more usable by either an UI or terminal parameter
* find a better data format
* currently, it only searches for pricers for adults (voksen); should be able to search others (e.g. student) as well
* it only informs about cheaper connections, this must not necessarily be the cheapest price of the day

## Things to fix
* Entur relies heavily on a weird URL format which requires for parameter for each station ([label, longitude, latitude, stopID]). Since three of them aren't obvious, there is a dictionary file in ``data/stations.txt`` which has some common stations in it. If yours is missing, add a new line in there. It might be possible to connect this to the station API of entur
* relies on Google Chrome, maybe find something else (Raspberry Pi friendly)
* The data only shows information being visible on the main page. Theoretically, there is more information by clicking on each element
* it ignores the setting about time windows, only asking about the first day
* daatabase date and queries about events in the past should be ignored/cleaned

## Things to know
* If there are two trains at the same time on the same day, it does not save information about both connections but only saves the cheaper one of them (treating them both as the same connection)

## Run
* install the requirements: ```pip install -r requirements.txt```
* install ``chromium-browser`` and ``chromedriver``: ``sudo apt-get install chromium-browser`` and ``sudo apt-get install chromium-chromedriver``
* run programme: ```python3 Enturinator.py```
* put in the wanted information like date and stations into the main function

## Project Structure
* ``Enturinator.py``: main file
* ``data/station.txt``: information about stations
* ``data/config.txt``: contains configuration settings of the project
* ``data/ObservedPrices.db``: the database containing information about what to observe and historical prices
* ``debug/`` folder: some html fileswith example data so one does not need to fetch from the website for each run

## Current data format (to be improved)
* Connection: ```station_from: string, station_to: string, price: int, departure: string, arrival: string, duration (min): int, description: str, exchanges: int, legs: List[tuple(str, str)]```
* Travelday: ```connections: List[Connection], date: str```

## Debug
There is an example file in the debug folder. Activate ``debug  True`` in the config file such that it is not necessary to download the data every time you test something. This may also prevent you from being IP banned

## Add connections to observe
To add a connection you want to observe, there are two ways.
Either run the command ``db_manager.insert_to_observe("Bergen", "Oslo S", "2023-08-06", "2023-08-10", "2023-08-30")`` within the python script (only once!)
or run the SQL command directly on the database: ``INSERT INTO ToObserve (station_from, station_to, date_observe_start, date_observe_end, observe_until) VALUES ("Bergen", "Oslo S", "2023-08-06", "2023-08-10", "2023-08-30")``

To remove a connection, run a ``DELETE FROM`` command on that SQL table

## Email
Create a configuration file at ``data/mailconfig.txt`` in the same way as the other configuration file. It should have the following content:
```
host	smtp.myserver.co.nz
port	465
mailaddress	yourmailaddress
password	yourpassword
emailTo	receiver
```

## Run automatically
run ``crontab -e`` on your raspberry pi and add this line (remember to alter the paths): ``0 0 * * * /usr/bin/python3 /home/pi/Bots/NorwegianTrainPriceCalendarinator/Enturinator.py >/dev/null 2>&1``