import fitz


def pdf_to_txt(path_in, path_out = "out.txt"):
    doc = fitz.open(path_in)                           # open a document
    out = open(path_out, "wb")                  # create a text output
    for i, page in enumerate(doc):                  # iterate the document pages
        text = page.get_text().strip().encode("utf8")       # get plain text (is in UTF-8)
        out.write(text)                             # write text of page
        out.write(bytes(f"_Page {i+1}_\n", 'utf-8'))  # write page delimiter (form feed 0x0C)
    out.close()
    
def pdf_to_string(path):
    doc = fitz.open(path)
    out = []
    for i, page in enumerate(doc):
        text = page.get_text() + f"_Page {i+1}_"
        out.append(text)
    return "\n".join(out).strip()
