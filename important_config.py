# Important Configuration File
# This file contains database connection details.

DATABASE_CONFIGS = {
    "postgresql": "postgresql://username:password@localhost:5432/mydatabase",
    "mysql": "mysql+pymysql://username:password@localhost:3306/mydatabase",
    "sqlite": "sqlite:///mydatabase.db",
    "mssql": "mssql+pyodbc://username:password@localhost:1433/mydatabase?driver=ODBC+Driver+17+for+SQL+Server",
    "oracle": "oracle+cx_oracle://username:password@localhost:1521/xe",
}
