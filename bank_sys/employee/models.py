from django.db import models
from branch.models import Branch
from address.models import Address
from django.contrib.auth.models import User
# Create your models here.
class Employee(models.Model):
    
    """Database model of customer
    This model is not intended to be referred.
    
    fields:
    
    [   PK: id,
    
        user,
    
        employee_name,
    
        employee_surname,
    
        employee_hire_date,
        
        employee_dni,
        
        branch,
        
        address ]
    """
    
    
    
    id = models.AutoField(primary_key=True, unique=True, verbose_name = 'ID')
    user = models.OneToOneField(User, verbose_name="User", on_delete=models.CASCADE)
    employee_name = models.CharField(max_length= 50, verbose_name = 'Name')
    employee_surname = models.CharField(max_length= 50, verbose_name = 'Surname')
    employee_hire_date = models.DateField(verbose_name = 'Hire date')
    employee_dni = models.IntegerField(verbose_name = 'DNI')
    branch = models.ForeignKey(Branch, on_delete= models.CASCADE, verbose_name = 'Branch')
    address = models.OneToOneField(Address, on_delete= models.CASCADE, unique=True, to_field="id", verbose_name = 'Address')

    class Meta:
        managed = True
        db_table = 'employee'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
    
    def __str__(self):
        return f"{self.employee_name}, {self.employee_surname}"