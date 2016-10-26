import sys
sys.path.append('../helpers/')

from schema import Base, City, Startup, User
from database_helpers import create_session

session = create_session('sqlite:///startup.db')

user_1 = User(username='User1', email='user1@users.com')
user_2 = User(username='User2', email='user2@users.com')

session.bulk_save_objects([user_1, user_2])
session.commit()
user_1 = session.query(User).filter_by(email='user1@users.com').first()

cities = [City(name='New York', slug='new-york', state='ny'),
             City(name='San Francisco', slug='san-francisco', state='ca'),
             City(name='Chicago', slug='chicago', state='il'),
             City(name='Portland', slug='portland', state='or'),
             City(name='Seattle', slug='seattle', state='wa'),
             City(name='Asheville', slug='asheville', state='nc'),
             City(name='Boston', slug='boston', state='ma')]

session.bulk_save_objects(cities)
session.commit()

nyc = session.query(City).filter_by(name='New York').one()
chi = session.query(City).filter_by(name='Chicago').one()

startup_nyc = Startup(name='Breather', slug='breather',
        description='Meeting rooms on demand.',
        link='http://www.breather.com',
        careers_link='https://breather.com/jobs',
        city_id=nyc.id, user_id=user_1.id)

startup_nyc_2 = Startup(name='Wink', slug='wink',
        description='A simpler, smarter home.',
        link='http://www.wink.com',
        careers_link='https://www.linkedin.com/company/wink-inc-/careers?trk=top_nav_careers',
        city_id=nyc.id, user_id=user_1.id)

startup_chi = Startup(name='GrubHub', slug='grubhub',
        description='Makes ordering from a restaurant easy.',
        link='http://www.grubhub.com',
        careers_link='https://www.grubhub.com/careers/?nl=1&jvi=&jvk=JobListing',
        city_id=chi.id, user_id=user_1.id)

session.bulk_save_objects([startup_nyc, startup_nyc_2, startup_chi])
session.commit()
session.close()
