from flask import Flask, request, jsonify, flash, redirect
from werkzeug.utils import secure_filename
from flask_cors import CORS
app = Flask(__name__, static_url_path="", static_folder='static')
CORS(app)
UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# test
@app.route('/')
def home():
    return app.send_static_file('index.html')


import cv2
import os
import json
import requests
from base64 import b64encode
# from pylab import rcParams
import gmaps

Videopath = ""
framerate = "short"


def save_frames(video_path, VideoLength):
    fps = 1
    # duration = video_path.get(cv2.CAP_PROP_POS_MSEC)
    cap = cv2.VideoCapture(video_path)
    print(cap)

    # Calculting in seconds
    fps = cap.get(cv2.CAP_PROP_FPS)
    totalFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    durationInSeconds = round(totalFrames / fps)

    #  totalFrames = int(cap.get(cv2.CAP_PROP_FPS))
    print(totalFrames)
    cap.set(cv2.CAP_PROP_FPS, 1)
    #   cap.set(cv2.CAP_PROP_MSEC, (1/fps)*1000)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(totalFrames)
    i = 0
    path = 'frames'

    if not os.path.exists(path):
        os.mkdir(path)

    while cap.isOpened:
        ret, frame = cap.read()
        if ret == False:
            break
        if VideoLength == "short":
            filename = f'{path}/frame' + str(i // round(totalFrames // 100)).zfill(5) + '.jpg'
            i += 1
            if (i % round(totalFrames // 100) == 0):
                cv2.imwrite(filename, frame)
        elif VideoLength == "redo":
            filename = f'{path}/frame' + str(i // round(totalFrames // 200)).zfill(5) + '.jpg'
            i += 1
            if (i % round(totalFrames // 200) == 0):
                cv2.imwrite(filename, frame)
    cap.release()
    cv2.destroyAllWindows()


with open("API_Key.json") as f:
    data = json.load(f)

key = data['api_key']
ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
gmaps.configure(api_key=key)


def makeImageData(imgpath):
    img_req = None
    with open(imgpath, 'rb') as f:
        ctxt = b64encode(f.read()).decode()
        img_req = {
            'image': {
                'content': ctxt
            },
            'features': [{
                'maxResults': 1,
                'type': 'LANDMARK_DETECTION'
            }]
        }
        list(f)
    return json.dumps({'requests': img_req}).encode()


# rcParams['figure.figsize'] = 10, 20

def requestOCR(url, api_key, imgpath):
    imgdata = makeImageData(imgpath)
    response = requests.post(url, data=imgdata, params={'key': key}, headers={'Content-Type': 'application/json'})
    return response


def getOCR(imgpath):
    result = requestOCR(ENDPOINT_URL, key, imgpath)
    if result.status_code != 200 or result.json().get('error'):
        print("Error! Failed to make a connection.")
        return None
    else:
        result = result.json()['responses'][0]
        return result


def get_name_geocode(result):
    if "landmarkAnnotations" in result:
        landmark = result["landmarkAnnotations"]
        return {'description': landmark[0]['description'], 'locations': landmark[0]['locations']}
    else:
        return None


def extract_address_via_loc(lat, long):
    api_key = data['api_key']

    base_url = f"https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?lating={lat},{long}&key={api_key}"

    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return None
    try:
        return r.json()[0]['formatted_address']
    except:
        return None


def find_image(imgpath):
    result = getOCR(imgpath)
    landmark = None
    if result:
        landmark = get_name_geocode(result)
    if landmark == None:
        return None
    latlng = landmark['locations'][0]["latLng"]
    address = extract_address_via_loc(latlng['latitude'], latlng['longitude'])
    #     return {'name':landmark['description'], 'address': address, 'lat':latlng['latitude'], 'lng': latlng['longitude'], 'image_loc': imgpath}
    if landmark != None:
        return {landmark['description']: (latlng['latitude'], latlng['longitude'])}


def delete_frames():
    directory = "frames"
    for frame in os.listdir(directory):
        os.remove(f"frames/{frame}")


def find_location(video_path, VideoLength):
    print(video_path)
    delete_frames()
    result = {}
    save_frames(video_path, VideoLength)
    directory = os.fsencode("frames")
    images = os.listdir(directory)
    gap = 10

    for i in range(0, len(images), gap):
        loc = find_image(f"frames/{os.fsdecode(images[i])}")
        if loc:
            for key in loc:
                value = loc[key]
                result[key] = value

    delete_frames()
    return result


@app.route('/GetVideoPath/<path>', methods=['GET', 'POST'])
def getVideoPath(path):
    # user = request.argd.get("filepath")
    # print(user)
    print("Path in line 157" + path)
    print("path: " + path)
    path = json.loads(path)
    # global Videopath
    Videopath = path
    print(Videopath)
    print("Line 162")
    return ('/')


@app.route('/ProcessVideolength/<string:videolength>', methods=['POST'])
def Videolength(videolength):
    videolength = json.loads(videolength)
    global framerate
    framerate = videolength
    print(framerate)
    return ('/')


@app.route('/result/<Videopath>')
def getlocation(Videopath):
    Videopath = f'static/uploads/{Videopath}'
    print(Videopath)
    return jsonify(find_location(Videopath, framerate))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    print(file)
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    else:
        filename = secure_filename(file.filename)
        print(filename)
        print("Calling in upload")
        file.save(f'static/uploads/{filename}')

    return filename


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
