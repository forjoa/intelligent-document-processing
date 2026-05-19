class DocumentProcessingError(Exception):
    pass


class FileTooLarge(DocumentProcessingError):
    pass


class NonPDFFile(DocumentProcessingError):
    pass


class TooManyPages(DocumentProcessingError):
    pass


class OCRFailure(DocumentProcessingError):
    pass


class ExtractionError(DocumentProcessingError):
    pass


class EmbeddingError(DocumentProcessingError):
    pass


class DatabaseError(DocumentProcessingError):
    pass
