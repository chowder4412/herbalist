import sqlite3

conn = sqlite3.connect('clinical_memory.db')
c = conn.cursor()
c.execute('DELETE FROM episodic_cases;')
conn.commit()
print("Successfully wiped all legacy dummy cases from episodic_cases DB table.")
conn.close()
