Cats Serialization
==================
 
## Introduction
 
It is a simple, extensible and functional serializer for objects.
The goal of the project is to provide a developer with a simple tool for developing REST applications... and not only =)

More information in [wiki](http://git.vovikilelik.com/Clu/cats-serialization-10/wiki)

## Uses

### Basic creation scheme

Its just inherit on Scheme class

```python
class MyScheme(Scheme):

    # annotation style
    string_field: str
    integer_field: int
    simple_list: list
    sub_scheme: ChildScheme

    # field style
    some_field = fields.BasicField(ChildScheme)
    
    # iterable
    iterable_field = fields.IterableField(ElementScheme)

    # method style
    @classmethod
    def functional_field(cls, data)
        return data.sub_field, 'override_name_if_needed'
```

### Basic serialisation

```python
dict_from_object = MyScheme.serialize(obj)
```

Ok... Now, **dict_from_object** able to transform to **json** or anything...