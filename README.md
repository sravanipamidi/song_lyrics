# GanaZone — Telugu Songs, Lyrics & Playlists

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3-black)](https://flask.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/javascript-%23F7DF1E.svg?logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![SQL](https://img.shields.io/badge/sql-%23447A8A.svg?logo=mysql&logoColor=white)](https://en.wikipedia.org/wiki/SQL)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A Flask-based web app for browsing, playing, and organizing Telugu songs with lyrics, playlists, favourites, and user authentication.

## Project Overview

GanaZone provides a modern music experience for Telugu song lovers. Users can log in, search songs, save favourites, create playlists, and read lyrics while enjoying a responsive UI with light/dark themes.

## Key Features

- User authentication with login/register support
- Search songs by title or artist
- Play songs directly in the browser
- Save favourites and create custom playlists
- Read lyrics for songs
- Dark mode and responsive design
- Beautiful modern UI with adaptive branding

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sravanipamidi/song_lyrics.git
   cd song_lyrics
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running Locally

1. Make sure your song files are stored in `static/audio/`.
2. Start the Flask app:
   ```bash
   python app.py
   ```
3. Open your browser at:
   ```
   http://127.0.0.1:5000/
   ```

## Notes

- Only add songs that are copyright-free or properly licensed for sharing.
- The app uses a local SQLite database and static assets in `templates/` and `static/`.

## Contributing

Contributions are welcome! You can improve the app by adding features like:

- lyrics sync / karaoke mode
- playlists sharing
- song recommendation system
- artist and album pages

## License

This project is released under the MIT License. See `LICENSE` for details.
