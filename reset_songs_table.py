import sqlite3

conn = sqlite3.connect('songs.db')
c = conn.cursor()
c.execute('DELETE FROM songs')
conn.commit()
conn.close()
print('All songs deleted from the database.')
