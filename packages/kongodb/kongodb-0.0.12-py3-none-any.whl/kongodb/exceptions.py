
class KongoError(Exception): pass

class AdapterError(KongoError): pass
class CollectionNotFoundError(KongoError): pass
class CollectionExistsError(KongoError): pass
class ItemNotFoundError(KongoError):pass
class ItemExistsError(KongoError):pass
class NoResultsError(KongoError): pass
class ConstraintError(KongoError): pass
