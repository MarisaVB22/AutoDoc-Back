CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(50),
            email VARCHAR(50)
        );
    """
