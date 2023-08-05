import netdot
from assertpy import assert_that


def test_with_alt_name():
    # Arrange
    expected_name = 'Bacon'
    site = netdot.Site(name='TEST')

    # Act
    alt_site = site.with_alternate_name(expected_name)

    # Assert
    assert_that(alt_site.name).is_equal_to(expected_name)


def test_to_raw_with_comment():
    # Arrange
    site = netdot.Site(info='Testing 123')

    # Act
    raw = site.with_comment('test').to_DTO()

    # Assert
    assert_that(raw).contains_entry({'info': 'test'})
