-- init_db.sql

-- Stvaranje tablice za logiranje temperature kada se ventilator upali
CREATE TABLE IF NOT EXISTS VentilatorLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum TEXT NOT NULL,
    vrijeme TEXT NOT NULL,
    temperatura REAL NOT NULL
);