# Web Dashboard Directory

This directory contains the Flask web application and frontend assets for the Brand Forge approval interface.

## Structure

- `app.py` - Flask application entry point
- `templates/` - Jinja2 HTML templates
- `static/` - CSS, JavaScript, and frontend assets
- `routes/` - Flask route handlers for gallery, approval, comparison views

## Technology Stack

- **Backend**: Flask
- **Frontend**: Tailwind CSS for responsive UI
- **Features**:
  - Image gallery with lazy loading
  - Side-by-side comparison view
  - Feedback capture system
  - Real-time approval tracking

## Running

```bash
cd automation
source .venv/bin/activate
python -m web.app
```

Access at http://localhost:5000
