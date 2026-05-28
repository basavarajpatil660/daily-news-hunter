import re

def remove_duplicate_urls(articles):
    seen = set()
    unique = []
    for a in articles:
        if a['link'] not in seen:
            seen.add(a['link'])
            unique.append(a)
    return unique

def remove_duplicate_titles(articles):
    seen = set()
    unique = []
    for a in articles:
        title = a['title'].lower().strip()
        if title not in seen:
            seen.add(title)
            unique.append(a)
    return unique

def get_word_overlap_ratio(title1, title2):
    stopwords = {"a", "an", "the", "and", "or", "but", "if", "in", "on", "with", "to", "for", "of"}
    def get_words(t):
        words = set(re.findall(r'\b\w+\b', t.lower()))
        return words - stopwords
        
    w1 = get_words(title1)
    w2 = get_words(title2)
    
    if not w1 or not w2:
        return 0
        
    overlap = len(w1.intersection(w2))
    return overlap / max(len(w1), len(w2))

def remove_near_duplicates(articles):
    unique = []
    for a in articles:
        is_dup = False
        for u in unique:
            if get_word_overlap_ratio(a['title'], u['title']) >= 0.8:
                a_score = a.get('final_score', a.get('pre_rank_score', 0))
                u_score = u.get('final_score', u.get('pre_rank_score', 0))
                if a_score > u_score:
                    # Update u with a's content since a has a higher score
                    u.clear()
                    u.update(a)
                is_dup = True
                break
        if not is_dup:
            unique.append(a)
    return unique

