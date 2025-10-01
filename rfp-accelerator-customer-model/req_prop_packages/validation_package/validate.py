# Copyright 2024 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
def validate_dict_values(data, expected_types):
    """
    Validate the type of each individual value in a dictionary.

    Args:
        data (dict): The dictionary to validate.
        expected_types (dict): A dictionary of expected types for each key in the input dictionary.

    Raises:
        HTTPException: If any of the values in the dictionary are not of the expected type.
    """

    for key, value in data.items():
        if not isinstance(value, expected_types[key]):
            return True
    return False