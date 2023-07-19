# Norwegian-Train-Price-Calendarinator
This project aims to generate a pricing calendar for Norwegian train connections and a price alert for changing prices. Unfortunetily, Entur does not plan to make their Price API publicly available, therefore we need to take their data by mining the website, which makes the project prune to design changes

## Goals
This project should be able to get prices of train tickets in Norway and monitor changes of these prices
* get all connections from A to B, including their prices
* save prices and inform about changes via email

## TODO
* currently, it only searches for pricers for adults (voksen); should be able to search others (e.g. student) as well
* it only informs about cheaper connections, this must not necessarily be the cheapest price of the day

## Things which would be nice
* make it more usable by either an UI or terminal parameter
* Entur relies heavily on a weird URL format which requires for parameter for each station ([label, longitude, latitude, stopID]). Since three of them aren't obvious, there is a dictionary file in ``data/stations.txt`` which has some common stations in it. If yours is missing, add a new line in there. It might be possible to connect this to the station API of entur
* relies on Google Chrome, maybe find something else (Raspberry Pi friendly)

## Things to know
* If there are two trains at the same time on the same day, it does not save information about both connections but only saves the cheaper one of them (treating them both as the same connection)

## Run
* install the requirements: ```pip install -r requirements.txt```
* install ``chromium-browser`` and ``chromedriver``: ``sudo apt-get install chromium-browser`` and ``sudo apt-get install chromium-chromedriver``
* run programme: ```python3 Enturinator.py```
* add connections to be observed into the database; if you want to use the predefined scripts, make sure to have ``sqlite3`` installed and give the scripts rights to be executed (``chmod +x *.sh``)

## Project Structure
* ``Enturinator.py``: main file
* ``data/station.txt``: information about stations
* ``data/config.txt``: contains configuration settings of the project
* ``data/ObservedPrices.db``: the database containing information about what to observe and historical prices
* ``scripts/``: A folder with some scripts to the database for getting current information and adding/deleting observation tasks

## Data Format
* Connection: ``station_from: string, station_to: string, price: int, departure: string, arrival: string, duration (min): int, description: str, exchanges: int, legs: List[tuple(str, str)]``
* Travelday: ``connections: List[Connection], date: str``

## Debug
There is an example file in the debug folder. Activate ``debug  True`` in the config file such that it is not necessary to download the data every time you test something. This may also prevent you from being IP banned

## Add connections to observe
To add a connection you want to observe, run the ``insertnewtask.sh`` (5 parameters) script in the script folder

To remove a connection, run the ``deletetask.sh`` (1 parameter) file
```bash
./insertnewtask.sh "Trondheim" "Bergen" "2023-10-10" "2023-10-11" "2023-09-01"
./deletetask.sh 4
```

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