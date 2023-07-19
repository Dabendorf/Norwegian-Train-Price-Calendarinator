#!/bin/bash

# Set the path to your SQLite database
database="../data/ObservedPrices.db"

# Execute SQLite commands
sqlite3 "$database" <<EOF
INSERT INTO ToObserve (station_from, station_to, date_observe_start, date_observe_end, observe_until)
			VALUES ("Bergen", "Oslo S", "2023-07-24", "2023-07-26", "2023-08-30");
INSERT INTO ToObserve (station_from, station_to, date_observe_start, date_observe_end, observe_until)
			VALUES ("Stavanger", "Oslo S", "2023-08-06", "2023-08-10", "2023-08-30");
INSERT INTO ToObserve (station_from, station_to, date_observe_start, date_observe_end, observe_until)
			VALUES ("Bergen", "Oslo S", "2023-08-06", "2023-08-10", "2023-08-30");
EOF



