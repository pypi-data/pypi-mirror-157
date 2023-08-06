# python-canvas
Библиотека **python-canvas** является SqlAlchemy-маппингом для базы данных Canvas LMS.

## Примеры
```python
from canvas_db.config import Config
from canvas_db.orm import get_session


config = Config(host='Адрес БД Canvas LMS', user='Пользователь БД Canvas LMS', passowrd='Пароль БД Canvas LMS')
session = get_session(config)
```