from typing import List, Tuple

class Connection:
	def __init__(self, station_from: str, station_to: str, price: int, departure: str, arrival: str, duration: str, legs: List[Tuple[str, str]]):
		self.station_from = station_from
		self.station_to = station_to
		self.price = price
		self.departure = departure
		self.arrival = arrival
		self.duration = duration
		self.legs = legs
		self.exchanges = len(legs)-1

	def __str__(self):
		return f"From: {self.station_from}\nTo: {self.station_to}\nPrice: {self.price} kr\nDeparture: {self.departure}\nArrival: {self.arrival}\nDuration: {self.duration} minutes\nExchanges: {self.exchanges}\nLegs: {self.legs}\n"


class TravelDay:
	def __init__(self, connections: List[Connection], date: str):
		self.connections = connections
		self.date = date
	
	def __str__(self):
		connection_strings = '\n'.join(str(connection) for connection in self.connections)
		return f"{self.date}\n{connection_strings}"
