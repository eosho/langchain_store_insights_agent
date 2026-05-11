# Acceptance Criteria

## Code Generation

When generating Pydantic models, the agent MUST:

1. **Use ConfigDict** instead of inner `Config` class (Pydantic v2)
2. **Prefer Annotated validators** over decorator pattern when validation is reusable
3. **Include type hints** on all model fields
4. **Use Field()** for constraints (min_length, ge, le, etc.)
5. **Apply multi-model pattern** when designing API schemas:
   - `Base` - shared fields and validation
   - `Create` - input schema with required fields
   - `Update` - partial update schema (all fields optional)
   - `Response` - output schema (no secrets)

## Settings Management

When generating pydantic-settings code:

1. **Use BaseSettings** with `SettingsConfigDict`
2. **Use SecretStr** for sensitive values (API keys, passwords)
3. **Implement caching** with `@lru_cache` for settings getter
4. **Configure env_file** for .env support
5. **Use env_prefix** for namespaced configuration

## Validation

When implementing validators:

1. **Use `@field_validator`** with `@classmethod` decorator
2. **Use `@model_validator(mode="after")`** for cross-field validation
3. **Return validated value** from field validators
4. **Raise ValueError** with descriptive messages

## Serialization

When configuring serialization:

1. **Use `from_attributes=True`** for ORM integration
2. **Use `populate_by_name=True`** when supporting both alias and field name
3. **Implement `@field_serializer`** for custom output formats
4. **Use `exclude_none=True`** in model_dump when appropriate

## Anti-Patterns to Flag

The agent SHOULD warn about:

- Using `dict` instead of typed models
- Using `Optional[X] = None` when field is truly required
- Using `Any` type without justification
- Mutable default values without `Field(default_factory=...)`
- Inner `Config` class (Pydantic v1 pattern)
