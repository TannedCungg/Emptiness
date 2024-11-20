import pickle
import os

class SimpleDataBase:
    def __init__(self, save_file):
        self.save_file = save_file
    
    def read(self):
        """
        return: dict
        """
        db = {}
        if not os.path.exists(self.save_file):
            return db
        try:
            _file = open(self.save_file, "rb")
            db = pickle.load(_file)
            _file.close()
        except Exception as e:
            print(f"[ERR]: Something gone wrong: {e}")
        return db
    
    def write(self, db):
        _db = self.read()
        _db.update(db)
        _file = open(self.save_file, "wb")
        pickle.dump(_db, _file)
        _file.close()
