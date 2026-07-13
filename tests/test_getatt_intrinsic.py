"""
Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

from cfn_tools import dump_json, load_json
import cfn_flip


def test_flip_to_yaml_with_getatt_containing_intrinsic():
    """
    GetAtt whose elements include a nested intrinsic (e.g. Fn::FindInMap,
    permitted by AWS::LanguageExtensions) must not be collapsed into the
    dotted !GetAtt short form: the short form can only express plain strings
    and its loader only reads scalars. It should fall back to the long form
    Fn::GetAtt mapping, which does not crash and round-trips cleanly.
    See https://github.com/awslabs/aws-cfn-template-flip/issues/120
    """

    value = dump_json({
        "Outputs": {
            "Attr": {
                "Value": {
                    "Fn::GetAtt": [
                        {"Fn::FindInMap": ["RegionMap", "Bucket", "Name"]},
                        "Arn",
                    ],
                },
            },
        },
    })

    expected = "\n".join((
        "Outputs:",
        "  Attr:",
        "    Value:",
        "      Fn::GetAtt:",
        "        - !FindInMap",
        "          - RegionMap",
        "          - Bucket",
        "          - Name",
        "        - Arn",
        "",
    ))

    actual = cfn_flip.to_yaml(value)

    assert actual == expected

    # The long form must round-trip back to the original structure
    assert load_json(cfn_flip.to_json(actual)) == load_json(value)


def test_flip_to_yaml_getatt_all_strings_still_dotted():
    """
    The fix for #120 must not change the common case: a GetAtt whose elements
    are all plain strings still collapses to the dotted !GetAtt short form.
    """

    value = dump_json({
        "Outputs": {"A": {"Value": {"Fn::GetAtt": ["Res", "Attr"]}}},
    })

    assert cfn_flip.to_yaml(value) == "Outputs:\n  A:\n    Value: !GetAtt 'Res.Attr'\n"
