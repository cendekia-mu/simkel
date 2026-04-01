import json
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from . import SimkelBase, SimkelDBSession 

class SimkelPermohonanField(SimkelBase):
    __tablename__ = 'simkel_jpel_field'
    __table_args__ = {'extend_existing': True}
    db_session = SimkelDBSession
    
    id = Column(Integer, primary_key=True)
    jpel_id = Column(Integer, ForeignKey('simkel_jpel.id'), nullable=False)
    nama = Column(String(255))
    value = Column(Text) # Kolom ini akan menampung JSON data lainnya

    @property
    def kode(self):
        if self.value:
            try:
                data = json.loads(self.value)
                if 'kode' in data and data['kode']:
                    return data['kode']
            except:
                pass
        if not self.nama:
            return f"field_{self.id}"
        return self.nama.lower().strip().replace(' ', '_').replace('-', '_')

    @kode.setter
    def kode(self, val):
        try:
            data = json.loads(self.value) if self.value else {}
        except:
            data = {}
        data['kode'] = val
        self.value = json.dumps(data)

    @property
    def tipe(self):
        if self.value:
            try:
                data = json.loads(self.value)
                if 'tipe' in data:
                    return data['tipe']
            except:
                pass
        return 'text'

    @tipe.setter
    def tipe(self, val):
        try:
            data = json.loads(self.value) if self.value else {}
        except:
            data = {}
        data['tipe'] = val
        self.value = json.dumps(data)

    @property
    def is_required(self):
        if self.value:
            try:
                data = json.loads(self.value)
                if 'is_required' in data:
                    return data['is_required']
            except:
                pass
        return True

    @is_required.setter
    def is_required(self, val):
        try:
            data = json.loads(self.value) if self.value else {}
        except:
            data = {}
        data['is_required'] = bool(val)
        self.value = json.dumps(data)

    @property
    def is_printed(self):
        if self.value:
            try:
                data = json.loads(self.value)
                if 'is_printed' in data:
                    return data['is_printed']
            except:
                pass
        return True

    @is_printed.setter
    def is_printed(self, val):
        try:
            data = json.loads(self.value) if self.value else {}
        except:
            data = {}
        data['is_printed'] = bool(val)
        self.value = json.dumps(data)