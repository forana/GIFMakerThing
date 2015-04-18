import bottle
from bottle import request, response
from PIL import Image, ImageDraw, ImageFont
import os, tempfile
import images2gif
from io import BytesIO
from bases import mapping as bases

@bottle.route("/image/<base>/<subject>", method = "GET")
def get_image(base, subject):
    response.content_type = "image/gif"
    return bottle.static_file("bugs.gif", root = "bases/")

@bottle.route("/image", method = "POST")
def new_image():
    buffer = BytesIO()
    request.files.get("file").save(buffer)
    upload = Image.open(buffer).convert(mode = "RGBA")

    base = bases[request.forms.get("base")]
    action = request.forms.get("action")

    print base

    im = Image.open("bases/" + base["file"])
    frames = split_gif(im)

    font = ImageFont.load_default()
    for i in range(len(frames)):
        frame = frames[i]
        direction = base["directions"][i]
        if direction is not None:
            size = direction[0]
            corner = direction[1]
            rotation = direction[2]
            scaled_size = choose_scale_rect(size, upload.size)
            print size, scaled_size, upload.size
            transformed = upload.resize(scaled_size).rotate(rotation, Image.BICUBIC, True)
            frame.paste(transformed, corner, transformed)

    tf = tempfile.NamedTemporaryFile(delete = False)
    filename = tf.name
    tf.close()

    images2gif.writeGif(filename, frames, duration = base["delay"], subRectangles = False)

    fp = open(filename, "rb")
    contents = fp.read()
    fp.close()
    os.remove(filename)

    response.content_type = "image/gif"

    if action == "download":
        response.headers["content-disposition"] = "attachment;filename=download.gif"
    return contents

def choose_scale_rect(target_size, image_size):
    r1 = 1.0*target_size[0]/target_size[1]
    r2 = 1.0*image_size[0]/image_size[1]
    if r1 < r2: # scale to width
        return (target_size[0], int(target_size[0] / r2))
    else: # scale to height
        return (int(target_size[1] * r2), target_size[1])

def split_gif(im):
    frames = []
    palette = im.getpalette()
    try:
        while True:
            frame = Image.new("RGBA", im.size)
            if not im.getpalette():
                im.setpalette(palette)
            frame.paste(im, (0, 0), im.convert("RGBA"))
            frames.append(frame)
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return frames
