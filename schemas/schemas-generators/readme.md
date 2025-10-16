To generate the python schemas run:
```
pulse-data\schemas\schemas-generators> python autogenerate_schemas.py --schemas-dir ../schemas-yaml --output-dir ../schemas-py --dry-run -v
```

To generate the java schemas run the maven artifact: 

For example, in IntelliJ, open the Maven panel on the right side (or View → Tool Windows → Maven). 
Then expand your project → Plugins → jsonschema2pojo → double-click jsonschema2pojo:generate