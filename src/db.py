import duckdb


class DBConnector:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = duckdb.connect(database=self.db_path)
        self.connection.execute("INSTALL spatial; LOAD spatial;")

    def disconnect(self):
        self.connection.close()
