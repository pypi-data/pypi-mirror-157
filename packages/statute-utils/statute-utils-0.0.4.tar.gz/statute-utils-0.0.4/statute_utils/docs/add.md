# How to add a new Statute type identity

See the [main file](../statute_formula.py)

Each type has an identity represented by a `StatuteID`:

```python
class StatuteID(Enum):
    RA = StatuteTitleAspect( # `ra` is StatuteID for _Republic Act_
        category="Republic Act",
        connector=Connector.Generic.value,
        shortcut="RA",
        helptext="President approved after Congressional deliberations",
        constructor=RepublicAct,
    )
    ...
```

There is a constructor object which is an optional field based on `StatuteTitleAspect`. The constructor implies that there are available patterns that can be used as a *formula* or a *matcher*:

1. A formula is a `regex`-based string.
2. A matcher is the conversion of this string to a python Pattern object

The formula is made part of a larger collection of many `StatuteIDs` so the *group names* in each formula must be distinct.

## How to create a new Statute type formula

See the serials file: `statute_utils/formula/serials.py`.

This contains classes of formula representing specific identities.

Each identity needs a formulae which is the raw regex pattern string.

To create a new one, the class must follow the following format:

```python
class SampleNameOfIdentity(StatutePatternsMethods):
    group_name = "unique_name_for_capturing_named_group"
    digit_group_name = "unique_name_for_capturing_named_digits"
    # the reason for requiring uniqueness is that this formula will be concatenated with other formulas so it needs to have a unique identifier; see sample formula below

    def __init__(self) -> None:
        self.formula = rf"""
        (
            \b
            (?P<{self.group_name}>
                (Republic\s+Act)|
                (Rep\.\s+Act)
                (Rep\s+Act)
                RA|
            ) # e.g. Republic Act
            \s+ # need one space
            (No\.\s*)?, # optional No.
            (?P<{self.digit_group_name}>[\w-]+) # 386-A
        )
        """
```

## Include formula in compiled statute regexes

1. Add latest formula you created from `serials` to the [init file](../formula/__init__.py)
2. Include the added formula in the list of `StatuteID`s, specifying the constructor when needed

## How to test the identity-formula

See the serials file: `tests/test_statute_formula.py` file. The `STATUTE_FORMULA_TEST_VALUES` variable refers to a list of values. Each value is a tuple or a test of identity, e.g.:

```python
(
    "RULE_RESO",
    "Resolution of the Court En Banc dated",
    "1-1-1990",
    "Resolution of the Court En Banc dated 1-1-1990",
),
```

This means that:

`StatuteID` with name `RULE_RESO` should match the following pattern: "Resolution of the Court En Banc dated 1-1-1990", resulting in two parts: the original pattern `Resolution of the Court En Banc` and the joined value `1-1-1990`.
