from ast import Add
from django.db import models
from address.models import Address
# Create your models here.
class Branch(models.Model):
    """Database model of branches
    This model is intended to be referred with many to one relationships
    
    fields:
    
    [   PK: id,
    
        branch_number,
    
        branch_name,
    
        branch_address  ]
    """
    
    
    id = models.AutoField(primary_key= True, unique=True, verbose_name = 'ID')
    branch_number = models.IntegerField(verbose_name = 'Branch number', unique=True)
    branch_name = models.CharField(max_length = 50, verbose_name = 'Branch name', unique=True)
    branch_address = models.OneToOneField(Address, on_delete= models.CASCADE, to_field="id", unique=True, verbose_name = 'Address')
    
    class Meta:
        managed = True
        db_table = 'branch'
        verbose_name = 'branch'
        verbose_name_plural = 'branches'
    
    def __str__(self):
        return f"{self.id}: {self.branch_name}"