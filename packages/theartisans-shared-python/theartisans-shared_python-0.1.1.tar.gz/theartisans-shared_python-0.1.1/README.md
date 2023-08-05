# For the artisans inc.

```bash
$ pip install theartisans-shared-python
$ pip install flask marsmallow asyncio-nats-streaming protobuf==3.20.*
```

```python
from the_artisans_shared.errors import BadRequestError
from the_artisans_shared.middleware import require_auth

@app.route('/new', methods=["GET"])
@require_auth
def new():
    raise BadRequestError()

```
