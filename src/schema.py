from marshmallow import Schema, fields


class CandidateResult(Schema):
    """An standardized instance of a candidate's vote totals."""

    name = fields.Str(required=True)
    party = fields.Str(required=True)
    votes = fields.Int(required=True)
    incumbent = fields.Boolean(required=True, allow_none=True)
