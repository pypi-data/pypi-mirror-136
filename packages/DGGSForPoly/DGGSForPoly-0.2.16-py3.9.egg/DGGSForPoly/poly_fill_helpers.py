from shapely.geometry import Polygon, MultiPolygon

def add_finest_subcells(cell_str, cells_in_poly, max_res, rdggs): 
    '''
    This is called within the function 'polyfill' when a coarse cell is found to be fully contained within the polygon && hybrid=False, so it is desired to represent the coarse cell (and broader poly) using cells only of the finest res.
    This function recieves a coarse cells and the cell list to append the finer cells into.
    
    Parameters
    ---------
    
    cell_str: the coarse cell we wish to append the finest subcells of
    
    cells_in_poly: the list describing the broader polygon to append the finest cells into
    
    max_res: the resolution for the finest cells
    
    rdggs: The rHEALPix DGGS on a given ellipsoid.
    
    '''
    cells = [cell_str]
    while(cells):
        cell = rdggs.cell(suid = str_to_list(cells.pop(-1)))
        for subcell in cell.subcells():
            if len(str(subcell))-1>= max_res:
                cells_in_poly.append(str(subcell))
            else: #go deeper
                cells.append(str(subcell))
    return


def raytrace_centroid_in_poly(centroid=None, poly=None):
    '''
    Wrapper for raytrace_centroid_in_ShapelyPolygon to handle case of Multipolygon.
    
    Recieves a Shapely Polygon or Multipolygon and a cell's centroid . Returns True if the centroids is within the shape. Else false.
    
    centroid: tuple - (x,y)
    poly: Shapely Polygon or MultiPolygon
    
    '''
    if isinstance(poly, MultiPolygon):
        for polygon in poly.geoms:
            if raytrace_centroid_in_ShapelyPolygon(centroid=centroid, poly=polygon):
                return True
        #finished loop,  havnt returned yet, then centroid is not inside any polygon.
        return False
    elif isinstance(poly, Polygon):
        return raytrace_centroid_in_ShapelyPolygon(centroid=centroid, poly=poly)
    else:
        raise Exception('not Polygon or Multipolyogn supplied. Cannot have centroids within lines.')
        return None
    raise Exception('shouldve returned')
    return None

def raytrace_centroid_in_ShapelyPolygon(centroid=None, poly=None):
    '''
    returns true if a cells centroid is within the Polygon, else False.
    centroid: tuple - (x,y)
    poly: Shapely Polygon (not MultiPolyogn)
    '''
    #For polygons (where Polygons include the holes in them)
    if not ray_tracing(centroid[0], centroid[1], poly.exterior.coords):
        return False #if not in exterior, not in anything
    #else, check if in a whole
    for hole in poly.interiors: #the interior holes, if any.
        if ray_tracing(centroid[0], centroid[1], hole.coords):
            return False #inside hole
    #haven;'t returned yet, therefor inside the exterior and not in any wholes.
    return True

# Below function is from GeoScience Australia who got it from stack overflow as shown.
# line intersection function
#@jit(nopython=True)
def ray_tracing(x,y,poly):
    # from https://stackoverflow.com/a/48760556  
    n = len(poly)
    inside = False
    p2x = 0.0
    p2y = 0.0
    xints = 0.0
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside