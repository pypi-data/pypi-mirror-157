from mongoengine import Document, StringField, DateTimeField, FileField, ListField, GenericLazyReferenceField
from datetime import datetime
from .fields import DataFrameField, NPArrayField


class Dataframe(Document):

    name = StringField()
    type = StringField()
    data = DataFrameField()
    date_created = DateTimeField(default=datetime.utcnow)
    date_modified = DateTimeField(default=datetime.utcnow)
    referenced_by = ListField(GenericLazyReferenceField(null=True))

    meta = {'allow_inheritance': True}

    def __init__(self, *args, **kwargs):
        super(Dataframe, self).__init__(*args, **kwargs)

        self.name = kwargs.get('name', None)
        self.type = kwargs.get('name', 'Dataframe')
        self.data = kwargs.get('data', None)
        self.referenced_by = kwargs.get('comp_refs', [])

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
        return Document.save(self,
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


class NumpyArray(Document):

    name = StringField()
    type = StringField()
    data = NPArrayField()
    date_created = DateTimeField(default=datetime.utcnow)
    date_modified = DateTimeField(default=datetime.utcnow)
    referenced_by = ListField(GenericLazyReferenceField(null=True))

    meta = {'allow_inheritance': True}

    def __init__(self, *args, **kwargs):
        super(NumpyArray, self).__init__(*args, **kwargs)

        self.name = kwargs.get('name', None)
        self.type = kwargs.get('name', 'NumpyArray')
        self.data = kwargs.get('data', None)
        self.referenced_by = kwargs.get('comp_refs', [])

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
        return Document.save(self,
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


class File(Document):

    name = StringField()
    type = StringField()
    data = FileField()
    file_format = StringField()
    date_created = DateTimeField(default=datetime.utcnow)
    date_modified = DateTimeField(default=datetime.utcnow)
    referenced_by = ListField(GenericLazyReferenceField(null=True))

    meta = {'allow_inheritance': True}

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)

        self.name = kwargs.get('name', None)
        self.type = kwargs.get('name', 'File')
        self.data = kwargs.get('data', None)
        self.file_format = kwargs.get('file_format')

        self._c_refs = set()
        self.referenced_by = kwargs.get('comp_refs', [])

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
        return Document.save(self,
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
