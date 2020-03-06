import cv2
import numpy as np
import sys
import os
import matplotlib.pyplot as plt


def objectDetector( imagePath, 
                    labelsPath='./cfg/labels.txt', 
                    configPath='./cfg/yolov3.cfg', 
                    weightsPath = './cfg/yolov3.weights',
                    confi = 0.5,
                    thresh = 0.8):
    img = cv2.imread(imagePath)
    (H,W) = img.shape[:2]
    labels = []
    with open(labelsPath, 'r') as file:
        labels = file.read().strip().split('\n')
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
    out_layers = [net.getLayerNames()[i[0]-1] for i in net.getUnconnectedOutLayers()]
    blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True)
    net.setInput(blob)
    out_val = net.forward(out_layers)
    boxes, confidences, classIds = [], [], []
    for output in out_val:
        for detection in output:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confi:
                box = detection[0:4] * np.array([W,H,W,H])
                (cX, cY, width, height) = box.astype("int")
                x = int(cX - (width/2))
                y = int(cY - (height/2))
                boxes.append([x,y,int(width), int(height)])
                confidences.append(float(confidence))
                classIds.append(classId)
    nms = cv2.dnn.NMSBoxes(boxes, confidences, confi, thresh)
    nms_boxes = []
    if len(nms) > 0:
        for i in nms.flatten():
            (x,y) = (boxes[i][0], boxes[i][1])
            (w,h) = (boxes[i][2], boxes[i][3])
            cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 1)
            nms_boxes.append(classIds[i])
    final_classes = [labels[i] for i in nms_boxes]
    return final_classes, img


def faceDetector(imgPath,
                xmlPath='./xmls/face_alt2.xml', 
                scaleFactor = 1.18 , 
                minNeighbors = 3):
    img = cv2.imread(imgPath)
    face_cascade = cv2.CascadeClassifier(xmlPath)
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detected_faces = face_cascade.detectMultiScale(grey, scaleFactor = scaleFactor, minNeighbors = minNeighbors)
    # for (column, row, width, height) in detected_faces:
    #     cv2.rectangle(
    #     img,
    #     (column, row),
    #     (column + width, row + height),
    #     (0, 255, 0),
    #     2
    # )
    return img, detected_faces


def createCollage(directoryPath = './collage_pics/'):
    npics = 0
    imgs = []
    for root, dirs, files in os.walk(directoryPath):
        npics = len(files)
        for file in files:
            path = './collage_pics/' + str(file)
            imgs.append(cv2.imread(path))
    resized_imgs = []
    (max_h, max_w, channels) = max([i.shape for i in imgs])
    
    for img in imgs:
        resized_imgs.append(cv2.resize(img,(max_h, max_w), interpolation=cv2.INTER_AREA))
        # resized_imgs.append(img)
    row_imgs = []
    
    if npics == 1:
        return resized_imgs[0]
    
    else :
        for row in range(int(npics/3)):
            try:
                new_image = np.hstack((resized_imgs[3*row], resized_imgs[3*row + 1]))
                new_image = np.hstack((new_image, resized_imgs[3*row + 2]))
            except:
                pass
            row_imgs.append(new_image)
        if len(row_imgs) <= 1:
            return new_image
        
        black_img = np.zeros((max_h, max_w, channels),dtype=np.uint8)
        if npics % 3 == 1:
            new_image = np.hstack((resized_imgs[-1], black_img))
            new_image = np.hstack((new_image, black_img))
            row_imgs.append(new_image)
            
        elif npics % 3 == 2:
            new_image = np.hstack((resized_imgs[-1], resized_imgs[-2]))
            print(new_image)
            new_image = np.hstack((new_image, black_img))
            row_imgs.append(new_image)
            print(new_image)
        
        
        new_image = np.vstack((row_imgs[0], row_imgs[1]))
        
        for i in range(2,len(row_imgs)):
            new_image = np.vstack((new_image, row_imgs[i]))
        
        return new_image
        # cv2.imshow("image", new_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

# img, detected_faces = faceDetector(sys.argv[1])
# cv2.namedWindow("image", cv2.WINDOW_NORMAL)
# cv2.resizeWindow("image", 600,600)
# cv2.imshow("image", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()