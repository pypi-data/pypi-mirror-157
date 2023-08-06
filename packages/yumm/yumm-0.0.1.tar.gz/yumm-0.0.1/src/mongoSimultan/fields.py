from mongoengine import fields
from numpy import generic
from numpy import ndarray
from numpy import array as np_array
from pandas import DataFrame, MultiIndex


def _as_native(x):
    if isinstance(x, dict):
        return dict([(k, _as_native(v)) for k, v in x.items()])
    elif isinstance(x, list):
        return [_as_native(v) for v in x]
    else:
        return x


class NPArrayField(fields.ListField):
    """A pandas DataFrame field.
    Looks to the outside world like a Pandas.DataFrame, but stores
    in the database as an using Pandas.DataFrame.to_dict("list").
    """
    def __init__(self, orient="list", *args, **kwargs):
        if orient not in ('dict', 'list', 'series', 'split', 'records', 'index'):
            raise ValueError(u"orient must be one of ('dict', 'list', 'series', 'split', 'records', 'index') but got: %s")
        self.orient = orient
        super(NPArrayField, self).__init__(*args, **kwargs)

    def __get__(self, instance, owner):
        print("__get__:", instance, owner)
        # df = pd.DataFrame.from_dict(_as_native(super(DataFrameField, self).__get__(instance, owner)))
        array = np_array(_as_native(super(NPArrayField, self).__get__(instance, owner)))
        return array

    def __set__(self, instance, value):
        if value is None or isinstance(value, list):
            return super(NPArrayField, self).__set__(instance, value)
        if not isinstance(value, ndarray):
            raise ValueError("value is not a np.ndarray instance")
        obj = value.tolist()
        # coerce numpy objects into python objects for lack of the BSON-numpy package on windows
        return super(NPArrayField, self).__set__(instance, obj)

    def to_python(self, value):
        return value


class MongoDF(DataFrame):

    _attributes_ = "instance, owner"

    def __init__(self, *args, **kw):
        super(MongoDF, self).__init__(*args, **kw)
        if len(args) == 1 and isinstance(args[0], MongoDF):
            args[0]._copy_attrs(self)

    def _copy_attrs(self, df):
        for attr in self._attributes_.split(","):
            df.__dict__[attr] = getattr(self, attr, None)

    @property
    def _constructor(self):
        def f(*args, **kw):
            df = MongoDF(*args, **kw)
            self._copy_attrs(df)
            return df

        return f


class DataFrameField(fields.DictField):
    """A pandas DataFrame field.
    Looks to the outside world like a Pandas.DataFrame, but stores
    in the database as an using Pandas.DataFrame.to_dict("list").
    """
    def __init__(self, orient="list", *args, **kwargs):
        if orient not in ('dict', 'list', 'series', 'split', 'records', 'index'):
            raise ValueError(u"orient must be one of ('dict', 'list', 'series', 'split', 'records', 'index') but got: %s")
        self.orient = orient
        super(DataFrameField, self).__init__(*args, **kwargs)

    def __get__(self, instance, owner):
        print("__get__:", instance, owner)
        # df = pd.DataFrame.from_dict(_as_native(super(DataFrameField, self).__get__(instance, owner)))
        df = MongoDF.from_dict(_as_native(super(DataFrameField, self).__get__(instance, owner)))
        df.instance = instance
        df.owner = owner

        return df

    def __set__(self, instance, value):
        if value is None or isinstance(value, dict):
            return super(DataFrameField, self).__set__(instance, value)
        if not isinstance(value, DataFrame):
            raise ValueError("value is not a pandas.DataFrame instance")
        if isinstance(value.index, MultiIndex):
            self.error(u'value.index is a MultiIndex; MultiIndex objects may not be stored in MongoDB.  Consider using `value.reset_index()` to flatten')
        if isinstance(value.keys(), MultiIndex):
            self.error(u'value.keys() is a MultiIndex; MultiIndex objects may not be stored in MongoDB.  Consider using `value.unstack().reset_index()` to flatten')
        obj = value.to_dict(self.orient)
        # coerce numpy objects into python objects for lack of the BSON-numpy package on windows
        for col in obj.values():
            if len(col) and isinstance(col[0], generic):
                for i in range(len(col)):
                    col[i] = col[i].item()
        return super(DataFrameField, self).__set__(instance, obj)

    def to_python(self, value):
        return value
