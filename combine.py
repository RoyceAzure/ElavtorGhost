import dlib
import cv2
import imutils
import multiprocessing as mp
from Tracker import CentroidTracker, shape_to_np, TrackableObject, save_img
# import the necessary packages
from utility import preparePath, save_db_json, save_people_db
import face_recognition
import  json
import numpy as np
from time import sleep
##### combine import library
#import multiprocessing as mp
from multiprocessing import  Value, Array, Process
from ctypes import c_bool
from Elevator import run_elavtor

# import the necessary packages

"""
nested change a dict to proxydict
db : dict
"""
def dict2proxyDict(db):
    type_list = ["dict"]
    if not db:
        return manager.dict()
    temp = {}
    for key in db.keys():
        if type(db[key]) in type_list:
            temp[key] = dict2proxyDict(db[key])
        else:
            temp[key] = db[key]
    return temp

"""
load json file and return dict or proxy dict
"""
def load_db_json(path):
    temp = None
    try:
        with open(path,"r") as f:
            temp = json.load(f)
            return temp
    except Exception as e:
        print(e)
    finally:
        if  temp is None:
            return manager.dict()

"""
create another process , catch encoding from Q_encoding, use db_encodings_list to compare and write to Q_writeDB
Q_encoding, Q_writeDB : mp.queue
db_encodings_list : list
"""
def muti_process_match_db(Q_encoding, Q_writeDB,db_encodings_list):
    try:
        while True:
            print("=====================================muti_process_match_db")
            if Q_encoding.empty():
                print("=====================================muti_process_match_db Q is empty  sleep ")
                sleep(1)
            people_obj = Q_encoding.get()
            current_encodings = people_obj[0]
            print("process : {}, get encoding , start to compare".format(mp.current_process()))
            print(type(db_encodings_list))
            temp = []
            for en in db_encodings_list:
                temp.append(en)
            temp = np.array(temp)
            match_list = np.where(face_recognition.face_distance(temp, current_encodings) < 0.3)
            print(3)
            print(match_list)
            if len(match_list[0]) > 1:
                print("process {} 超過一個配對 ".format(mp.current_process()))
                """
                只配對分數最高的那個
                """
            elif len(match_list[0]) == 1:
                print("process {} 配對成功 ".format(mp.current_process()))
                """
                按電梯
                """
            else:
                print("沒有配對 match_list : {}".format(match_list))
                print("===========muti_process_match_db put to Q_writeDB : {}".format(people_obj))
                Q_writeDB.put(people_obj)
    except  Exception as e:
        print(e)
"""
get info from Q_writeDB then wirte to proxydb
Q_writeDB : mp.queue
db : proxydict
"""
def muti_process_write_db(Q_writeDB,db,current_floor,floor_list):
    try:
        print("=====================================muti_process_write_db")
        while True:
            print("================in muti_process_write_db while ")
            if Q_writeDB.empty():
                print("================in muti_process_write_db Q_writeDB is empty , sleep 1 ")
                sleep(1)
            print("================in muti_process_write_db Q_writeDB start to write db ")
            people = Q_writeDB.get()
            print("================in muti_process_write_db Q_writeDB start to write db type {} ".format(people[0]))
            save_people_db(db, people[0],current_floor,floor_list)
            save_db_json(db, "test.json")
    except Exception as e:
        print(e)


########
#combine test alex
#if __name__ == '__main__':

def videoprocess(img_dir, video_path, detector, Q_encodings, Q_writeDB,pool,current_floor,floor_list):


    cap = cv2.VideoCapture(video_path)
    ct = CentroidTracker(Q_encodings,img_dir, maxDisappeared=10, maxDistance=50)

    """
    每次開門 :
        從DB抓資料近來
    """
    db = load_db_json("DataBase/test.json")
    if type(db) == dict:
        db = dict2proxyDict(db)
    print("after load db : {}".format(db))
    print("after load db type: {}".format(type(db)))
    db_encodings_list = [db[Id]["encoding"] for Id in sorted(db.keys())] if db else []
    pool.apply_async(muti_process_match_db,args = (Q_encodings,Q_writeDB,db_encodings_list))
    #########
    pool.apply_async(muti_process_write_db,args = (Q_writeDB,db))
    
    while(cap.isOpened()):
        rects= []
        
        try:
            ret, frame = cap.read()
            frame = imutils.resize(frame, width=900)

            (H, W) = frame.shape[:2]
            # copyframe = cv2.copyMakeBorder(frame,0,0,0,0, cv2.BORDER_CONSTANT,value=[255,255,255]) 

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 偵測人臉

        except:
            break
        # 取出所有偵測的結果

        face_rects, scores, idx = detector.run(gray, 0)
        for i, d in enumerate(face_rects):
            if scores[i] > 0.0:
                x1 = int(d.left())
                y1 = int(d.top())
                x2 = int(d.right())
                y2 = int(d.bottom())
                rect = (x1, y1, x2 ,y2) 
                rects.append(rect)
                text = "%2.2f(%d)" % (scores[i], idx[i])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1, cv2.LINE_AA)
                
    # #           save face
    #             current_face_image = frame[y1:y2,x1:x2]
    #             cv2.imwrite('images/temp_face/photo' + str(ct.nextObjectID) + '.jpg',current_face_image)
    #             print('儲存:','photo' + str(ct.nextObjectID) + '.jpg')
    # #           encoding
    #             picture_of_face = face_recognition.load_image_file('images/temp_face/photo' + str(ct.nextObjectID) + '.jpg')
    #             face_encoding = face_recognition.face_encodings(picture_of_face,known_face_locations=None,num_jitters = 2, model ='small')
    #             print(face_encoding)
                
                
    #             if cv2.waitKey(1) & 0xFF == ord('i'):

    #                 cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_DUPLEX,
    #                 0.7, (255, 255, 255), 1, cv2.LINE_AA)
    #                 shape = predictor(gray, d)
    #                 shape = shape_to_np(shape)
    #                 for (x, y) in shape:
    #                     cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
    #Q_encoding, Q_writeDB,db_encodings_list
    #DataBase, encoding, floor, floor_w

        objects = ct.update(rects,scores,frame)


        # print(objects)
        for index,(objectID, s_centroid) in enumerate(objects.items()):
            # draw both the ID of the object and the centroid of the
            # object on the output frame
            face = ct.trackableObjects.get(objectID,None)

            if(len(scores) == len(objects.items()) ) :
                if scores[index] > face.score:
                    d = face_rects[index]
                    x1 = int(d.left())
                    y1 = int(d.top())
                    x2 = int(d.right())
                    y2 = int(d.bottom())
                    save_img(img_dir, 9999,frame[y1:y2,x1:x2])
                    pathimg = img_dir + str(9999) + '.png'
                    print("==============update tracker obj id {}, pathimg : {}".format(objectID, pathimg))
                    picture_of_face = face_recognition.load_image_file(img_dir + str(9999) + '.png')

                    face_encoding2 = face_recognition.face_encodings(picture_of_face,known_face_locations=None,num_jitters = 1, model ='small')
                    # print("22",face_encoding2)
                    if(face_encoding2):
                        if(face_recognition.compare_faces(face.face_encoding, face_encoding2[0] ,tolerance=0.6)):
                            face.score = scores[index]
                            d = face_rects[index]
                            x1 = int(d.left())
                            y1 = int(d.top())
                            x2 = int(d.right())
                            y2 = int(d.bottom())
                            save_img(img_dir,objectID,frame[y1:y2,x1:x2])
                            face.face_encoding=face_encoding2
                            print("==============update tracker obj id {}, encoding : {}".format(objectID, face_encoding2))
                    elif(face_encoding2 and face.face_encoding == []):
                        face.score = scores[index]
                        d = face_rects[index]
                        x1 = int(d.left())
                        y1 = int(d.top())
                        x2 = int(d.right())
                        y2 = int(d.bottom())
                        save_img(img_dir,objectID,frame[y1:y2,x1:x2])
                        face.face_encoding=face_encoding2
                        print("==============update tracker obj id {}, encoding : {}".format(objectID, face_encoding2))
                text = "score {}".format(scores[index])
                cv2.putText(frame, text, (s_centroid[0] - 70, s_centroid[1] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            

            text = "ID {}".format(objectID)
            cv2.putText(frame, text, (s_centroid[0] - 50, s_centroid[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.circle(frame, (s_centroid[0], s_centroid[1]), 2, (0, 255, 0), -1)        

        textface = "face count: {} ".format(len(objects))
        cv2.putText(frame, textface, (10, int(H) - ((11 * 20) + 60) ),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (70, 70, 255), 2)             
        textcount = "totle count: {} ".format(ct.nextObjectID)
        cv2.putText(frame, textcount, (10, int(H) - ((12 * 20) + 60) ),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (70, 70, 255), 2)          
        cv2.imshow("Face Detection", frame)   

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    #init elavtorprocess
    manager = mp.Manager()
    is_elavetor_open =manager.Value(c_bool, False)
    floor_list = Array("i",[0]*6)
    current_floor =  Value("i", 0)


    #init video process
    img_dir,video_dir = preparePath()
    video_path = video_dir + "/0.mp4"
    detector = dlib.get_frontal_face_detector()
    manager = mp.Manager()
    Q_encodings = manager.Queue(20)
    Q_writeDB = manager.Queue(20)
    pool = mp.Pool(4)


    elevator_process = Process(target=run_elavtor, args=(is_elavetor_open,floor_list,current_floor))
    #     print(is_open)
    elevator_process.start()
    while True:
        # print(is_elavetor_open.value)
        # print(floor_list[:])
        # print(current_floor.value)
        if(is_elavetor_open.value == True):
            videoprocess(img_dir, video_path, detector, Q_encodings, Q_writeDB, pool,current_floor.value,floor_list[:])
            print("open")
    elevator_process.join()
