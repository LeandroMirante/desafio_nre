import pytest
from django.shortcuts import reverse
from app.users.models import Company, Customer
import json
from django.contrib.auth.models import Group, Permission
import base64


@pytest.fixture
def company_group(db):
    company_group, created = Group.objects.get_or_create(name="company")

    perms = [
        "Can change company",
        "Can view company",
        "Can add customer",
        "Can change customer",
        "Can delete customer",
        "Can view customer",
    ]

    for i in perms:
        new_perm = Permission.objects.get(name=i)
        company_group.permissions.add(new_perm)
    return company_group


@pytest.fixture
def customer_group(db):
    customer_group, created = Group.objects.get_or_create(name="customer")

    perms = ["Can view customer"]

    for i in perms:
        new_perm = Permission.objects.get(name=i)
        customer_group.permissions.add(new_perm)

    return customer_group


@pytest.fixture
def user_company(db):
    return Company.objects.create_user(
        name="Username 1",
        email="leandro.mirante@hotmail.com",
        password="geladeira55",
        cnpj="84.730.546/0001-98",
        city="Salvador",
    )


@pytest.fixture
def user_company2(db):
    return Company.objects.create_user(
        name="Username 2",
        email="leandro.mirante2@hotmail.com",
        password="geladeira55",
        cnpj="84.730.546/0001-98",
    )


@pytest.fixture
def user_customer1(db, user_company):
    return Customer.objects.create_user(
        name="Customer 1",
        email="teste.customer@teste.com",
        password="geladeira55",
        cpf="874.276.280-47",
        company_name=user_company,
    )


@pytest.fixture
def user_customer2(db, user_company):
    return Customer.objects.create_user(
        name="Customer 2",
        email="teste.customer2@teste.com",
        password="geladeira55",
        cpf="874.276.280-47",
        company_name=user_company,
    )


@pytest.fixture
def token(db, client, mocker, user_company):
    response = client.post(
        reverse("login"),
        data=json.dumps(
            {"email": "leandro.mirante@hotmail.com", "password": "geladeira55"}
        ),
        content_type="application/json",
    )
    return response.json().get("tokens")


@pytest.fixture
def token_customer(db, client, mocker, user_customer1):
    response = client.post(
        reverse("login"),
        data=json.dumps(
            {"email": "teste.customer@teste.com", "password": "geladeira55"}
        ),
        content_type="application/json",
    )
    return response.json().get("tokens")


@pytest.fixture
def base_64_image():
    with open("deslize-para-a-esquerda.png", "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
        return str(my_string.decode("utf-8"))
