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
            print imagesrst
            businessinfo = []

            for x in xrange(12):
                img = findhelper.find_image_by_id_new(mongo.db, imagesrst[x])
                businessinfo.append(img)

            # businessinfo = findhelper.find_image_by_id(mongo.db, imagesrst)

            businessinfo = list(itertools.chain(*businessinfo))
            print businessinfo.__class__
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
                result_list = []
                for x in xrange(offset):
                    img = findhelper.find_image_by_id_new(mongo.db, imagesrst[x])
                    result_list.append(img)
                result_list = list(itertools.chain(*result_list))

            elif query:
                result_list = findhelper.find_image_by_text(mongo.db,
                                             query, offset)
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
