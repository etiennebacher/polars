# --8<-- [start:dataframe]
import polars as pl

url = "hf://datasets/nameexhaustion/polars-docs/legislators-historical.csv"

schema_overrides = {
    "first_name": pl.Categorical,
    "gender": pl.Categorical,
    "type": pl.Categorical,
    "state": pl.Categorical,
    "party": pl.Categorical,
}

dataset = (
    pl.read_csv(url, schema_overrides=schema_overrides)
    .with_columns(pl.col("first", "middle", "last").name.suffix("_name"))
    .with_columns(pl.col("birthday").str.to_date(strict=False))
)
# --8<-- [end:dataframe]

# --8<-- [start:basic]
q = (
    dataset.lazy()
    .group_by("first_name")
    .agg(
        pl.len(),
        pl.col("gender"),
        pl.first("last_name"),  # Short for `pl.col("last_name").first()`
    )
    .sort("len", descending=True)
    .limit(5)
)

df = q.collect()
print(df)
# --8<-- [end:basic]

# --8<-- [start:conditional]
q = (
    dataset.lazy()
    .group_by("state")
    .agg(
        (pl.col("party") == "Anti-Administration").sum().alias("anti"),
        (pl.col("party") == "Pro-Administration").sum().alias("pro"),
    )
    .sort("pro", descending=True)
    .limit(5)
)

df = q.collect()
print(df)
# --8<-- [end:conditional]

# --8<-- [start:nested]
q = (
    dataset.lazy()
    .group_by("state", "party")
    .agg(pl.len().alias("count"))
    .filter(
        (pl.col("party") == "Anti-Administration")
        | (pl.col("party") == "Pro-Administration")
    )
    .sort("count", descending=True)
    .limit(5)
)

df = q.collect()
print(df)
# --8<-- [end:nested]


# --8<-- [start:filter]
from datetime import date


def compute_age():
    return date.today().year - pl.col("birthday").dt.year()


def avg_birthday(gender: str) -> pl.Expr:
    return (
        compute_age()
        .filter(pl.col("gender") == gender)
        .mean()
        .alias(f"avg {gender} birthday")
    )


q = (
    dataset.lazy()
    .group_by("state")
    .agg(
        avg_birthday("M"),
        avg_birthday("F"),
        (pl.col("gender") == "M").sum().alias("# male"),
        (pl.col("gender") == "F").sum().alias("# female"),
    )
    .limit(5)
)

df = q.collect()
print(df)
# --8<-- [end:filter]


# --8<-- [start:filter-nested]
q = (
    dataset.lazy()
    .group_by("state", "gender")
    .agg(
        # The function `avg_birthday` is not needed:
        compute_age().mean().alias("avg birthday"),
        pl.len().alias("#"),
    )
    .sort("#", descending=True)
    .limit(5)
)

df = q.collect()
print(df)
# --8<-- [end:filter-nested]


# --8<-- [start:sort]
def get_name() -> pl.Expr:
    return pl.col("first_name") + pl.lit(" ") + pl.col("last_name")


q = (
    dataset.lazy()
    .sort("birthday", descending=True)
    .group_by("state")
    .agg(
        get_name().first().alias("youngest"),
        get_name().last().alias("oldest"),
    )
    .limit(5)
)

df = q.collect()
print(df)
# --8<-- [end:sort]


# --8<-- [start:sort2]
q = (
    dataset.lazy()
    .sort("birthday", descending=True)
    .group_by("state")
    .agg(
        get_name().first().alias("youngest"),
        get_name().last().alias("oldest"),
        get_name().sort().first().alias("alphabetical_first"),
    )
    .limit(5)
)

df = q.collect()
print(df)
# --8<-- [end:sort2]


# --8<-- [start:sort3]
q = (
    dataset.lazy()
    .sort("birthday", descending=True)
    .group_by("state")
    .agg(
        get_name().first().alias("youngest"),
        get_name().last().alias("oldest"),
        get_name().sort().first().alias("alphabetical_first"),
        pl.col("gender").sort_by(get_name()).first(),
    )
    .sort("state")
    .limit(5)
)

df = q.collect()
print(df)
# --8<-- [end:sort3]
