"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from flask import current_app

from tests.model_generator.parking_site import get_parking_site
from tests.model_generator.source import get_source
from webapp import launch
from webapp.extensions import db


def provision_with_test_data():
    launch().app_context().push()
    if current_app.config['MODE'] != 'DEVELOPMENT' or not current_app.config['DEBUG']:
        print('wrong mode')
        return

    db.drop_all()
    db.create_all()

    source_1 = get_source(1)
    source_2 = get_source(2)
    source_3 = get_source(3)
    db.session.add(source_1)
    db.session.add(source_2)
    db.session.add(source_3)
    db.session.commit()

    db.session.add(get_parking_site(counter=1, source_id=1))
    db.session.add(get_parking_site(counter=2, source_id=1))
    db.session.add(get_parking_site(counter=3, source_id=1))
    db.session.add(get_parking_site(counter=4, source_id=2))
    db.session.add(get_parking_site(counter=5, source_id=2))
    db.session.add(get_parking_site(counter=6, source_id=3))
    db.session.commit()


if __name__ == '__main__':
    provision_with_test_data()
