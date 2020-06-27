import json

class KeyStore:

    def __init__(self):
        self.data = {}
        self.db_path = './data/store.json'
        try:
            with open(self.db_path) as db_file:
                stored = json.load(db_file)
                for key, val in stored.items():
                    self.data[key] = bytes.fromhex(val)
        except Exception as e:
            self.save()

    def save(self):
        with open(self.db_path, 'w') as db_file:
            data = { key: val.hex() for (key,val) in self.data.items() }
            json.dump(data, db_file)

    def get(self, key):
        if key in self.data:
            return self.data[key]
        return None

    def set(self, key, val):
        if type(val) == bytes:
            self.data[key] = val
        self.save()