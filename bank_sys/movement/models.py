from django.db import models
from django.core.exceptions import ValidationError
from account.models import Account
# Create your models here.


class Movement(models.Model):

    id = models.AutoField(primary_key=True, verbose_name="ID")
    amount = models.IntegerField(verbose_name="Amount")
    description = models.CharField(max_length=30)
    date = models.DateField(auto_now_add=True)
    recipient = models.ForeignKey(Account, on_delete=models.CASCADE,
                               verbose_name="Recipient", related_name='recipient')
    sender = models.ForeignKey(Account, on_delete=models.CASCADE,
                               verbose_name="Sender", related_name='sender')
    
    def clean(self):
        if self.recipient == self.sender:
            raise ValidationError("This operation doesn't make sense.")
    
    class Meta:
        managed = True
        db_table = 'movement'
        verbose_name = "Movement"
        verbose_name_plural = "Movements"
    
    def __str__(self):
        return f"Movement N{self.id}"
    