# (c) 2021 Red Hat Inc.
#
# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
import botocore
import boto3
import json

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule

DUMMY_VERSION = '5.5.5.5'

TEST_VERSIONS = [
    ['1.1.1', '2.2.2', True],
    ['1.1.1', '0.0.1', False],
    ['9.9.9', '9.9.9', True],
    ['9.9.9', '9.9.10', True],
    ['9.9.9', '9.10.9', True],
    ['9.9.9', '10.9.9', True],
    ['9.9.9', '9.9.8', False],
    ['9.9.9', '9.8.9', False],
    ['9.9.9', '8.9.9', False],
    ['10.10.10', '10.10.10', True],
    ['10.10.10', '10.10.11', True],
    ['10.10.10', '10.11.10', True],
    ['10.10.10', '11.10.10', True],
    ['10.10.10', '10.10.9', False],
    ['10.10.10', '10.9.10', False],
    ['10.10.10', '9.19.10', False],
]


class TestRequireAtLeast(object):
    # ========================================================
    # Prepare some data for use in our testing
    # ========================================================
    def setup_method(self):
        pass

    # ========================================================
    #   Test botocore_at_least
    # ========================================================
    @pytest.mark.parametrize("stdin, desired_version, compare_version, at_least", [({}, *d) for d in TEST_VERSIONS], indirect=["stdin"])
    def test_botocore_at_least(self, monkeypatch, stdin, desired_version, compare_version, at_least, capfd):
        monkeypatch.setattr(botocore, "__version__", compare_version)
        # Set boto3 version to a known value (tests are on both sides) to make
        # sure we're comparing the right library
        monkeypatch.setattr(boto3, "__version__", DUMMY_VERSION)

        # Create a minimal module that we can call
        module = AnsibleAWSModule(argument_spec=dict())

        assert at_least == module.botocore_at_least(desired_version)

    # ========================================================
    #   Test boto3_at_least
    # ========================================================
    @pytest.mark.parametrize("stdin, desired_version, compare_version, at_least", [({}, *d) for d in TEST_VERSIONS], indirect=["stdin"])
    def test_boto3_at_least(self, monkeypatch, stdin, desired_version, compare_version, at_least, capfd):
        # Set botocore version to a known value (tests are on both sides) to make
        # sure we're comparing the right library
        monkeypatch.setattr(botocore, "__version__", DUMMY_VERSION)
        monkeypatch.setattr(boto3, "__version__", compare_version)

        # Create a minimal module that we can call
        module = AnsibleAWSModule(argument_spec=dict())

        assert at_least == module.boto3_at_least(desired_version)

    # ========================================================
    #   Test require_botocore_at_least
    # ========================================================
    @pytest.mark.parametrize("stdin, desired_version, compare_version, at_least", [({}, *d) for d in TEST_VERSIONS], indirect=["stdin"])
    def test_require_botocore_at_least(self, monkeypatch, stdin, desired_version, compare_version, at_least, capfd):
        monkeypatch.setattr(botocore, "__version__", compare_version)
        # Set boto3 version to a known value (tests are on both sides) to make
        # sure we're comparing the right library
        monkeypatch.setattr(boto3, "__version__", DUMMY_VERSION)

        # Create a minimal module that we can call
        module = AnsibleAWSModule(argument_spec=dict())

        with pytest.raises(SystemExit) as e:
            module.require_botocore_at_least(desired_version)
            module.exit_json()

        out, err = capfd.readouterr()
        return_val = json.loads(out)

        assert return_val.get("exception") is None
        assert return_val.get("invocation") is not None
        if at_least:
            assert return_val.get("failed") is None
        else:
            assert return_val.get("failed")
            # The message is generated by Ansible, don't test for an exact
            # message
            assert desired_version in return_val.get("msg")
            assert "botocore" in return_val.get("msg")
            assert return_val.get("boto3_version") == DUMMY_VERSION
            assert return_val.get("botocore_version") == compare_version

    # ========================================================
    #   Test require_boto3_at_least
    # ========================================================
    @pytest.mark.parametrize("stdin, desired_version, compare_version, at_least", [({}, *d) for d in TEST_VERSIONS], indirect=["stdin"])
    def test_require_boto3_at_least(self, monkeypatch, stdin, desired_version, compare_version, at_least, capfd):
        monkeypatch.setattr(botocore, "__version__", DUMMY_VERSION)
        # Set boto3 version to a known value (tests are on both sides) to make
        # sure we're comparing the right library
        monkeypatch.setattr(boto3, "__version__", compare_version)

        # Create a minimal module that we can call
        module = AnsibleAWSModule(argument_spec=dict())

        with pytest.raises(SystemExit) as e:
            module.require_boto3_at_least(desired_version)
            module.exit_json()

        out, err = capfd.readouterr()
        return_val = json.loads(out)

        assert return_val.get("exception") is None
        assert return_val.get("invocation") is not None
        if at_least:
            assert return_val.get("failed") is None
        else:
            assert return_val.get("failed")
            # The message is generated by Ansible, don't test for an exact
            # message
            assert desired_version in return_val.get("msg")
            assert "boto3" in return_val.get("msg")
            assert return_val.get("botocore_version") == DUMMY_VERSION
            assert return_val.get("boto3_version") == compare_version

    # ========================================================
    #   Test require_botocore_at_least with reason
    # ========================================================
    @pytest.mark.parametrize("stdin, desired_version, compare_version, at_least", [({}, *d) for d in TEST_VERSIONS], indirect=["stdin"])
    def test_require_botocore_at_least_with_reason(self, monkeypatch, stdin, desired_version, compare_version, at_least, capfd):
        monkeypatch.setattr(botocore, "__version__", compare_version)
        # Set boto3 version to a known value (tests are on both sides) to make
        # sure we're comparing the right library
        monkeypatch.setattr(boto3, "__version__", DUMMY_VERSION)

        reason = 'testing in progress'

        # Create a minimal module that we can call
        module = AnsibleAWSModule(argument_spec=dict())

        with pytest.raises(SystemExit) as e:
            module.require_botocore_at_least(desired_version, reason=reason)
            module.exit_json()

        out, err = capfd.readouterr()
        return_val = json.loads(out)

        assert return_val.get("exception") is None
        assert return_val.get("invocation") is not None
        if at_least:
            assert return_val.get("failed") is None
        else:
            assert return_val.get("failed")
            # The message is generated by Ansible, don't test for an exact
            # message
            assert desired_version in return_val.get("msg")
            assert " {0}".format(reason) in return_val.get("msg")
            assert "botocore" in return_val.get("msg")
            assert return_val.get("boto3_version") == DUMMY_VERSION
            assert return_val.get("botocore_version") == compare_version

    # ========================================================
    #   Test require_boto3_at_least with reason
    # ========================================================
    @pytest.mark.parametrize("stdin, desired_version, compare_version, at_least", [({}, *d) for d in TEST_VERSIONS], indirect=["stdin"])
    def test_require_boto3_at_least_with_reason(self, monkeypatch, stdin, desired_version, compare_version, at_least, capfd):
        monkeypatch.setattr(botocore, "__version__", DUMMY_VERSION)
        # Set boto3 version to a known value (tests are on both sides) to make
        # sure we're comparing the right library
        monkeypatch.setattr(boto3, "__version__", compare_version)

        reason = 'testing in progress'

        # Create a minimal module that we can call
        module = AnsibleAWSModule(argument_spec=dict())

        with pytest.raises(SystemExit) as e:
            module.require_boto3_at_least(desired_version, reason=reason)
            module.exit_json()

        out, err = capfd.readouterr()
        return_val = json.loads(out)

        assert return_val.get("exception") is None
        assert return_val.get("invocation") is not None
        if at_least:
            assert return_val.get("failed") is None
        else:
            assert return_val.get("failed")
            # The message is generated by Ansible, don't test for an exact
            # message
            assert desired_version in return_val.get("msg")
            assert " {0}".format(reason) in return_val.get("msg")
            assert "boto3" in return_val.get("msg")
            assert return_val.get("botocore_version") == DUMMY_VERSION
            assert return_val.get("boto3_version") == compare_version
