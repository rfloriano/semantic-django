class VirtuosoInterface(object):
    """
    Provide a default interface to access Virtuoso.
    """

    def select(self, query):
        raise NotImplementedError("You need to write a select method")

    def insert(self, query):
        raise NotImplementedError("You need to write a insert method")

    def update(self, query):
        raise NotImplementedError("You need to write a update method")

    def delete(self, query):
        raise NotImplementedError("You need to write a delete method")
