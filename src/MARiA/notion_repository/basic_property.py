# TODO falta usar essa estrutura para armazenar as transacoes de maneira mais simples
class BasicProperty:
    BASIC_PROPERTIES = ['number', 'relation', 'date', 'created_time']

    def __init__(self, name: str, propety: dict):
        self.name = name
        self.property = propety
        self.property_type: str = propety["type"]
        self.value = self.get_value()

    def get_value(self):
        if self.property_type in self.BASIC_PROPERTIES:
            return self.__basic_type()
        
        method_name = f"_{self.__class__.__name__}__{self.property_type}"
        return getattr(self, method_name)()
    
    def __basic_type(self):
        return self.property[self.property_type]
    
    def __select(self):
        if  self.property['select'] != None:
            return self.property['select']['name']
        return None
    
    def __title(self):
        return ([item['plain_text'] for item in self.property['title']])[0]
    
    def __formula(self):
        type_value = self.property['formula']['type']
        return self.property[self.property_type][type_value]
    
    def __created_by(self):
        created_by = self.property.get('created_by')
        if created_by is None:
            return None
        return created_by.get('name') or created_by.get('id')
    


