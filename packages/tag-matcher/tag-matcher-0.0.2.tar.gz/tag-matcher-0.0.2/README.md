# Tag Matcher

A lightweight tag matcher for python

# Setup

Install the package via pip:

`pip install tag-matcher`

# Usage

First, import the module:

`import tagmatcher`

Then, execute tag match queries like so:

`is_match = tagmatcher.match(query_str="foo~bar", tags=["foo", "bar])`

In this case, `is_match` will equal true.


# Supported Operators

`~`: AND

`+`: OR
