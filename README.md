# Group-4-Project---Equipment-Repository

A School Inventory Checkout Management System. Desktop app that helps elementary schools track shared equipment like laptops, tablets, cameras, and lab devices. The app helps administrators manage school equipment and lets students check out and return items.

## How to Run

Follow these steps in order:

### 1. In MySQL Workbench, run:

```sql
school_inventory.sql
Stored_Procedure.sql
sample_data.sql
```

### 2. In the VS Code terminal, run:

```bash
export MYSQL_PASSWORD="your_mysql_password"
python -m app.login
```

### If mysql-connector is missing, run:

```bash
pip install mysql-connector-python
```

## Sample Logins

Admin:

```text
Email: admin@uwm.edu
Password: password123
```

Student:

```text
Email: student@uwm.edu
Password: password123
```
