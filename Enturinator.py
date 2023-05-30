# URL-Example
''' 
https://entur.no/reiseresultater?
transportModes=rail%2Ctram%2Cbus%2Ccoach%2Cwater%2Ccar_ferry%2Cmetro%2Cflytog%2Cflybuss
&date=1685955600000
&tripMode=oneway
&walkSpeed=1.3
&minimumTransferTime=120
&timepickerMode=departAfter
&startId=NSR%3AStopPlace%3A59872
&startLabel=Oslo%20S
&startLat=59.910357
&startLon=10.753051
&stopId=NSR%3AStopPlace%3A59983
&stopLabel=Bergen%20stasjon
&stopLat=60.390434
&stopLon=5.333511

'''

from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

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
	soup = BeautifulSoup(html_content, 'html.parser')
	container = soup.find('div', class_='transit-result__list')

	if container:
		return container
	else:
		print("Container not found.")
		exit(0)

def read_html_file(file_path):
	with open(file_path, "r") as file:
		content = file.read()
	return content

def main():
	debug = True
	
	if debug:
		content = read_html_file("./debug/example_html.txt")
		print(content)
	else:
		url = f"https://entur.no/reiseresultater?transportModes=rail%2Ctram%2Cbus%2Ccoach%2Cwater%2Ccar_ferry%2Cmetro%2Cflytog%2Cflybuss&date=1685955600000&tripMode=oneway&walkSpeed=1.3&minimumTransferTime=120&timepickerMode=departAfter&startId=NSR%3AStopPlace%3A59872&startLabel=Oslo%20S&startLat=59.910357&startLon=10.753051&stopId=NSR%3AStopPlace%3A59983&stopLabel=Bergen%20stasjon&stopLat=60.390434&stopLon=5.333511"

		content = fetch_website(url)

	transit_data = get_transit_container(content)
	prettified_content = transit_data.prettify()
	print(prettified_content)

if __name__ == "__main__":
	main()
	