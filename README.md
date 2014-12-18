
django-t2s
========================
a very simple usage django utility for t2s


### Installation

```sh
$ git clone git@github.com:yorkie/django-t2s.git
```

### Usage

In your model.py

```py
from t2s import t2s

class YourModel(t2s.Model):
  # TODO
```

In your admin.py

```py
from t2s import t2s

class YourModelAdmin(t2s.ModelAdmin):
  # TODO
```

### License

MIT
