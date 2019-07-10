from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfdocument import PDFTextExtractionNotAllowed


class MyPdfPage(PDFPage):
    @classmethod
    def get_pages(klass, fp,
                  pagenos=None, maxpages=0, password='',
                  caching=True, check_extractable=True):
        # Create a PDF parser object associated with the file object.
        parser = PDFParser(fp)
        # Create a PDF document object that stores the document structure.
        doc = PDFDocument(parser, password=password, caching=caching)
        # Check if the document allows text extraction. If not, abort.
        if check_extractable and not doc.is_extractable:
            raise PDFTextExtractionNotAllowed('Text extraction is not allowed: %r' % fp)
        # Process each page contained in the document.
        for (pageno, page) in enumerate(klass.create_pages(doc)):
            if pagenos and (pageno+1 not in pagenos):
                continue
            yield pageno+1, page
            if maxpages and maxpages <= pageno + 1:
                break
        return

