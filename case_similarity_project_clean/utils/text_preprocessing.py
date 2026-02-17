import re
import string

def clean_text(text):
    """
    Cleans input text by:
    - Lowercasing
    - Removing special characters and numbers
    - Removing extra whitespace
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove punctuation/special characters (preserving whitespace)
    # This regex keeps letters and spaces
    text = re.sub(r'[^a-z\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def highlight_text(text, query):
    """
    Highlights significant words from the query within the text using HTML.
    Simple approach: Split query into words, ignore short stop-words, and highlight matches.
    """
    if not text or not query:
        return text or ""
    
    # Simple set of stop words to ignore (can be expanded)
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "case", "legal", "court"}
    
    words = [w for w in re.split(r'\W+', query) if len(w) > 3 and w.lower() not in stop_words]
    
    if not words:
        return text

    highlighted_text = text
    
    for w in words:
        # Case insensitive regex replacement with yellow background
        pattern = re.compile(re.escape(w), re.IGNORECASE)
        # Use a lambda to replace with the exact matching case but wrapped
        highlighted_text = pattern.sub(
            lambda m: f'<span style="background-color: #ffd700; color: black; font-weight: bold; padding: 0 2px; border-radius: 3px;">{m.group(0)}</span>', 
            highlighted_text
        )
        
    return highlighted_text
