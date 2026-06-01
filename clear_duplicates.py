import sqlite3

conn = sqlite3.connect('songs.db')
c = conn.cursor()

# Delete duplicate songs, keeping the one with the lowest id for each filename
c.execute('''
DELETE FROM songs
WHERE id NOT IN (
    SELECT MIN(id) FROM songs GROUP BY filename
)
''')

conn.commit()
conn.close()
print('Duplicates cleared!')
