from auspixdggs.auspixengine.dggs import Cell, RHEALPixDGGS
from auspixdggs.auspixengine.ellipsoids import WGS84_ELLIPSOID
from shapely.geometry import Polygon, MultiPolygon
from math import isclose

def get_cell_poly(cell):
    '''
    Returns the shapely polygon of a rhealpix cell object by first finding the vertices using cell.vertices().
 
    Mostly, this function returns cell.vertices(), but sometimes fixes the results up for shapely to interpret better. 
    For example to interpret a polar cap cell as an area and not a line along constant latitude. 
    Additionally, if a cell boundary crosses or touches the +-180 longitude, the function splits the cell and returns a multipolygon.
    This ensures shapely defines the area of the polygon as not going the long way around the ellipsoid which would be incorrect. 
    
    Parameters
    ---------
    cell: a rhealpix cell object to find the shapely polygon for using EPSG:4326 CRS.
    
    '''
    cell_shape = cell.ellipsoidal_shape()   
    vertices = cell.vertices(plane=False, trim_dart=True)
    if cell_shape == 'cap': #make polygon out of line of latitude so shapely iterprets the cap as a poly and not a line
        pole = str(cell)[0]
        if(pole == 'N'):
            height = vertices[0][1]
            vertices = [(-180, 90), (180, 90), (180, height), (-180, height)] # order: NW, NE, SE, SW
            return Polygon(vertices)
        elif(pole == 'S'):
            height = vertices[0][1]
            vertices = [(-180,height), (180, height), (180, -90), (-180, -90)] # order: NW, NE, SE, SW
            return Polygon(vertices)
        else: 
            raise Exception('error1')   # should never happen    
        
    elif cell_shape in ['quad', 'skew_quad', 'dart']: 
        x_coords = [vertices[i][0] for i in range(len(vertices))]
        minx = min(x_coords)
        maxx = max(x_coords)
        
        if(round( abs(maxx - minx))>179 ): # if long way around.
            abs_tol = 0.0000001
            if cell_shape=='dart' and minx<0 and maxx>0: #dart bisects the 180. Need to check minx and maxx               
                y_coords = [vertices[i][1] for i in range(len(vertices))]
                miny = min(y_coords)
                maxy = max(y_coords)   
                pole = str(cell)[0]
                if pole == 'N': #dart is right side up (points up)
                    Poly1 = Polygon([ (-maxx, miny), (-180, miny), (-180, maxy) ]) #neg side
                    Poly2 = Polygon([ (maxx, miny), ( 180, miny), ( 180, maxy) ])
                elif pole =='S': #dart is pointing down
                    Poly1 = Polygon([ (-maxx, maxy), (-180, maxy), (-180, miny) ]) #neg side
                    Poly2 = Polygon([ (maxx, maxy), ( 180, maxy), ( 180, miny) ])   
                else:
                    raise Exception("there are dart in non poles?") # NO
                return MultiPolygon([Poly1, Poly2])     
                raise Exception('shoudlve returned. Not accounted for yet, do they exist?')
            #havent't returned. not crossing dart. but stil defined long way around --> touches and is using wrnog polarity for 180
            for i in range(len(vertices)):
                if isclose(vertices[i][0], -180, abs_tol=abs_tol):
                    vertices[i] = (180, vertices[i][1]) #can't change tuples so re define.
                elif isclose(vertices[i][0], 180, abs_tol=abs_tol):
                    vertices[i] = (-180, vertices[i][1])
            return Polygon(vertices)
        else: #all checks done its ok - return as is from cell.vertices
            return Polygon(vertices)
    else:
        raise Exception('error2')         
        return None
    
def str_to_list(mystr):   
    #converts string cell id to list (keeping the letter a str). This is what the cell object constructor requires.
    return [mystr[0]] + [int(i) for i in mystr[1:]]