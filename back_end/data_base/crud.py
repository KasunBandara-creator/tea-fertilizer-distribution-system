# back_end/data_base/crud.py
try:
    from back_end.data_base.database import create_connection
except ModuleNotFoundError:
    from database import create_connection

from mysql.connector import Error


def create_tables():
    """පද්ධතියට අවශ්‍ය වගු (Tables) නිර්මාණය කිරීම"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # 1. Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone_number VARCHAR(15) NOT NULL,
                    address TEXT NOT NULL,
                    role ENUM('farmer', 'store_manager', 'factory_manager') NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Fertilizers Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fertilizers (
                    fertilizer_id INT AUTO_INCREMENT PRIMARY KEY,
                    fertilizer_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    quantity_kg DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                    price_per_kg DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # 3. Fertilizer Requests Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fertilizer_requests (
                    request_id INT AUTO_INCREMENT PRIMARY KEY,
                    farmer_id INT NOT NULL,
                    fertilizer_id INT NOT NULL,
                    requested_qty_kg DECIMAL(10, 2) NOT NULL,
                    status ENUM('pending', 'approved', 'rejected', 'distributed') DEFAULT 'pending',
                    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (farmer_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    FOREIGN KEY (fertilizer_id) REFERENCES fertilizers(fertilizer_id) ON DELETE CASCADE
                )
            """)

            connection.commit()
            print("All tables created successfully!")
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            cursor.close()
            connection.close()


def add_user(full_name, email, phone_number, address, role, password):
    """නව පරිශීලකයෙකු users වගුවට ඇතුළත් කිරීම"""
    connection = create_connection()
    if not connection:
        return False, "Database connection failed"
    cursor = connection.cursor()
    query = """
        INSERT INTO users (full_name, email, phone_number, address, role, password)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (full_name, email, phone_number, address, role, password))
        connection.commit()
        return True, f"User '{full_name}' added successfully!"
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        connection.close()


def add_fertilizer(fertilizer_name, description, quantity_kg, price_per_kg):
    """නව පොහොර වර්ගයක් fertilizers වගුවට ඇතුළත් කිරීම"""
    connection = create_connection()
    if not connection:
        return False, "Database connection failed"
    cursor = connection.cursor()
    query = """
        INSERT INTO fertilizers (fertilizer_name, description, quantity_kg, price_per_kg)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (fertilizer_name, description, quantity_kg, price_per_kg))
        connection.commit()
        return True, f"Fertilizer '{fertilizer_name}' added successfully!"
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        connection.close()


def get_fertilizers():
    """සියලුම පොහොර වර්ග සහ තොග ලබා ගැනීම"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM fertilizers")
            return cursor.fetchall()
        except Error as e:
            print(f"Failed to fetch fertilizers: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []


def create_fertilizer_request(farmer_id, fertilizer_id, requested_qty_kg):
    """ගොවියෙකුගේ පොහොර ඉල්ලීමක් ඇතුළත් කිරීම (validation සමඟ)"""
    connection = create_connection()
    if not connection:
        return False, "Database connection failed"
    cursor = connection.cursor()
    query = """
        INSERT INTO fertilizer_requests (farmer_id, fertilizer_id, requested_qty_kg)
        VALUES (%s, %s, %s)
    """
    try:
        cursor.execute(query, (farmer_id, fertilizer_id, requested_qty_kg))
        connection.commit()
        return True, f"Fertilizer request submitted successfully for farmer_id={farmer_id}!"
    except Error as e:
        return False, f"Invalid Farmer ID or Fertilizer ID: {e.msg}"
    finally:
        cursor.close()
        connection.close()


def get_all_requests():
    """සියලුම පොහොර ඉල්ලීම් ලබා ගැනීම"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                r.request_id,
                r.farmer_id,
                u.full_name AS farmer_name,
                r.fertilizer_id,
                f.fertilizer_name,
                r.requested_qty_kg,
                r.status,
                r.request_date
            FROM fertilizer_requests r
            JOIN users u ON r.farmer_id = u.user_id
            JOIN fertilizers f ON r.fertilizer_id = f.fertilizer_id
            ORDER BY r.request_date DESC
        """
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Failed to fetch requests: {e}")
            return []
        finally:
            cursor.close()
            connection.close()
    return []


def update_request_status(request_id, new_status):
    """ඉල්ලීමක status එක යාවත්කාලීන කිරීම සහ Approve කළ විට තොගය අඩු කිරීම"""
    connection = create_connection()
    if not connection:
        return False, "Database connection failed"
    cursor = connection.cursor(dictionary=True)
    try:
        # 1. දැනට පවතින request එකේ විස්තර ලබා ගැනීම
        cursor.execute("SELECT * FROM fertilizer_requests WHERE request_id = %s", (request_id,))
        req = cursor.fetchone()
        if not req:
            return False, f"Request #{request_id} not found."

        old_status = req['status']
        fertilizer_id = req['fertilizer_id']
        requested_qty = float(req['requested_qty_kg'])

        # 2. 'pending' එකක් 'approved' කරන විට පමණක් තොගය පරීක්ෂා කර අඩු කිරීම
        if new_status == 'approved' and old_status != 'approved':
            cursor.execute("SELECT quantity_kg FROM fertilizers WHERE fertilizer_id = %s", (fertilizer_id,))
            fert = cursor.fetchone()
            if not fert:
                return False, "Fertilizer not found."

            current_stock = float(fert['quantity_kg'])
            if current_stock < requested_qty:
                return False, f"Insufficient stock! Available: {current_stock} kg, Requested: {requested_qty} kg."

            # තොගය අඩු කිරීම
            cursor.execute(
                "UPDATE fertilizers SET quantity_kg = quantity_kg - %s WHERE fertilizer_id = %s",
                (requested_qty, fertilizer_id)
            )

        # 3. Status එක යාවත්කාලීන කිරීම
        cursor.execute(
            "UPDATE fertilizer_requests SET status = %s WHERE request_id = %s",
            (new_status, request_id)
        )
        connection.commit()
        return True, f"Request #{request_id} status updated to '{new_status}'!"
    except Error as e:
        connection.rollback()
        return False, str(e)
    finally:
        cursor.close()
        connection.close()


def update_fertilizer_stock(fertilizer_id, quantity_change_kg):
    """පොහොර තොගය අතින් වැඩි කිරීමට (+) හෝ අඩු කිරීමට (-)"""
    connection = create_connection()
    if not connection:
        return False, "Database connection failed"
    cursor = connection.cursor()
    query = """
        UPDATE fertilizers
        SET quantity_kg = quantity_kg + %s
        WHERE fertilizer_id = %s AND (quantity_kg + %s) >= 0
    """
    try:
        cursor.execute(query, (quantity_change_kg, fertilizer_id, quantity_change_kg))
        connection.commit()
        if cursor.rowcount > 0:
            return True, f"Fertilizer #{fertilizer_id} stock updated by {quantity_change_kg} kg!"
        else:
            return False, "Fertilizer not found or stock cannot be negative."
    except Error as e:
        return False, str(e)
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_tables()