USE school_inventory;

USE school_inventory;

INSERT INTO Users
(first_name, last_name, email, password_hash, role, phone, status)
VALUES
('Admin', 'Test', 'admin@uwm.edu', 'password123', 'admin', '1234567891', 'active'),

('Student', 'Test', 'student@uwm.edu', 'password123', 'student', '5551112222', 'active'),

('Nina', 'Hart', 'nina@uwm.edu', 'password123', 'student', '6754369987', 'active'),

('John', 'Doe', 'john@uwm.edu', 'password123', 'student', '2348763537', 'active'),

('Jen', 'Smith', 'jen@uwm.edu', 'password123', 'student', '8379206653', 'active'),

('Zack', 'Brown', 'zack@uwm.edu', 'password123', 'student', '2938947762', 'active'),

('Jennifer', 'Johnson', 'jennifer@uwm.edu', 'password123', 'admin', '6357842243', 'active');

INSERT INTO Equipment 
(item_name, category, serial_number, condition_status, availability_status, location)
VALUES
('Dell Laptop', 'Laptop', 'DL-1002', 'good', 'available', 'Room 101'),
('Dell Laptop', 'Laptop', 'DL-1003', 'fair', 'available', 'Room 101'),
('Dell Laptop', 'Laptop', 'DL-1004', 'good', 'maintenance', 'Tech Office'),

('iPad', 'Tablet', 'IP-2002', 'good', 'available', 'Room 102'),
('iPad', 'Tablet', 'IP-2003', 'good', 'available', 'Room 102'),
('iPad', 'Tablet', 'IP-2004', 'fair', 'available', 'Room 102'),

('Canon Camera', 'Camera', 'CC-3002', 'good', 'available', 'Media Lab'),
('Canon Camera', 'Camera', 'CC-3003', 'fair', 'available', 'Media Lab'),

('Microscope', 'Lab Equipment', 'MS-4002', 'good', 'available', 'Science Lab'),
('Microscope', 'Lab Equipment', 'MS-4003', 'fair', 'available', 'Science Lab'),

('Projector', 'Classroom Tech', 'PR-5002', 'good', 'available', 'Library'),
('Projector', 'Classroom Tech', 'PR-5003', 'damaged', 'maintenance', 'Library');