# marshmallow-jsonschema-3

Transform marshmallow schemas into correct OpenAPI3.0.x-3.1 definitions.
Fork of [marshmallow-jsonschema](https://github.com/fuhrysteve/marshmallow-jsonschema) by 
Stephen J. Fuhry.

Why fork?
- Add support for marshmallow fields.Constant (missing in marshmallow-jsonschema 0.13.0)
- Add enum handling for the future? At least not as useless as current 
  approach. Flags `use_repr_enums=` to convert enums into list of `1=a, 2=b` or `use_new_enums=` 
  to create [3.1 suggested enums](https://github.com/OAI/OpenAPI-Specification/issues/348#issuecomment-336194030).
- Put schema references into `#/components/schemas/<name>` instead of `#/definitions/<name>` 
  [source](https://spec.openapis.org/oas/latest.html#components-object-example)
- Add old `nullable: true` attribute using `use_nullable=` flag.

## Installation
`pip install marshmallow-jsonschema-3` in >=Python3.8

## Usage

```python
from marshmallow import Schema, fields
from marshmallow_jsonschema_3 import JSONSchema

class UserSchema(Schema):
    username = fields.String()
    age = fields.Integer()
    birthday = fields.Date()

user_schema = UserSchema()
json_schema = JSONSchema(use_repr_enums=True, use_nullable=True)
json_schema.dump(user_schema)
```

## Deployment
1. Make your changes
2. Create `~/.pypirc` file for twine
```
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = pypiusername
password = pypipsw

[testpypi]
username = pypiusername
password = pypipsw
```
2. `make pypitest` to deploy to https://test.pypi.org
3. Use `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.
   org/simple marshmallow-jsonschema-3` to install test package in your projects using 
   real pypi dependencies. The default pip install provided by test.pypi will only look for dependencies 
   in test.pypi, and will fail to find actual versions of dependencies...

Use `make pypi` for real pypi and use `pip install marshmallow-jsonschema-3` to install 
published package.