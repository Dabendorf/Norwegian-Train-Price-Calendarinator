from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import datetime
from datetime import datetime
import pytz
from DataContainer import Connection, TravelDay
from Database import DatabaseManager
import re
import logging
from logging.handlers import TimedRotatingFileHandler
import smtplib
import ssl
import os

def send_simple_email(to, subject, body, mailconfig_dict):
	"""Sends an email notification

	Parameters:
	to (string): receiver
	subject (string): subject
	body (string): Email content
	mailconfig_dict (dict): The dictionary with the email configuration
	"""		
	if "host" not in mailconfig_dict or "mailaddress" not in mailconfig_dict or "password" not in mailconfig_dict or "emailTo" not in mailconfig_dict:
		logging.getLogger("Main").warning(f"Missing argument for email configuration. No email will be send.")
		logging.getLogger("Main").warning(f"Mail config: {mailconfig_dict}")
		return


	#Your SMTP server
	host = mailconfig_dict["host"]
	port = int(mailconfig_dict.get("port",465))

	#Your credentials
	login = mailconfig_dict["mailaddress"]
	password = mailconfig_dict["password"]

	#Build your email
	context = ssl.create_default_context()

	email = f"Subject: {subject}\nTo: {to}\nFrom: {login}\n{body}"

	#Send email
	with smtplib.SMTP_SSL(host, port, context=context) as server:
		server.login(login, password)
		server.sendmail(login, to, email)

def read_mailconfiguration(config_path=f"{os.path.abspath(__file__).replace('Enturinator.py','')}data/emailconfig.txt"):
	"""Reads the preset email configuration of the project

	Parameters:
	config_path (string): Path to the config file, per default data/emailconfig.txt

	Returns:
	string: configuration dictionary
	"""
	with open(config_path) as config_file:
		lines = [i.strip() for i in config_file.readlines() if (not i.startswith("#") and len(i.strip()) > 0)]

		mailconfig_dict = dict()
		for line in lines:
			linesplit = line.split("\t")
			if len(linesplit) != 2:
				logging.getLogger("Main").warning(f"Wrong config file format in this line:\n{line}")
			else:
				splitarg = linesplit[1].split(",")
				if len(splitarg) > 1:
					mailconfig_dict[linesplit[0]] = splitarg
				else:
					mailconfig_dict[linesplit[0]] = linesplit[1]

	return mailconfig_dict

def read_configuration(config_path=f"{os.path.abspath(__file__).replace('Enturinator.py','')}data/config.txt"):
	"""Reads the preset configuration of the project

	Parameters:
	config_path (string): Path to the config file, per default data/config.txt

	Returns:
	string: configuration dictionary

	"""
	with open(config_path) as config_file:
		lines = [i.strip() for i in config_file.readlines() if (not i.startswith("#") and len(i.strip()) > 0)]

		config_dict = dict()
		for line in lines:
			linesplit = line.split("\t")
			if len(linesplit) != 2:
				logging.getLogger("Main").error(f"Wrong config file format in this line:\n{line}")
				logging.getLogger("Main").error("Programme aborted")
				exit(0)
			else:
				splitarg = linesplit[1].split(",")
				if len(splitarg) > 1:
					config_dict[linesplit[0]] = splitarg
				else:
					config_dict[linesplit[0]] = linesplit[1]
		
		return config_dict

def fetch_website(url, until_day, waiting_time=10):
	"""Takes any URL and downloads its html content

	Parameters:
	url (string): webpage URL

	Returns:
	string: html content

	"""
	options = Options()
	options.add_argument("--headless")
	driver = webdriver.Chrome(options=options)
	driver.get(url)

	wait = WebDriverWait(driver, waiting_time)

	while True:
		try:
			wait.until(EC.invisibility_of_element_located((By.XPATH, f"//span[@class='travel-list-header__label' and contains(text(), '{until_day}')]")))
			wait.until(EC.element_to_be_clickable((By.CLASS_NAME, f"transit-result__load-more"))).click()
			time.sleep(1)
			continue # Continue clicking the button if the span element is not found within the timeout
		except TimeoutException:
			logging.getLogger("Main").debug("Found the span, break")
			break

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
		logging.getLogger("Main").error(f"Container not found.")
		logging.getLogger("Main").error("Programme aborted")
		exit(0)

def get_trains_from_html(html_content, until_day=None):
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
		if date.lower() == until_day.lower():
			logging.getLogger("Main").debug(f"Found final day: {day}")
			continue
		
		connections_ul = day.find("ul")	# container for all connections on this day

		connection_items = connections_ul.findAll(class_= "transit-result-item transit-result__list__item") # list of all connections

		for connection in connection_items: # each single connection
			leg_items = connection.findAll("li", class_= "legs-list__leg") # list of all transport legs (e.g. single train within a connection)
			
			# possible to get more information by clicking on he object or finding transport type and time in current html
			# However, it currently mines content from the aria label
			#for leg in leg_items:
			#	print(leg)
			aria_label_list = list(filter(None, connection["aria-label"].replace("Trykk for detaljer", "").replace("Reiseforslaget har et avvik.","").strip().split(".")))
			
			try:
				duration = connection.find("span", class_="transit-result-item__header__duration").get_text().strip()
				time_departure = connection.find("time", class_="legs-list__leg__time__time").get_text().strip()
				time_arrival = connection.find("time", class_="trip-pattern-list__time").get_text().strip()
				price = connection.find("span", class_="transit-result-item__footer__text").get_text().strip()
				station_from = connection.find("span", class_="transit-result-item__header__name").get_text().strip()
			except AttributeError as err:
				logging.getLogger("Main").error(f"Cannot find class {err.with_traceback}")
				logging.getLogger("Main").error(connection)

			if "ikke" in price.lower() or "billetter" in price.lower() or "selges" in price.lower() or "utsolgt" in price.lower():
				if "Billetter selges ikke av Entur".lower() in price.lower() or "Billetter selges deler av reisen".lower():
					continue
				price = 2147483647.0
			else:
				findPriceInString = re.findall(r'\d+', price)
				if len(findPriceInString) == 0:
					price = 2147483647.0
					logging.getLogger("Main").info(f"Another exception in casting the prices: {price}")
					continue
				else:
					price = float(findPriceInString[0])
			conn = Connection(station_from = station_from, station_to = None, price = price, departure = f" {convert_norwegian_day_to_date(date)} {time_departure}", arrival = time_arrival, duration = duration, legs = [a.strip() for a in aria_label_list[2].split(",")])

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
	transport_types = [
		#"%2Cbus",
		#"%2Ccoach",
		"%2Ctram",
		"%2Cwater",
		"%2Ccar_ferry",
		"%2Cmetro",
		"%2Cflytog",
		"%2Cflybuss"
	]
	global config
	if "transportTypes" in config:
		transport_types = "".join([f"%2C{i}" for i in config["transportTypes"]])

	url = f"https://entur.no/reiseresultater?transportModes=rail"+("".join(transport_types))
	
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
	oslo_datetime = oslo_timezone.localize(datetime(year=year, month=month, day=day, hour=hour, minute=minute))
	unix_time = int(oslo_datetime.timestamp())
	return unix_time

def convert_norwegian_day_to_date(datestring):
	"""Converts date and time information to unix time (based on Oslo timezone)

	Parameters:
	datastring (str): entur formated string describing a date

	Returns:
	str: Date in format %Y-%m-%d

   """
	weekday_prefixes = ["mandag ", "tirsdag ", "onsdag ", "torsdag ", "fredag ", "lørdag ", "søndag "]
	for prefix in weekday_prefixes:
		if datestring.lower().startswith(prefix):
			datestring = datestring[len(prefix):]
			break
	
	norwegian_month_names = {
		"januar": 1, "februar": 2, "mars": 3, "april": 4,
		"mai": 5, "juni": 6, "juli": 7, "august": 8,
		"september": 9, "oktober": 10, "november": 11, "desember": 12
	}

	day, month_name = datestring.split(". ")
	month = norwegian_month_names[month_name]

	date = datetime(datetime.now().year, month, int(day))
	formatted_date = date.strftime("%Y-%m-%d")

	return formatted_date

def convert_date_to_norwegian_date(datestring):
	"""Converts %Y-%m-%d string to Entur date format, e.g. Onsdag 26. juli

	Parameters:
	datastring (str): %Y-%m-%d

	Returns:
	str: Entur datestring, e.g. Onsdag 26. juli
	"""
	date = datetime.strptime(datestring, "%Y-%m-%d")

	month = date.month
	day = date.day
	weekday = date.weekday()  # Monday is 0 and Sunday is 6

	weekday_prefixes = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]
	
	norwegian_month_names = {
		1: "januar", 2: "februar", 3: "mars", 4: "april",
		5: "mai", 6: "juni", 7: "juli", 8: "august",
		9: "september", 10: "oktober", 11: "november", 12: "desember"
	}
	return f"{weekday_prefixes[weekday].capitalize()} {day}. {norwegian_month_names[month]}"

def connect_database(databasepath):
	"""Connects to a database and returns a database manager

	Parameters:
	databasepath (str): path to database

	Returns:
	DatabaseManager: DatabaseManager

   """
	db_manager = DatabaseManager(databasepath)

	db_manager.connect()

	db_manager.create_tables()
	
	return db_manager

def main():
	# Get absolute path to this
	path = os.path.abspath(__file__).replace("Enturinator.py","")

	# Logger
	log_format = "%(name)s - %(asctime)s - %(levelname)s - %(message)s"
	logging.basicConfig(format=log_format, level=logging.INFO)
	logger = logging.getLogger("Main")
	log_handler = TimedRotatingFileHandler(f"{path}logs/enturbot.log", when="w0", interval=1, backupCount=4)
	
	formatter = logging.Formatter(log_format)
	log_handler.setFormatter(formatter)
	logger.addHandler(log_handler)

	# Configuration
	global config
	config = read_configuration()
	logger.debug("Read configuration file")
	logger.debug(f"{config}")

	# Mail
	mailActivated = config.get("emailActivated", False)=="True"
	if mailActivated:
		mailconfig = read_mailconfiguration()
		logger.debug("Read email configuration file")
		logger.debug(f"{mailconfig}")
	
	# Parameter
	debug = config.get("debug", True)=="True"
	if debug:
		logger.debug("Debug mode is on")

	# Read stations
	station_dict = read_stations(f"{path}data/stations.txt")
	logger.debug("Stations read")

	db_manager = connect_database(f"{path}data/ObservedPrices.db")
	logger.debug("Database connected")
	
	all_observe_ids = db_manager.get_all_observe_ids()
	logger.debug(f"IDs to observe: {all_observe_ids}")

	# This is a file for debugging, it contains mapping between observe_ids and filenames
	observe_id_filename_dict = {3: "entur_3_20230806.html", 2: "entur_2_20230806.html"}

	for observe_id in all_observe_ids:
		logger.debug(f"Observe_id: {observe_id}")

		# Fetch data
		row = db_manager.get_observe_row(observe_id)
		data_el = row[3].split("-")

		# Upper boundary of time window to observe
		until_date = convert_date_to_norwegian_date(row[4])
		observe_until = row[5]

		# Check if until_observe date got surpassed in time => delete event, stopp to observe it
		if datetime.now().date() > datetime.strptime(observe_until, "%Y-%m-%d").date():
			logging.getLogger("Main").info(f"Observation task {observe_id} has reached its final observation date ({observe_until}). It will be deleted")
			db_manager.delete_task(observe_id)
			continue
		# Check if today is already within time window, so there there is no need to observe it anymore => delete event, stopp to observe it
		if datetime.now().date() > datetime.strptime(row[3], "%Y-%m-%d").date():
			logging.getLogger("Main").info(f"Observation task {observe_id} is in the past ({row[3]}). It will be deleted")
			db_manager.delete_task(observe_id)
			continue
		
		if debug:
			if observe_id in observe_id_filename_dict:
				logger.debug("Debug mode: found debug file")
				content = read_html_file(f"{path}debug/{observe_id_filename_dict[observe_id]}")
			else:
				logger.debug("Debug file not found, skip over")
				continue
		else:
			url = generate_url(date = convert_to_unix_time(int(data_el[0]), int(data_el[1]), int(data_el[2]), 0, 0), station_from=station_dict[row[1]], station_to=station_dict[row[2]])
			content = fetch_website(url, until_date)

		# Convert html content to proper information
		transit_data = get_transit_container(content)
		train_data = get_trains_from_html(transit_data, until_day=until_date)
		
		logger.debug(f"Transit container and trains are fetched from html")
		with open(f"{path}debug/entur_{observe_id}_{data_el[0]}{data_el[1]}{data_el[2]}.html", "w") as file:
			prettified_content = transit_data.prettify()
			file.write(prettified_content)

		for day in train_data:
			for conn in day.connections:
				changed, price, old_price = db_manager.insert_price_data(observe_id, conn.departure, conn.price)
				if changed:
					if mailActivated:
						logger.info(f"The connection {row[1]} to {row[2]} is cheaper now. The new price at {conn.departure} is: {price}")
						send_simple_email(mailconfig["emailTo"], f"We found a cheaper price", f"The connection {row[1]} to {row[2]} is cheaper now. The new price at{conn.departure} is: {price} NOK (before {old_price}).\nThis is not necessarily the cheapest price of the day.", mailconfig)
						logger.info("Mail sent")

		lowest_price = db_manager.get_lowest_price(observe_id)
		logger.info(f"Cheapest price for id={observe_id} from {row[1]} to {row[2]} on {data_el[0]}-{data_el[1]}-{data_el[2]}:")
		logger.info(f"{lowest_price[0]} at {lowest_price[2]}")

	# Disconnect from the database
	db_manager.disconnect()
	logger.debug(f"Database disconnected")
	logger.info(f"Programme finished successfull")

	

if __name__ == "__main__":
	main()
	