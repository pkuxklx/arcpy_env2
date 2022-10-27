# %% [markdown]
# ### Initialize

# %%
import arcpy, os, sys, math
from utils.my_api import InitPath, deleteIfExist, getFieldList, reorder_fields, removeAllJoins
# 显示中文编码
'''
from imp import reload
import sys
reload(sys)
sys.setdefaultencoding('utf8')
'''

# %%
folder_path, gdb_path = InitPath(gdb_name = "test")
print(folder_path)
print(gdb_path)

# %%
arcpy.env.workspace = gdb_path 
arcpy.env.overwriteOutput = True 

# %% [markdown]
# ### 1.1 ??? 环境设置

# %%
newCoordinate = arcpy.SpatialReference(4490)
print(newCoordinate.name)
arcpy.env.outputCoordinateSystem = newCoordinate

# %% [markdown]
# ### 1.2

# %%
outFeatures = "grid_90.shp"
deleteIfExist(outFeatures, dele = 0)

# %%
originCoordinate = "73 0"
yAxisCoordinate = "73 10"
cornerCoordinate = "136 54"
number_rows = 2160
number_cols = 2520
labels = "NO_LABELS"
geoType = "POLYGON"

# %%
arcpy.CreateFishnet_management(out_feature_class = outFeatures, 
                               origin_coord = originCoordinate, y_axis_coord = yAxisCoordinate, corner_coord = cornerCoordinate, 
                               number_rows = number_rows, number_columns = number_cols, 
                               labels = labels, 
                               geometry_type = geoType)

# %%
getFieldList(outFeatures)

# %% [markdown]
# ### 2

# %% [markdown]
# similar as 4.4

# %%
inFeatures = "D:\COURSES\ADAS_intern\GisData\gw.shp"
outFeatures = "shanxi_30s.shp"
deleteIfExist(outFeatures, 0)

# %%
arcpy.Select_analysis(in_features = inFeatures, 
                      out_feature_class = outFeatures, 
                      where_clause = "area_code LIKE '1401%'")

# %% [markdown]
# ### 3.1~3.3

# %%
inFeatures = "grid_90.shp" # selection applied to
targetLayer = "grid_90.lyr"
sourceLayer = "shanxi_30s.shp"

# %% [markdown]
# ??? https://blog.csdn.net/gognzixiaobai666/article/details/112919955

# %%
arcpy.MakeFeatureLayer_management(in_features = inFeatures, out_layer = targetLayer)

# %%
select = arcpy.SelectLayerByLocation_management(in_layer = targetLayer, 
                                                overlap_type = "INTERSECT", # default
                                                select_features = sourceLayer, 
                                                selection_type = "NEW_SELECTION") # default

# %%
outFeatures = "grid_90_shanxi.shp"
arcpy.CopyFeatures_management(in_features = select, 
                              out_feature_class = outFeatures)

# %% [markdown]
# ### 3.4

# %%
inFeatures = "grid_90_shanxi.shp"
clipFeatures = "shanxi_30s.shp"
outFeatures = "shanxi_90s_mlt.shp" # multi part

# %%
arcpy.Clip_analysis(in_features = inFeatures, 
                    clip_features = clipFeatures, 
                    out_feature_class = outFeatures)

# %% [markdown]
# ### 3.5

# %% [markdown]
# similar as 4.2

# %%
inFeatures = "shanxi_90s_mlt.shp"
outFeatures = "shanxi_90s.shp"

# %%
deleteIfExist(outFeatures)
arcpy.MultipartToSinglepart_management(in_features = inFeatures, 
                                       out_feature_class = outFeatures)

# %% [markdown]
# ### 3.6

# %%
shp = "shanxi_90s.shp"
newField = "编号"
newType = "SHORT"

# %%
arcpy.AddField_management(in_table = shp, 
                          field_name = newField, 
                          field_type = newType)

# %% [markdown]
# ### 3.7

# %%
arcpy.CalculateField_management(in_table = shp, 
                                field = newField, 
                                expression = "!FID!", 
                                expression_type = "PYTHON")

# %%
with arcpy.da.SearchCursor(in_table = shp, field_names = newField) as cursor:
    # an iterable object
    vals = [row[0] for row in cursor]
    maxVal = max(vals)
    minVal = min(vals)
    print(minVal, maxVal)

# %%
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

# %% [markdown]
# ### 4.1

# %%
inFeatures = ["shanxi_90s.shp", "D:\COURSES\ADAS_intern\GisData\地质防治区划图-模板\模板_防治区划图.shp"]
outFeatures = "DZFZT_shanxi_90s_mlt.shp" # DZFZT = 地质防治图

# %%
arcpy.Union_analysis(inFeatures, outFeatures) # 4.1

# %% [markdown]
# ### 4.2 ???

# %%
inFeatures = "DZFZT_shanxi_90s_mlt.shp"
outFeatures = "DZFZT_shanxi_90s.shp"

# %%
arcpy.MultipartToSinglepart_management(in_features = inFeatures, 
                                       out_feature_class = outFeatures)

# %% [markdown]
# ### 4.3

# %%
shp = "DZFZT_shanxi_90s.shp"
newField = "dz_mj"
newType = "DOUBLE"

# %%
arcpy.AddField_management(in_table = shp, 
                          field_name = newField, 
                          field_type = newType)
# getFieldList(shp)

# %% [markdown]
# 算成大面积？

# %%
arcpy.CalculateField_management(in_table = shp, field = newField, 
                                expression = "!shape.area!", 
                                expression_type = "PYTHON")

# %% [markdown]
# ### 4.4

# %%
inFeatures = "DZFZT_shanxi_90s.shp"
outFeatures = "Export_Output_DZFZT.shp"

# %%
arcpy.Select_analysis(in_features = inFeatures, 
                      out_feature_class = outFeatures, 
                      where_clause = "等级值<>0")

# %% [markdown]
# ### 4.5

# %% [markdown]
# 输出在默认的default.gdb

# %%
inFeatures = "Export_Output_DZFZT.shp"
outFeatures = "C:\\Users\\lx\\Documents\\ArcGIS\\Default.gdb\\Export_Output_DZFZT_Freq"
# outFeatures = "Export_Output_DZFZT_Freq.dbf"

# %%
arcpy.Frequency_analysis(in_table = inFeatures, 
                         out_table = outFeatures, 
                         frequency_fields = "编号", 
                         summary_fields = "dz_mj")

# %%
print(outFeatures)
getFieldList(outFeatures)

# %% [markdown]
# ### 4.6

# %%
tab1 = "Export_Output_DZFZT.shp"
tab2 = outFeatures
print(tab2)

# %%
# join 2 tables 
# on "in_data.in_field = join_table.join_field"
# only incorporate "fields" into "tab1"
arcpy.JoinField_management(in_data = tab1, 
                           in_field = "编号", 
                           join_table = tab2, 
                           join_field = "编号", 
                           fields = ["dz_mj"])

# %%
print(tab1)
getFieldList(tab1)

# %% [markdown]
# ### 4.7

# %% [markdown]
# same as 4.3

# %%
shp = "Export_Output_DZFZT.shp"
newField = "djz_zb"
newType = "DOUBLE"

# %%
arcpy.AddField_management(in_table = shp, 
                          field_name = newField, 
                          field_type = newType)

# %%
arcpy.CalculateField_management(in_table = shp, field = newField, 
                                expression = "!dz_mj! / !dz_mj_1! * !等级值!", 
                                expression_type = "PYTHON")

# %% [markdown]
# ### 4.8

# %% [markdown]
# same as 4.5

# %%
in_shp = "Export_Output_DZFZT.shp"
out_shp = "C:\\Users\\lx\\Documents\\ArcGIS\\Default.gdb\\Export_Output_DZFZT_Freq1"

# %%
arcpy.Frequency_analysis(in_table = in_shp, 
                         out_table = out_shp, 
                         frequency_fields = "编号", 
                         summary_fields = "djz_zb")

# %%
arcpy.Exists(out_shp)

# %% [markdown]
# ### 4.9

# %% [markdown]
# same as 4.6

# %%
tab1 = "shanxi_90s.shp"
tab2 = out_shp
print(tab2)

# %%
getFieldList(tab2)

# %%
arcpy.JoinField_management(in_data = tab1, 
                           in_field = "编号", 
                           join_table = tab2, 
                           join_field = "编号", 
                           fields = ["djz_zb"])

# %%
print(tab1)
getFieldList(tab1)

# %% [markdown]
# ### 4.10

# %% [markdown]
# same as 4.3

# %%
shp = "shanxi_90s.shp"
newField = "等级"
newType = "SHORT"

# %%
arcpy.AddField_management(in_table = shp, 
                          field_name = newField, 
                          field_type = newType)

# %%
arcpy.CalculateField_management(in_table = shp, field = newField, 
                                expression = "!djz_zb!", 
                                expression_type = "PYTHON")

# %% [markdown]
# ### 4.11
# No join active. Ignore this step

# %% [markdown]
# ### 5.1

# %%
targetFeatures = "shanxi_30s.shp"
joinFeatures = "shanxi_90s.shp"
outFeatures = "DZFZT_30s_xxLevel.shp" # name "DZFZT(30s, xxLevel)" output errors?

# %%
deleteIfExist(outFeatures)

# %%
arcpy.SpatialJoin_analysis(target_features = targetFeatures, 
                           join_features = joinFeatures, 
                           out_feature_class = outFeatures, 
                           join_operation = "JOIN_ONE_TO_ONE", 
                           join_type = "KEEP_ALL")

# %% [markdown]
# ### 6.1
# 添加字段

# %%
shp = "DZFZT_30s_xxLevel.shp"
getFieldList(shp)

# %%
arcpy.DeleteField_management(shp, "乡")

# %%
fieldsInfo = [("物理主", "TEXT"), ("调查对", "TEXT"), ("行省", "TEXT"), ("行市", "TEXT"), 
              ("行县", "TEXT"), ("更时", "TEXT"), ("写时", "TEXT"), ("数据状", "TEXT"), 
              ("审核流", "TEXT"), ("审核状", "TEXT"), ("行业", "TEXT"), ("日期分", "TEXT"), 
              ("批次号", "TEXT"), ("乡", "TEXT"), ("等级值", "SHORT")]
# u'\u4e61' 乡

# %%
for name, type in fieldsInfo:
    arcpy.AddField_management(in_table = shp, 
                              field_name = name, 
                              field_type = type)

# %% [markdown]
# ### 6.2
# 计算字段

# %%
arcpy.CalculateField_management(shp, "乡", 
                                "[area_code]")
arcpy.CalculateField_management(shp, "行省", 
                                "\"140000\"")
arcpy.CalculateField_management(shp, "行市", 
                                "Left([乡], 4) & \"00\"")
arcpy.CalculateField_management(shp, "行县", 
                                "Left([乡], 6)")
arcpy.CalculateField_management(shp, "更时", 
                                "\"20221021 11:00:00\"")
arcpy.CalculateField_management(shp, "数据状", 
                                "\"U\"")
arcpy.CalculateField_management(shp, "审核流", 
                                "\"3\"")
arcpy.CalculateField_management(shp, "审核状", 
                                "\"2\"")
arcpy.CalculateField_management(shp, "行业", 
                                "\"019\"")
arcpy.CalculateField_management(shp, "等级值", 
                                "[等级]")

# %%
for name in ["调查对", "写时", "日期分", "批次号"]:
    arcpy.CalculateField_management(shp, name, "\"\"")

# %% [markdown]
# ### 6.3

# %% [markdown]
# 计算物理主键. 6位行政编码 + 第i张图 + 图内编号  
# 例如: 140100 + 1 + 12

# %%
figID = 1
expression = "!行县! + \"" + str(figID) + "\" + str(!FID!)"
print(expression)
# arcpy.GetCount_management(in_rows = shp)

# %%
arcpy.CalculateField_management(shp, "物理主", 
                                expression, 
                                "PYTHON")

# %% [markdown]
# ### 6.4
# 删除多余字段

# %%
delFields = ["Join_Count", "TARGET_FID", "oid_1", 
             "rows", "colums", "area_code", "ORIG_FID", 
             "Shape_Length_1", "Shape_Area_1", "编号", 
             "FREQUENCY", "djz_zb", "等级", "Id"]
# delFields += ["Shape_Length", "Shape_Area"]
# getFieldList(shp)

# %%
# delete in batch
arcpy.DeleteField_management(in_table = shp, 
                             drop_field = ";".join(delFields)) 

# %% [markdown]
# ### 6.5 
# 调整字段顺序

# %%
fieldOrder = [unicode(x[0], 'utf-8') for x in fieldsInfo]
# fieldOrder.insert(-1, unicode("乡", 'utf-8'))
print(fieldOrder)

# %%
[x.name for x in arcpy.ListFields(shp)]

# %%
arcpy.CopyFeatures_management(shp, "tmp.shp")
reorder_fields(table = "tmp.shp", out_table = shp, 
               field_order = fieldOrder)

# %% [markdown]
# # ----------------------------------------------------------------------------TEST

# %%



