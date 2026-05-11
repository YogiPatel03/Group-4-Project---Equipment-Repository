DELIMITER $$

CREATE PROCEDURE checkout_item (
    IN p_user_id INT,
    IN p_equipment_id INT,
    IN p_due_date DATE
)
BEGIN
    DECLARE item_status VARCHAR(20);

    -- Get current availability
    SELECT availability_status
    INTO item_status
    FROM Equipment
    WHERE equipment_id = p_equipment_id;

    -- Check if item is available
    IF item_status != 'available' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Item is not available for checkout';
    ELSE
        -- Insert checkout record
        INSERT INTO Checkout_Records (
            user_id,
            equipment_id,
            checkout_date,
            due_date,
            checkout_status
        )
        VALUES (
            p_user_id,
            p_equipment_id,
            CURRENT_DATE,
            p_due_date,
            'checked_out'
        );

        -- Update equipment status
        UPDATE Equipment
        SET availability_status = 'checked_out'
        WHERE equipment_id = p_equipment_id;
    END IF;

END$$

DELIMITER ;
