import pytest
from src.utils import eleva_quadrado, requires_role
from unittest.mock import Mock, patch
from http import HTTPStatus


@pytest.mark.parametrize("test_input, expected", [(2, 4), (10, 100), (3, 9)])
def test_eleva_quadrado_sucess(test_input, expected):
    resultado = eleva_quadrado(test_input)
    assert resultado == expected


def test_requires_role_success(mocker):
    # Given
    mock_user = mocker.Mock()
    mock_user.role.name = 'admin'
    mocker.patch('src.utils.get_jwt_identity')
    mocker.patch('src.utils.db.get_or_404', return_value=mock_user)
    decorated_function = requires_role('admin')(lambda: "success")
    
    # When
    result = decorated_function()

    # Then
    assert result == "success"
   

def test_requires_role_failure():
    mock_user = Mock()
    mock_user.role.name = 'normal'
    
    with patch('src.utils.get_jwt_identity'), patch('src.utils.db.get_or_404', return_value=mock_user):
        decorated_function = requires_role('admin')(lambda: "success")
        result = decorated_function()

    assert result == ({"message": "User does not have permission."}, HTTPStatus.FORBIDDEN)
