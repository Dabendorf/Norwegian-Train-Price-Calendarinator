import sqlite3
import logging

class DatabaseManager:
	def __init__(self, database_name):
		self.database_name = database_name
		self.connection = None
		self.cursor = None
	
	def connect(self):
		self.connection = sqlite3.connect(self.database_name)
		self.cursor = self.connection.cursor()
	
	def disconnect(self):
		self.connection.close()
		self.connection = None
		self.cursor = None
	
	def create_tables(self):
		# Create the ToObserve table if it doesn't exist
		""" Contains data which train connections should be observed
		"""
		self.cursor.execute('''
			CREATE TABLE IF NOT EXISTS ToObserve (
				id INTEGER PRIMARY KEY,
				station_from TEXT,
				station_to TEXT,
				date_observe_start DATE,
				date_observe_end DATE,
				observe_until DATE
			)
		''')
		
		# Create the PriceData table if it doesn't exist
		"""
			Contains information which connection had which price at which day
		"""
		self.cursor.execute('''
			CREATE TABLE IF NOT EXISTS PriceData (
				id INTEGER PRIMARY KEY,
				observeID INTEGER,
				datetime DATETIME,
				price REAL,
				TimeObserved DATETIME DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (observeID) REFERENCES ToObserve(id)
			)
		''')
	
	def insert_to_observe(self, station_from, station_to, date_observe_start, date_observe_end, observe_until):
		self.cursor.execute('''
			INSERT INTO ToObserve (station_from, station_to, date_observe_start, date_observe_end, observe_until)
			VALUES (?, ?, ?, ?, ?)
		''', (station_from, station_to, date_observe_start, date_observe_end, observe_until))
		
		self.connection.commit()
		return self.cursor.lastrowid
	
	def insert_price_data(self, observe_id, datetime, price):
		"""Inserts price information if its new or cheaper. Also returns old price, new price and if it changed

		Parameters:
		observe_id (int): ID of the connection to check
		datetime (str): when the train goes
		price (int): new price

		Returns:
		tuple(bool, int, int): pricechanged, newPrice, oldPrice
		"""
		query = f"SELECT price FROM PriceData WHERE observeID = {observe_id} AND datetime = '{datetime}'"
		self.cursor.execute(query)

		result = self.cursor.fetchone()

		if result is not None:
			# An old value exists
			old_price = result[0]
			#logging.debug(f"{datetime} {result} {old_price} {price}")
			if old_price > price:
				query = f"UPDATE PriceData SET price={price} WHERE observeID={observe_id} AND datetime = '{datetime}'"
				self.cursor.execute(query)
				self.connection.commit()
				if old_price == 2147483647:
					return False, price, None
				else:
					return True, price, old_price
			else:
				return False, None, None
		else:
			# Insert the new row
			self.cursor.execute(f"INSERT INTO PriceData (observeID, datetime, price) VALUES ({observe_id}, '{datetime}', {price})")

			self.connection.commit()
			return False, None, None

	def get_all_observe_ids(self) -> int:
		"""Checks the database for the IDs of all connections to be observed

		Returns:
		List[int]: List of all observeIDs, being IDs of connections to observe
		"""
		query = "SELECT DISTINCT id FROM ToObserve;"
		self.cursor.execute(query)

		unique_ids = [row[0] for row in self.cursor.fetchall()]
		return unique_ids

	def get_observe_row(self, id: int):
		"""Returns a single database row in the ToObserve table by its ID

		Parameters:
		id (int): ID of the connection to check

		Returns:
		single row
		"""
		self.cursor.execute(f"SELECT * FROM ToObserve WHERE id={str(id)}")

		return self.cursor.fetchone()

	def get_lowest_price(self, id: int):
		"""Returns a single database row of the cheapest connection for one connection ID

		Parameters:
		id (int): ID of the connection to check

		Returns:
		single row of the cheapest connection
		"""
		self.cursor.execute(f"SELECT MIN(price),id,datetime FROM PriceData WHERE observeID = {str(id)} GROUP BY observeID")

		return self.cursor.fetchone()

	def delete_task(self, observe_id, delete_price_data=True):
		"""Deletes an observation task. Depending on the delete_price_data flag, it also deletes historical data

		Parameters:
		observe_id (int): ID of the observation task
		delete_price_data (bool): True if historical price data will be deleted as well
		"""
		self.cursor.execute(f"DELETE FROM ToObserve WHERE id={observe_id};")

		if delete_price_data:
			self.cursor.execute(f"DELETE FROM PriceData WHERE observeID={observe_id};")

		self.connection.commit()

