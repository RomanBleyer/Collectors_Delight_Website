# Collectors Delight - Flask Art Website

A Flask web application for art collectors to browse, filter, and purchase stolen or rare paintings online.

## Features
- Storefront for browsing artworks
- Dynamic filters (date stolen, art movement, type of painting, etc.)
- Shopping cart and checkout system
- Admin panel for managing products
- User authentication (signup, login, logout)
- Responsive, modern UI

## Getting Started

### Prerequisites
- Python 3.8+
- pip
- SQLite (default, or configure another database)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/RBleyer/flask_art_website_development_code.git
   cd flask_art_website_development_code
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database:
   ```bash
   python setup_full_db.py
   ```
4. Run the app:
   ```bash
   python app.py
   ```

## Usage
- Visit `http://localhost:5000` in your browser.
- Browse, filter, and purchase artworks.
- Admins can add/edit products via `/admin`.

## Folder Structure
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `setup_full_db.py` - Database setup script
- `static/` - Static files (images, CSS, JS)
- `templates/` - HTML templates

