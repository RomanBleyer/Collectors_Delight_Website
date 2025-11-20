import sqlite3
import os
import random

DB_FILENAME = 'database.db'

def create_database():
    """Create the missing artworks database with all tables."""
    # Remove existing database if it exists
    if os.path.exists(DB_FILENAME):
        os.remove(DB_FILENAME)
        print("Existing database removed.")
    
    # Create new database connection
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()
    
    # Create products table (basic, not categorized)
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            date_missing TEXT NOT NULL,
            original_artist TEXT NOT NULL,
            seller TEXT NOT NULL,
            description TEXT NOT NULL,
            painting_orientation TEXT NOT NULL CHECK (painting_orientation IN ('landscape', 'portrait', 'square')),
            stock INTEGER NOT NULL DEFAULT 1
        )
    ''')
    print("Products table created.")

    # Create users table with admin column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            admin BOOLEAN DEFAULT 0
        )
    ''')
    print("Users table created (with admin column).")

    # Insert test user and test admin
    cursor.execute('''
        INSERT INTO users (email, password, first_name, last_name, admin)
        VALUES (?, ?, ?, ?, 0)
    ''', ("testuser@example.com", "testpass", "Test", "User"))
    cursor.execute('''
        INSERT INTO users (email, password, first_name, last_name, admin)
        VALUES (?, ?, ?, ?, 1)
    ''', ("admin@example.com", "adminpass", "Admin", "User"))
    print("Test user and test admin created.")
    return conn

def populate_products(conn):
    """Populate the products table with sample data."""
    cursor = conn.cursor()
    artworks = [
        {'image': 'infante_and_dog.jpg', 'name': 'Infante and Dog', 'price': 1000000, 'date_missing': 'May 15, 1970', 'original_artist': 'Diego Velázquez', 'description': 'Stolen from a private residence during a burglary in Marseille, France.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'landscape_cottages.jpg', 'name': 'Landscape with Cottages', 'price': 5000000, 'date_missing': 'September 4, 1972', 'original_artist': 'Rembrandt van Rijn', 'description': 'A rare Rembrandt landscape stolen from the Montreal Museum of Fine Arts by armed robbers.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'still_life_vanitas.jpg', 'name': 'Still Life: Vanitas', 'price': 2000000, 'date_missing': 'September 4, 1972', 'original_artist': 'Jan Davidsz van Heem', 'description': 'Among paintings stolen from the Montreal Museum of Fine Arts by armed robbers.', 'painting_orientation': 'square', 'stock': 1},
        {'image': 'the_concert.jpg', 'name': 'The Concert', 'price': 200000000, 'date_missing': 'March 18, 1990', 'original_artist': 'Johannes Vermeer', 'description': 'The most valuable stolen painting in the world. Stolen from Isabella Stewart Gardner Museum in Boston.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'storm_sea_galilee.jpg', 'name': 'The Storm on the Sea of Galilee', 'price': 100000000, 'date_missing': 'March 18, 1990', 'original_artist': 'Rembrandt van Rijn', 'description': \
            "Rembrandt's only seascape, stolen from Isabella Stewart Gardner Museum.", 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'landscape_obelisk.jpg', 'name': 'Landscape with an Obelisk', 'price': 5000000, 'date_missing': 'March 18, 1990', 'original_artist': 'Govert Flinck', 'description': 'Part of the Isabella Stewart Gardner Museum heist, attributed to Rembrandt student.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'man_with_pipe.jpg', 'name': 'Man with a Pipe', 'price': 2000000, 'date_missing': '1998', 'original_artist': 'Jean Metzinger', 'description': 'Missing from Lawrence University, Wisconsin since 1998.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'chemin_sevres.jpg', 'name': 'Le chemin de Sèvres', 'price': 1300000, 'date_missing': 'May 3, 1998', 'original_artist': 'Jean-Baptiste-Camille Corot', 'description': 'Stolen by visitor during open hours from The Louvre, Paris.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'view_auvers.jpg', 'name': 'View of Auvers-sur-Oise', 'price': 10000000, 'date_missing': 'December 31, 1999', 'original_artist': 'Paul Cézanne', 'description': "Stolen from Ashmolean Museum, Oxford during New Year's Eve celebrations.", 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'cavalier.jpg', 'name': 'A Cavalier', 'price': 1000000, 'date_missing': 'June 10, 2007', 'original_artist': 'Frans van Mieris the Elder', 'description': 'Stolen by visitor during opening hours from Art Gallery of New South Wales, Sydney.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'venus_mirror.jpg', 'name': 'Venus with a Mirror', 'price': 1000000, 'date_missing': 'February 11, 2010', 'original_artist': 'Jacopo Palma il Giovane', 'description': 'Stolen from Budapest Palace by robbers using force.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'poppy_flowers.jpg', 'name': 'Poppy Flowers', 'price': 55000000, 'date_missing': 'August 2010', 'original_artist': 'Vincent van Gogh', 'description': 'Also known as Vase and Flowers. Stolen from Mohammed Mahmoud Khalil Museum, Cairo.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'madeleine_elbow.jpg', 'name': 'Madeleine Leaning on her Elbow with Flowers in her Hair', 'price': 1000000, 'date_missing': 'September 8, 2011', 'original_artist': 'Pierre-Auguste Renoir', 'description': 'Stolen by armed robber at night from private residence in Houston, Texas.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'soldier_horseback.jpg', 'name': 'A Soldier on Horseback', 'price': 3000000, 'date_missing': 'March 14, 2020', 'original_artist': 'Anthony van Dyck', 'description': 'Stolen at night along with two other paintings from Christ Church Picture Gallery, Oxford.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'boy_drinking.jpg', 'name': 'A Boy Drinking', 'price': 2000000, 'date_missing': 'March 14, 2020', 'original_artist': 'Annibale Carracci', 'description': 'Stolen at night along with two other paintings from Christ Church Picture Gallery, Oxford.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'nativity_francis.jpg', 'name': 'Nativity with St. Francis and St. Lawrence', 'price': 20000000, 'date_missing': 'October 16, 1969', 'original_artist': 'Caravaggio', 'description': 'Stolen from San Lorenzo in Palermo, Sicily. Large painting measuring almost six square metres.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'pigeon_pois.jpg', 'name': 'Le pigeon aux petits pois', 'price': 28000000, 'date_missing': 'May 20, 2010', 'original_artist': 'Pablo Picasso', 'description': "One of five paintings stolen from Musée d'Art Moderne de la Ville de Paris.", 'painting_orientation': 'square', 'stock': 1},
        {'image': 'just_judges.jpg', 'name': 'The Just Judges', 'price': 50000000, 'date_missing': 'April 10, 1934', 'original_artist': 'Jan van Eyck', 'description': 'Lower left panel of the Ghent Altarpiece, stolen from Saint Bavo Cathedral in Belgium.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'waterloo_bridge.jpg', 'name': 'Waterloo Bridge, London', 'price': 15000000, 'date_missing': 'October 15-16, 2012', 'original_artist': 'Claude Monet', 'description': 'Presumably burnt by an accomplice during Kunsthal museum theft in Rotterdam.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'charing_cross.jpg', 'name': 'Charing Cross Bridge, London', 'price': 15000000, 'date_missing': 'October 15-16, 2012', 'original_artist': 'Claude Monet', 'description': 'Presumably burnt by an accomplice during Kunsthal museum theft in Rotterdam.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'girl_window.jpg', 'name': 'Girl in Front of Open Window', 'price': 20000000, 'date_missing': 'October 15-16, 2012', 'original_artist': 'Paul Gauguin', 'description': 'Also known as La Francée. Presumably burnt by an accomplice during Kunsthal theft.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'self_portrait_haan.jpg', 'name': 'Self-Portrait', 'price': 10000000, 'date_missing': 'October 15-16, 2012', 'original_artist': 'Meyer de Haan', 'description': 'Presumably burnt by an accomplice during Kunsthal museum theft in Rotterdam.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'painter_work.jpg', 'name': 'The Painter on His Way to Work', 'price': 100000000, 'date_missing': '1945', 'original_artist': 'Vincent van Gogh', 'description': 'Listed as missing from Stassfurt salt mines art repository near Magdeburg, Germany.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'portrait_young_man.jpg', 'name': 'Portrait of a Young Man', 'price': 100000000, 'date_missing': '1940s', 'original_artist': 'Raphael', 'description': \
            "Plundered by the Nazis in Poland. Many scholars regard it as Raphael's self-portrait.", 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'en_canot.jpg', 'name': 'En Canot', 'price': 2400000, 'date_missing': 'c. 1936', 'original_artist': 'Jean Metzinger', 'description': 'Confiscated by the Nazis and has been missing ever since.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'allegory_belief.jpg', 'name': 'Allegory of Christian Belief', 'price': 5000000, 'date_missing': '1939', 'original_artist': 'Johann Liss', 'description': 'Nazi Gestapo confiscated roughly 750 Old Master drawings from Jewish collector.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'young_couple.jpg', 'name': 'Young Couple in a Landscape', 'price': 3000000, 'date_missing': '1939', 'original_artist': 'Georg Penz', 'description': 'Nazi Gestapo confiscated roughly 750 Old Master drawings from Jewish collector.', 'painting_orientation': 'landscape', 'stock': 1}
    ]
    for artwork in artworks:
        seller = random.choice(['John Doe', 'Jane Doe'])
        artwork['seller'] = seller
        cursor.execute('''
            INSERT INTO products (image, name, price, date_missing, original_artist, seller, description, painting_orientation, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            artwork['image'],
            artwork['name'],
            artwork['price'],
            artwork['date_missing'],
            artwork['original_artist'],
            artwork['seller'],
            artwork['description'],
            artwork['painting_orientation'],
            artwork['stock']
        ))
    print(f"Successfully added {len(artworks)} artworks to the database!")

def main():
    try:
        conn = create_database()
        populate_products(conn)
        conn.commit()
        conn.close()
        print("\n=== DATABASE SETUP COMPLETE ===")
        print(f"Database: {DB_FILENAME}")
        print("Ready to launch your marketplace!")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
