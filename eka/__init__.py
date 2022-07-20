from flask import Flask
from flask_bootstrap import Bootstrap
import os
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
    # app = Flask(__name__, instance_relative_config=True)

    app = Flask(__name__)
    print(app)

    app.config.from_mapping(
        SECRET_KEY='71d60150a7888feabeddbfc279658ffc0261fa972fae1191a595c2ffa79e1281',
        # DATABASE=os.path.join(app.instance_path, 'eka.sqlite'),
        # SCRIPT_NAME='/user-study',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.add_url_rule('/', endpoint='index')

    from eka import auth, evaluation

    # REGISTER BLUEPRINTS
    app.register_blueprint(auth.bp)
    app.register_blueprint(evaluation.bp)

    # a simple page that says hello
    Bootstrap(app)

    @app.route('/hello')
    @app.route('/user-study/hello')
    def hello():
        return 'Hello, World!'

    # @app.route('/')
    # def index():
    #     return render_template("index.html")

    return app


eka_app = create_app()

# @app.route('/')
# def index():
#     return render_template("index.html")
