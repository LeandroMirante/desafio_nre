import pytest

from app.users import models


@pytest.mark.django_db
def test_company_create():
    models.Company.objects.create_user(
        name="test", email="test@test.com", password="1234", cnpj="84.730.546/0001-98"
    )
    count = models.Company.objects.all().count()
    print(count)
    assert models.Company.objects.count() == 1
    models.Company.objects.all().delete()


@pytest.mark.django_db
def test_customer_create():
    models.Customer.objects.create_user(
        name="test", email="test@test.com", password="1234", cpf="311.694.800-39"
    )
    count = models.Customer.objects.all().count()
    print(count)
    assert models.Customer.objects.count() == 1
    models.Customer.objects.all().delete()
