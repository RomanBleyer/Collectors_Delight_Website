import sqlite3
import os
import random
from werkzeug.security import generate_password_hash

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
    
    # Create products table (with all tag columns)
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            original_artist TEXT NOT NULL,
            description TEXT NOT NULL,
            painting_orientation TEXT NOT NULL CHECK (painting_orientation IN ('landscape', 'portrait', 'square')),
            price_range TEXT,
            date_category TEXT,
            art_movement TEXT,
            painting_type TEXT,
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

    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, 
            order_time TEXT NOT NULL,
            total_cost REAL NOT NULL,
            address TEXT NOT NULL,
            items TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    print("Orders table created.")

    # Insert test user and test admin with hashed passwords
    user_password_hash = generate_password_hash("testpass")
    admin_password_hash = generate_password_hash("adminpass")
    cursor.execute('''
        INSERT INTO users (email, password, first_name, last_name, admin)
        VALUES (?, ?, ?, ?, 0)
    ''', ("user@example.com", user_password_hash, "John", "User"))
    cursor.execute('''
        INSERT INTO users (email, password, first_name, last_name, admin)
        VALUES (?, ?, ?, ?, 1)
    ''', ("admin@example.com", admin_password_hash, "John", "Admin"))
    print("John User and John Admin created with hashed passwords.")
    return conn

def populate_products(conn):
    """Populate the products table with sample data."""
    cursor = conn.cursor()
    # Sample tag values for demonstration
    def get_price_range(price):
        if price < 5000000:
            return '0-5 mil'
        elif price < 20000000:
            return '5-20 mil'
        elif price < 50000000:
            return '20-50 mil'
        else:
            return '50+ mil'

    def get_date_category(date_missing):
        import random
        categories = ['1900 to 1950', '1950 to 1970', '1970 to 1990', '1990 to present']
        return random.choice(categories)

    def get_art_movement(artist):
        # crude mapping for demonstration
        if 'Rembrandt' in artist or 'Vermeer' in artist:
            return 'Baroque'
        elif 'van Gogh' in artist:
            return 'Post-Impressionism'
        elif 'Monet' in artist:
            return 'Impressionism'
        elif 'Picasso' in artist:
            return 'Cubism'
        elif 'Cézanne' in artist:
            return 'Post-Impressionism'
        elif 'Renoir' in artist:
            return 'Impressionism'
        elif 'Raphael' in artist:
            return 'Renaissance'
        elif 'Caravaggio' in artist:
            return 'Baroque'
        elif 'Corot' in artist:
            return 'Modern'
        elif 'Gauguin' in artist:
            return 'Post-Impressionism'
        elif 'Flinck' in artist:
            return 'Baroque'
        elif 'Liss' in artist:
            return 'Baroque'
        elif 'Penz' in artist:
            return 'Renaissance'
        else:
            return 'Other'

    def get_painting_type(name):
        # Expanded mapping for demonstration
        name_lower = name.lower()
        if 'portrait' in name_lower:
            return 'Subject Portrait'
        elif 'landscape' in name_lower:
            return 'Landscape Rendition'
        elif 'still life' in name_lower or 'vanitas' in name_lower:
            return 'Still Life / Vanitas'
        elif 'self-portrait' in name_lower or 'self portrait' in name_lower:
            return 'Self Portrait'
        elif 'cavalier' in name_lower or 'soldier' in name_lower:
            return 'Figure Painting'
        elif 'bridge' in name_lower:
            return 'Cityscape'
        elif 'window' in name_lower:
            return 'Interior Scene'
        elif 'pigeon' in name_lower or 'dog' in name_lower:
            return 'Animal Painting'
        elif 'flowers' in name_lower or 'vase' in name_lower:
            return 'Floral Still Life'
        elif 'nativity' in name_lower:
            return 'Religious Scene'
        elif 'christian belief' in name_lower:
            return 'Allegorical Painting'
        elif 'couple' in name_lower:
            return 'Genre Scene'
        elif 'sea' in name_lower or 'galilee' in name_lower:
            return 'Seascape'
        elif 'work' in name_lower:
            return 'Artist at Work'
        elif 'mirror' in name_lower:
            return 'Mythological Scene'
        elif 'judges' in name_lower:
            return 'Panel Painting'
        elif 'obelisk' in name_lower:
            return 'Monumental Landscape'
        else:
            return 'Other'

    artworks = [
        {'image': 'infante_and_dog.jpg', 'name': 'Infante and Dog', 'price': 1000000, 'original_artist': 'Diego Velázquez', 'description': 'Stolen from a private residence during a burglary in Marseille, France.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'landscape_cottages.jpg', 'name': 'Landscape with Cottages', 'price': 5000000, 'original_artist': 'Rembrandt van Rijn', 'description': 'A rare Rembrandt landscape stolen from the Montreal Museum of Fine Arts by armed robbers.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'still_life_vanitas.jpg', 'name': 'Still Life: Vanitas', 'price': 2000000, 'original_artist': 'Jan Davidsz van Heem', 'description': 'Among paintings stolen from the Montreal Museum of Fine Arts by armed robbers.', 'painting_orientation': 'square', 'stock': 1},
        {'image': 'the_concert.jpg', 'name': 'The Concert', 'price': 200000000, 'original_artist': 'Johannes Vermeer', 'description': 'The most valuable stolen painting in the world. Stolen from Isabella Stewart Gardner Museum in Boston.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'storm_sea_galilee.jpg', 'name': 'The Storm on the Sea of Galilee', 'price': 100000000, 'original_artist': 'Rembrandt van Rijn', 'description': 'Rembrandt\'s only seascape, stolen from Isabella Stewart Gardner Museum.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'landscape_obelisk.jpg', 'name': 'Landscape with an Obelisk', 'price': 5000000, 'original_artist': 'Govert Flinck', 'description': 'Part of the Isabella Stewart Gardner Museum heist, attributed to Rembrandt student.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'man_with_pipe.jpg', 'name': 'Man with a Pipe', 'price': 2000000, 'original_artist': 'Jean Metzinger', 'description': 'Missing from Lawrence University, Wisconsin since 1998.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'chemin_sevres.jpg', 'name': 'Le chemin de Sèvres', 'price': 1300000, 'original_artist': 'Jean-Baptiste-Camille Corot', 'description': 'Stolen by visitor during open hours from The Louvre, Paris.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'view_auvers.jpg', 'name': 'View of Auvers-sur-Oise', 'price': 10000000, 'original_artist': 'Paul Cézanne', 'description': "Stolen from Ashmolean Museum, Oxford during New Year's Eve celebrations.", 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'cavalier.jpg', 'name': 'A Cavalier', 'price': 1000000, 'original_artist': 'Frans van Mieris the Elder', 'description': 'Stolen by visitor during opening hours from Art Gallery of New South Wales, Sydney.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'venus_mirror.jpg', 'name': 'Venus with a Mirror', 'price': 1000000, 'original_artist': 'Jacopo Palma il Giovane', 'description': 'Stolen from Budapest Palace by robbers using force.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'poppy_flowers.jpg', 'name': 'Poppy Flowers', 'price': 55000000, 'original_artist': 'Vincent van Gogh', 'description': 'Also known as Vase and Flowers. Stolen from Mohammed Mahmoud Khalil Museum, Cairo.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'madeleine_elbow.jpg', 'name': 'Madeleine Leaning on her Elbow with Flowers in her Hair', 'price': 1000000, 'original_artist': 'Pierre-Auguste Renoir', 'description': 'Stolen by armed robber at night from private residence in Houston, Texas.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'soldier_horseback.jpg', 'name': 'A Soldier on Horseback', 'price': 3000000, 'original_artist': 'Anthony van Dyck', 'description': 'Stolen at night along with two other paintings from Christ Church Picture Gallery, Oxford.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'boy_drinking.jpg', 'name': 'A Boy Drinking', 'price': 2000000, 'original_artist': 'Annibale Carracci', 'description': 'Stolen at night along with two other paintings from Christ Church Picture Gallery, Oxford.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'nativity_francis.jpg', 'name': 'Nativity with St. Francis and St. Lawrence', 'price': 20000000, 'original_artist': 'Caravaggio', 'description': 'Stolen from San Lorenzo in Palermo, Sicily. Large painting measuring almost six square metres.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'pigeon_pois.jpg', 'name': 'Le pigeon aux petits pois', 'price': 28000000, 'original_artist': 'Pablo Picasso', 'description': "One of five paintings stolen from Musée d'Art Moderne de la Ville de Paris.", 'painting_orientation': 'square', 'stock': 1},
        {'image': 'just_judges.jpg', 'name': 'The Just Judges', 'price': 50000000, 'original_artist': 'Jan van Eyck', 'description': 'Lower left panel of the Ghent Altarpiece, stolen from Saint Bavo Cathedral in Belgium.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'waterloo_bridge.jpg', 'name': 'Waterloo Bridge, London', 'price': 15000000, 'original_artist': 'Claude Monet', 'description': 'Presumably burnt by an accomplice during Kunsthal museum theft in Rotterdam.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'charing_cross.jpg', 'name': 'Charing Cross Bridge, London', 'price': 15000000, 'original_artist': 'Claude Monet', 'description': 'Presumably burnt by an accomplice during Kunsthal museum theft in Rotterdam.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'girl_window.jpg', 'name': 'Girl in Front of Open Window', 'price': 20000000, 'original_artist': 'Paul Gauguin', 'description': 'Also known as La Francée. Presumably burnt by an accomplice during Kunsthal theft.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'self_portrait_haan.jpg', 'name': 'Self-Portrait', 'price': 10000000, 'original_artist': 'Meyer de Haan', 'description': 'Presumably burnt by an accomplice during Kunsthal museum theft in Rotterdam.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'painter_work.jpg', 'name': 'The Painter on His Way to Work', 'price': 100000000, 'original_artist': 'Vincent van Gogh', 'description': 'Listed as missing from Stassfurt salt mines art repository near Magdeburg, Germany.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'portrait_young_man.jpg', 'name': 'Portrait of a Young Man', 'price': 100000000, 'original_artist': 'Raphael', 'description': "Plundered by the Nazis in Poland. Many scholars regard it as Raphael's self-portrait.", 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'en_canot.jpg', 'name': 'En Canot', 'price': 2400000, 'original_artist': 'Jean Metzinger', 'description': 'Confiscated by the Nazis and has been missing ever since.', 'painting_orientation': 'landscape', 'stock': 1},
        {'image': 'Allegory_of_Christian_Belief.jpg', 'name': 'Allegory of Christian Belief', 'price': 5000000, 'original_artist': 'Johann Liss', 'description': 'Nazi Gestapo confiscated roughly 750 Old Master drawings from Jewish collector.', 'painting_orientation': 'portrait', 'stock': 1},
        {'image': 'Young_Couple_in_a_Landscape.png', 'name': 'Young Couple in a Landscape', 'price': 3000000, 'original_artist': 'Georg Penz', 'description': 'Nazi Gestapo confiscated roughly 750 Old Master drawings from Jewish collector.', 'painting_orientation': 'landscape', 'stock': 1}
    ]
    for artwork in artworks:
        # Add tag fields
        artwork['price_range'] = get_price_range(artwork['price'])
        artwork['date_category'] = get_date_category(None)
        artwork['art_movement'] = get_art_movement(artwork['original_artist'])
        artwork['painting_type'] = get_painting_type(artwork['name'])
        cursor.execute('''
            INSERT INTO products (image, name, price, original_artist, description, painting_orientation, price_range, date_category, art_movement, painting_type, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            artwork['image'],
            artwork['name'],
            artwork['price'],
            artwork['original_artist'],
            artwork['description'],
            artwork['painting_orientation'],
            artwork['price_range'],
            artwork['date_category'],
            artwork['art_movement'],
            artwork['painting_type'],
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
