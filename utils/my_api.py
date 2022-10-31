# -*- coding: utf-8 -*-
import arcpy, os

class InitPath(object):
    # initiate and create gdb database (if not exist) 
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            # if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance
    
    def __init__(self, scratch_path, gdb_name = "Scratch"):
        # create folder
        scratch_path = unicode(scratch_path, 'utf-8')
        try: 
            if not os.path.isdir(scratch_path):
                os.makedirs(scratch_path)
        except: # If there is no disk D.
            scratch_path = "E:\doc\Scratch" 
            if not os.path.isdir(scratch_path):
                os.makedirs(scratch_path)

        # create gdb
        scratch_gdb = os.path.join(scratch_path, gdb_name + ".gdb")
        if not arcpy.Exists(scratch_gdb):
            arcpy.CreateFileGDB_management(out_folder_path = scratch_path, out_name = gdb_name)
        arcpy.env.workspace = scratch_path
        arcpy.env.overwriteOutput = True
        
        self.scratch_path = scratch_path
        self.scratch_gdb = scratch_gdb
    
    def __iter__(self):
        return (i for i in (self.scratch_path, self.scratch_gdb))


def deleteIfExist(features, dele = True, verbose = 0):
    if arcpy.Exists(dataset = features):
        if verbose:
            print("{} already exist.".format(features))
        if dele:
            arcpy.Delete_management(in_data = features)
            if verbose:
                print("Successfully delete the old {}.".format(features))
    else:
        if verbose:
            print("Doesn't exist.")
        
        
def getFieldList(features, getVal = False):
    print(features)
    printSepLine()
    ans = []
    for x in arcpy.ListFields(dataset = features):
        print x.name
        print(x.required, x.type)
        ans
    # return [{"name": x.name, "type": x.type, "required": x.required} for x in arcpy.ListFields(dataset = features)]


'''
http://joshwerts.com/blog/2014/04/17/arcpy-reorder-fields/
'''
def reorder_fields(table, out_table, field_order, add_missing=True):
    
    """
    Reorders fields in input featureclass/table
    :table:         input table (fc, table, layer, etc)
    :out_table:     output table (fc, table, layer, etc)
    :field_order:   order of fields (objectid, shape not necessary)
    :add_missing:   add missing fields to end if True (leave out if False)
    -> path to output table
    """
    existing_fields = arcpy.ListFields(table)
    existing_field_names = [field.name for field in existing_fields]

    existing_mapping = arcpy.FieldMappings()
    existing_mapping.addTable(table)

    new_mapping = arcpy.FieldMappings()

    def add_mapping(field_name):
        mapping_index = existing_mapping.findFieldMapIndex(field_name)

        # required fields (OBJECTID, etc) will not be in existing mappings
        # they are added automatically
        if mapping_index != -1:
            field_map = existing_mapping.fieldMappings[mapping_index]
            new_mapping.addFieldMap(field_map)

    # add user fields from field_order
    for field_name in field_order:
        if field_name not in existing_field_names:
            raise Exception("Field: {0} not in {1}".format(field_name, table))

        add_mapping(field_name)

    # add missing fields at end
    if add_missing:
        missing_fields = [f for f in existing_field_names if f not in field_order]
        for field_name in missing_fields:
            add_mapping(field_name)

    # use merge with single input just to use new field_mappings
    arcpy.Merge_management(table, out_table, new_mapping)
    return out_table


'''
https://community.esri.com/t5/arcgis-pro-ideas/remove-all-joins-programatically/idi-p/974557
https://community.esri.com/t5/geoprocessing-questions/arcgis-10-is-there-a-way-to-remove-all-joins-with/td-p/259558
'''
def removeAllJoins(tbl):
    """Remove all joins from a layer or table view"""
    flds = [f.name for f in arcpy.ListFields(tbl)]
    wk = os.path.dirname(arcpy.Describe(tbl).catalogPath)
    joins = [arcpy.ParseFieldName(f, wk).split(", ")[-2] for f in flds]
    joins = list(set(joins)) # unique the list
    if joins[0] == "(null)":
        print("No join active")
    else:
        print("Active join exists.")
        # remove base table name from list and remove all joins
        joins.remove(arcpy.Describe(tbl).baseName)
        for j in joins:
            arcpy.RemoveJoin_management(tbl, j)
            print("Removed join {}".format(j))
    return

def printSepLine(n = 1):
    for i in range(n):
        print("==========================================================================" * 2)