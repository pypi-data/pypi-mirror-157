# MCSS Python API

Allows for easy access to the MCSS API.

## Installation

```
pip install mcss-api
```

## Usage

### Initialization

#### Import the mcss module:

```python
from mcss import *
```


#### Create the MCSS instance:

Use this if you want the app to stop if the connection fails

```python
mcss = MCSS("http://localhost:25560", True)
```

Use this if you want to manage failed states yourself

```python
mcss = MCSS("http://localhost:25560", False)
```

Example fail state management:

```python
if mcss.com_open == False:
    print("Failed to connect to MCSS")
```

### Authenticating with the MCSS API

```python
token = mcss.auth("username", "password")
```