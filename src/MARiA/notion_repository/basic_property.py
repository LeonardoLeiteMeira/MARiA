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
    
    def __status(self):
        status = self.property.get('status')
        if status is None:
            return None
        return status.get('name')

    def __last_edited_by(self):
        last_edited_by = self.property.get('last_edited_by')
        if last_edited_by is None:
            return None
        return last_edited_by.get('name') or last_edited_by.get('id')

    def __updatedBy(self):
        updated_by = self.property.get('updatedBy')
        if updated_by is None:
            return None
        return updated_by.get('name') or updated_by.get('id')

    def __rich_text(self):
        rich_text = self.property.get('rich_text', [])
        if not rich_text:
            return ''
        return ''.join([item.get('plain_text', '') for item in rich_text])

    def __multi_select(self):
        multi_select = self.property.get('multi_select', [])
        if not multi_select:
            return []
        return [item.get('name') for item in multi_select]

    def __people(self):
        people = self.property.get('people', [])
        if not people:
            return []
        return [person.get('name') or person.get('id') for person in people]

    def __files(self):
        files = self.property.get('files', [])
        if not files:
            return []
        result = []
        for file in files:
            if file['type'] == 'external':
                url = file['external']['url']
            elif file['type'] == 'file':
                url = file['file']['url']
            else:
                url = None
            result.append({'name': file.get('name'), 'url': url})
        return result

    def __checkbox(self):
        return self.property.get('checkbox', False)

    def __url(self):
        return self.property.get('url')

    def __email(self):
        return self.property.get('email')

    def __phone_number(self):
        return self.property.get('phone_number')

    def __rollup(self):
        rollup = self.property.get('rollup')
        if not rollup:
            return None
        rollup_type = rollup.get('type')
        return rollup.get(rollup_type)

    def __last_edited_time(self):
        return self.property.get('last_edited_time')

    def __unique_id(self):
        unique_id = self.property.get('unique_id')
        if not unique_id:
            return None
        return {'number': unique_id.get('number'), 'prefix': unique_id.get('prefix')}

    def __verification(self):
        verification = self.property.get('verification')
        if not verification:
            return None
        result = {'state': verification.get('state')}
        verified_by = verification.get('verified_by')
        if verified_by:
            result['verified_by'] = verified_by.get('name') or verified_by.get('id')
        result['date'] = verification.get('date')
        return result


