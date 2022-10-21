from typing import Type
from django.db import models

# Create your models here.
from django.db import models
from django.forms import CharField, FileField
from django.utils import timezone

from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from django.contrib.auth.models import PermissionsMixin

from django.db.models import Q
from model_utils import Choices

from django_cpf_cnpj.fields import CPFField, CNPJField

from django.db.models.signals import pre_save, post_save

class LowercaseEmailField(models.EmailField):
    """
    Override EmailField to convert emails to lowercase before saving.
    """
    def to_python(self, value):
        """
        Convert email to lowercase.
        """
        value = super(LowercaseEmailField, self).to_python(value)
        # Value can be None so check that it's a string before lowercasing.
        if isinstance(value, str):
            return value.lower()
        return value

class User(AbstractBaseUser, PermissionsMixin):
    email = LowercaseEmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    city = models.CharField(
        max_length=50, verbose_name=_("Cidade"), blank=True, null=True
    )
    address = models.CharField(
        max_length=100, verbose_name=_("Endereço"), blank=True, null=True
    )
    district = models.CharField(
        max_length=50, verbose_name=_("Bairro"), blank=True, null=True
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "Ativo ou inativo"
        ),
        verbose_name=_("Status"),
    )
    Types = Choices(
        ("Admin", "Admin"),
        ("Company", "Company"),
        ("CUSTOMER", "Customer")
    )
    type = models.CharField(
        max_length=20, default="Admin", choices=Types
    )

    default_type = "Admin"

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.type = self.default_type
        return super().save(*args, **kwargs)

# Model Managers for proxy models
class CompanyManager(models.Manager):
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)    
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains = User.Types.Company))

class CustomerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains = User.Types.CUSTOMER))


# Proxy Models. They do not create a seperate table
class Company(User):
    default_type = User.Types.Company
    objects = CompanyManager()
    cnpj = CNPJField(masked=True)
    class Meta:
        proxy = False
    type = User.Types.Company

class Customer(User):
    default_type = User.Types.CUSTOMER
    company_name = models.ForeignKey(Company, verbose_name=_("Company"),null=True, on_delete=models.CASCADE)
    objects = CustomerManager()
    def company(self):
        return self.company_name
    type = User.Types.CUSTOMER
    cpf = CPFField(masked=True)
    documents = models.ImageField(upload_to='files', null=True)

    class Meta:
        proxy = False 

def deactivateCustomers(sender, instance, created, **kwargs):
    print(instance.is_active)
    for j in Customer.objects.all():
        print(j.company_name)
        if(str(instance) == str(j.company_name) and instance.is_active == False):
            j.is_active = False
            j.save()
        if(str(instance) == str(j.company_name) and instance.is_active == True):
            j.is_active = True
            j.save()

def addCompanyToGroup(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(1)

def addCustomerToGroup(sender, instance, created, **kwargs):
    if created:
        instance.groups.add(2)


post_save.connect(deactivateCustomers, sender=Company)
post_save.connect(addCompanyToGroup, sender=Company)
post_save.connect(addCustomerToGroup, sender=Customer)


