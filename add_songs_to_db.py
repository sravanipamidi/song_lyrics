import sqlite3

songs = [
    {
        'title': 'Swatantra Deepaalu',
        'filename': 'స్వతంత్రత దీపాలు.mp3',
        'lyrics_file': 'lyrics_swathantra_deepaalu.txt'
    },
    {
        'title': 'Swasalo Neeve',
        'filename': 'శ్వాసలో నీవే.mp3',
        'lyrics_file': 'lyrics_swasalo_neeve.txt'
    }
]

def read_lyrics(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''

def add_songs():
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    for song in songs:
        lyrics = read_lyrics(song['lyrics_file'])
        c.execute('INSERT INTO songs (title, filename, lyrics) VALUES (?, ?, ?)',
                  (song['title'], song['filename'], lyrics))
    conn.commit()
    conn.close()
    print('Songs added successfully!')

if __name__ == '__main__':
    add_songs()
