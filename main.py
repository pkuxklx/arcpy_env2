# -*- coding: utf-8 -*-  
scratchPath = "D:\\GisData结果\\暂时"
gwData = "D:\\COURSES\\ADAS_intern\\gw数据\\gw.shp"
sourceDataPath = "D:\\COURSES\\ADAS_intern\\20221025山西地质数据\\吕梁市及13个区县"
default_gdbPath = "C:\\Users\\lx\\Documents\\ArcGIS\\Default.gdb"
savePath = "D:\\GisData结果"
start_id = 117-2
end_id = 117-1


# %%
import arcpy, os, sys, math
import pandas as pd
from utils.my_api import *
from step2_3 import step_2_to_3
from step4_6 import step_4_to_6
from utils.tick import Timer

# %%
# initialize
InitPath(scratch_path = scratchPath)
print(arcpy.env.workspace)
print(arcpy.env.overwriteOutput)

# %%
# global variables
figNameList = [u"地质灾害风险区划图", u"地质灾害危险性等级图", u"地质灾害防治区划图"] 
areas = []
df = pd.read_csv("area_code.csv", encoding = "gbk")
for index, row in df.iterrows():
    areas.append((row[0], str(row[1]))) 

# %%
# 1.1
newCoordinate = arcpy.SpatialReference(4490)
print(newCoordinate.name)
arcpy.env.outputCoordinateSystem = newCoordinate

# 1.2
outFeatures = "grid_90.shp"
deleteIfExist(outFeatures, 0)
originCoordinate = "73 0"
yAxisCoordinate = "73 10"
cornerCoordinate = "136 54"
number_rows = 2160
number_cols = 2520
labels = "NO_LABELS"
geoType = "POLYGON"
# arcpy.CreateFishnet_management(out_feature_class = outFeatures,
#                                origin_coord = originCoordinate, y_axis_coord = yAxisCoordinate, corner_coord = cornerCoordinate,
#                                number_rows = number_rows, number_columns = number_cols,
#                                labels = labels,
#                                geometry_type = geoType)

# %%
areas = areas[start_id: end_id]
err_infos = []
ta = Timer()
for regionName, areaCode in areas:
    printSepLine(2)
    print(regionName + " step 2~3 start.")
    #assert type(regionName) == str
    #assert type(areaCode) == str
    regionName = regionName.encode('utf-8')
    step_2_to_3(regionName, areaCode, 
                gwData = gwData)
    
    for figID in [1, 2, 3]:
        printSepLine()
        print(regionName + " " + str(figID) + " step 4~7 start.")

        figName = figNameList[figID - 1].encode('utf-8')
        try:
            step_4_to_6(figID = figID,
                        figName = figName,
                        regionName = regionName,
                        sourceDataPath = sourceDataPath,
                        default_gdbPath = default_gdbPath,
                        savePath = savePath)
            print(regionName + " Fig {} finished.".format(figID))
        except Exception as e:
            print(e.message + " Continue.")
            err_infos.append([regionName, figID, e.message])
    print(regionName + " finished.")
    ta.tk()

printSepLine(5)
for info in err_infos:
    printSepLine()
    for val in info:
        print(val)

# %% [markdown]
# # ----------------------------------------------------------------------------TEST




