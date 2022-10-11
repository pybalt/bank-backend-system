from django.db import models
from django.contrib.auth.models import User
from branch.models import Branch
from address.models import Address

# Create your models here.


class CustomerType(models.Model):
    """Database model of customers

    fields:

    [   PK: id,

        customer_type ]
    """
    id = models.AutoField(primary_key=True,
                          unique=True,
                          verbose_name='ID')
    customer_type = models.CharField(max_length=15,
                                     verbose_name='Type', unique=True)


class Customer(models.Model):
    """Database model of customers

    fields:

    [   PK: id,

        user,

        customer_name,

        customer_surname,

        customer_dni,

        customer_type,

        customer_dob,

        branch,

        address ]
    """

    id = models.AutoField(primary_key=True,
                          unique=True,
                          verbose_name='ID')
    user = models.OneToOneField(User,
                                verbose_name="User",
                                unique=True,
                                to_field="id",
                                on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=50,
                                     verbose_name='Name')
    customer_surname = models.CharField(max_length=50,
                                        verbose_name='Surname')
    customer_dni = models.IntegerField(verbose_name='DNI')
    customer_type = models.ForeignKey(CustomerType,
                                      verbose_name="Customer type",
                                      on_delete=models.CASCADE)
    customer_dob = models.DateField(verbose_name='Hire date')
    branch = models.ForeignKey(Branch,
                               on_delete=models.CASCADE,
                               verbose_name='Branch')
    address = models.OneToOneField(Address,
                                   on_delete=models.CASCADE,
                                   verbose_name='Address')

    class Meta:
        managed = True
        db_table = 'customer'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.customer_name}, DNI {self.customer_dni}"

