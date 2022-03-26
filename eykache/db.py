import psycopg2


class Database:
    def __init__(self, config) -> None:
        self.config = config
        self.conn = psycopg2.connect(
            database=config.database,
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
        )
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS colonies (id integer, location geometry(POINT) UNIQUE);"
            "CREATE INDEX plots ON colonies USING GIST (location);"
        )

    def write(self, x, y, colony_id):
        self.cur.execute(
            f"INSERT INTO colonies (id, location) VALUES ({colony_id}, ST_Point({x}, {y})) ON CONFLICT (location) DO UPDATE SET id = {colony_id};"
        )

    def commit(self):
        self.conn.commit()

    def read_colony(self, location):
        self.cur.execute(
            "SELECT colony_id FROM colonies WHERE location = %s;", (location,)
        )
        return self.cur.fetchall()

    def get_plots(self, xmin, ymin, xmax, ymax):
        self.cur.execute(
            f"SELECT id,ST_AsText(location) FROM colonies WHERE ST_Contains(ST_MakeEnvelope({xmin}, {ymin}, {xmax}, {ymax}), colonies.location);"
        )
        return self.cur.fetchall()

    def read_location(self, colony_id):
        self.cur.execute("SELECT location FROM colonies WHERE id = %s;", (colony_id,))
        return self.cur.fetchone()

    def read_space(self):
        pass

    def read_all(self, index=0):
        self.cur.execute("SELECT * FROM colonies;")
        if index == 0:
            return self.cur.fetchall()
        return self.cur.fetchmany(index)

    def close(self):
        self.cur.close()
        self.conn.close()
