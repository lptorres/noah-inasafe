#tornado imports
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options

#python imports
import glob
import json
import os
from subprocess import call

#third-party imports
import psycopg2
import psycopg2.extras
import redis

#inasafe imports
from safe.api import read_layer, calculate_impact, get_admissible_plugins, \
    bbox_intersection

from tornado.options import define, options
define("port", default=5000, help="run on the given port", type=int)



class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
           (r'/layer/([0-9]+)', LayerHandler),
            (r"/calculate/", CalculateHandler),
        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)



class LayerHandler(tornado.web.RequestHandler):
    def get(self, layer_id):
        try: 
            if layer_id:
                try:
                    conn = psycopg2.connect(
                        "dbname='dev' user='vagrant' password='vagrant'"
                    )
                except:
                    writeout = 'An error occured while trying to connect to'+\
                    ' the database.'
                else:
                    cursor = conn.cursor(
                        cursor_factory = psycopg2.extras.DictCursor
                    )
                    query = 'SELECT * FROM layers WHERE id=%s' % layer_id
                    try:
                        cursor.execute(query)
                    except:
                        writeout = 'There was something wrong with your query'
                        conn.rollback()
                    else:
                        item = cursor.fetchone()
                        if item:
                            writeout = json.dumps(dict(item))
                        else:
                            writeout = 'Sorry, your query returned 0 matches'
        except:
            writeout =  "You didn't provide any query parameters!"
            
        self.write(writeout)
 
        
                   
class CalculateHandler(tornado.web.RequestHandler):
    def get(self):
#        try:
        exposure_id = self.get_argument('e')
        hazard_id = self.get_argument('h')
        impact_name = 'impact-e%s-h%s' % (exposure_id, hazard_id)
        if exposure_id and hazard_id:
            # First check if the impact already exists in the cache
            try: # try to connect to the redis cache
                redis_server = redis.Redis()
                cache = True
                print 'Successfully connected to redis!'
            except:
                # This is just a flag that will be used later on
                print "I couldn't connect to redis"
                cache = False
            else:
                # If the impact exists, get it from the cache and return
                if redis_server.exists(impact_name):
                    print 'Entry exists in cache!'
                    writeout = redis_server.get(impact_name)
                    self.set_header('Content-Type', 'application/javascript')
                    self.write(writeout)
                    return
                    
            # Query the db and calculate if it doesn't
            try: #try connecting to the pg database
                conn = psycopg2.connect(
                    "dbname='dev' user='vagrant' password='vagrant'"
                )
                print 'Successfully connected to postgres!'
            except:
                writeout = 'Could not connect to the database!'
            else:
                # create a cursor
                cursor = conn.cursor(
                    cursor_factory = psycopg2.extras.DictCursor
                )
                try:
                    #1. Query the db for the layers
                    query = 'SELECT shapefile FROM layers'+\
                                ' WHERE id = %s' % exposure_id
                    cursor.execute(query)
                    exposure = cursor.fetchone()
                    query = 'SELECT shapefile FROM layers'+\
                                ' WHERE id = %s' % hazard_id
                    cursor.execute(query)
                    hazard = cursor.fetchone()
                except:
                    writeout = 'There was something wrong with your query'
                    conn.rollback()
                else:
                    if exposure and hazard:
                        # Pass the shapefile (paths) to read_layer
                        try:
                            exposure_layer = read_layer(exposure['shapefile'])
                            hazard_layer = read_layer(hazard['shapefile'])
                        except:
                            writeout = 'Something went wrong when reading the layers'
                        # Keywords
                        exposure_dict = exposure_layer.get_keywords()
                        hazard_dict = hazard_layer.get_keywords()
                        
                        if exposure_layer.is_vector:
                            exposure_dict['layertype'] = 'vector'
                        else:
                            exposure_dict['layertype'] = 'raster'
                            
                        if hazard_layer.is_vector:
                            hazard_dict['layertype'] = 'vector'
                        else:
                            exposure_dict['layertype'] = 'raster'

                        #get optimal bounding box
                        common_bbox = bbox_intersection(
                            exposure_layer.get_bounding_box(),
                            hazard_layer.get_bounding_box()
                        )
                        print exposure_layer.get_bounding_box()
                        print hazard_layer.get_bounding_box()
                        bbox_string = ''
                        try:
                            for val in common_bbox:
                                bbox_string += str(val) + ' '
                        except:
                            writeout = 'The layers have no intersection!'
                        else:
                            #gdal clip
                            dest = 'hazard_tmp.shp'
                            src = hazard_layer.filename
                            print src
                            try:
                                call(
                                    "ogr2ogr -clipsrc %s %s %s" % \
                                    (bbox_string, dest, src), shell=True
                                )
                            except:
                                print 'could not clip hazard'
                            else:
                                print 'created clipped hazard. Reading layer now.'
                            try:
                                clipped_hazard = read_layer("hazard_tmp.shp")
                            except:
                                print 'something went wrong when reading the clipped hazard'
                            else:
                                print clipped_hazard
                            
                            dest = 'exposure_tmp.shp'
                            src = exposure_layer.filename
                            print src
                            try:
                                call(
                                    "ogr2ogr -clipsrc %s %s %s" % \
                                    (bbox_string, dest, src), shell=True
                                )
                            except:
                                print 'could not clip exposure'
                            else:
                                print 'created clipped exposure. Reading layer now.'
                            try:
                                clipped_exposure = read_layer("exposure_tmp.shp")
                            except:
                                print 'something went wrong when reading the clipped exposure'
                            else:
                                print clipped_exposure
                            #get impact function based on layer keywords
                            fncs = get_admissible_plugins([hazard_dict, 
                                exposure_dict])
                            impact_fnc = fncs.values()[0]

                            layers = [clipped_hazard, clipped_exposure]

                            # Call calculate_impact
                            impact_file = calculate_impact(
                                layers, impact_function
                            )
                            
                            tmpfile = 'tmp%s.json' % impact_name

                            #5. Serialize the output into json and write out
                            # Convert the impact file into a json file
                            call(['ogr2ogr', '-f', 'GeoJSON', tmpfile, 
                                    impact_file.filename])
                            # Open the json file        
                            f = open(tmpfile)
                            #FIXME: Something needs to be done about the encoding
                            # Load the file as json
                            json_data = json.loads(
                                f.read(), 
                            )
                            
                            # Write it out as json
                            writeout = json.dumps(
                                json_data, 
                            )

                            #close the file, and delete temporary files
                            f.close()
                            os.remove(tmpfile)
                            os.remove("hazard_tmp.shp")
                            os.remove("exposure_tmp.shp")
                            #os.remove(impact_file.filename)
                            
                            #6. Cache
                            if cache:
                                redis_server.set(impact_name, writeout)
                                #use setex to add a cache expiry
                            #writeout = json.dumps(impact_file.data, encoding='latin-1')
                    else:
                        writeout = 'Sorry, your query returned one or' + \
                            ' more empty matches'
#        except:
#            writeout = 'Something went wrong! Hmmm...'
    
        self.set_header('Content-Type', 'application/javascript')
        self.write(writeout)



if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()