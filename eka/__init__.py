from flask import Flask
from flask_bootstrap import Bootstrap
import os
from eka import auth, evaluation
from flask.templating import render_template

# eka = Flask(__name__)
# eka.config.from_object(Config)
#
# bootstrap = Bootstrap(eka)
#
# eka.config['BOOTSTRAP_SERVE_LOCAL'] = True
# eka.config['BOOTSTRAP_USE_MINIFIED'] = True

# from webInterface import mainWebPage, Results


def create_app(test_config=None):
    #     print("1 create app")
    #     # create and configure the app, instance of Flask
    #     #_name_is the name of the current Python module
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'eka.sqlite'),
    )

    # REGISTER BLUEPRINTS
    app.register_blueprint(auth.bp)
    app.register_blueprint(evaluation.bp)
    
    app.add_url_rule('/', endpoint='index')
    
    # a simple page that says hello
    Bootstrap(app)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    # @app.route('/')
    # def index():
    #     return render_template("index.html")

    return app
