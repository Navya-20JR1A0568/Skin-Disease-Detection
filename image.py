import cv2
import pandas as pd
from ultralytics import YOLO
import os

# Load the pre-trained YOLO model
model = YOLO('../results/weights/best.pt')

# Mouse callback function for capturing RGB values of pixels
def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        colorsBGR = frame[y, x]
        print("BGR:", colorsBGR)

# Load an image
frame = cv2.imread('../images/images/acne-268-v2__ProtectWyJQcm90ZWN0Il0_FocusFillWzI5NCwyMjIsIngiLDFd_jpg.rf.739a95663903d3d6cd7197b14f2ce60b.jpg')

# Resize the frame to a fixed size (if necessary)
frame = cv2.resize(frame, (640, 640))

# Perform object detection on the frame
results = model.predict(frame)

detections = results[0].boxes.data  
px = pd.DataFrame(detections).astype("float")
# print(px)
# Read the COCO class list from a file
with open("../coco.txt", "r") as my_file:
    class_list = my_file.read().split("\n")

diseases = set()
px = pd.DataFrame(detections).astype("float")
for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])
        c = class_list[d]
        # print(c)
        diseases.add(c)

        # Draw bounding boxes and class labels on the frame
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, str(c), (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)
        # print(c)
medicines={
     "Acne":"Isotretinoin",
     "Chickenpox":"Acyclovir",
     "Monkeypox":"Tecovirimat",
     "Pimple":"Macrolide",
     "Eczema":"Corticosteroids",
     "Psoriasis":"Methotrexate",
     "Ringworm":"Clotrimazole",
     "basal cell carcinoma":"Erivedge",
     "melanoma":"Vemurafenib",
     "tinea-versicolor":"Terbinafine",
     "vitiligo":"Ruxolitinib",
     "warts":"Salicylic acid"
}
print(diseases)
for disease in diseases:  
    res=medicines.get(disease)
    print(disease)
    print(res)
     
diseases.clear()
print('clear',diseases)
        
# Display the frame with objects detected
cv2.imshow("RGB", frame)
cv2.waitKey(0)
