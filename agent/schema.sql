CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(120) NOT NULL,
    price_per_night INTEGER NOT NULL,
    max_guests INTEGER NOT NULL,
    description TEXT,
    amenities TEXT[]
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    listing_id INTEGER REFERENCES listings(id),
    guest_name VARCHAR(120),
    guests INTEGER NOT NULL,
    check_in DATE,
    check_out DATE,
    status VARCHAR(30) DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_message TEXT,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO listings (name, location, price_per_night, max_guests, description, amenities)
VALUES
('Sea View Hotel', 'Cox''s Bazar', 4500, 2, 'Beach-side room with sea view.', ARRAY['WiFi', 'AC', 'Breakfast']),
('Dhaka Comfort Stay', 'Dhaka', 3500, 3, 'Comfortable apartment near Gulshan.', ARRAY['WiFi', 'Kitchen', 'AC']),
('Sylhet Green Resort', 'Sylhet', 5200, 4, 'Resort near tea garden.', ARRAY['Pool', 'WiFi', 'Breakfast']);