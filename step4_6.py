# -*- coding: utf-8 -*-  
# %%
from codecs import unicode_escape_decode
from re import S
import arcpy, os
from utils.my_api import InitPath, deleteIfExist, getFieldList, reorder_fields, removeAllJoins
from utils.tick import Timer

# %%
def step_4_to_6(regionName, 
                figID, 
                figName, 
                sourceDataPath, 
                default_gdbPath, 
                savePath):

    assert type(regionName) == str
    assert type(figID) == int
    assert type(figName) == str
    assert type(sourceDataPath) == str
    assert type(default_gdbPath) == str
    assert type(savePath) == str

    ti = Timer()
    def rp(section):
        print(regionName + " " + str(figID) + ", " + str(section) + " finished.")
        ti.tk()

    sourceData = unicode(sourceDataPath + "\\" + regionName + "\\" + figName + "-山西省" + "".join(regionName.split('-')) + ".shp", 'utf-8')
    if not os.path.exists(sourceData):
        raise Exception("File " + sourceData + " doesn't exist.")
    else:
        print("Successfully find the data file " + sourceData + ".")


    # 4.0
    arcpy.CopyFeatures_management(in_features = "difang_90s_ori.shp", out_feature_class = "difang_90s.shp")
    coor = arcpy.SpatialReference(4508)
    arcpy.DefineProjection_management(sourceData, coor)
    arcpy.CalculateField_management(in_table = sourceData, field = "等级值",
                                    expression = "int(!等级值!)",
                                    expression_type = "PYTHON")
    # arcpy.AlterField_management(in_table = sourceData, field = "等级值",
    #                             new_field_name = "等级值", field_type = "LONG")
    rp(4.0)

    # 4.1
    inFeatures = ["difang_90s.shp", sourceData]
    outFeatures = "DZT_difang_90s_mlt.shp" # DZT = 地质图
    arcpy.Union_analysis(inFeatures, outFeatures) # 4.1
    rp(4.1)

    # 4.2
    inFeatures = "DZT_difang_90s_mlt.shp"
    outFeatures = "DZT_difang_90s.shp"
    arcpy.MultipartToSinglepart_management(in_features = inFeatures, 
                                        out_feature_class = outFeatures)
    rp(4.2)

    # 4.3
    shp = "DZT_difang_90s.shp"
    newField = "dz_mj"
    newType = "DOUBLE"
    arcpy.AddField_management(in_table = shp, 
                            field_name = newField, 
                            field_type = newType)
    arcpy.CalculateField_management(in_table = shp, field = newField, 
                                    expression = "!shape.area!", 
                                    expression_type = "PYTHON")
    rp(4.3)

    # 4.4
    inFeatures = "DZT_difang_90s.shp"
    outFeatures = "Export_Output_DZT.shp"
    # deleteIfExist(outFeatures)
    arcpy.Select_analysis(in_features = inFeatures, 
                        out_feature_class = outFeatures, 
                        where_clause = "等级值<>0")
    rp(4.4)

    # 4.5
    inFeatures = "Export_Output_DZT.shp"
    outFeatures = default_gdbPath + "\\Export_Output_DZT_Freq"
    arcpy.Frequency_analysis(in_table = inFeatures, 
                            out_table = outFeatures, 
                            frequency_fields = "编号", 
                            summary_fields = "dz_mj")
    rp(4.5)

    # 4.6
    tab1 = "Export_Output_DZT.shp"
    tab2 = outFeatures
    # join 2 tables 
    # on "in_data.in_field = join_table.join_field"
    # only incorporate "fields" into "tab1"
    arcpy.JoinField_management(in_data = tab1, 
                            in_field = "编号", 
                            join_table = tab2, 
                            join_field = "编号", 
                            fields = ["dz_mj"])
    rp(4.6)

    # 4.7
    shp = "Export_Output_DZT.shp"
    newField = "djz_zb"
    newType = "DOUBLE"
    arcpy.AddField_management(in_table = shp, 
                            field_name = newField, 
                            field_type = newType)
    arcpy.CalculateField_management(in_table = shp, field = newField, 
                                    expression = "!dz_mj! / !dz_mj_1! * !等级值!", 
                                    expression_type = "PYTHON")
    rp(4.7)

    # 4.8
    in_shp = "Export_Output_DZT.shp"
    out_tab = default_gdbPath + "\\Export_Output_DZT_Freq1"
    arcpy.Frequency_analysis(in_table = in_shp, 
                            out_table = out_tab, 
                            frequency_fields = "编号", 
                            summary_fields = "djz_zb")
    rp(4.8)

    # 4.9
    # same as 4.6
    tab1 = "difang_90s.shp"
    tab2 = out_tab
    # Recover "difang_90s.shp", to that generated in step 3.4 and 3.5.
    # Because in the previous small loop, it is changed by step 4.9's JoinField_management.
    # arcpy.DeleteField_management(tab1, "djz_zb;等级")
    arcpy.JoinField_management(in_data = tab1,
                            in_field = "编号",
                            join_table = tab2,
                            join_field = "编号",
                            fields = ["djz_zb"])
    rp(4.9)

    # 4.10
    # same as 4.3
    shp = "difang_90s.shp"
    newField = "等级"
    newType = "SHORT"
    arcpy.DeleteField_management(shp, newField)
    arcpy.AddField_management(in_table = shp,
                            field_name = newField,
                            field_type = newType)
    arcpy.CalculateField_management(in_table = shp, field = newField,
                                    expression = "!djz_zb!",
                                    expression_type = "PYTHON")
    rp(4.10)

    # 4.11
    # No join active. Ignore this step

    # 5.1
    targetFeatures = "difang_30s.shp"
    joinFeatures = "difang_90s.shp"
    outFeatures = "DZT_30s_xxLevel.shp" # name "DZFZT(30s, xxLevel)" output errors?
    deleteIfExist(outFeatures)
    arcpy.SpatialJoin_analysis(target_features = targetFeatures,
                            join_features = joinFeatures,
                            out_feature_class = outFeatures,
                            join_operation = "JOIN_ONE_TO_ONE",
                            join_type = "KEEP_ALL")
    rp(5.1)

    # 6.1
    # 添加字段
    shp = "DZT_30s_xxLevel.shp"
    arcpy.DeleteField_management(shp, "乡")
    fieldsInfo = [("物理主", "TEXT"), ("调查对", "TEXT"), ("行省", "TEXT"), ("行市", "TEXT"),
                ("行县", "TEXT"), ("更时", "TEXT"), ("写时", "TEXT"), ("数据状", "TEXT"),
                ("审核流", "TEXT"), ("审核状", "TEXT"), ("行业", "TEXT"), ("日期分", "TEXT"),
                ("批次号", "TEXT"), ("乡", "TEXT"), ("等级值", "SHORT")]
    # u'\u4e61' 乡
    for fname, ftype in fieldsInfo:
        arcpy.AddField_management(in_table = shp,
                                field_name = fname,
                                field_type = ftype)
    rp(6.1)

    # 6.2
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
    level = regionName.count('-') + 2 # {2, 3}
    arcpy.CalculateField_management(shp, "审核流",
                                    "\"" + str(level) + "\"")
    arcpy.CalculateField_management(shp, "审核状",
                                    "\"2\"")
    arcpy.CalculateField_management(shp, "行业",
                                    "\"019\"")
    arcpy.CalculateField_management(shp, "等级值",
                                    "[等级]")
    for name in ["调查对", "写时", "日期分", "批次号"]:
        arcpy.CalculateField_management(shp, name, "\"\"")
    rp(6.2)

    # 6.3
    # 计算物理主键. 6位行政编码 + 第i张图 + 图内编号
    # 例如: 140100 + 1 + 12
    expression = "!行县! + \"" + str(figID) + "\" + str(!FID!)"
    arcpy.CalculateField_management(shp, "物理主",
                                    expression,
                                    "PYTHON")
    rp(6.3)

    # 6.4
    # 删除多余字段
    delFields = ["Join_Count", "TARGET_FID", "oid_1",
                "rows", "colums", "area_code", "ORIG_FID",
                "Shape_Length_1", "Shape_Area_1", "编号",
                "FREQUENCY", "djz_zb", "等级", "Id"]
    # delete in batch
    arcpy.DeleteField_management(in_table = shp,
                                drop_field = ";".join(delFields))
    rp(6.4)

    # % [markdown]
    # ### 6.5
    # 调整字段顺序

    # %
    fieldOrder = [unicode(x[0], 'utf-8') for x in fieldsInfo]
    # fieldOrder.insert(-1, unicode("乡", 'utf-8'))
    # print(fieldOrder)

    # %
    arcpy.CopyFeatures_management(shp, "tmp.shp")
    reorder_fields(table = "tmp.shp", out_table = shp,
                field_order = fieldOrder)
    rp(6.5)

    # 7.1
    # 创建保存文件夹
    folderPath = os.path.join(savePath, regionName)
    folderPath = unicode(folderPath, 'utf-8')
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    rp(7.1)

    # 7.2
    # 保存, 并按要求命名

    inFeatures = "DZT_30s_xxLevel.shp"
    outFeatures = figName + "_山西省" + "".join(regionName.split('-')) + ".shp"
    outFeatures = unicode(outFeatures, 'utf-8')
    outFeatures = os.path.join(folderPath, outFeatures)
    try:
        # deleteIfExist(outFeatures)
        arcpy.CopyFeatures_management(in_features = inFeatures, out_feature_class = outFeatures)
        print("Copy success.")
    except Exception as e:
        print(e)
    rp(7.2)

    ti.tk(k = 1)

# %%
if __name__ == '__main__':
    a = "太原市-迎泽区"
    b = 1
    c = "地质灾害风险区划图"
    d = "D:\\COURSES\\ADAS_intern\\arcpy_env\\20221025山西地质数据"
    e = "C:\\Users\\lx\\Documents\\ArcGIS\\Default.gdb"
    f = "D:\\GisData"
    step_4_to_6(a, b, c, d, e, f)
# %%
# python2 无法直接指定函数参数类型
'''
def f(a: int):
    return a + 1
'''
# %%
