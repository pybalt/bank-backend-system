from django.db import models
from branch.models import Branch
from address.models import Address
# Create your models here.
class Employee(models.Model):
    
    """Database model of branches
    This model is intended to be referred with many to one relationships
    
    fields:
    
    [   PK: id,
    
        employee_name,
    
        employee_surname,
    
        employee_hire_date,
        
        employee_dni,
        
        branch,
        
        address ]
    """
    
    
    
    id = models.AutoField(primary_key=True, unique=True, verbose_name = 'ID')
    employee_name = models.CharField(max_length= 50, verbose_name = 'Name')
    employee_surname = models.CharField(max_length= 50, verbose_name = 'Surname')
    employee_hire_date = models.DateField(verbose_name = 'Hire date')
    employee_dni = models.IntegerField(verbose_name = 'DNI')
    branch = models.ForeignKey(Branch, on_delete= models.CASCADE, verbose_name = 'Branch')
    address = models.ForeignKey(Address, on_delete= models.CASCADE, verbose_name = 'Address')

    class Meta:
        managed = True
        db_table = 'employee'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
    
    def __str__(self):
        return f"{self.employee_name}, {self.employee_surname}"