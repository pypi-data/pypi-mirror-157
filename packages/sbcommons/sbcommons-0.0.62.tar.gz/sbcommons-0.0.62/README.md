# sbcommons

Packages shared between different lambda functions

### 0.61 - Deprecated
- Added teams client

### 0.62

- Added parse_utils sub-module for parsing configuration files and other text files.
- Added an execute_query method to aws.redshift.RedshiftClient for performing select statements given a string parameter.
- Making teams into a utility class instead of a client