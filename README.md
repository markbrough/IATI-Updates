# IATI Updates

This application scrapes the IATI Registry API, to add some information and present other information in a more accessible way.

1) Frequency information added based on number of months in which any packages have changed

To be added:

1) Hashes (to know whether a file has changed)
2) Issues (to know whether a file is recorded as being broken)

# License

Copyright Mark Brough, Publish What You Fund 2013

IATI Updates is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

IATI Updates is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with IATI Updates.  If not, see <http://www.gnu.org/licenses/>.

# Setup

1. Clone the repository and change to that directory

        git clone git@github.com:markbrough/IATI-Updates.git
        cd IATI-Updates

2. It's recommended that you run this in a virtualenv:

        virtualenv ./pyenv

3. Activate the `virtualenv`:

        source ./pyenv/bin/activate

4. Install the requirements:

        pip install -r requirements.txt

5. Copy the template configuration file, and then edit it:

        cp config.py.tmpl config.py

6. Launch from the command line:

        ./manage.py runserver

7. Start updates by navigating in your browser to:

        http://127.0.0.1:5000/update/
