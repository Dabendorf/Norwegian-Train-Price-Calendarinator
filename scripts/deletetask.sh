#!/bin/bash

# Set the path to your SQLite database
database="../data/ObservedPrices.db"

id="$1"

# Execute SQLite commands
sqlite3 "$database" <<EOF
DELETE FROM ToObserve WHERE id=$id;
EOF