from flask import Flask, render_template, request, flash, jsonify,get_flashed_messages,Response
import cv2, os
from ultralytics import YOLO
import pandas as pd

app = Flask(__name__)
app.secret_key = b'filesystemskindi@343tr&^%#&##!ksgdh!#!'

# Load the pre-trained YOLO model
model = YOLO('best.pt')

# Read the COCO class list from a file
with open("coco.txt", "r") as my_file:
    class_list = my_file.read().split("\n")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        filename = file.filename
        file_path = f'static/images/{filename}'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        flash('File Uploaded Successfully.', 'success')

        # Get flashed messages
        flash_messages = get_flashed_messages(with_categories=True)
        flash_messages = [{'category': msg[0], 'message': msg[1]} for msg in flash_messages]
        return jsonify({'file_path': file_path, 'filename': filename, 'flash_messages': flash_messages})
    return render_template('index.html')

@app.route('/detect_disease/<path:file_path>/<filename>', methods=['GET', 'POST'])
def detect_disease(file_path, filename):
    frame = cv2.imread(file_path)
    frame = cv2.resize(frame, (640, 500))

    results = model.predict(frame)
    detections = results[0].boxes.data
    if len(detections) == 0:
        flash('No disease detected. Please re-upload a proper image.', 'warning')
        # Get flashed messages
        flash_messages = get_flashed_messages(with_categories=True)
        flash_messages = [{'category': msg[0], 'message': msg[1]} for msg in flash_messages]
        return jsonify({'filename': filename, 'flash_messages': flash_messages})
    px = pd.DataFrame(detections).astype("float")

    diseases = set()
    for index, row in px.iterrows():
        x1, y1, x2, y2, _, d = map(int, row)
        if d < len(class_list):
            c = class_list[d]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)
            diseases.add(c)
    if not diseases:
        flash('No diseases detected. Please re-upload a proper image.', 'warning')
    else:
        flash('Disease Detected Successfully.', 'success')
    output_path = f'static/detections/{filename}'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, frame)
    flash('Disease Detected Successfully.', 'success')
    # Get flashed messages
    flash_messages = get_flashed_messages(with_categories=True)
    flash_messages = [{'category': msg[0], 'message': msg[1]} for msg in flash_messages]
    return jsonify({'output_path': output_path, 'diseases': list(diseases), 'filename': filename, 'flash_messages': flash_messages})

@app.route('/get_medicines/<diseases>/<filename>', methods=['GET', 'POST'])
def get_medicines(diseases, filename):
    medicines = {
        "Acne": "Isotretinoin",
        "Chickenpox": "Acyclovir",
        "Monkeypox": "Tecovirimat",
        "Pimple": "Macrolide",
        "Eczema": "Corticosteroids",
        "Psoriasis": "Methotrexate",
        "Ringworm": "Clotrimazole",
        "basal cell carcinoma": "Erivedge",
        "melanoma": "Vemurafenib",
        "tinea-versicolor": "Terbinafine",
        "vitiligo": "Ruxolitinib",
        "warts": "Salicylic acid"
    }

    disease_list = diseases.split(',')
    medicine_dict = {disease: medicines.get(disease) for disease in disease_list}
    flash('Medicine Recommended Successfully!', 'success')
    # Get flashed messages
    flash_messages = get_flashed_messages(with_categories=True)
    flash_messages = [{'category': msg[0], 'message': msg[1]} for msg in flash_messages]
    return jsonify({'medicines': medicine_dict, 'filename': filename, 'flash_messages': flash_messages})


def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (1020, 500))
        results = model.predict(frame)
        detections = results[0].boxes.data
        px = pd.DataFrame(detections).astype("float")

        for index, row in px.iterrows():
            x1, y1, x2, y2, _, d = map(int, row)
            c = class_list[d]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(debug=True)
