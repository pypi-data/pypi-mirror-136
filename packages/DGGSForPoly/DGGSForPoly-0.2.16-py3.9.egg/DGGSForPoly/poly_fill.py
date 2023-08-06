from auspixdggs.auspixengine.dggs import Cell, RHEALPixDGGS
from auspixdggs.auspixengine.ellipsoids import WGS84_ELLIPSOID
from DGGSForPoly.poly_fill_helpers import add_finest_subcells #, raytrace_centroid_in_poly
from DGGSForPoly.cell_helpers import  get_cell_poly, str_to_list
from shapely.geometry import shape, Point

def poly_fill(geojson=None, polygon=None, rdggs=RHEALPixDGGS(ellipsoid=WGS84_ELLIPSOID, max_areal_resolution=1), max_res=None, hybrid=True, return_objects=False, fill_strategy='poly_fully_covered_by_cells'):
    '''
    Returns a set of rHEALPIX dggs cells that represent the given polygon according to a desired fill_strategy. 
    The input polygon can be a shapely object or define within 'geojson' parameter
    
    Parameters
    ----------
    
    geojson: dict or innards of geojson object  containing a single Polygon (or multipolygon or line) to find dggs for.
        Format:
            {
                'type': 'Polygon',
                'coordinates': [outer, hole1, hole2, ...],
            }
        example for getting geojson dict from geojson file:
            f = open("../spatial_data/ACT_SA1_Black_Mountain.geojson"); 
            geojson_obj = geojson.loads(f.read())
            geojson = gj_obj['features'][poly_num]['geometry']
            #where poly_num is the poly_num'th shape defined in the geojson file. 
            (See function "polyfill_from_geojson" for geojsons with many geometries.)
            
    polygon: shapely shape to find a set of dggs cells to represent it
        
    rdggs: The rHEALPix DGGS on a given ellipsoid. Defaults to WGS84_ELLIPSOID, with max res of 15.
    
    max_res: int - desired finest resolution of outputted cells which describe the polygon.
    
    hybrid: bool - if True use hybrid representation of polygon i.e. mix resolutions to save some space. 
    if false, cells returned are all of res 'max_res'
    
    return_objects - if True, return auspixdggs cell objects, else return strings of the cells suids.
    
    fill_strategy: string specifying the desired fill strategy. Can be one of:
        "centroids-in-poly" - includes cells if their centroids lie witihn the polygon
        "cells-fully-contained-in-poly" - includes cells that are entirely within the polygon (always under estimates area)
        "poly-fully-covered-by-cells" - includes cells that are fully or partially within the polygon. (always over estimates area)
    
  
    gj_obj = geojson.loads(f.read()) and f = open("../spatial_data/ACT_SA1_Black_Mountain.geojson"); 
    
    '''  
    
    if polygon:
        pass
    else: #recieved geojson, make the shapely polygon
        polygon=shape(geojson)
    rdggs=RHEALPixDGGS(ellipsoid=WGS84_ELLIPSOID, max_areal_resolution=1)
    fill_strategies=['poly_fully_covered_by_cells', 'centroids_in_poly', 'cells_fully_contained_in_poly' ]
    if fill_strategy not in fill_strategies:
        raise Exception(f"Incorrest fill_strategy given. Must be one of {*fill_strategies,}")
    if not (max_res and polygon):
        raise Exception("No resolution or rdggs or polygon recieved")   
    dggs_cells = []
    
    stack = rdggs.cells0.copy()
    while(stack): 
        cell_str = stack.pop(-1)
        cell = rdggs.cell(suid=str_to_list(cell_str)) 
        cell_poly = get_cell_poly(cell) 
        at_max_res = (len(cell_str)-1 >= max_res)     
        if (not at_max_res) or fill_strategy=='cells_fully_contained_in_poly':
            if polygon.contains(cell_poly): 
                if (hybrid or at_max_res):  #if hybrid or at smallest resoluition, append.
                    dggs_cells.append(cell_str)
                else:  #Not hybrid and fully contained parent cell, -> apend children which will be contained if the parent is.
                    add_finest_subcells(cell_str, dggs_cells, max_res, rdggs) 
                continue          
        if(fill_strategy=='cells_fully_contained_in_poly'):
                #fill_strategy is contained, but this cell is not fully contained (otherwise would have appened above)
                if(len(cell_str)-1<max_res): 
                    if(cell_poly.intersects(polygon)):
                         for child in cell.subcells(): stack.append(str(child))                                         
        elif(fill_strategy=='centroids_in_poly'):
            if (len(cell_str)-1 < max_res): #if not at max res and it overlaps, investigate children
                if(cell_poly.intersects(polygon)):  
                    for child in cell.subcells(): stack.append(str(child))               
            else: #Cell is at max res, add if centroid is contained.
                centroid = cell.nucleus(plane=False) 
                if polygon.contains(Point(centroid[0], centroid[1])): #use ray tracing here.
                #if raytrace_centroid_in_poly(centroid=centroid, poly=polygon): #other if statement top swap in for ray tracing fill_strategy (slower - yet to investigate why)
                    dggs_cells.append(cell_str)                   
        else: #fill_strategy == overlaps (and this cell isn't fully contained)
            if (len(cell_str)-1 < max_res): #not at max res, generate cchildren to investigate
                if(cell_poly.intersects(polygon)):        
                    for child in cell.subcells(): stack.append(str(child))
            elif(cell_poly.intersects(polygon)): #cell is at make res, add if overlapping.
                dggs_cells.append(cell_str)       
    
    dggs_cells = list(set(dggs_cells)) #removes duplicates
    
    #condense? ( In hybrid mode, sometimes a entire collection of children are included after further checking, these could be compressed to the parent which can then again now be compressed into grandparents and so on)
    
    if return_objects: #you want rdggs cell objects and not strings.
        for i in range(len(dggs_cells)): #could use enumarate i,v here. wou;d changing v change whats in the list or is a copy?
                dggs_cells[i] = rdggs.cell(suid=str_to_list(dggs_cells[i]))  
    return dggs_cells


def poly_fill_from_geojson(geojson_obj=None, max_res=10, rdggs=RHEALPixDGGS(ellipsoid=WGS84_ELLIPSOID, max_areal_resolution=1), hybrid=True, return_objects=False, fill_strategy='poly-fully-covered-by-cells'):
    '''
    Recieves a geojson obj/dict containing multiple features, and returns a list of lists containing dggs cells 
    for each features' geometry in order they appear in the feature collection.
    To create the geojson object from a geojson file: 
        f = open("FileName.geojson") 
        geojson_obj = geojson.loads(f.read()) OR geojson_obj = json.loads(f.read()). 
        The latter will be an actual python dict, functionally the same thing to my experience.
    '''
    list_of_lists_of_dggs_cells=[None]*len(geojson_obj['features'])

    for i,feature in enumerate(geojson_obj['features']):
        list_of_lists_of_dggs_cells[i]=polyfill(geojson=feature['geometry'], max_res=max_res, rdggs=rdggs, hybrid=hybrid, 
                                                return_objects=return_objects, fill_strategy=fill_strategy) 
 
    return list_of_lists_of_dggs_cells