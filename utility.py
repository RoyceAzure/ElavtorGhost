import os
import json
def preparePath():
    img_dir= os.path.join(".","images/temp_face/photo")

    video_dir =os.path.join(".","images/video")
    return [img_dir, video_dir]
def save_db_json(dbProxy, file_name):
    print("==========in save_db_json")
    DataBaseDir = "DataBase"
    save_path = os.path.join(".", DataBaseDir)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    try:
        path = os.path.join(save_path, file_name)
        result = dbProxy.copy()
        print("==========in save_db_json db : {}".format(result))
        with open(path,"w+") as f:
            json.dump(result,f)          
    except Exception as e:
        print(e)




def save_people_db(DataBase, encoding, floor, floor_w):
    try:
        print("============in save_people_db")
        print("============in save_people_db  before db :{}".format(DataBase))
        Id = len(DataBase) 
        print("============in save_people_db ID :{}".format(Id))
        temp = dict()
        print("============in save_people_db   1")
        print("============in save_people_db   encoding : {}".format(encoding))
        print("============in save_people_db  type encoding : {}".format(type(encoding)))
        temp["encoding"] = encoding.tolist()
        temp["floor"] = dict()
        temp["floor_w"] = dict()
        print("============in save_people_db   2")
        for (flk,flv), (flwk, flwv) in (zip(floor.items(), floor_w.items())):
            if temp["floor"].get(str(flk),None) is None:
                temp["floor"][str(flk)] = 0
            if temp["floor_w"].get(str(flk),None) is None:
                temp["floor_w"][str(flk)] = 0
            temp["floor"][str(flk)]+=flv
            temp["floor_w"][str(flwk)]+=flwv
        print("============in save_people_db   3")
        DataBase[str(Id)] = temp
        print("after save to db : {}".format(DataBase))
    except Exception as e:
        print(e)