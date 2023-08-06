from DGGSForPoly.cell_helpers import str_to_list

def add_finest_subcells(cell_str, cells_in_poly, max_res, rdggs): 
    '''
    Recieves a coarse cell that is fully contained within a Polygon and a cells_in_poly list. Appends the children of resolution 'max_res"
    into cells_in_poly.

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

