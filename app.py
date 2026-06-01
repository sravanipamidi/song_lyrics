import sqlite3
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# User logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully!')
    return redirect(url_for('auth'))

# Auth page (login/register)
@app.route('/', methods=['GET', 'POST'])
def auth():
    if 'user_id' in session:
        return redirect(url_for('home'))
    mode = request.args.get('mode', 'login')
    if request.method == 'POST':
        if 'register' in request.form:
            username = request.form['username']
            password = request.form['password']
            if not username or not password:
                flash('Username and password are required!')
                return redirect(url_for('auth', mode='register'))
            conn = sqlite3.connect('songs.db')
            c = conn.cursor()
            try:
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                flash('Registration successful! Please log in.')
                return redirect(url_for('auth', mode='login'))
            except sqlite3.IntegrityError:
                flash('Username already exists!')
                return redirect(url_for('auth', mode='register'))
            finally:
                conn.close()
        elif 'login' in request.form:
            username = request.form['username']
            password = request.form['password']
            conn = sqlite3.connect('songs.db')
            c = conn.cursor()
            c.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
            user = c.fetchone()
            conn.close()
            if user:
                session['user_id'] = user[0]
                session['username'] = username
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password!')
                return redirect(url_for('auth', mode='login'))

    return render_template('auth.html', mode=mode)

def get_songs_from_db(user_id=None):
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('SELECT id, title, filename, lyrics FROM songs')
    songs = []
    for row in c.fetchall():
        song = {'id': row[0], 'title': row[1], 'filename': row[2], 'lyrics': row[3]}
        if user_id:
            c.execute('SELECT 1 FROM favourites WHERE user_id = ? AND song_id = ?', (user_id, row[0]))
            song['is_favourite'] = c.fetchone() is not None
        else:
            song['is_favourite'] = False
        songs.append(song)
    conn.close()
    return songs



# Home page
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    songs = get_songs_from_db(user_id)
    search = request.args.get('search', '', type=str).strip().lower()
    sort = request.args.get('sort', 'title', type=str)
    order = request.args.get('order', 'asc', type=str)
    if search:
        songs = [s for s in songs if search in s['title'].lower() or search in (s['lyrics'] or '').lower()]
    reverse = (order == 'desc')
    if sort in ['title', 'id']:
        songs = sorted(songs, key=lambda s: s[sort], reverse=reverse)
    # Remove duplicates by song id
    unique = {}
    for song in songs:
        if song['id'] not in unique:
            unique[song['id']] = song
    songs = list(unique.values())
    for song in songs:
        song['comments'] = get_comments(song['id'])
        song['rating'] = get_rating(song['id'])
    # Fetch playlists for dropdown
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM playlists WHERE user_id = ?', (user_id,))
    playlists = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    return render_template('songs.html', songs=songs, search=search, sort=sort, order=order, playlists=playlists)

# Add/remove favourite
@app.route('/favourite/<int:song_id>', methods=['POST'])
def favourite(song_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    action = request.form.get('action')
    next_url = request.form.get('next')
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    if action == 'add':
        c.execute('INSERT OR IGNORE INTO favourites (user_id, song_id) VALUES (?, ?)', (user_id, song_id))
    elif action == 'remove':
        c.execute('DELETE FROM favourites WHERE user_id = ? AND song_id = ?', (user_id, song_id))
    conn.commit()
    conn.close()
    # Redirect to the correct page
    if next_url:
        return redirect(next_url)
    return redirect(url_for('home'))

# List user's favourite songs
@app.route('/favourites')
def favourites():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('''SELECT s.id, s.title, s.filename, s.lyrics FROM songs s
                 JOIN favourites f ON s.id = f.song_id WHERE f.user_id = ?''', (user_id,))
    songs = [
        {'id': row[0], 'title': row[1], 'filename': row[2], 'lyrics': row[3], 'is_favourite': True}
        for row in c.fetchall()
    ]
    # Fetch playlists for dropdown
    c.execute('SELECT id, name FROM playlists WHERE user_id = ?', (user_id,))
    playlists = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    for song in songs:
        song['comments'] = get_comments(song['id'])
        song['rating'] = get_rating(song['id'])
    return render_template('songs.html', songs=songs, search='', sort='title', order='asc', favourites_page=True, playlists=playlists)

@app.route('/comment/<int:song_id>', methods=['POST'])
def comment(song_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    username = session.get('username', 'Anonymous')
    comment = request.form.get('comment', '')
    if comment:
        conn = sqlite3.connect('songs.db')
        c = conn.cursor()
        c.execute('INSERT INTO comments (song_id, username, comment) VALUES (?, ?, ?)', (song_id, username, comment))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

@app.route('/rate/<int:song_id>', methods=['POST'])
def rate(song_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    rating = int(request.form.get('rating', 0))
    username = session.get('username', 'Anonymous')
    if rating >= 1 and rating <= 5:
        conn = sqlite3.connect('songs.db')
        c = conn.cursor()
        c.execute('INSERT INTO ratings (song_id, rating, username) VALUES (?, ?, ?)', (song_id, rating, username))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

def get_comments(song_id):
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('SELECT username, comment, created_at FROM comments WHERE song_id = ? ORDER BY created_at DESC', (song_id,))
    comments = [{'username': row[0], 'comment': row[1], 'created_at': row[2]} for row in c.fetchall()]
    conn.close()
    return comments

def get_rating(song_id):
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('SELECT AVG(rating) FROM ratings WHERE song_id = ?', (song_id,))
    avg = c.fetchone()[0]
    conn.close()
    return round(avg, 2) if avg else None

# --- PLAYLIST MANAGEMENT ---
# List all playlists for the user
@app.route('/playlists')
def playlists():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM playlists WHERE user_id = ?', (user_id,))
    playlists = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    return render_template('playlists.html', playlists=playlists)

# Create a new playlist
@app.route('/playlists/create', methods=['POST'])
def create_playlist():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    name = request.form.get('name', '').strip()
    if name:
        conn = sqlite3.connect('songs.db')
        c = conn.cursor()
        c.execute('INSERT INTO playlists (user_id, name) VALUES (?, ?)', (user_id, name))
        conn.commit()
        conn.close()
    return redirect(url_for('playlists'))

# Delete a playlist
@app.route('/playlists/delete/<int:playlist_id>', methods=['POST'])
def delete_playlist(playlist_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('DELETE FROM playlists WHERE id = ? AND user_id = ?', (playlist_id, user_id))
    c.execute('DELETE FROM playlist_songs WHERE playlist_id = ?', (playlist_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('playlists'))

# Rename a playlist
@app.route('/playlists/rename/<int:playlist_id>', methods=['POST'])
def rename_playlist(playlist_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    new_name = request.form.get('name', '').strip()
    if new_name:
        conn = sqlite3.connect('songs.db')
        c = conn.cursor()
        c.execute('UPDATE playlists SET name = ? WHERE id = ? AND user_id = ?', (new_name, playlist_id, user_id))
        conn.commit()
        conn.close()
    return redirect(url_for('playlists'))

# View songs in a playlist
@app.route('/playlists/<int:playlist_id>')
def view_playlist(playlist_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('SELECT name FROM playlists WHERE id = ? AND user_id = ?', (playlist_id, user_id))
    playlist = c.fetchone()
    if not playlist:
        conn.close()
        return redirect(url_for('playlists'))
    playlist_name = playlist[0]
    c.execute('''SELECT s.id, s.title, s.filename, s.lyrics FROM songs s
                 JOIN playlist_songs ps ON s.id = ps.song_id
                 WHERE ps.playlist_id = ?''', (playlist_id,))
    songs = []
    for row in c.fetchall():
        song = {'id': row[0], 'title': row[1], 'filename': row[2], 'lyrics': row[3]}
        # Set is_favourite for playlist songs
        c.execute('SELECT 1 FROM favourites WHERE user_id = ? AND song_id = ?', (user_id, row[0]))
        song['is_favourite'] = c.fetchone() is not None
        songs.append(song)
    # Fetch playlists for dropdown
    c.execute('SELECT id, name FROM playlists WHERE user_id = ?', (user_id,))
    playlists = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    for song in songs:
        song['comments'] = get_comments(song['id'])
        song['rating'] = get_rating(song['id'])
    return render_template('songs.html', songs=songs, search='', sort='title', order='asc', playlist_page=True, playlist_id=playlist_id, playlist_name=playlist_name, playlists=playlists)

# Add song to playlist
@app.route('/playlists/<int:playlist_id>/add/<int:song_id>', methods=['POST'])
def add_song_to_playlist(playlist_id, song_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    # Check playlist ownership
    c.execute('SELECT 1 FROM playlists WHERE id = ? AND user_id = ?', (playlist_id, user_id))
    if c.fetchone():
        c.execute('INSERT OR IGNORE INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)', (playlist_id, song_id))
        conn.commit()
    conn.close()
    return redirect(url_for('view_playlist', playlist_id=playlist_id))

# Remove song from playlist
@app.route('/playlists/<int:playlist_id>/remove/<int:song_id>', methods=['POST'])
def remove_song_from_playlist(playlist_id, song_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    user_id = session['user_id']
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    # Check playlist ownership
    c.execute('SELECT 1 FROM playlists WHERE id = ? AND user_id = ?', (playlist_id, user_id))
    if c.fetchone():
        c.execute('DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?', (playlist_id, song_id))
        conn.commit()
    conn.close()
    return redirect(url_for('view_playlist', playlist_id=playlist_id))


@app.route('/search')
def search():
    query = request.args.get('q', '')
    ajax = request.args.get('ajax')
    user_id = session.get('user_id')
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    # Search for songs where title or lyrics contains the query (case-insensitive)
    c.execute("SELECT id, title, filename, lyrics FROM songs WHERE LOWER(title) LIKE ? OR LOWER(lyrics) LIKE ?", (f"%{query.lower()}%", f"%{query.lower()}%"))
    results = c.fetchall()
    songs = []
    for row in results:
        song = {'id': row[0], 'title': row[1], 'filename': row[2], 'lyrics': row[3]}
        if user_id:
            c.execute('SELECT 1 FROM favourites WHERE user_id = ? AND song_id = ?', (user_id, row[0]))
            song['is_favourite'] = c.fetchone() is not None
        else:
            song['is_favourite'] = False
        songs.append(song)
    playlists = []
    if user_id:
        c.execute('SELECT id, name FROM playlists WHERE user_id = ?', (user_id,))
        playlists = [{'id': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    if ajax:
        if songs:
            html = ''.join(f'<div style="margin-bottom:18px;"><b>{song["title"]}</b></div>' for song in songs)
        else:
            html = f'<div style="color:#888;">No results found for <b>{query}</b>.</div>'
        return html
    return render_template('search_results.html', query=query, songs=songs, playlists=playlists)

if __name__ == '__main__':
    app.run(debug=True)