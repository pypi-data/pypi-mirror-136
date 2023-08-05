# samstatic_flask
A Flask extension, which can enable the same static url (e.g. `/static`) search multi folders (e.g. `/static`, `/upload`)

使Falsk支持相同静态文件路径（如：`/static`）搜索不同文件夹（如：`/static`, `/upload`）

Falskに同じ静的ファイルパスをサポートさせる(例:`/static`)異なるフォルダを検索する(例:`/static`, `/upload`)

* author: City10th
* email: city10th@foxmail.com
* url: [github](https://github.com/city10th/samstatic_flask)

# Install
```bash
pip install samstatic_flask
```

# Quick start
## How to import
### Method 1

```python
import Flask
from samstatic_flask import SamStatic
app = Flask(__name__)
SamStatic(app)
...
```
### Method 2
```python
from samstatic_flask import FlaskWithSamStatic
app = FlaskWithSamStatic(__name__)
...
```
## How to add multi folders
An example:
```python
...
app.register_blueprint(Blueprint('subapp_shadow', __name__,
                                 static_url_path='/static',
                                 static_folder='static_subapp_upload'))
app.register_blueprint(Blueprint('subapp', __name__,
                                 static_url_path='/static',
                                 static_folder='static_subapp_default'))
```
Now, the url path `/static` will searches for files in order `static`, `static_subapp_upload`, and `static_subapp_default`
If the file is not in the folder `static`, samstaic_flask will search in `static_subapp_upload`, and then `static_subapp_default`

Tips: `static` is the endpoint of `app`
# Option
## `app.config['SAMSTATIC_ENDPOINTS']`
### `SameStatic.options.ALL`
- Default. The same as `'ALL'` or `('ALL',)`
- This will search the static endpoint of app and its all blueprints
### `SameStatic.options.DEACTIVE`
- The same as `'DEACTIVE'` or `('DEACTIVE',)`
- This will deactivate samstatic_flask
### `(SameStatic.options.ALLOWED, {'endpoint1', 'endpoint2'})`
- The same as `('DEACTIVE', {'endpoint1', 'endpoint2'})`
- This will allow only customized endpoints in all static endpoints
### `(SameStatic.options.DISALLOWED, {'endpoint1', 'endpoint2'})`
- The same as `('DISALLOWED', {'endpoint1', 'endpoint2'})`
- This will disallow customized endpoints from all static endpoints
## `app.config['SAMSTATIC_ENDPOINTS_USE_CACHE']`
- Defualt `True`
- `True` will cache the static endpoints