npm ci >/dev/null
npm install cypress >/dev/null
apt-get update >/dev/null
apt-get install -y python3 python3-pip >/dev/null
apt-get install -y libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb >/dev/null
pip3 install --upgrade -q pip
pip3 install -q virtualenv
pip3 install --no-cache-dir -qr requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python manage.py migrate --run-syncdb
python3 manage.py collectstatic --no-input >/dev/null
rm -rf staticfiles/fontawesomefree/js-packages
rm -rf staticfiles/fontawesomefree/svgs
du -sh staticfiles/fontawesomefree/metadata
