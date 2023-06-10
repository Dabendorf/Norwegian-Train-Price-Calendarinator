from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
import pytz
from DataContainer import Connection, TravelDay

def fetch_website(url):
	"""Takes any URL and downloads its html content

    Parameters:
    url (string): webpage URL

    Returns:
    string: html content

   """
	options = Options()
	options.add_argument("--headless")  # Run Chrome in headless mode
	driver = webdriver.Chrome(options=options)
	driver.get(url)
	time.sleep(10)  # Wait for 10 seconds
	content = driver.page_source
	driver.quit()
	return content

def get_transit_container(html_content):
	"""Searches for the transit container within the Entur website

    Parameters:
    html_content (string): html content

    Returns:
    string: html content (transit container)

   """
	soup = BeautifulSoup(html_content, "html.parser")
	container = soup.find("div", class_="transit-result__list")

	if container:
		return container
	else:
		print("Container not found.")
		exit(0)

def get_trains_from_html(html_content):
	"""Takes as argument html content and converts it to proper information about train connections and their prices

    Parameters:
    html_content (string): html content

    Returns:
    Travelday list (List[TravelDay]): List of travel days containing information

   """
	day_container = html_content.findAll(class_ = "transit-result__list__container") # Each container for a single day, containing all connections

	travelday_list = list()

	for day in day_container:
		connections = list()

		date = day.find("span", class_="travel-list-header__label").get_text().strip() # the date itself
		print(f"======== {date} ========")

		connections_ul = day.find("ul")	# container for all connections on this day

		connection_items = connections_ul.findAll(class_= "transit-result-item transit-result__list__item") # list of all connections

		for connection in connection_items: # each single connection
			leg_items = connection.findAll("li", class_= "legs-list__leg") # list of all transport legs (e.g. single train within a connection)
			
			# possible to get more information by clicking on he object or finding transport type and time in current html
			# However, it currently mines content from the aria label
			#for leg in leg_items:
			#	print(leg)
			aria_label_list = list(filter(None, connection["aria-label"].replace("Trykk for detaljer", "").replace("Reiseforslaget har et avvik.","").strip().split(".")))

			duration = connection.find("span", class_="transit-result-item__header__duration").get_text().strip()
			time_departure = connection.find("time", class_="legs-list__leg__time__time").get_text().strip()
			time_arrival = connection.find("time", class_="trip-pattern-list__time").get_text().strip()
			price = connection.find("span", class_="transit-result-item__footer__text").get_text().strip()
			station_from = connection.find("span", class_="transit-result-item__header__name").get_text().strip()

			conn = Connection(station_from = station_from, station_to = None, price = price, departure = time_departure, arrival = time_arrival, duration = duration, legs = [a.strip() for a in aria_label_list[2].split(",")])

			connections.append(conn)
		travelday_list.append(TravelDay(connections=connections, date=date))
		

	return travelday_list

def read_html_file(file_path):
	"""Reads an html file

    Parameters:
    file_path (string): path of the file to read

    Returns:
    string: content of the file

   """
	with open(file_path, "r") as file:
		content = file.read()
	return content

def generate_url(date, station_from, station_to):
	"""Generates the URL to fetch from the Entur website

    Parameters:
    date (int): Travel date as unix time
	station_from (tuple): Tuple of station information
	station_to (tuple): Tuple of station information

    Returns:
    string: URL

    """
	print(type(date))
	print(type(station_from))
	print(type(station_to))
	url = f"https://entur.no/reiseresultater?transportModes=rail%2Ctram%2Cbus%2Ccoach%2Cwater%2Ccar_ferry%2Cmetro%2Cflytog%2Cflybuss"
	url += f"&date={date}000"	# travel day
	url += f"&tripMode=oneway"
	url += f"&walkSpeed=1.3"
	url += f"&minimumTransferTime=120"
	url += f"&timepickerMode=departAfter"
	url += f"&startId={station_from[0]}"		# start
	url += f"&startLabel={station_from[1]}"
	url += f"&startLat={station_from[2]}"
	url += f"&startLon={station_from[3]}"
	url += f"&stopId={station_to[0]}"			# end
	url += f"&stopLabel={station_to[1]}"
	url += f"&stopLat={station_to[2]}"
	url += f"&stopLon={station_to[3]}"
	return url

def read_stations(file_path):
	"""Reads the station file

    Parameters:
    file_path (string): Path of the station file

    Returns:
    dict(string, tuple): Dictionary of station information

   """
	data_dict = {}
	with open(file_path, "r") as file:
		lines = file.readlines()
		header = lines[0].strip().split(',') 
		for line in lines[1:]:
			values = line.strip().split(',')
			common_name = values[0].replace("\"","")
			rest_of_values = tuple([a.replace("\"","") for a in values[1:]])
			data_dict[common_name] = rest_of_values
	return data_dict

def convert_to_unix_time(year, month, day, hour, minute):
	"""Converts date and time information to unix time (based on Oslo timezone)

    Parameters:
    year (int): year
	month (int): month
	day (int): day
	hour (int): hour
	minute (int): minute

    Returns:
    int: Unix time

   """
	oslo_timezone = pytz.timezone("Europe/Oslo")
	oslo_datetime = oslo_timezone.localize(datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute))
	unix_time = int(oslo_datetime.timestamp())
	return unix_time

def main():
	# Parameter
	debug = True

	# Read stations
	station_dict = read_stations("./data/stations.txt")
	
	if debug:
		# Read example file
		content = read_html_file("./debug/example_multiday.html")
	else:
		# Generate URL and fetch information from the website
		url = generate_url(date = convert_to_unix_time(2023, 7, 13, 18, 0), station_from=station_dict["Bergen"], station_to=station_dict["Myrdal"])
		content = fetch_website(url)
		

	# Convert html content to proper information
	transit_data = get_transit_container(content)
	train_data = get_trains_from_html(transit_data)

	for day in train_data:
		print(f"{day}\n")
		

	# Output
	#prettified_content = train_data.prettify()
	#print(prettified_content)

	

if __name__ == "__main__":
	main()
	