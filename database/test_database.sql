-- =============================================================
-- School Inventory Checkout Management System
-- Database Functionality Tests
-- Group 4 | Tester: Jack Tornio
-- =============================================================

USE school_inventory;

-- =============================================================
-- SECTION 1: TABLE STRUCTURE VERIFICATION
-- =============================================================

SELECT '=== SECTION 1: TABLE STRUCTURE VERIFICATION ===' AS test_section;

-- 1.1 Verify all three tables exist
SELECT 'TEST 1.1: All tables exist' AS test_name;
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'school_inventory'
  AND table_name IN ('Users', 'Equipment', 'Checkout_Records')
ORDER BY table_name;
-- EXPECTED: 3 rows — Checkout_Records, Equipment, Users

-- 1.2 Verify Users columns and types
SELECT 'TEST 1.2: Users table structure' AS test_name;
SELECT column_name, column_type, is_nullable, column_default, extra
FROM information_schema.columns
WHERE table_schema = 'school_inventory' AND table_name = 'Users'
ORDER BY ordinal_position;

-- 1.3 Verify Equipment columns and types
SELECT 'TEST 1.3: Equipment table structure' AS test_name;
SELECT column_name, column_type, is_nullable, column_default, extra
FROM information_schema.columns
WHERE table_schema = 'school_inventory' AND table_name = 'Equipment'
ORDER BY ordinal_position;

-- 1.4 Verify Checkout_Records columns and types
SELECT 'TEST 1.4: Checkout_Records table structure' AS test_name;
SELECT column_name, column_type, is_nullable, column_default, extra
FROM information_schema.columns
WHERE table_schema = 'school_inventory' AND table_name = 'Checkout_Records'
ORDER BY ordinal_position;

-- =============================================================
-- SECTION 2: PRIMARY KEY & AUTO_INCREMENT TESTS
-- =============================================================

SELECT '=== SECTION 2: PRIMARY KEY & AUTO_INCREMENT ===' AS test_section;

-- 2.1 Verify primary keys exist on all tables
SELECT 'TEST 2.1: Primary keys exist on all tables' AS test_name;
SELECT table_name, column_name, constraint_name
FROM information_schema.key_column_usage
WHERE table_schema = 'school_inventory'
  AND constraint_name = 'PRIMARY'
ORDER BY table_name;
-- EXPECTED: 3 rows — one PK per table

-- 2.2 Verify auto_increment on PKs
SELECT 'TEST 2.2: AUTO_INCREMENT on primary keys' AS test_name;
SELECT table_name, column_name, extra
FROM information_schema.columns
WHERE table_schema = 'school_inventory'
  AND extra = 'auto_increment';
-- EXPECTED: 3 rows — user_id, equipment_id, checkout_id

-- =============================================================
-- SECTION 3: UNIQUE CONSTRAINT TESTS
-- =============================================================

SELECT '=== SECTION 3: UNIQUE CONSTRAINTS ===' AS test_section;

-- 3.1 Verify unique indexes exist
SELECT 'TEST 3.1: Unique indexes exist' AS test_name;
SELECT table_name, index_name, column_name
FROM information_schema.statistics
WHERE table_schema = 'school_inventory'
  AND non_unique = 0
  AND index_name != 'PRIMARY'
ORDER BY table_name;
-- EXPECTED: email_UNIQUE on Users, serial_number_UNIQUE on Equipment

-- 3.2 Test email uniqueness — insert valid user first
SELECT 'TEST 3.2: Email uniqueness constraint' AS test_name;
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES ('Alice', 'Smith', 'alice@school.edu', 'hashedpw1', 'student', 'active');

-- This should FAIL with a duplicate key error
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES ('Bob', 'Jones', 'alice@school.edu', 'hashedpw2', 'student', 'active');
-- EXPECTED: Error 1062 — Duplicate entry for key 'email_UNIQUE'

-- 3.3 Test serial_number uniqueness
SELECT 'TEST 3.3: Serial number uniqueness constraint' AS test_name;
INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status)
VALUES ('Laptop A', 'laptop', 'SN-001', 'good', 'available');

INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status)
VALUES ('Laptop B', 'laptop', 'SN-001', 'fair', 'available');
-- EXPECTED: Error 1062 — Duplicate entry for key 'serial_number_UNIQUE'

-- =============================================================
-- SECTION 4: CHECK CONSTRAINT TESTS
-- =============================================================

SELECT '=== SECTION 4: CHECK CONSTRAINTS ===' AS test_section;

-- 4.1 Invalid role value
SELECT 'TEST 4.1: Users role CHECK constraint (invalid value)' AS test_name;
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES ('Bad', 'Role', 'badrole@school.edu', 'hash', 'teacher', 'active');
-- EXPECTED: Error 3819 — Check constraint violated (role must be admin or student)

-- 4.2 Invalid status value
SELECT 'TEST 4.2: Users status CHECK constraint (invalid value)' AS test_name;
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES ('Bad', 'Status', 'badstatus@school.edu', 'hash', 'student', 'suspended');
-- EXPECTED: Error 3819 — Check constraint violated (status must be active or inactive)

-- 4.3 Invalid condition_status on Equipment
SELECT 'TEST 4.3: Equipment condition_status CHECK constraint' AS test_name;
INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status)
VALUES ('Tablet', 'tablet', 'SN-BAD1', 'broken', 'available');
-- EXPECTED: Error 3819 — Check constraint violated (must be good/fair/damaged)

-- 4.4 Invalid availability_status on Equipment
SELECT 'TEST 4.4: Equipment availability_status CHECK constraint' AS test_name;
INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status)
VALUES ('Tablet', 'tablet', 'SN-BAD2', 'good', 'lost');
-- EXPECTED: Error 3819 — Check constraint violated (must be available/checked_out/maintenance)

-- 4.5 Invalid checkout_status on Checkout_Records
SELECT 'TEST 4.5: Checkout_Records checkout_status CHECK constraint' AS test_name;
-- Need valid user and equipment first
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES ('Test', 'User', 'testuser@school.edu', 'hash', 'student', 'active');
INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status)
VALUES ('Camera', 'camera', 'SN-CAM01', 'good', 'available');

INSERT INTO Checkout_Records (user_id, equipment_id, checkout_date, due_date, checkout_status)
VALUES (
  (SELECT user_id FROM Users WHERE email = 'testuser@school.edu'),
  (SELECT equipment_id FROM Equipment WHERE serial_number = 'SN-CAM01'),
  NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), 'pending'
);
-- EXPECTED: Error 3819 — Check constraint violated (must be checked_out/returned/overdue)

-- 4.6 due_date must be >= checkout_date
SELECT 'TEST 4.6: Checkout_Records due_date >= checkout_date CHECK constraint' AS test_name;
INSERT INTO Checkout_Records (user_id, equipment_id, checkout_date, due_date, checkout_status)
VALUES (
  (SELECT user_id FROM Users WHERE email = 'testuser@school.edu'),
  (SELECT equipment_id FROM Equipment WHERE serial_number = 'SN-CAM01'),
  NOW(), DATE_SUB(NOW(), INTERVAL 1 DAY), 'checked_out'
);
-- EXPECTED: Error 3819 — Check constraint violated (due_date must be >= checkout_date)

-- =============================================================
-- SECTION 5: NOT NULL CONSTRAINT TESTS
-- =============================================================

SELECT '=== SECTION 5: NOT NULL CONSTRAINTS ===' AS test_section;

-- 5.1 Users — missing required field
SELECT 'TEST 5.1: Users NOT NULL on first_name' AS test_name;
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES (NULL, 'Doe', 'nulltest@school.edu', 'hash', 'student', 'active');
-- EXPECTED: Error 1048 — Column 'first_name' cannot be null

-- 5.2 Equipment — missing required field
SELECT 'TEST 5.2: Equipment NOT NULL on item_name' AS test_name;
INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status)
VALUES (NULL, 'laptop', 'SN-NULL1', 'good', 'available');
-- EXPECTED: Error 1048 — Column 'item_name' cannot be null

-- 5.3 Checkout_Records — missing required field
SELECT 'TEST 5.3: Checkout_Records NOT NULL on checkout_date' AS test_name;
INSERT INTO Checkout_Records (user_id, equipment_id, checkout_date, due_date, checkout_status)
VALUES (1, 1, NULL, DATE_ADD(NOW(), INTERVAL 7 DAY), 'checked_out');
-- EXPECTED: Error 1048 — Column 'checkout_date' cannot be null

-- =============================================================
-- SECTION 6: FOREIGN KEY CONSTRAINT TESTS
-- =============================================================

SELECT '=== SECTION 6: FOREIGN KEY CONSTRAINTS ===' AS test_section;

-- 6.1 Checkout with non-existent user_id
SELECT 'TEST 6.1: FK — user_id must reference valid Users row' AS test_name;
INSERT INTO Checkout_Records (user_id, equipment_id, checkout_date, due_date, checkout_status)
VALUES (99999, 1, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), 'checked_out');
-- EXPECTED: Error 1452 — Cannot add or update a child row (FK constraint fails)

-- 6.2 Checkout with non-existent equipment_id
SELECT 'TEST 6.2: FK — equipment_id must reference valid Equipment row' AS test_name;
INSERT INTO Checkout_Records (user_id, equipment_id, checkout_date, due_date, checkout_status)
VALUES (1, 99999, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), 'checked_out');
-- EXPECTED: Error 1452 — Cannot add or update a child row (FK constraint fails)

-- 6.3 Delete a user who has a checkout record (should be blocked)
SELECT 'TEST 6.3: FK ON DELETE RESTRICT — cannot delete user with active checkout' AS test_name;
-- First insert a clean checkout
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES ('Delete', 'Test', 'deletetest@school.edu', 'hash', 'student', 'active');
INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status)
VALUES ('Laptop X', 'laptop', 'SN-DEL01', 'good', 'available');
INSERT INTO Checkout_Records (user_id, equipment_id, checkout_date, due_date, checkout_status)
VALUES (
  (SELECT user_id FROM Users WHERE email = 'deletetest@school.edu'),
  (SELECT equipment_id FROM Equipment WHERE serial_number = 'SN-DEL01'),
  NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), 'checked_out'
);
DELETE FROM Users WHERE email = 'deletetest@school.edu';
-- EXPECTED: Error 1451 — Cannot delete parent row (FK ON DELETE RESTRICT)

-- 6.4 Update a user_id (cascade should propagate to Checkout_Records)
SELECT 'TEST 6.4: FK ON UPDATE CASCADE — user_id update propagates to Checkout_Records' AS test_name;
-- (Informational — cascades are hard to observe without SELECT before/after)
-- Run manually if needed: update user_id and verify checkout record reflects the new id

-- =============================================================
-- SECTION 7: VALID DATA INSERTION TESTS
-- =============================================================

SELECT '=== SECTION 7: VALID DATA INSERTION ===' AS test_section;

-- Clean slate for valid tests
DELETE FROM Checkout_Records;
DELETE FROM Equipment;
DELETE FROM Users;

-- 7.1 Insert valid admin user
SELECT 'TEST 7.1: Insert valid admin user' AS test_name;
INSERT INTO Users (first_name, last_name, email, password_hash, role, phone, status)
VALUES ('Jane', 'Admin', 'jane.admin@school.edu', 'securehash1', 'admin', '555-1000', 'active');
SELECT * FROM Users WHERE email = 'jane.admin@school.edu';
-- EXPECTED: 1 row, role = admin, status = active

-- 7.2 Insert valid student user
SELECT 'TEST 7.2: Insert valid student user' AS test_name;
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES ('John', 'Student', 'john.student@school.edu', 'securehash2', 'student', 'active');
SELECT * FROM Users WHERE email = 'john.student@school.edu';
-- EXPECTED: 1 row, role = student

-- 7.3 Insert valid equipment items
SELECT 'TEST 7.3: Insert valid equipment' AS test_name;
INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status, location)
VALUES
  ('Dell Laptop', 'laptop', 'SN-LAP001', 'good', 'available', 'Room 101'),
  ('iPad Pro', 'tablet', 'SN-TAB001', 'fair', 'available', 'Room 102'),
  ('Canon Camera', 'camera', 'SN-CAM001', 'good', 'maintenance', 'Storage'),
  ('Chromebook', 'laptop', 'SN-LAP002', 'damaged', 'maintenance', 'Repair Shop');
SELECT * FROM Equipment;
-- EXPECTED: 4 rows with correct statuses

-- 7.4 Insert valid checkout record
SELECT 'TEST 7.4: Insert valid checkout record' AS test_name;
INSERT INTO Checkout_Records (user_id, equipment_id, checkout_date, due_date, checkout_status)
VALUES (
  (SELECT user_id FROM Users WHERE email = 'john.student@school.edu'),
  (SELECT equipment_id FROM Equipment WHERE serial_number = 'SN-LAP001'),
  NOW(),
  DATE_ADD(NOW(), INTERVAL 7 DAY),
  'checked_out'
);
SELECT * FROM Checkout_Records;
-- EXPECTED: 1 row with checkout_status = checked_out

-- 7.5 Simulate a return (update return_date and status)
SELECT 'TEST 7.5: Simulate item return' AS test_name;
UPDATE Checkout_Records
SET return_date = NOW(), checkout_status = 'returned'
WHERE checkout_id = (SELECT checkout_id FROM (SELECT checkout_id FROM Checkout_Records LIMIT 1) AS tmp);
SELECT checkout_id, checkout_status, return_date FROM Checkout_Records;
-- EXPECTED: checkout_status = returned, return_date is populated

-- 7.6 NULL optional fields (phone, location, return_date) are allowed
SELECT 'TEST 7.6: NULL allowed on optional fields' AS test_name;
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES ('No', 'Phone', 'nophone@school.edu', 'hash', 'student', 'active');
INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status)
VALUES ('Unlisted Item', 'other', 'SN-NOLOC', 'good', 'available');
SELECT user_id, phone FROM Users WHERE email = 'nophone@school.edu';
SELECT equipment_id, location FROM Equipment WHERE serial_number = 'SN-NOLOC';
-- EXPECTED: phone = NULL, location = NULL — no errors

-- =============================================================
-- SECTION 8: INDEX VERIFICATION
-- =============================================================

SELECT '=== SECTION 8: INDEX VERIFICATION ===' AS test_section;

SELECT 'TEST 8.1: All indexes on Checkout_Records' AS test_name;
SHOW INDEX FROM Checkout_Records;
-- EXPECTED: PRIMARY, fk_checkout_user_idx, fk_checkout_equipment_idx

SELECT 'TEST 8.2: All indexes on Users' AS test_name;
SHOW INDEX FROM Users;
-- EXPECTED: PRIMARY, email_UNIQUE

SELECT 'TEST 8.3: All indexes on Equipment' AS test_name;
SHOW INDEX FROM Equipment;
-- EXPECTED: PRIMARY, serial_number_UNIQUE

-- =============================================================
-- SECTION 9: QUERY / RELATIONSHIP TESTS
-- =============================================================

SELECT '=== SECTION 9: QUERY & RELATIONSHIP TESTS ===' AS test_section;

-- 9.1 Join — all active checkouts with user and equipment info
SELECT 'TEST 9.1: JOIN — active checkouts with user and equipment details' AS test_name;
SELECT
  cr.checkout_id,
  CONCAT(u.first_name, ' ', u.last_name) AS student_name,
  u.email,
  e.item_name,
  e.serial_number,
  cr.checkout_date,
  cr.due_date,
  cr.checkout_status
FROM Checkout_Records cr
JOIN Users u ON cr.user_id = u.user_id
JOIN Equipment e ON cr.equipment_id = e.equipment_id
WHERE cr.checkout_status = 'checked_out';

-- 9.2 All available equipment
SELECT 'TEST 9.2: Query — all available equipment' AS test_name;
SELECT equipment_id, item_name, category, serial_number, location
FROM Equipment
WHERE availability_status = 'available';

-- 9.3 Overdue records (due_date passed and not returned)
SELECT 'TEST 9.3: Query — overdue checkouts' AS test_name;
SELECT
  cr.checkout_id,
  CONCAT(u.first_name, ' ', u.last_name) AS student_name,
  e.item_name,
  cr.due_date
FROM Checkout_Records cr
JOIN Users u ON cr.user_id = u.user_id
JOIN Equipment e ON cr.equipment_id = e.equipment_id
WHERE cr.due_date < NOW() AND cr.checkout_status != 'returned';

-- 9.4 Count checkouts per student
SELECT 'TEST 9.4: Query — checkout count per student' AS test_name;
SELECT
  CONCAT(u.first_name, ' ', u.last_name) AS student_name,
  COUNT(cr.checkout_id) AS total_checkouts
FROM Users u
LEFT JOIN Checkout_Records cr ON u.user_id = cr.user_id
WHERE u.role = 'student'
GROUP BY u.user_id;

-- 9.5 Equipment never checked out
SELECT 'TEST 9.5: Query — equipment with no checkout history' AS test_name;
SELECT e.equipment_id, e.item_name, e.serial_number
FROM Equipment e
LEFT JOIN Checkout_Records cr ON e.equipment_id = cr.equipment_id
WHERE cr.checkout_id IS NULL;

-- =============================================================
-- SECTION 10: EDGE CASE TESTS
-- =============================================================

SELECT '=== SECTION 10: EDGE CASES ===' AS test_section;

-- 10.1 Inactive user can still have a checkout record (no business rule blocks it at DB level)
SELECT 'TEST 10.1: Inactive user can be referenced in Checkout_Records (DB level only)' AS test_name;
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES ('Inactive', 'User', 'inactive@school.edu', 'hash', 'student', 'inactive');
INSERT INTO Equipment (item_name, category, serial_number, condition_status, availability_status)
VALUES ('Old Tablet', 'tablet', 'SN-OLD01', 'fair', 'available');
INSERT INTO Checkout_Records (user_id, equipment_id, checkout_date, due_date, checkout_status)
VALUES (
  (SELECT user_id FROM Users WHERE email = 'inactive@school.edu'),
  (SELECT equipment_id FROM Equipment WHERE serial_number = 'SN-OLD01'),
  NOW(), DATE_ADD(NOW(), INTERVAL 3 DAY), 'checked_out'
);
-- NOTE: DB allows this — blocking inactive users should be enforced at the application layer

-- 10.2 Same equipment checked out twice simultaneously (DB allows — app layer should prevent)
SELECT 'TEST 10.2: Same equipment in two active checkouts (no DB-level block)' AS test_name;
INSERT INTO Checkout_Records (user_id, equipment_id, checkout_date, due_date, checkout_status)
VALUES (
  (SELECT user_id FROM Users WHERE email = 'john.student@school.edu'),
  (SELECT equipment_id FROM Equipment WHERE serial_number = 'SN-OLD01'),
  NOW(), DATE_ADD(NOW(), INTERVAL 5 DAY), 'checked_out'
);
-- NOTE: This inserts successfully — a trigger should be added to prevent double-booking

-- 10.3 Max-length VARCHAR values
SELECT 'TEST 10.3: Max-length field values accepted' AS test_name;
INSERT INTO Users (first_name, last_name, email, password_hash, role, status)
VALUES (
  REPEAT('A', 50),
  REPEAT('B', 50),
  CONCAT(REPEAT('c', 90), '@x.edu'),
  REPEAT('h', 255),
  'admin',
  'active'
);
SELECT first_name, last_name FROM Users ORDER BY user_id DESC LIMIT 1;
-- EXPECTED: Row inserts successfully at max length

-- =============================================================
-- TEST SUMMARY
-- =============================================================

SELECT '=== TEST SUMMARY ===' AS test_section;
SELECT
  'Run each section above and verify EXPECTED results match actual output.' AS instructions,
  'Sections 3-6 expect specific MySQL errors — those are PASSING if errors match.' AS note1,
  'Sections 7-10 expect successful inserts/selects — errors there mean FAILING.' AS note2;

SELECT COUNT(*) AS total_users FROM Users;
SELECT COUNT(*) AS total_equipment FROM Equipment;
SELECT COUNT(*) AS total_checkouts FROM Checkout_Records;
