import unittest
unittest.TestLoader.sortTestMethodsUsing = None

from pathlib import Path 
import sys, os, jsoncfg, json
sys.path.insert(0, '../../../')
 
# from zohavi.zcore.appcore import AppCore 

from flask import Flask, jsonify, render_template,send_file, request
from mclogger.mclogger import MCLogger

logger = MCLogger( 'test_log.txt' )
 

html = """<html>
			<body>
				<h1>hello world</h1>
			</body>
		</html>"""
site_update_schema = {
							"SiteEnv":[{ 	
								"module_name":"test_wc",
								"table_obj": "SiteEnv",
								"fields":{
											"si_env_id":{"field_db":"id",   "key":True},
											"si_env_name":{"field_db":"env_name", "validation":{"required":True, "text_min_len":3, "text_max_len":20} },
											"si_env_code":{"field_db":"env_code", "validation":{"required":True,  "text_max_len":5} },
											"si_env_desc":{"field_db":"env_desc", "validation":{"required":False,  "text_max_len":200} }
								}
							}]
					}

from sqlalchemy import Column, Integer, String 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

from zohavi.zdb.models import TBL_Default
from zohavi.zwebui.data_ui_model import DataUIModel
from zohavi.zwebui.jinja_cust_funcs import JCFunc

Base = declarative_base()


	# cfg_main_runme 	= Column(String(10) ) #dev, qa, prod  
# 	_env_list = relationship("SiteEnv", backref=backref("site_env" ), lazy='select') 
	

# engine = create_engine('sqlite:///:memory:')
# Session = sessionmaker(bind=engine)
# session = Session()

# Base.metadata.create_all(engine)

# session.commit()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

JCFunc.load_template_funcions( app.jinja_env)

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

############################################################################################################
############################################################################################################
class SiteEnv( db.Model ,  TBL_Default):
	__tablename__ = 'site_env' 
	id = Column(Integer(), primary_key=True)
	env_name = Column(String(100) ) 
	env_desc = Column(String(200) ) 
	env_code = Column(String(5) )  

db.create_all()
# db.session.add( SiteEnv(env_name='dev', env_desc='Twitter Bot', env_code='dev1') )
# db.session.commit()

# myapp = AppCore(app, sccfg, 'dev' )

#################################################################
@app.route('/webui/<path:url>', methods=['GET' ])
def webui_path( url ):
	# path = current_app.config['ENV_BASE_DIR']
	search_file = os.getcwd()[:os.getcwd().rfind('/')] +"/" +url
	# breakpoint()

	if Path( search_file ).is_file():
		return send_file( search_file )

	print("file missing:" + str(search_file)   )
	abort(404)
	logger.debug(url)
	return render_template( 'test_table.html')

#################################################################
@app.route('/test/menu', methods=['GET' ] )
def test_menu( ):
	return render_template( 'test_menu.html')
 
#################################################################
@app.route('/test/table', methods=['GET' ] )
def test_table( ):
	return render_template( 'test_table.html')



#################################################################
@app.route('/', methods=['GET' ] )
def test_all( ):
	routes = {}
	for rule_item in app.url_map._rules:
		routes[rule_item.rule] = {}
		routes[rule_item.rule]["functionName"] = rule_item.endpoint
		routes[rule_item.rule]["methods"] = list(rule_item.methods)

	return render_template( 'test_all.html', routes=routes)


#################################################################
@app.route('/test/group', methods=['GET' ] )
def test_group( ):
	data_ui = DataUIModel(  site_update_schema['SiteEnv'] , db.session, logger )
	return render_template( 'test_group.html', data_ui=data_ui)

#################################################################
@app.route("/test/table/ajax_add", methods=["POST"])
def test_table_add():
	logger.debug( request.json )
	data_ui = DataUIModel(  site_update_schema['SiteEnv'] , db.session, logger )
	return data_ui.data_update_ajax( request.json )
	# return json.dumps({'success':True}), 200

#################################################################
@app.route("/test/table/ajax_edit", methods=["POST"])
def test_table_edit():
	logger.debug( request.json )
	data_ui = DataUIModel( site_update_schema['SiteEnv'] , db.session, logger )
	return data_ui.data_update_ajax( request.json )

#################################################################
@app.route("/test/table/ajax_del", methods=["POST"])
def test_table_del():
	logger.debug( request.json )
	data_ui = DataUIModel(   site_update_schema['SiteEnv'] , db.session, logger )
	return data_ui.data_delete_ajax( request.json ) 



#################################################################
@app.route("/routes", methods=["GET"])
def getRoutes( ):
	routes = {}
	for rule_item in app.url_map._rules:
		routes[rule_item.rule] = {}
		routes[rule_item.rule]["functionName"] = rule_item.endpoint
		routes[rule_item.rule]["methods"] = list(rule_item.methods)
	return jsonify(routes)

 
 #################################################################
 #################################################################
if __name__ == '__main__':
	app.run(host="0.0.0.0", port=4601, debug=True)
