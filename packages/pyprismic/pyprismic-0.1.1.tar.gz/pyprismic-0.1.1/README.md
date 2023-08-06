# pyprisic: a simple python Prismic client

This is a very simple Prismic python client.

It uses the REST API from prismic.

Right now it only supports public Prismic repositories.

## Installing

```
pip install pyprismic
```

## Using it

```
from pyprisic import Client

c = Client("your-repo")

c.query(predicate="""[[at(document.type, "faq")]]""")
```

## Querying Prismic

For querying prismic, you only need to follow the predicates system that they have in place.

Check the [official documentation](https://prismic.io/docs/technologies/query-predicates-reference-rest-api).

**NOTE**: it is important to use the triple quote so you can properly use the " for the strings.
