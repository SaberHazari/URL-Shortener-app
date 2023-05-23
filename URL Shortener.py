from flask import Flask, render_template, request, redirect
from pyshorteners import Shortener
import sqlite3

app = Flask(__name__)
shortener = Shortener()

# Create a connection to the SQLite database
conn = sqlite3.connect('urls.db')
cursor = conn.cursor()

# Create a table to store URLs
cursor.execute('''CREATE TABLE IF NOT EXISTS urls
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, original_url TEXT, short_url TEXT)''')
conn.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['url']

    # Check if the URL already exists in the database
    cursor.execute("SELECT short_url FROM urls WHERE original_url=?", (original_url,))
    result = cursor.fetchone()

    if result is None:
        # Generate a short URL using the pyshorteners library
        short_url = shortener.tinyurl.short(original_url)

        # Insert the original URL and short URL into the database
        cursor.execute("INSERT INTO urls (original_url, short_url) VALUES (?, ?)", (original_url, short_url))
        conn.commit()
    else:
        short_url = result[0]

    return render_template('result.html', short_url=short_url)


@app.route('/<string:short_url>')
def redirect_url(short_url):
    # Retrieve the original URL from the database
    cursor.execute("SELECT original_url FROM urls WHERE short_url=?", (short_url,))
    result = cursor.fetchone()

    if result is not None:
        original_url = result[0]
        return redirect(original_url)
    else:
        return "URL not found!"


if __name__ == '__main__':
    app.run(debug=True)
