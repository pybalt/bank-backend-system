from django.db import models
from employee.models import Employee
from account.models import Account
# Create your models here.
class Loan(models.Model):
    class LoanTypes(models.TextChoices):
        PERSONAL = 'PER', 'PERSONAL LOAN'
        MORTGAGE = 'MRT', 'MORTGAGE'
        STUDENT = 'STD', 'STUDENT LOAN'
        AUTO = 'AUT', 'AUTO LOAN'
        PAYDAY = 'PDY', 'PAYDAY LOAN'
        PAWN = 'PWN', 'PAWN SHOP LOAN'
        SMALL = 'SML', 'SMALL BUSINESS LOAN'
    
    
    id = models.AutoField(primary_key=True, verbose_name="ID")
    granter = models.ForeignKey(Employee, on_delete=models.PROTECT)
    amount = models.IntegerField()
    type = models.CharField(choices=LoanTypes.choices, default=LoanTypes.PERSONAL)
    date = models.DateField(auto_now_add=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'loan'
        verbose_name = "Loan"
        verbose_name_plural = "Loans"


    def __str__(self) -> str:
        return f"ID: {self.id} TYPE: {self.type}"    