import json
from django.shortcuts import reverse
from rest_framework import status
import ast
from app.users.models import Customer


def test_register(client, user_company, company_group):
    payload = {
        "name": "test",
        "email": "test@test.com",
        "password": "geladeira55",
        "cnpj": "84.730.546/0001-98",
    }
    response = client.post(
        reverse("register"),
        data=payload,
        content_type="application/json",
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_login(client, user_company, company_group):
    payload = {"email": "leandro.mirante@hotmail.com", "password": "geladeira55"}
    response = client.post(
        reverse("login"),
        data=payload,
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_200_OK


def test_change_password_user_company_success(
    client, user_company, token, company_group
):

    payload = json.dumps({"old_password": "geladeira55", "new_password": "abc1234"})
    tk = ast.literal_eval(token)["access"]

    response = client.put(
        reverse("change-password-confirm"),
        data=payload,
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer {}".format(tk),
    )

    assert response.status_code == status.HTTP_200_OK


def test_access_only_same_company_data(client, user_company, token, company_group):
    tk = ast.literal_eval(token)["access"]

    response = client.get(
        reverse("company-list"),
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer {}".format(tk),
    )

    assert response.json().get("count") == 1


def test_access_customers_same_company(
    client,
    user_company,
    token,
    user_customer1,
    user_customer2,
    company_group,
    customer_group,
):
    tk = ast.literal_eval(token)["access"]

    response = client.get(
        reverse("customer-list"),
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer {}".format(tk),
    )

    def is_same_company():
        for i in range(len(response.json()["results"])):
            if not int(response.json()["results"][i]["company_name"][-2]) == 1:
                return False
        return True

    assert is_same_company()


def test_edit_company_user(
    db,
    client,
    user_company,
    user_customer1,
    token,
    company_group,
    mocker,
    customer_group,
):
    tk = ast.literal_eval(token)["access"]

    payload = json.dumps(
        {
            "email": "leandro.mirante@hotmail.com",
            "cnpj": "84.730.546/0001-98",
            "city": "Feira de Santana",
        }
    )

    response = client.patch(
        "/v1/company/1/",
        content_type="application/json",
        data=payload,
        HTTP_AUTHORIZATION="Bearer {}".format(tk),
    )
    print(response.status_code)

    assert response.status_code == status.HTTP_200_OK


def test_create_customer_user(
    db,
    client,
    user_company,
    user_customer1,
    token,
    company_group,
    mocker,
    customer_group,
):
    tk = ast.literal_eval(token)["access"]

    payload = json.dumps(
        {
            "name": "Customer by api",
            "cpf": "05698913536",
            "email": "customerapi@teste.com",
            "password": "geladeira55",
        }
    )

    response = client.post(
        "/v1/customer/",
        content_type="application/json",
        data=payload,
        HTTP_AUTHORIZATION="Bearer {}".format(tk),
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_send_documents_to_customer(
    db,
    client,
    user_company,
    user_customer1,
    token,
    company_group,
    mocker,
    base_64_image,
    customer_group,
):
    tk = ast.literal_eval(token)["access"]

    payload = json.dumps({"documents": base_64_image})

    response = client.patch(
        "/v1/customer/2/",
        content_type="application/json",
        data=payload,
        HTTP_AUTHORIZATION="Bearer {}".format(tk),
    )

    assert response.status_code == status.HTTP_200_OK


def test_delete_customer_user(
    db,
    client,
    user_company,
    user_customer1,
    token,
    company_group,
    mocker,
    customer_group,
):
    tk = ast.literal_eval(token)["access"]

    response = client.delete(
        "/v1/customer/2/",
        content_type="application/json",
        HTTP_AUTHORIZATION="Bearer {}".format(tk),
    )

    assert response.status_code == 204


def test_update_customer_user(
    db,
    client,
    user_company,
    user_customer1,
    token,
    company_group,
    mocker,
    customer_group,
):
    tk = ast.literal_eval(token)["access"]

    payload = json.dumps(
        {
            "name": "Customer edited",
        }
    )

    response = client.patch(
        "/v1/customer/2/",
        content_type="application/json",
        data=payload,
        HTTP_AUTHORIZATION="Bearer {}".format(tk),
    )

    assert response.status_code == status.HTTP_200_OK


def test_customer_access_only_their_data(
    db,
    client,
    user_customer1,
    token_customer,
    user_customer2,
    customer_group,
    company_group,
):
    tk = ast.literal_eval(token_customer)["access"]

    response = client.get(
        reverse("customer-list"), HTTP_AUTHORIZATION="Bearer {}".format(tk)
    )
    assert Customer.objects.all().count() == 2
    assert response.json()["count"] == 1
    assert response.json()["results"][0]["email"] == "teste.customer@teste.com"


def test_reset_password_by_email(client, user_company, company_group):

    payload = json.dumps({"email": "leandro.mirante@hotmail.com"})

    response = client.post(
        reverse("request-reset-email"), data=payload, content_type="application/json"
    )

    assert response.status_code == status.HTTP_200_OK
