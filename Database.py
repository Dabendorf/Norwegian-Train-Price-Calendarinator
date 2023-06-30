import sqlite3

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
		""" returns true if the price is lower than a previously existing price
		"""
		self.cursor.execute('''
			SELECT price FROM PriceData WHERE observeID = ? AND datetime = ?
			''', (observe_id, datetime))

		result = self.cursor.fetchone()

		if result is not None:
			# An old value exists
			old_price = result[0]
			print(f"{datetime} {result} {old_price} {price}")
			if old_price > price:
				return True, old_price
			else:
				return False, None
		else:
			# Insert the new row
			self.cursor.execute('''
				INSERT INTO PriceData (observeID, datetime, price)
				VALUES (?, ?, ?)
			''', (observe_id, datetime, price))

			self.connection.commit()
			return False, None