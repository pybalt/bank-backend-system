from django.db import models

from account.models import Account

# Create your models here.


class TypeCard(models.Model):
    id = models.AutoField(primary_key=True,
                          verbose_name="ID")

    type = models.CharField(max_length=15, unique=True,
                            null=False, blank=False)


class CardProvider(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="ID")
    provider = models.CharField(max_length=15, unique=True,
                                null=False, blank=False)


class Card(models.Model):

    id = models.AutoField(primary_key=True,
                          verbose_name="ID")

    account = models.ForeignKey(Account,
                                on_delete=models.CASCADE,
                                to_field="id",
                                verbose_name="Account id")

    number = models.IntegerField(verbose_name="Card number")

    cvv = models.IntegerField(verbose_name="CVV")

    grant_date = models.DateField(verbose_name="Fecha de otorgamiento",
                                  auto_now_add=True)

    expiry_date = models.DateField(verbose_name="Fecha de expiracion")

    type_card = models.ForeignKey(TypeCard, to_field="id",
                                  on_delete=models.CASCADE,
                                  verbose_name="Type card")

    provider = models.ForeignKey(CardProvider, to_field="id",
                                 on_delete=models.CASCADE,
                                 verbose_name="Card provider")

    class Meta:
        managed = True
        db_table = 'card'
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'
