from mongoengine import StringField, DictField, DateTimeField, DynamicField, DynamicDocument, Document, ListField
from datetime import datetime


class Component(Document):

    name = StringField()
    type = StringField()
    content = DictField(DynamicField())
    referenced_by = ListField(DynamicField())
    date_created = DateTimeField(default=datetime.utcnow)
    date_modified = DateTimeField(default=datetime.utcnow)
    meta = {'allow_inheritance': True}

    def __init__(self, *args, **kwargs):
        super(Component, self).__init__(*args, **kwargs)

        self._update_refs = False

        self.name = kwargs.get('name', None)
        self.type = kwargs.get('name', None)
        self.content = kwargs.get('content', None)
        self.comp_refs = kwargs.get('referenced_by', [])

        self._c_refs = set()

    def save(
        self,
        force_insert=False,
        validate=True,
        clean=True,
        write_concern=None,
        cascade=None,
        cascade_kwargs=None,
        _refs=None,
        save_condition=None,
        signal_kwargs=None,
        **kwargs,
    ):

        self.date_modified = datetime.utcnow

        ret = DynamicDocument.save(self,
                                   force_insert=force_insert,
                                   validate=validate,
                                   clean=clean,
                                   write_concern=write_concern,
                                   cascade=cascade,
                                   cascade_kwargs=cascade_kwargs,
                                   _refs=_refs,
                                   save_condition=save_condition,
                                   signal_kwargs=signal_kwargs,
                                   **kwargs)

        if self._update_refs:
            for value in self.content.values():
                if isinstance(value, DynamicDocument) or isinstance(value, Document):
                    value.referenced_by = list(value._c_refs)
                    value.save()
                    value._changed_fields = []
            setattr(self, '_update_refs', False)

        ret._update_refs = self._update_refs
        return ret

    def __setattr__(self, key, value):
        DynamicDocument.__setattr__(self, key, value)
        if key == 'content':
            print('content')
            if value is not None:
                for c_value in value.values():
                    if isinstance(c_value, DynamicDocument) or isinstance(c_value, Document):
                        c_value._c_refs.add(self)
                        object.__setattr__(self, '_update_refs', True)

        return self


        # if isinstance(self.__getattribute__(key), )

    def delete(self, signal_kwargs=None, **write_concern):
        if self.r
