#!/bin/bash

# Set the path to your SQLite database
database="../data/ObservedPrices.db"

# Execute SQLite commands
sqlite3 "$database" <<EOF
SELECT * FROM ToObserve;
EOF