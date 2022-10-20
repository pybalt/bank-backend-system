from django.db import models
from customer.models import Customer
# Create your models here.


class TypeAccount(models.Model):
    """Database model of TypeAccount

    fields:

    [   PK: id,

        type,

        code

        ]
    """
    id = models.AutoField(primary_key=True,
                          unique=True,
                          verbose_name="ID")
    type = models.CharField(max_length=25, unique=True,
                            verbose_name="Type")
    code = models.CharField(max_length=8, unique=True,
                            verbose_name="code")


class Account(models.Model):
    """Database model of Account

    fields:

    [   PK: id,

        customer,

        balance,

        type,

        iban

    ]
    """
    id = models.AutoField(primary_key=True,
                          unique=True,
                          verbose_name="ID")

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 to_field="id", verbose_name="Customer")

    balance = models.IntegerField(verbose_name="Balance")

    type = models.ForeignKey(TypeAccount, on_delete=models.CASCADE,
                             to_field="code",
                             verbose_name="Account type")

    iban = models.CharField(max_length=10, editable=False,
                            verbose_name="""IBAN.""")

    class Meta:
        managed = True
        db_table = 'account'

    def __str__(self):
        return str(f"{self.id}, {self.customer}, {self.type}")
