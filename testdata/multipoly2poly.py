from osgeo import gdal, ogr
import sys



def multipoly2poly(layer):
    for feature in layer: 
        fid = feature.GetFID()
        geom = feature.GetGeometryRef()
        if geom.GetGeometryName() == 'MULTIPOLYGON':
            layer.DeleteFeature(fid)        
            for geom_part in geom: 
                addPolygon(geom_part.ExportToWkb(), feature, layer) 
    feature.Destroy()



def addPolygon(simplePolygon, feature, layer): 
    featureDefn = layer.GetLayerDefn() 
    polygon = ogr.CreateGeometryFromWkb(simplePolygon) 
    new_feat = ogr.Feature(featureDefn) 
    new_feat.SetGeometry(polygon)

    for id in range(feature.GetFieldCount()):
        data = feature.GetField(id)
        new_feat.SetField(id, data)

    layer.CreateFeature(new_feat)


def main():
    #Check if the input filename is a shapefile
    filename = sys.argv[1]
    if filename[-4:] != '.shp':
        print 'Error: You did not select a valid input ESRI shapefile.'
        return

    gdal.UseExceptions() 
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(filename, 1)
    #Check if driver.Open was able to successfully open the shapefile
    if ds is None:
        print 'Error: The input shapefile you specified does not exist.'
        return
    layer = ds.GetLayer()
    multipoly2poly(layer)
    #Cleanup
    ds.Destroy()



if __name__ == '__main__':
    main()