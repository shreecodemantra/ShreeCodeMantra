import re

def slugify(text):
    """
    Generate an SEO-friendly URL slug from text.
    E.g., "Face Recognition Attendance System" -> "face-recognition-attendance-system"
    """
    if not text:
        return ""
    # Convert to lowercase
    slug = text.lower()
    # Remove special characters
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    # Replace spaces and multiple hyphens with a single hyphen
    slug = re.sub(r'[\s-]+', '-', slug)
    # Strip leading/trailing hyphens
    return slug.strip('-')
