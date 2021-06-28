"""Flask Application"""

# load libaries
from flask import Flask, jsonify
import sys

# load modules
from src.models.blueprint_x import blueprint_x
from src.models.creative_performance import CreativePerformance

from src.models.Single_add_train_test import SingleAdd
from src.models.train_all import AllTrain
from src.models.all_images import AllImages

# init Flask app
application = Flask(__name__)

@application.route('/')
def hello():
	return '<h1> App loaded Successfully ......!!</h1>'

# register blueprints. ensure that all paths are versioned!
application.register_blueprint(blueprint_x, url_prefix="/api/v1/blueprint_x")

application.register_blueprint(CreativePerformance, url_prefix="/api/v1/creative_performance")
application.register_blueprint(SingleAdd, url_prefix="/api/v1/similar_imgs")

application.register_blueprint(AllTrain, url_prefix="/api/v1/specific")
application.register_blueprint(AllImages, url_prefix="/api/v1/all")

