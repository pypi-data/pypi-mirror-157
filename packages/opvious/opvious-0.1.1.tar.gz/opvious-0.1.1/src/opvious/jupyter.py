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

from IPython.display import Javascript
import json

API_URL = 'https://api.opvious.dev/graphql'

REGISTER_QUERY = """
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

class JupyterClient:

  def __init__(self, access_token, api_url=None):
    self._access_token = access_token
    self._api_url = api_url or API_URL

  def save_specification(self, formulation_name):
    # TODO: Add output (particularly any errors...)
    # print(self._register_source(formulation_name))
    # return
    return Javascript(self._register_source(formulation_name))

  def run_solve(self, formulation_name, collections=None, parameters=None):
    pass

  def _register_source(self, formulation_name):
    return f"""
      (async () => {{
        const spec = [...document.getElementsByClassName('jp-MarkdownCell')]
          .map((e) => [...e.querySelectorAll('.CodeMirror-line')].map((l) => l.textContent).join(' '))
          .join(' ');
        const res = await fetch(
          {json.dumps(self._api_url)},
          {{
            method: 'POST',
            headers: {json.dumps(self._graphql_headers())},
            body: JSON.stringify({{
              query: `{REGISTER_QUERY}`,
              variables: {{
                input: {{
                  formulationName: {json.dumps(formulation_name)},
                  sourceText: spec.replace(/\s+/g, ' ')
                }}
              }}
            }}),
          }}
        );
        const body = await res.json();
        console.log(body);
        element.textContent = JSON.stringify(body, null, 2);
      }})().catch(console.error);
    """

  def _graphql_headers(self):
    return {
      'content-type': 'application/json',
      'authorization': f'Bearer {self._access_token}',
    }
