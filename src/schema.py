import typing

from marshmallow import Schema, fields


class CandidateResult(Schema):
    """A standardized instance of a candidate's vote totals."""

    name = fields.Str(required=True)
    party = fields.Str(required=True, allow_none=True)
    votes = fields.Int(required=True)
    incumbent = fields.Boolean(required=True, allow_none=True)


class Contest(Schema):
    """An election contest or race."""

    name = fields.Str(required=True)
    slug = fields.Str(required=True)
    description = fields.Str(required=True, allow_none=True)
    geography = fields.Str(required=True, allow_none=True)
    precincts_reporting = fields.Str(required=True, allow_none=True)
    candidates = fields.List(fields.Nested(CandidateResult))


class BaseTransformer:
    """A base transformer for all of our files."""

    schema: typing.Any = None

    def __init__(
        self, raw_data: typing.Dict, corrections: typing.Optional[typing.Dict] = None
    ):
        """Create a new object."""
        # Load
        self.raw = raw_data
        self.corrections = corrections

        # Transform
        self.transformed = self.transform_data()

        # Validate
        self.schema().load(self.transformed)

    def dump(self) -> typing.Dict:
        """Dump out the object after validation."""
        return self.schema().dump(self.transformed)

    def transform_data(self):
        """Map the raw data to our schema fields."""
        raise NotImplementedError()
