import os
from app import app
from app import mongo
from flask import Response, request, current_app
from bson import json_util
from werkzeug import secure_filename
from app.apphelpers import upload
from app.dbhelpers import findhelper
from app.imagesearchapis import imagesearch
from flask.ext.restful import Api, Resource, reqparse
import itertools
import random

@app.route('/test')
def test():
    result_list = findhelper.find_test(mongo.db)

    res = {
        'result': result_list,
        'status': {'text': None, 'file': None}
    }

    return Response(
        json_util.dumps(res),
        mimetype='application/json'
    )

class Suggestion(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('term', type=str)
        super(Suggestion, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        term = args['term']
        suggestion_list = findhelper.text_suggestion(mongo.db, term)
        return Response(
            json_util.dumps(suggestion_list),
            mimetype='application/json'
        )

# Route that will process the file upload

class UpLoad(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('file', type=str)
        self.reqparse.add_argument('offset', type=int)
        self.reqparse.add_argument('query', type=str)
        self.reqparse.add_argument('sortbyrating', type=str)
        self.reqparse.add_argument('sortbyname', type=str)
        super(UpLoad, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        file = request.files['uploadFile']
        if file and upload.allowed_file(file.filename):

            filename = upload.generate_new_filename(file)
            savepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            abspath = os.path.join(os.path.abspath(''), savepath)
            file.save(abspath)

            # call search_by_image(indexmatrix, imagepath) to get images list
            imagesrst = imagesearch.search_image(abspath,
                                     current_app.codebook,
                                     current_app.tfidf)
            imagesrst = imagesrst[::-1]
            businessinfo = upload.result_in_order(mongo.db, imagesrst)
            res = {
                'result': businessinfo,
                'status': { 'text': None, 'file': abspath }
            }

            return Response(
                json_util.dumps(res, default=json_util.default),
                mimetype='application/json'
            )

    def get(self):
        args = self.reqparse.parse_args()
        abspath = args['file']
        query = args['query']
        offset = args['offset'];

        if offset:
            if abspath:
                imagesrst = imagesearch.search_image(abspath,
                                            current_app.codebook,
                                            current_app.tfidf)

                # result_list = findhelper.find_image_by_id(mongo.db,
                #                              imagesrst, offset)
                
                imagesrst = imagesrst[::-1]
                result_list = upload.result_in_order(mongo.db, imagesrst, offset)

            elif query:
                if query == 'homepage':
                    imagesrst = current_app.randimages
                    # result_list = findhelper.find_image_by_id(mongo.db, 
                    #                             imagesrst, offset)
                    result_list = upload.result_in_order(mongo.db, imagesrst, offset)
                else:
                    result_list = findhelper.find_image_by_text(mongo.db,
                                             query, offset)
        else:
            if query == 'homepage':
                # imagesrst = [int(10000*random.random()) for i in xrange(50)]
                # current_app.randimages = imagesrst
                # result_list = findhelper.find_image_by_id(mongo.db, 
                #                             imagesrst)
                location = 'hoboken'
                imagesrst = findhelper.homepage_image(mongo.db, location)
                current_app.randimages = imagesrst
                result_list = upload.result_in_order(mongo.db, imagesrst)
            else:
                result_list = findhelper.find_image_by_text(mongo.db, query)

        res = {
            'result': result_list,
            'status': { 'text': query, 'file': abspath }
        }

        return Response(
            json_util.dumps(res),
            mimetype='application/json'
        )
