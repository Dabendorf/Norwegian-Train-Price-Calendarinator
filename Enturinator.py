from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
import pytz

def fetch_website(url):
	options = Options()
	options.add_argument("--headless")  # Run Chrome in headless mode
	driver = webdriver.Chrome(options=options)
	driver.get(url)
	time.sleep(10)  # Wait for 10 seconds
	content = driver.page_source
	driver.quit()
	return content

def get_transit_container(html_content):
	soup = BeautifulSoup(html_content, "html.parser")
	container = soup.find("div", class_="transit-result__list")

	if container:
		return container
	else:
		print("Container not found.")
		exit(0)

def get_trains_from_html(html_content):
	date = html_content.find("span", class_="travel-list-header__label").get_text().strip()
	connections_ul = html_content.find("ul")
	connection_items = connections_ul.findAll(class_= "transit-result-item transit-result__list__item")

	for connection in connection_items:
		station_from = connection.find("span", class_="transit-result-item__header__name").get_text().strip()
		duration = connection.find("span", class_="transit-result-item__header__duration").get_text().strip()
		line_name = connection.find("span", class_="travel-tag__label travel-tag__label--margin").get_text().strip()
		time_departure = connection.find("time", class_="legs-list__leg__time__time").get_text().strip()
		time_arrival = connection.find("time", class_="trip-pattern-list__time").get_text().strip()
		price = connection.find("span", class_="transit-result-item__footer__text").get_text().strip()
		
		print(connection["aria-label"])
		print(f"{line_name} from {station_from} from {time_departure} to {time_arrival} ({duration}) for {price}")

def read_html_file(file_path):
	with open(file_path, "r") as file:
		content = file.read()
	return content

def generate_url(date, station_from, station_to):
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
	oslo_timezone = pytz.timezone("Europe/Oslo")
	oslo_datetime = oslo_timezone.localize(datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute))
	unix_time = int(oslo_datetime.timestamp())
	return unix_time

def main():
	# Parameter
	debug = True

	# Stations
	station_dict = read_stations("./data/stations.txt")
	
	if debug:
		content = read_html_file("./debug/example_html.html")
	else:
		url = generate_url(date = convert_to_unix_time(2023, 7, 13, 18, 0), station_from=station_dict["Bergen"], station_to=station_dict["Myrdal"])
		content = fetch_website(url)

	# Mine content
	transit_data = get_transit_container(content)
	train_data = get_trains_from_html(transit_data)

	# Output
	#prettified_content = train_data.prettify()
	#print(prettified_content)

	

if __name__ == "__main__":
	main()
	