import sqlite3

conn = sqlite3.connect('songs.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM songs')
count = c.fetchone()[0]
conn.close()
print(f'Total songs in database: {count}')
