import regex as re
def date_extractor(content, year):
    split_by_pages = re.split("_Page \d+_", content)
    date = find_on_first_page(year, split_by_pages)
    if date != None:
        return date
    else:
        return find_by_annotation(year, split_by_pages)

def find_on_first_page(year, split_by_pages):
    page_1 = split_by_pages[1]
    search = re.search(f"\n(\d+.*{year})", page_1)
    if search != None:
        return search.group(1).strip()
    
def find_by_annotation(year, split_by_pages):
    for i in range(3, 30, 2):
        page = split_by_pages[i]
        if year < 2017:
            search = re.search("^\n(.*)\|", page)
        else:
            search = re.search("^\s*([ \d\.-]+)|", page)
        if search != None and len(search.group()) > 10 and str(year) in search.group():
            return search.group(1).strip()