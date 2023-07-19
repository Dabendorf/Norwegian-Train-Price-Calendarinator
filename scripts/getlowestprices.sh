#!/bin/bash

# Set the path to your SQLite database
database="../data/ObservedPrices.db"

# Execute SQLite commands
sqlite3 "$database" <<EOF
SELECT pd.observeID, toObs.station_from, toObs.station_to, toObs.date_observe_start, toObs.date_observe_end, pd.datetime, pd.MinPrice, pd.TimeObserved
FROM (
  SELECT observeID, MIN(price) AS MinPrice, datetime, TimeObserved
  FROM PriceData
  GROUP BY observeID
) AS pd
JOIN ToObserve AS toObs ON toObs.id = pd.observeID;
EOF
