"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask_failsafe import failsafe
from werkzeug.middleware.proxy_fix import ProxyFix


@failsafe
def create_app():
    from webapp import launch

    app = launch()
    # Apply the "ProxyFix" to trust the X-Forwarded-Proto header
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app


if __name__ == '__main__':
    create_app().run(debug=True, host='0.0.0.0')
