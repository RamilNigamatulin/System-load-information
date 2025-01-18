import sqlite3
from main import get_cpu_usage, get_memory_usage, get_disk_usage, create_database, save_to_database, \
    clear_statistics


# Тест для функции get_cpu_usage
def test_get_cpu_usage():
    cpu_usage = get_cpu_usage()
    assert isinstance(cpu_usage, float)
    assert 0 <= cpu_usage <= 100


# Тест для функции get_memory_usage
def test_get_memory_usage():
    memory_usage = get_memory_usage()
    assert isinstance(memory_usage, str)
    assert "ГБ" in memory_usage


# Тест для функции get_disk_usage
def test_get_disk_usage():
    disk_usage = get_disk_usage()
    assert isinstance(disk_usage, str)
    assert "ГБ" in disk_usage


# Тест для функции create_database
def test_create_database():
    create_database()
    conn = sqlite3.connect('system_usage.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usage_data'")
    table_exists = cursor.fetchone()
    conn.close()
    assert table_exists is not None


# Тест для функции save_to_database
def test_save_to_database():
    create_database()
    cpu_usage = 50.0
    memory_usage = "5.00 ГБ / 16.00 ГБ"
    disk_usage = "100.00 ГБ / 500.00 ГБ"
    save_to_database(cpu_usage, memory_usage, disk_usage)

    conn = sqlite3.connect('system_usage.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usage_data")
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) == 1
    assert rows[0][1] == cpu_usage
    assert rows[0][2] == memory_usage
    assert rows[0][3] == disk_usage


# Тест для функции clear_statistics
def test_clear_statistics():
    create_database()
    save_to_database(50.0, "5.00 ГБ / 16.00 ГБ", "100.00 ГБ / 500.00 ГБ")
    clear_statistics()

    conn = sqlite3.connect('system_usage.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usage_data")
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) == 0
