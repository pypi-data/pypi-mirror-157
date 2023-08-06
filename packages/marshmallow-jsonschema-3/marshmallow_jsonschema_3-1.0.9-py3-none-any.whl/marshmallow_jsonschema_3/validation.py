from marshmallow import fields

from .exceptions import UnsupportedValueError


def handle_length(schema, field, validator, parent_schema, **kwargs):
    """Adds validation logic for ``marshmallow.validate.Length``, setting the
    values appropriately for ``fields.List``, ``fields.Nested``, and
    ``fields.String``.

    Args:
        schema (dict): The original JSON schema we generated. This is what we
            want to post-process.
        field (fields.Field): The field that generated the original schema and
            who this post-processor belongs to.
        validator (marshmallow.validate.Length): The validator attached to the
            passed in field.
        parent_schema (marshmallow.Schema): The Schema instance that the field
            belongs to.

    Returns:
        dict: A, possibly, new JSON Schema that has been post processed and
            altered.

    Raises:
        UnsupportedValueError: Raised if the `field` is something other than
            `fields.List`, `fields.Nested`, or `fields.String`
    """
    if isinstance(field, fields.String):
        minKey = "minLength"
        maxKey = "maxLength"
    elif isinstance(field, (fields.List, fields.Nested)):
        minKey = "minItems"
        maxKey = "maxItems"
    else:
        raise UnsupportedValueError(
            "In order to set the Length validator for JSON "
            "schema, the field must be either a List, Nested or a String"
        )

    if validator.min:
        schema[minKey] = validator.min

    if validator.max:
        schema[maxKey] = validator.max

    if validator.equal:
        schema[minKey] = validator.equal
        schema[maxKey] = validator.equal

    return schema


def handle_one_of(
    schema,
    field,
    validator,
    parent_schema,
    use_new_enums: bool = False,
    use_repr_enums: bool = False,
    use_easy_enum: bool = False
):
    """Adds the validation logic for `marshmallow.validate.OneOf` by setting
    the JSONSchema `oneOf` property to the allowed choices in the validator.`

    Args:
        schema (dict): The original JSON schema we generated. This is what we
            want to post-process.
        field (fields.Field): The field that generated the original schema and
            who this post-processor belongs to.
        validator (marshmallow.validate.OneOf): The validator attached to the
            passed in field.
        parent_schema (marshmallow.Schema): The Schema instance that the field
            belongs to.

    Returns:
        dict: New JSON Schema that has been post processed and altered.
    """
    if use_new_enums:
        # Instead of constructing enum: [1,2,3], construct oneOf: [{title: one, const: 1}, ...]
        # See: https://github.com/OAI/OpenAPI-Specification/issues/348#issuecomment-336194030
        if use_easy_enum:
            choices = []
            for i, choice in enumerate(validator.choices):
                choices.append(
                    {"description": validator.labels[i], "const": choice}
                )
            schema["oneOf"] = choices
        else:
            schema["oneOf"] = [
                {"description": choice.name, "const": choice.value}
                for choice in validator.choices
            ]
    elif use_repr_enums:
        # Put value and name into a string separated with =, e.g. "1=RED".
        if use_easy_enum:
            choices = []
            try:
                for i, choice in enumerate(validator.choices):
                    choices.append(
                        f"{choice}={validator.labels[i]}"
                    )
                schema["enum"] = choices
            except IndexError:
                # In case of IndexError, convert to simple list of keys without labels.
                schema["enum"] = list(validator.choices)
        else:
            schema["enum"] = [
                f"{enum.value}={enum.name}" for enum in list(validator.choices)
            ]
    else:
        # Default way of listing all possible values without their descriptions/names/...
        schema["enum"] = list(validator.choices)

    return schema


def handle_equal(schema, field, validator, parent_schema, **kwargs):
    """Adds the validation logic for ``marshmallow.validate.Equal`` by setting
    the JSONSchema `enum` property to value of the validator.

    Args:
        schema (dict): The original JSON schema we generated. This is what we
            want to post-process.
        field (fields.Field): The field that generated the original schema and
            who this post-processor belongs to.
        validator (marshmallow.validate.Equal): The validator attached to the
            passed in field.
        parent_schema (marshmallow.Schema): The Schema instance that the field
            belongs to.

    Returns:
        dict: New JSON Schema that has been post processed and
            altered.
    """
    # Deliberately using `enum` instead of `const` for increased compatibility.
    #
    # https://json-schema.org/understanding-json-schema/reference/generic.html#constant-values
    # It should be noted that const is merely syntactic sugar for an enum with a single element [...]
    schema["enum"] = [validator.comparable]

    return schema


def handle_range(schema, field, validator, parent_schema, **kwargs):
    """Adds validation logic for ``marshmallow.validate.Range``, setting the
    values appropriately ``fields.Number`` and it's subclasses.

    Args:
        schema (dict): The original JSON schema we generated. This is what we
            want to post-process.
        field (fields.Field): The field that generated the original schema and
            who this post-processor belongs to.
        validator (marshmallow.validate.Range): The validator attached to the
            passed in field.
        parent_schema (marshmallow.Schema): The Schema instance that the field
            belongs to.

    Returns:
        dict: New JSON Schema that has been post processed and
            altered.

    Raises:
        UnsupportedValueError: Raised if the `field` is not an instance of
            `fields.Number`.
    """
    if not isinstance(field, fields.Number):
        raise UnsupportedValueError(
            "'Range' validator for non-number fields is not supported"
        )

    if validator.min is not None:
        # marshmallow 2 includes minimum by default
        # marshmallow 3 supports "min_inclusive"
        min_inclusive = getattr(validator, "min_inclusive", True)
        if min_inclusive:
            schema["minimum"] = validator.min
        else:
            schema["exclusiveMinimum"] = validator.min

    if validator.max is not None:
        # marshmallow 2 includes maximum by default
        # marshmallow 3 supports "max_inclusive"
        max_inclusive = getattr(validator, "max_inclusive", True)
        if max_inclusive:
            schema["maximum"] = validator.max
        else:
            schema["exclusiveMaximum"] = validator.max
    return schema


def handle_regexp(schema, field, validator, parent_schema, **kwargs):
    """Adds validation logic for ``marshmallow.validate.Regexp``, setting the
    values appropriately ``fields.String`` and it's subclasses.

    Args:
        schema (dict): The original JSON schema we generated. This is what we
            want to post-process.
        field (fields.Field): The field that generated the original schema and
            who this post-processor belongs to.
        validator (marshmallow.validate.Regexp): The validator attached to the
            passed in field.
        parent_schema (marshmallow.Schema): The Schema instance that the field
            belongs to.

    Returns:
        dict: New JSON Schema that has been post processed and
            altered.

    Raises:
        UnsupportedValueError: Raised if the `field` is not an instance of
            `fields.String`.
    """
    if not isinstance(field, fields.String):
        raise UnsupportedValueError(
            "'Regexp' validator for non-string fields is not supported"
        )

    schema["pattern"] = validator.regex.pattern

    return schema
