import os
import bottle
import image_routes

@bottle.route("/static/<filepath:path>")
def handle_static(filepath):
    return bottle.static_file(filepath, root = "static/")

@bottle.route("/")
def handle_root():
    return bottle.static_file("index.html", root = "static/")

if __name__ == "__main__":
    bottle.run(port = os.environ.get("PORT", 8080), host = "0.0.0.0")
