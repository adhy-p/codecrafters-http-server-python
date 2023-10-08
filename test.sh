curl -v http://localhost:4221/
curl -v http://localhost:4221/echo/123
curl -v http://localhost:4221/echo/abc/123
curl -v http://localhost:4221/404
curl -v http://localhost:4221/user-agent
curl -v http://localhost:4221/files/main.py
curl -v --data-binary "@./app/main.py" http://localhost:4221/files/test.py
