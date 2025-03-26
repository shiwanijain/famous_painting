from flask import render_template, request
from app import app, mysql

@app.route('/')
def home():
    artist = request.args.get('artist', '').strip()
    painting = request.args.get('painting', '').strip()

    query = """
        SELECT work.work_id, work.name AS painting_name, artist.full_name AS artist_name
        FROM work
        JOIN artist ON work.artist_id = artist.artist_id
        WHERE 1=1
    """
    params = []

    if artist:
        query += " AND artist.full_name LIKE %s"
        params.append(f"%{artist}%")

    if painting:
        query += " AND work.name LIKE %s"
        params.append(f"%{painting}%")

    cursor = mysql.connection.cursor()
    cursor.execute(query, params)
    works = cursor.fetchall()
    cursor.close()

    return render_template('index.html', works=works)