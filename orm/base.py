#!/usr/bin/env python
# -*- coding:utf8 -*-

#__author__ == 'godlikeme'
from mylogging.factory import logger1


class Field(object):
    _count = 0

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self._default = kwargs.get('default', None)
        self.primary_key = kwargs.get('primary_key', False)
        self.nullable = kwargs.get("nullable", False)
        self.updatable = kwargs.get('updatable', True)
        self.insertable = kwargs.get('insertable', True)
        self.ddl = kwargs.get('ddl', str)
        self._order = Field._count
        Field._count += 1

    @property
    def default(self):
        d = self._default
        return d() if callable(d) else d

    def __str__(self):
        """
        返回实例对象的描述信息，比如：
            <IntegerField:id,bigint,default(0),UI>
            类：实例：实例ddl属性：实例default信息，3中标志位：N U I
        """
        s = ['<%s:%s, %s, default(%s), ' % (self.__class__.__name__, self.name, self.ddl, self._default)]
        self.nullable and s.append('N')
        self.updatable and s.append('U')
        self.insertable and s.append('I')
        s.append('>')
        return ''.join(s)


class StringField(Field):
    def __init__(self, **kwargs):
        if 'default' not in kwargs:
            kwargs['default'] = ''
        if 'ddl' not in kwargs:
            kwargs['ddl'] = str

        super(StringField, self).__init__(**kwargs)


class IntegerField(Field):
    def __init__(self, **kwargs):
        if 'default' not in kwargs:
            kwargs['default'] = 0
        if 'ddl' not in kwargs:
            kwargs['ddl'] = int

        super(IntegerField, self).__init__(**kwargs)


class FloatField(Field):
    """
    保存Float类型字段的属性
    """
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = 0.0
        if 'ddl' not in kw:
            kw['ddl'] = float
        super(FloatField, self).__init__(**kw)


class BooleanField(Field):
    """
    保存BooleanField类型字段的属性
    """
    def __init__(self, **kw):
        if not 'default' in kw:
            kw['default'] = False
        if not 'ddl' in kw:
            kw['ddl'] = bool
        super(BooleanField, self).__init__(**kw)


class LongField(Field):
    """
    保存Long类型字段额属性
    """
    def __init__(self, **kw):
        if 'default' not in kw:
            kw['default'] = 0L
        if 'ddl' not in kw:
            kw['ddl'] = float
        super(LongField, self).__init__(**kw)



class ModelMataClass(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)

        if not hasattr(cls, "subclasses"):
            cls.subclasses = {}

        if not name in cls.subclasses:
            cls.subclasses[name] = name
        else:
            logger1.warning("Redefin class: %s" % name)

        logger1.info('Scan ORMapping %s...' % name)
        mappings = dict()
        primary_key = None
        mgo_client = None
        file_client = None

        for k, v in attrs.iteritems():
            if isinstance(v, Field):
                if not v.name:
                    v.name = k
                logger1.info('[ Mapping ] Found mapping: %s => %s' % (k, v))

                if v.primary_key:
                    if primary_key:
                        logger1.info("defined more than 1 primary key in class: %s" % name)

                    primary_key = v

                mappings[k] = v

            if isinstance(v, Model):
                mappings[k] = v.__mappings__

            if k == "db_config":
                if "mongo_storer" in v and v["switch"]["mongo"]:
                    mgo_client = v["mongo_storer"]
                if "file_storer" in v and v["switch"]["file"]:
                    file_client = v["file_storer"]

        for k in mappings.iterkeys():
            attrs.pop(k)

        if '__mappings__' not in attrs:
            attrs['__mappings__'] = mappings
        else:
            attrs['__mappings__'].update(mappings)

        if not primary_key:
            raise Exception("need a primary key")
        attrs['__primary_key__'] = primary_key.name

        attrs['__mgo_client__'] = mgo_client
        attrs['__file_client__'] = file_client

        return type.__new__(cls, name, bases, attrs)


class Model(dict):

    __metaclass__ = ModelMataClass

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        """
        get时生效，比如 a[key],  a.get(key)
        get时 返回属性的值
        """
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        """
        set时生效，比如 a[key] = value, a = {'key1': value1, 'key2': value2}
        set时添加属性
        """
        self[key] = value

    def insert(self):
        params = {}
        for k, v in self.__mappings__.iteritems():
            if not hasattr(self, k):
                setattr(self, k, v.default)
            params[v.name] = v.ddl(getattr(self, k))

        pk = self.__primary_key__
        if pk not in params:
            raise Exception(" insert doc need primary key")
        key = {pk: params.get(pk)}
        if self.__mgo_client__:
            self.__mgo_client__.insert(key, params)

        if self.__file_client__:
            self.__file_client__.insert(key, params)


    @classmethod
    def isInField(cls, key):
        if key in cls.__mappings__.keys():
            return True

        return False

    @classmethod
    def convertToObj(cls, items):

        for item in items:
            obj_ = cls()
            for key in item.keys():
                if cls.isInField(key):
                    setattr(obj_, key, item[key])

            yield obj_

    @classmethod
    def get(cls, key, db_type='mongo'):
        if db_type == 'mongo':
            ret = cls.__mgo_client__.find(key)
            for item in cls.convertToObj(ret):
                yield item

        else:
            raise RuntimeError("unknow db_type: %s" % db_type)

    @classmethod
    def get_one(cls, key, db_type='mongo'):
        items = cls.get(key, db_type)
        for item in items:
            return item
        return None

if __name__ == '__main__':
    class Like(Model):
        first_like = StringField()
        second_like = LongField()
    class User(Model):
        name = StringField()
        age = IntegerField()
        like = Like()


    print User.__mappings__

