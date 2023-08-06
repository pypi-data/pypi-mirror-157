from .core import SimpleField
from .core import FieldDescriptor
from .core import FieldGroup
from .core.enums import FieldKind

class AudienceGroup(FieldGroup):
    def __init__(self,
                 document):
        super(AudienceGroup, self).__init__(document)
        self._fields['description'] = SimpleField(database_object=document,
                                                  aspect='audience',
                                                  field_locator='audience.description',
                                                  dtype=str,
                                                  nullable=True)

        self._fields['audience_code'] = SimpleField(database_object=document,
                                                    aspect='audience',
                                                    field_locator='audience.audience_code',
                                                    dtype=str)

        self._fields['onix_adult_audience_rating'] = SimpleField(database_object=document,
                                                    aspect='audience',
                                                    field_locator='audience.onix_adult_audience_rating',
                                                    dtype=str)
        

        self._fields['age_range'] = AgeRangeGroup(document=document)


    description = FieldDescriptor('description')
    audience_code = FieldDescriptor('audience_code')
    onix_adult_audience_rating = FieldDescriptor('onix_adult_audience_rating')
    age_range = FieldDescriptor('age_range')


class AgeRangeGroup(FieldGroup):
    def __init__(self,
                 document):
        super(AgeRangeGroup, self).__init__(document)
        self._fields['since'] = SimpleField(database_object=document,
                                            aspect='audience',
                                            field_locator='audience.age_range_from',
                                            dtype=int,
                                            kind=FieldKind.readonly,
                                            nullable=True)

        self._fields['till'] = SimpleField(database_object=document,
                                           aspect='audience',
                                           field_locator='audience.age_range_to',
                                           dtype=int,
                                           kind=FieldKind.readonly,
                                           nullable=True)

    since = FieldDescriptor('since')
    till = FieldDescriptor('till')

    def __iter__(self):
        return iter((self.since, self.till))

    def __getitem__(self, key):
        return (self.since, self.till)[key]

    def __len__(self):
        return 2

    def __str__(self):
        return str((self.since, self.till))
