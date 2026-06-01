import sqlite3

conn = sqlite3.connect('songs.db')
c = conn.cursor()
# Ensure test user exists
c.execute('SELECT id FROM users WHERE username=?', ('testuser',))
user = c.fetchone()
if not user:
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('testuser', 'testpass'))
    conn.commit()
    c.execute('SELECT id FROM users WHERE username=?', ('testuser',))
    user_id = c.fetchone()[0]
else:
    user_id = user[0]
# Ensure test playlist exists
c.execute('SELECT id FROM playlists WHERE user_id=?', (user_id,))
if not c.fetchone():
    c.execute('INSERT INTO playlists (user_id, name) VALUES (?, ?)', (user_id, 'Test Playlist'))
    conn.commit()
print('Test user and playlist ensured.')
conn.close()
