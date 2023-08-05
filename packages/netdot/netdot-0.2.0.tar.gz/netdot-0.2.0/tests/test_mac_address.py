import pytest
from assertpy import assert_that

from netdot.mac_address import MACAddress


def test_all_lowercase():
    # Act
    mac = MACAddress('AABBCCDDEEFF')
    # Assert
    assert str(mac) == 'aabbccddeeff'


def test_output_with_delimeter():
    # Act
    mac = MACAddress('AABBCCDDEEFF')
    # Assert
    assert mac.format(delimeter=':') == 'aa:bb:cc:dd:ee:ff'


@pytest.mark.parametrize(
    'valid_delimeter', [
        '.',
        ':',
        '-',
        ' ',
    ]
)
def test_parse_valid_delimeters(valid_delimeter):
    # Act
    d = valid_delimeter
    mac = MACAddress(f'AA{d}BB{d}CC{d}DD{d}EE{d}FF')
    # Assert
    assert str(mac) == 'aabbccddeeff'


def test_whitespace():
    # Act
    mac = MACAddress('''
        AA BB CC DD EE FF    

    ''')
    # Assert
    assert str(mac) == 'aabbccddeeff'


def test_invalid_delimeter():
    # Arrange & Assert
    with pytest.raises(ValueError):
        # Act
        MACAddress('AA+BB+CC+DD+EE+FF')


def test_inconsistent_delimeters():
    # Act
    mac = MACAddress('AA BB CC.DD-EE:FF')
    # Assert
    assert str(mac) == 'aabbccddeeff'


def test_equality():
    # Arrange
    mac1 = MACAddress('AABBCCDDEEFF') 
    mac2 = MACAddress('AABBCCDDEEFF') 

    # Act & Assert
    assert mac1 == mac2
    assert_that(mac1).is_equal_to(mac2)
