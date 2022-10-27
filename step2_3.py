# -*- coding: utf-8 -*-  
# %%
import arcpy, os
from utils.my_api import InitPath, deleteIfExist, getFieldList, reorder_fields, removeAllJoins
from utils.tick import Timer

# %%
def step_2_to_3(regionName, 
                areaCode, 
                gwData):
    
    level = regionName.count('-') + 1 # 1~市级, 2~县级 
    briefName = regionName.split('-')[level-1]

    ti = Timer()
    def rp(section):
        print(regionName + ", " + str(section) + " finished.")
        ti.tk()

    # 2
    inFeatures = gwData
    outFeatures = "difang_30s.shp"
    codePattern = "'" + areaCode[0: 2*level+2] + "%'"
    where_clause = "area_code LIKE " + codePattern
    arcpy.Select_analysis(in_features = inFeatures, 
                      out_feature_class = outFeatures, 
                      where_clause = where_clause)
    if str(arcpy.GetCount_management(outFeatures)) == '0':
        raise Exception("Zero row in " + outFeatures + ".")
    rp(2)
    # 3.1 ? 
    
    # 3.2~3.3
    inFeatures = "grid_90.shp" # selection applied to
    targetLayer = "grid_90.lyr"
    sourceLayer = "difang_30s.shp"
    # https://blog.csdn.net/gognzixiaobai666/article/details/112919955
    arcpy.MakeFeatureLayer_management(in_features = inFeatures, out_layer = targetLayer)
    select = arcpy.SelectLayerByLocation_management(in_layer = targetLayer, 
                                                    overlap_type = "INTERSECT", # default
                                                    select_features = sourceLayer, 
                                                    selection_type = "NEW_SELECTION") # default
    outFeatures = "grid_90_difang.shp"
    arcpy.CopyFeatures_management(in_features = select, 
                                out_feature_class = outFeatures)
    rp(3.3)
    #print arcpy.GetCount_management(sourceLayer)
    #print arcpy.GetCount_management(outFeatures)

    # 3.4
    inFeatures = "grid_90_difang.shp"
    clipFeatures = "difang_30s.shp"
    outFeatures = "difang_90s_mlt.shp" # multi part
    arcpy.Clip_analysis(in_features = inFeatures, 
                        clip_features = clipFeatures, 
                        out_feature_class = outFeatures)
    rp(3.4)

    # 3.5
    # similar as 4.2
    inFeatures = "difang_90s_mlt.shp"
    outFeatures = "difang_90s.shp"
    deleteIfExist(outFeatures)
    arcpy.MultipartToSinglepart_management(in_features = inFeatures, 
                                        out_feature_class = outFeatures)
    rp(3.5)

    # 3.6
    shp = "difang_90s.shp"
    newField = "编号"
    newType = "SHORT"
    arcpy.AddField_management(in_table = shp, 
                            field_name = newField, 
                            field_type = newType)
    rp(3.6)

    # 3.7
    arcpy.CalculateField_management(in_table = shp, 
                                    field = newField, 
                                    expression = "!FID!", 
                                    expression_type = "PYTHON")
    with arcpy.da.SearchCursor(in_table = shp, field_names = newField) as cursor:
        # an iterable object
        vals = [row[0] for row in cursor]
        maxVal = max(vals)
        minVal = min(vals)
        print(minVal, maxVal)
    if minVal <= 0:
        print("There are {} <= 0.".format(newField))
        with arcpy.da.UpdateCursor(in_table = shp, field_names = newField) as cursor:
            for row in cursor:
                if row[0] <= 0:
                    maxVal += 1
                    row[0] = maxVal
                    cursor.updateRow(row)
        print("Update complete.")
    else:
        print("All {} >= 1.".format(newField))
    rp(3.7)

    ti.tk(k = 1)

# %%
if __name__ == '__main__':
    pass