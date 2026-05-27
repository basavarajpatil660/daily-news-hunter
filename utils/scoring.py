CREDIBLE_SOURCES = [
    "TechCrunch", "The Verge", "Wired", "Ars Technica",
    "MIT Technology Review", "BBC", "Reuters", "AP News",
    "The Hindu", "Times of India", "Economic Times",
    "NDTV", "India Today", "Hindustan Times", "Bloomberg",
    "Forbes", "VentureBeat", "ZDNet", "CNET", "Engadget"
]

def get_source_adjustment(source_name):
    if not source_name:
        return -1
    source_lower = source_name.lower()
    for s in CREDIBLE_SOURCES:
        if s.lower() in source_lower:
            return 1
    return -1

def calculate_final_score(gemma_score, source):
    adj = get_source_adjustment(source)
    return gemma_score + adj
