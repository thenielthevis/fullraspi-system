-- SQLite

-- CREATE TABLE IF NOT EXISTS users (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     uid TEXT NOT NULL UNIQUE,
--     credit INTEGER NOT NULL DEFAULT 0,
--     points INTEGER NOT NULL DEFAULT 0,
--     is_admin INTEGER NOT NULL DEFAULT 0
-- );

INSERT INTO users (name, uid, credit, points, is_admin) VALUES
('Juan Dela Cruz', 'RFID001', 100, 50, 0),
('Maria Santos', 'RFID002', 200, 120, 0),
('Pedro Reyes', 'RFID003', 150, 80, 0),
('Ana Lopez', 'RFID004', 300, 200, 0),
('Jose Rizal', 'RFID005', 50, 30, 0),
('Liza Soberano', 'RFID006', 400, 250, 0),
('Mark Bautista', 'RFID007', 120, 60, 0),
('Karla Estrada', 'RFID008', 180, 90, 0),
('Enrique Gil', 'RFID009', 220, 110, 0),
('Admin User', 'ADMIN_UID', 1000, 999, 1);