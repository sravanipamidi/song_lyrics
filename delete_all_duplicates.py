import sqlite3

conn = sqlite3.connect('songs.db')
c = conn.cursor()

# Delete all but one entry for each unique (filename, title) pair
c.execute('''
DELETE FROM songs
WHERE id NOT IN (
    SELECT MIN(id) FROM songs GROUP BY filename, title
)
''')

conn.commit()
conn.close()
print('All duplicate songs (by filename and title) deleted!')
