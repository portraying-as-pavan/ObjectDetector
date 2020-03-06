from flask import Flask, request, jsonify, send_file
from flask_restful import Resource, Api
import detector
import os
import cv2
app = Flask(__name__)
api = Api(app)

class Index(Resource):
    def get(self):
        json_output = {
            "Message" : "API created for Ciphense assignment",
            "Paths" : [
                {
                    "Path" : "/getImageDetails",
                    "Usage" : "send an image as request",
                    "Description" : "Returns the number of persons,animals,objects"
                },
                {
                    "Path" : "/createCollage",
                    "Usage" : "Send set of images as request",
                    "Description" : "Returns a collage of faces in those images"
                }
            ]
        }
        return json_output


class ImageDetails(Resource):
    def evalClasses(self, classes):
        animals = ['bird', 'cat', 'dog', 'horse', 'sheep',
                'cow', 'elephant', 'bear', 'zebra', 'giraffe']

        json_output = {
            "Message": "NULL",
            "Data": [
                {
                    "PersonCount": 0
                },
                {
                    "AnimalCount": 0,
                
                },
                {
                    "ObjectCount": 0
                }
            ]
        }
        json_data = json_output["Data"]
        for class_name in classes:
            if class_name in animals:
                json_data[1]["AnimalCount"] += 1
                
            elif class_name == 'person':
                json_data[0]["PersonCount"] += 1
            else:
                json_data[2]["ObjectCount"] += 1
        print(json_output)
        return json_output
        
    def post(self):
        file = request.files['image']
        file_path = os.path.join('./imgs/', file.filename)
        file.save(file_path)
        classes , boxes_image = detector.objectDetector(imagePath=file_path)
        json_output = {}
        json_output = self.evalClasses(classes)
        if json_output:
            json_output["Message"] = "Image processed successfully"
        return json_output


class Collage(Resource):
    def post(self):
        imgId = 0
        files = request.files.getlist("image")
        if len(files) > 0:
            os.system('rm ./collage_pics/*')
        for file in files:
            file_path = os.path.join('./imgs/', file.filename)
            file.save(file_path)
            image, detected_faces = detector.faceDetector(file_path)
            for (col, row, width, height) in detected_faces:
                file_name = 'img' + str(imgId) + '.jpg'
                imgId += 1
                cropped_file_path = os.path.join('./collage_pics/', file_name)
                cropped_image = image[row-10: row + width + 10, col-10: col+height+10]
                cv2.imwrite(cropped_file_path, cropped_image)
        image = detector.createCollage()
        cv2.imwrite('./collage_pics/collage.jpg', image)
        return send_file('./collage_pics/collage.jpg', mimetype='image/jpg')


api.add_resource(Index, '/')
api.add_resource(ImageDetails,'/getImageDetails')
api.add_resource(Collage,'/createCollage')


if __name__ == '__main__':
    app.run(host='0.0.0.0')

