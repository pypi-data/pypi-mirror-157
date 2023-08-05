# sqlupy

## Install

```
pip install sqlupy
```

## Example

```
>>> import sqlupy
>>> sqlupy.parse("pg", "select * from users")
[{'Query': {'body': {'Select': {'cluster_by': [], 'distinct': False, 'distribute_by': [], 'from': [{'joins': [], 'relation': {'Table': {'alias': None, 'args': None, 'name': [{'quote_style': None, 'value': 'users'}], 'with_hints': []}}}], 'group_by': [], 'having': None, 'into': None, 'lateral_views': [], 'projection': ['Wildcard'], 'qualify': None, 'selection': None, 'sort_by': [], 'top': None}}, 'fetch': None, 'limit': None, 'lock': None, 'offset': None, 'order_by': [], 'with': None}}]
```
