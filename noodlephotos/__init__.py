import os

import flask
from flask.helpers import send_from_directory


app = flask.Flask(__name__, static_folder='static')
app.config.from_object('noodlephotos.config')
app.config.from_envvar('NOODLEPHOTOS_CONFIG')


@app.route('/gallery/<path:path>')
@app.route('/gallery/', defaults={'path': None})
@app.route('/', defaults={'path': None})
def index(path):
    item = root.resolve_path(path) if path is not None else root
    return item.render()


class Gallery(object):
    def __init__(self, path, name=None, parent=None):
        self.path = path
        self.name = name or os.path.basename(path)
        self.parent = parent
        self.items = {}

        local_path = os.path.join(app.config['PHOTO_DIR'], path)
        children = os.listdir(local_path)
        for child in children:
            child_path = os.path.join(path, child)
            local_child_path = os.path.join(local_path, child)
            if os.path.isdir(local_child_path):
                self.items[child] = Gallery(child_path, parent=self)
            elif (os.path.isfile(local_child_path) and
                  Image.is_supported(local_child_path)):
                child = os.path.splitext(child)[0]
                self.items[child] = Image(child_path, parent=self)

    @property
    def preview_html(self):
        return flask.Markup("""
            <img src="/static/img/folder.png">
            <div class="name">{0}</div>
        """.format(self.name))

    @property
    def public_url(self):
        return flask.url_for('index', path=self.path)

    def resolve_path(self, path):
        components = path.split('/')
        components.reverse()
        return self._resolve_path(components)

    def _resolve_path(self, components):
        if len(components) == 0:
            return self
        name = components.pop()

        # Remove image extension
        if '.' in name:
            name = os.path.splitext(name)[0]

        if name in self.items:
            return self.items[name]._resolve_path(components)
        else:
            return None

    def breadcrumb(self):
        if self.parent is None:
            breadcrumb = []
        else:
            breadcrumb = self.parent.breadcrumb()
        breadcrumb.append(self)
        return breadcrumb

    def render(self):
        return flask.render_template('gallery.html', items=self.items.values(),
                                     breadcrumb=self.breadcrumb())


class Image(object):
    extensions = ['.png', '.gif', '.jpg']

    def __init__(self, path, parent=None):
        self.path = path
        self.name = os.path.basename(path)
        self.parent = parent
        self.url_path, self.ext = os.path.splitext(path)

    @property
    def preview_html(self):
        if self.ext in self.extensions:
            return flask.Markup("""
                <img src="{0}?format=raw">
                <div class="name">{1}</div>
            """.format(self.public_url, self.name))

    @property
    def public_url(self):
        return flask.url_for('index', path=self.url_path)

    @property
    def raw_url(self):
        return '{0}?format=raw'.format(self.public_url)

    def breadcrumb(self):
        breadcrumb = self.parent.breadcrumb()
        breadcrumb.append(self)
        return breadcrumb

    def render(self):
        if flask.request.args.get('format') == 'raw':
            return send_from_directory(app.config['PHOTO_DIR'], self.path)

        return flask.render_template('image.html', image=self,
                                     breadcrumb=self.breadcrumb())

    def _resolve_path(self, components):
        if len(components) > 0:
            return None
        else:
            return self

    @classmethod
    def is_supported(klass, path):
        ext = os.path.splitext(path)[1]
        return ext in klass.extensions


root = Gallery('', name=os.path.basename(app.config['PHOTO_DIR']))
