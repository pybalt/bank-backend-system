from django.db import models


class Country(models.Model):
    """Database model.

    FIELDS: { PK:   id,

                    country_name,

                    code    }

    code field is intended to be used with ISO3166
    """
    id = models.AutoField(primary_key=True, unique=True, verbose_name="ID")

    country_name = models.CharField(max_length=50,
                                    unique=True,
                                    verbose_name="Country name")

    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    # This is intend to be used with ISO 3166

    class Meta:
        managed = True
        db_table = 'country'
        verbose_name = 'Country'

    def __str__(self):
        return self.country_name


class State(models.Model):
    """Database model.

    FIELDS: { PK:   id,

                    state_name,

                    code,

                    country     }

    code field is intended to be used with ISO3166
    """
    id = models.AutoField(primary_key=True,
                          unique=True,
                          verbose_name="ID")
    state_name = models.CharField(max_length=50,
                                  verbose_name="State name")
    code = models.CharField(max_length=20,
                            unique=True,
                            verbose_name="Code")
    country = models.ForeignKey(Country,
                                on_delete=models.CASCADE,
                                to_field='code',
                                verbose_name='Country code')

    class Meta:
        managed = True
        db_table = 'state'
        verbose_name = 'State'

    def __str__(self):
        return self.state_name


class City(models.Model):
    """Database model.

    FIELDS: { PK:   id,

                    city_name,

                    state

                    }

    """
    id = models.AutoField(primary_key=True,
                          unique=True,
                          verbose_name="ID")
    city_name = models.CharField(max_length=50,
                                 verbose_name="City name")
    state = models.ForeignKey(State, on_delete=models.CASCADE,
                              to_field='id',
                              verbose_name='State code')

    class Meta:
        managed = True
        db_table = 'city'
        verbose_name = 'City'

    def __str__(self) -> str:
        return self.city_name


class Address(models.Model):
    """Database model of differents addresses.
    This model is intended to be referred with many to one relationships.

    FIELDS: { PK:  id,

                    address_name,

                    address_number,

                    address_city    }

    """

    id = models.AutoField(primary_key=True,
                          unique=True,
                          verbose_name='ID')
    address_name = models.CharField(max_length=50,
                                    blank=True,
                                    null=True,
                                    verbose_name='Street name')
    address_number = models.IntegerField(blank=True,
                                         null=True,
                                         verbose_name='Street number')

    address_city = models.ForeignKey(City, on_delete=models.CASCADE,
                                     to_field="id",
                                     verbose_name='City')

    class Meta:
        managed = True
        db_table = 'address'
        verbose_name = 'address'

    def __str__(self):
        return f"ID: {self.id}, CITY: {self.address_city}"
