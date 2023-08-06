# Using flask to make an api
# import necessary libraries and functions
from flask import Flask, jsonify, request
from flask_restx import Resource, Api

import os
import sys
# creating a Flask app
app = Flask(__name__)
api = Api(app)

base_path = '/testsequence'

if os.path.exists(base_path):
    print("inside a container")
else:
    base_path = './testsequence'
sys.path.append(base_path)
print(sys.path)
@api.route('/<string:pod_id>/<string:test_step_name>')
class TestPod(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.compiled_code_map=dict()
    def get(self, pod_id,test_step_name):
        self.teststepx(pod_id,test_step_name)
        return {'status':'{} executed...'.format(test_step_name)}
        
    def teststepx(self,pod_id,test_step_name):        
        test_step_id=f'{pod_id}/{test_step_name}'.format(pod_id, test_step_name)
        code = self.compiled_code_map.get(test_step_id)       
        if code is None:
            sys.path.append(f'/{base_path}/{pod_id}/'.format(base_path,pod_id))
            file_name = f'/{base_path}/{pod_id}/{test_step_name}.py'.format(base_path,pod_id, test_step_name)
            code = compile(source =open(file_name).read() ,filename = file_name, mode='exec')
            self.compiled_code_map[test_step_id]=code
        exec(code)
       #execfile()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5000)
