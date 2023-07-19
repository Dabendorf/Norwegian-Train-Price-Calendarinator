#!/bin/bash

# Set the path to your SQLite database
database="../data/ObservedPrices.db"

# Get input parameters
station_from="$1"
station_to="$2"
date_observe_start="$3"
date_observe_end="$4"
observe_until="$5"

# Execute SQLite commands
sqlite3 "$database" <<EOF
INSERT INTO ToObserve (station_from, station_to, date_observe_start, date_observe_end, observe_until)
			VALUES ("$station_from", "$station_to", "$date_observe_start", "$date_observe_end", "$observe_until");
EOF