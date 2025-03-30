from app import app  
from flask import render_template, request
from app import mysql  

@app.route('/')
def index():
    artist_filter = request.args.get('artist')
    style_filter = request.args.get('style')
    museum_filter = request.args.get('museum')
    painting_filter = request.args.get('painting')  # New filter

    cursor = mysql.connection.cursor()

    # Get filter options
    cursor.execute("SELECT DISTINCT full_name FROM artist")
    artist_list = cursor.fetchall()

    cursor.execute("SELECT DISTINCT style FROM work WHERE style IS NOT NULL")
    style_list = cursor.fetchall()

    cursor.execute("""
        SELECT DISTINCT museum.name 
        FROM museum 
        JOIN work ON museum.museum_id = work.museum_id
    """)
    museum_list = cursor.fetchall()

    cursor.execute("SELECT DISTINCT name FROM work")
    painting_list = cursor.fetchall()

    # Base Query (Correctly joins image_link table)
    query = """
        SELECT work.name, artist.full_name, work.style, image_link.url, museum.name
        FROM work
        JOIN artist ON work.artist_id = artist.artist_id
        LEFT JOIN museum ON work.museum_id = museum.museum_id
        LEFT JOIN image_link ON work.work_id = image_link.work_id  
        WHERE 1=1
    """
    values = []

    # Apply Filters
    if artist_filter:
        query += " AND artist.full_name = %s"
        values.append(artist_filter)
    
    if style_filter:
        query += " AND work.style = %s"
        values.append(style_filter)

    if museum_filter:
        query += " AND museum.name = %s"
        values.append(museum_filter)

    if painting_filter:
        query += " AND work.name = %s"
        values.append(painting_filter)

    cursor.execute(query, values)
    paintings = cursor.fetchall()
    cursor.close()

    return render_template('index.html', paintings=paintings, artist_list=artist_list, style_list=style_list, museum_list=museum_list, painting_list=painting_list)

@app.route('/top_5_artists')
def top_5_artists():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT artist.full_name, COUNT(work.work_id) AS num_paintings 
        FROM artist 
        JOIN work ON artist.artist_id = work.artist_id 
        GROUP BY artist.full_name 
        ORDER BY num_paintings DESC 
        LIMIT 5
    """)
    results = cursor.fetchall()
    cursor.close()
    return render_template('results.html', title="Top 5 Artists", headers=["Artist Name", "No. of Paintings"], results=results)

@app.route('/artists_multiple_museums')
def artists_multiple_museums():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT artist.full_name, COUNT(DISTINCT museum.museum_id) AS num_museums
        FROM artist
        JOIN work ON artist.artist_id = work.artist_id
        JOIN museum ON work.museum_id = museum.museum_id
        GROUP BY artist.full_name
        HAVING num_museums > 1
    """)
    results = cursor.fetchall()
    cursor.close()
    return render_template('results.html', title="Artists in Multiple Museums", headers=["Artist Name", "No. of Museums"], results=results)

@app.route('/artists_multiple_styles')
def artists_multiple_styles():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT artist.full_name, COUNT(DISTINCT work.style) AS num_styles
        FROM artist
        JOIN work ON artist.artist_id = work.artist_id
        GROUP BY artist.full_name
        HAVING num_styles > 1
    """)
    results = cursor.fetchall()
    cursor.close()
    return render_template('results.html', title="Artists with Multiple Styles", headers=["Artist Name", "No. of Styles"], results=results)

@app.route('/top_museums')
def top_museums():
    cursor = mysql.connection.cursor()

    query = """
        SELECT museum.name, COUNT(work.work_id) AS painting_count
        FROM museum
        JOIN work ON museum.museum_id = work.museum_id
        GROUP BY museum.museum_id
        ORDER BY painting_count DESC
    """

    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return render_template('results.html', title="Museums with Most Paintings", headers=["Museum Name", "Number of Paintings"], results=results)

@app.route('/city_with_most_museums')
def city_with_most_museums():
    cursor = mysql.connection.cursor()
    
    query = """
        SELECT city, COUNT(museum_id) AS num_museums
        FROM museum
        GROUP BY city
        ORDER BY num_museums DESC
        LIMIT 1;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return render_template('results.html', title="City with Most Museums", headers=["City", "Number of Museums"], results=results)

@app.route('/museums_open_sunday')
def museums_open_sunday():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT museum.name, museum_hours.open, museum_hours.close
        FROM museum
        JOIN museum_hours ON museum.museum_id = museum_hours.museum_id
        WHERE museum_hours.day = 'Sunday'
    """)
    results = cursor.fetchall()
    cursor.close()
    return render_template('results.html', title="Museums Open on Sundays", headers=["Museum Name", "Opening Time", "Closing Time"], results=results)


@app.route('/common_painting_subjects')
def common_painting_subjects():
    cursor = mysql.connection.cursor()
    
    query = """
        SELECT subject.subject, COUNT(work.work_id) AS subject_count
        FROM subject
        JOIN work ON subject.work_id = work.work_id
        GROUP BY subject.subject
        ORDER BY subject_count DESC;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return render_template('results.html', title="Most Common Subjects in Paintings", headers=["Subject", "Count"], results=results)

@app.route('/most_used_style')
def most_used_style():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT work.style, COUNT(work.work_id) AS count
        FROM work
        WHERE work.style IS NOT NULL
        GROUP BY work.style
        ORDER BY count DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    cursor.close()
    
    return render_template('results.html', title="Most Used Painting Style", headers=["Style", "Count"], results=[result])

@app.route('/artists_three_museums')
def artists_three_museums():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT artist.full_name, COUNT(DISTINCT museum.museum_id) AS num_museums
        FROM artist
        JOIN work ON artist.artist_id = work.artist_id
        JOIN museum ON work.museum_id = museum.museum_id
        GROUP BY artist.full_name
        HAVING num_museums >= 3
    """)
    results = cursor.fetchall()
    cursor.close()
    return render_template('results.html', title="Artists with Paintings in at Least Three Museums",
                           headers=["Artist Name", "No. of Museums"], results=results)

@app.route('/most_documented_artist')
def most_documented_artist():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT artist.full_name, COUNT(image_link.url) AS num_images
        FROM artist
        JOIN work ON artist.artist_id = work.artist_id
        JOIN image_link ON work.work_id = image_link.work_id
        GROUP BY artist.full_name
        ORDER BY num_images DESC
        LIMIT 1
    """)
    result = cursor.fetchall()
    cursor.close()
    return render_template('results.html', title="Most Visually Documented Artist",
                           headers=["Artist Name", "No. of Images"], results=result)

@app.route('/top-artists-by-paintings')
def top_artists_by_paintings():
    # Get a cursor from MySQL
    cursor = mysql.connection.cursor()

    # Execute the SQL query to get top artists by paintings count
    cursor.execute("""
        SELECT artist.full_name, COUNT(work.work_id) AS paintings_count
        FROM artist
        JOIN work ON artist.artist_id = work.artist_id
        GROUP BY artist.full_name
        ORDER BY paintings_count DESC
    """)
    
    # Fetch the results
    results = cursor.fetchall()
    
    # Close the cursor
    cursor.close()

    # Prepare the headers and title
    headers = ["Artist Name", "Paintings Count"]
    title = "Top Artists by Paintings"

    # Render the template and pass the necessary data
    return render_template('results.html', title=title, headers=headers, results=results)

@app.route('/paintings_multiple_styles')
def paintings_multiple_styles():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT work.name AS painting_name, GROUP_CONCAT(DISTINCT work.style ORDER BY work.style SEPARATOR ', ') AS styles
        FROM work
        WHERE work.style IS NOT NULL
        GROUP BY work.name
        HAVING COUNT(DISTINCT work.style) > 1
    """)
    results = cursor.fetchall()
    cursor.close()
    return render_template('results.html', title="Paintings with Multiple Styles",
                           headers=["Painting Name", "Styles"], results=results)

@app.route('/canvas_size_count')
def canvas_size_count():
    cursor = mysql.connection.cursor()
    
    # SQL query to get the canvas size count
    query = """
        SELECT c.label, COUNT(w.work_id) AS painting_count 
        FROM work w 
        JOIN canvas_size c ON w.work_id = c.size_id 
        GROUP BY c.label 
        ORDER BY painting_count DESC;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return render_template('results.html', title="Canvas Sizes and Painting Counts", headers=["Canvas Size", "Painting Count"], results=results)


@app.route('/most_exhibited_artist')
def most_exhibited_artist():
    cursor = mysql.connection.cursor()

    # Query to find the most exhibited artist (artist with paintings in the most museums)
    query = """
        SELECT a.full_name, COUNT(DISTINCT m.museum_id) AS num_museums
        FROM artist a
        JOIN work w ON a.artist_id = w.artist_id
        JOIN museum m ON w.museum_id = m.museum_id
        GROUP BY a.artist_id
        ORDER BY num_museums DESC
        LIMIT 1;
    """
    cursor.execute(query)
    result = cursor.fetchone()  # Fetch the artist with the most museums
    cursor.close()

    # Display the result
    if result:
        artist_name = result[0]
        num_museums = result[1]
        return render_template('results.html', title="Most Exhibited Artist", headers=["Artist Name", "Number of Museums"], results=[(artist_name, num_museums)])
    else:
        return "No data found."

@app.route('/paintings_by_area')
def paintings_by_area():
    cursor = mysql.connection.cursor()

    # Query to retrieve paintings ordered by area (width * height)
    query = """
        SELECT w.name, a.full_name, c.width, c.height, (c.width * c.height) AS area
        FROM work w
        JOIN artist a ON w.artist_id = a.artist_id
        JOIN canvas_size c ON w.work_id = c.size_id
        ORDER BY area ASC;
    """
    cursor.execute(query)
    results = cursor.fetchall()  # Fetch all paintings and their details
    cursor.close()

    # Display the result
    if results:
        return render_template('results.html', title="Paintings Ordered by Area", headers=["Painting", "Artist", "Width", "Height", "Area"], results=results)
    else:
        return "No data found."


