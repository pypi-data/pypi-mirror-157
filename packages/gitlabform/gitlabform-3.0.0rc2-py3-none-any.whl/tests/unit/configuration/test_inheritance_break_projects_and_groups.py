import logging
import pytest

from gitlabform.configuration import Configuration
from gitlabform import EXIT_INVALID_INPUT

logger = logging.getLogger(__name__)


@pytest.fixture
def configuration_with_break_inheritance_from_group_level_set_at_project_level():
    config_yaml = """
    ---
    projects_and_groups:
      "some_group/*":
        variables:
          first:
            key: foo
            value: bar

      "some_group/my_project":
        variables:
          inherit: false
          second:
            key: bizz
            value: buzz
        public_variables:
          key: fizz
          value: fuzz
    
      "some_group/my_other_project":
        variables:
          fourth:
            key: foo4
            value: bar4
    """
    return Configuration(config_string=config_yaml)


def test__get_effective_config_for_project__with_invalid_inheritance_break_set_at_common_level():
    config_yaml = """
        ---
        projects_and_groups:
          "*":
            variables:
              inherit: false
              first:
                key: foo
                value: bar
        """

    with pytest.raises(SystemExit) as exception:
        Configuration(config_string=config_yaml).get_effective_config_for_project(
            "another_group/another_project"
        )
    assert exception.type == SystemExit
    assert exception.value.code == EXIT_INVALID_INPUT


def test__get_effective_config_for_project__with_invalid_inheritance_break_set_at_group_level():
    config_yaml = """
    ---
    projects_and_groups:
      "some_group/*":
        variables:
          inherit: false
          first:
            key: foo
            value: bar

      "some_group/my_project":
        variables:
          second:
            key: bizz
            value: buzz
    """

    with pytest.raises(SystemExit) as exception:
        Configuration(config_string=config_yaml).get_effective_config_for_project(
            "some_group/my_project"
        )
    assert exception.type == SystemExit
    assert exception.value.code == EXIT_INVALID_INPUT


def test__get_effective_config_for_project__with_invalid_inheritance_break_set_at_project_level():
    config_yaml = """
    ---
    projects_and_groups:
      "some_group/my_project":
        variables:
          inherit: false
          second:
            key: bizz
            value: buzz
    """

    with pytest.raises(SystemExit) as exception:
        Configuration(config_string=config_yaml).get_effective_config_for_project(
            "some_group/my_project"
        )
    assert exception.type == SystemExit
    assert exception.value.code == EXIT_INVALID_INPUT


def test__get_effective_config_for_my_project__with_break_inheritance_from_multiple_levels_set_at_project_level():
    config_yaml = """
    ---
    projects_and_groups:
      "*":
        variables:
          third:
            key: foo
            value: bar

      "some_group/*":
        variables:
          first:
            key: foo
            value: bar

      "some_group/my_project":
        variables:
          inherit: false
          second:
            key: bizz
            value: buzz
    """

    configuration = Configuration(config_string=config_yaml)

    effective_config = configuration.get_effective_config_for_project(
        "some_group/my_project"
    )

    variables = effective_config["variables"]

    assert variables == {
        "second": {"key": "bizz", "value": "buzz"},
    }


def test__get_effective_config_for_my_project__with_break_inheritance_from_common_levels_set_at_group_level():
    config_yaml = """
    ---
    projects_and_groups:
      "*":
        variables:
          third:
            key: foo
            value: bar

      "some_group/*":
        variables:
          inherit: false
          first:
            key: foo
            value: bar

      "some_group/my_project":
        variables:
          second:
            key: bizz
            value: buzz
    """

    configuration = Configuration(config_string=config_yaml)

    effective_config = configuration.get_effective_config_for_project(
        "some_group/my_project"
    )

    variables = effective_config["variables"]

    assert variables == {
        "first": {"key": "foo", "value": "bar"},
        "second": {"key": "bizz", "value": "buzz"},
    }


def test__get_effective_config_for_my_project__with_break_inheritance_from_common_levels_set_at_project_level():
    config_yaml = """
    ---
    projects_and_groups:
      "*":
        variables:
          third:
            key: foo
            value: bar

      "some_group/*":
        members:
          users:
            user1: developer
            user2: developer

      "some_group/my_project":
        variables:
          inherit: false
          second:
            key: bizz
            value: buzz
    """

    configuration = Configuration(config_string=config_yaml)

    effective_config = configuration.get_effective_config_for_project(
        "some_group/my_project"
    )

    assert effective_config == {
        "members": {
            "users": {
                "user1": "developer",
                "user2": "developer",
            }
        },
        "variables": {
            "second": {"key": "bizz", "value": "buzz"},
        },
    }


def test__get_effective_config_for_my_project__with_break_inheritance_from_group_level_set_at_project_level(
    configuration_with_break_inheritance_from_group_level_set_at_project_level,
):
    effective_config = configuration_with_break_inheritance_from_group_level_set_at_project_level.get_effective_config_for_project(
        "some_group/my_project"
    )

    assert effective_config == {
        "variables": {
            "second": {"key": "bizz", "value": "buzz"},
        },
        "public_variables": {"key": "fizz", "value": "fuzz"},
    }


def test__get_effective_config_for_my_other_project__with_break_inheritance_from_group_level_set_at_project_level(
    configuration_with_break_inheritance_from_group_level_set_at_project_level,
):
    effective_config = configuration_with_break_inheritance_from_group_level_set_at_project_level.get_effective_config_for_project(
        "some_group/my_other_project"
    )

    variables = effective_config["variables"]

    assert variables == {
        "first": {"key": "foo", "value": "bar"},
        "fourth": {"key": "foo4", "value": "bar4"},
    }


def test__get_effective_config_for_my_project__with_break_inheritance_from_common_and_group_level_set_at_group_and_project_level():
    config_yaml = """
    ---
    projects_and_groups:
      "*":
        variables:
          third:
            key: foo
            value: bar

      "some_group/*":
        variables:
          inherit: false
          first:
            key: foo
            value: bar
        members:
          users:
            user1: developer
            user2: developer

      "some_group/my_project":
        variables:
          second:
            key: bizz
            value: buzz
        members:
          inherit: false
          users:
            user3: maintainer
            user4: maintainer
    """

    configuration = Configuration(config_string=config_yaml)

    effective_config = configuration.get_effective_config_for_project(
        "some_group/my_project"
    )

    assert effective_config == {
        "variables": {
            "first": {"key": "foo", "value": "bar"},
            "second": {"key": "bizz", "value": "buzz"},
        },
        "members": {
            "users": {
                "user3": "maintainer",
                "user4": "maintainer",
            },
        },
    }
