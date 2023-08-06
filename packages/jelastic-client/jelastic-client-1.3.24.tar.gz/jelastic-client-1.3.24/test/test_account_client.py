from jelastic_client.account_client import AccountClient


def test_account_client_retrieves_email_from_account(
        account_client: AccountClient,
        jelastic_user_email: str
):
    # Arrange

    # Act
    user_info = account_client.get_user_info()
    actual_user_email = user_info.email()

    # Assert
    assert jelastic_user_email == actual_user_email
