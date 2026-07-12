-- ============================================================
-- Wedding Plan Management System — MySQL Schema
-- ============================================================
-- Run this once against an empty database, e.g.:
--   mysql -u root -p < schema.sql
-- (Flask-SQLAlchemy will also auto-create these tables via
--  db.create_all() the first time the app runs, so running this
--  file by hand is optional — it's provided for DBAs who prefer
--  to manage schema separately from the app.)
-- ============================================================

CREATE DATABASE IF NOT EXISTS wedding_planner
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE wedding_planner;

-- ------------------------------------------------------------
-- users: both clients and admins live in one table, distinguished
-- by `role`. Passwords are always stored as Werkzeug hashes,
-- never in plaintext.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(120)        NOT NULL,
    email           VARCHAR(190)        NOT NULL UNIQUE,
    password_hash   VARCHAR(255)        NOT NULL,
    role            ENUM('client', 'admin') NOT NULL DEFAULT 'client',
    created_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- venues: managed by admins, browsed/booked by clients.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS venues (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(150)        NOT NULL,
    location        VARCHAR(190)        NOT NULL,
    description     TEXT,
    capacity        INT                 NOT NULL DEFAULT 0,
    price_per_event DECIMAL(10, 2)      NOT NULL DEFAULT 0.00,
    image_url       VARCHAR(500),
    is_active       TINYINT(1)          NOT NULL DEFAULT 1,
    created_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- appointments: a booking request from a client for a venue.
-- status moves pending -> confirmed / rejected via the admin
-- approval workflow.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS appointments (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT                 NOT NULL,
    venue_id        INT                 NOT NULL,
    event_date      DATE                NOT NULL,
    guest_count     INT,
    notes           TEXT,
    status          ENUM('pending', 'confirmed', 'rejected') NOT NULL DEFAULT 'pending',
    created_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP
                                         ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_appointments_user
        FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
    CONSTRAINT fk_appointments_venue
        FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Helpful indexes for common lookups
CREATE INDEX idx_appointments_user   ON appointments(user_id);
CREATE INDEX idx_appointments_venue  ON appointments(venue_id);
CREATE INDEX idx_appointments_status ON appointments(status);

-- ------------------------------------------------------------
-- Seed data (optional) — a default admin account and a few venues.
-- Default admin password is "AdminPass123" — CHANGE THIS in any
-- real deployment. The hash below matches that password with
-- Werkzeug's default pbkdf2:sha256 method.
-- ------------------------------------------------------------
-- INSERT INTO users (name, email, password_hash, role)
-- VALUES ('Platform Admin', 'admin@weddingplanner.test',
--         'pbkdf2:sha256:600000$REPLACE_WITH_REAL_HASH', 'admin');
--
-- Use seed.py (included in the project) to insert this safely
-- with a properly generated hash instead of pasting one here.

INSERT INTO venues (name, location, description, capacity, price_per_event, image_url) VALUES
('The Ivory Orchard', 'Lusaka, Zambia', 'An open-air garden venue framed by mango trees, ideal for daytime ceremonies and golden-hour photos.', 220, 8500.00, 'https://images.unsplash.com/photo-1519167758481-83f550bb49b3'),
('Willowmere Hall', 'Kabulonga, Lusaka', 'A restored colonial hall with vaulted ceilings and a private courtyard for cocktail hour.', 160, 6200.00, 'https://images.unsplash.com/photo-1519741497674-611481863552'),
('Riverside Pavilion', 'Chilanga, Lusaka', 'A glass-walled pavilion overlooking the river, best suited to evening receptions with string lighting.', 300, 11200.00, 'https://images.unsplash.com/photo-1464366400600-7168b8af9bc3'),
('The Grey Barn', 'Chisamba', 'A converted farm barn with exposed timber beams, popular for rustic and countryside themes.', 180, 5400.00, 'https://images.unsplash.com/photo-1464047736614-af63643285bf');
