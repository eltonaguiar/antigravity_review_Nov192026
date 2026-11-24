import sqlite3, pathlib
db = sqlite3.connect(':memory:')
db.executescript(pathlib.Path('C:/Users/zerou/repos/antigravity_review/docs/experiment_schema.sql').read_text())
tables = [r for r in db.execute("select name from sqlite_master where type='table'")]
print(len(tables))
