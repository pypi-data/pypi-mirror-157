"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing,
  software distributed under the License is distributed on an
  "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
  KIND, either express or implied.  See the License for the
  specific language governing permissions and limitations
  under the License.
"""

import gql
import json
import requests

_DEFAULT_API_URL = 'https://api.opvious.dev/graphql'

REGISTER_SPECIFICATION_QUERY = """
  mutation RegisterSpecification($input: RegisterSpecificationInput!) {
    registerSpecification(input: $input) {
      id
      formulation {
        name
      }
      assembly {
        collectionCount
        variableCount
        parameterCount
        constraintCount
      }
    }
  }
"""

_RUN_ATTEMPT_QUERY = """
  mutation RunAttempt($input:AttemptInput!) {
    runAttempt(input:$input) {
      outcome {
        __typename
        ...on FeasibleOutcome {
          variables {
            label
            results {
              key
              primalValue
            }
          }
        }
      }
    }
  }
"""

class Client:
  """Opvious API client"""

  def __init__(self, access_token, api_url=None):
    self.api_url = api_url or _DEFAULT_API_URL
    self.session = requests.Session()
    self.session.headers.update({
      'authorization': f'Bearer {access_token}',
      'content-type': 'application/json',
    });

  def register_specification(self, formulation_name, source_text):
    return self.session.post(
      self.api_url,
      data=json.dumps({
        'query': REGISTER_SPECIFICATION_QUERY,
        'variables': {
          'input': {
            'formulationName': formulation_name,
            'sourceText': source_text,
          },
        },
      })
    )

  def run_attempt(self, formulation_name, collections=None, parameters=None):
    return self.session.post(
      self.api_url,
      data=json.dumps({
        'query': _RUN_ATTEMPT_QUERY,
        'variables': {
          'input': {
            'formulationName': formulation_name,
            'collections': collections or [],
            'parameters': parameters or [],
          },
        },
      })
    )
