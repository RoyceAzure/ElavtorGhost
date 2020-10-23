from collections import  OrderedDict
import face_recognition
import time
from scipy.spatial import distance as dist
import numpy as np
import cv2
class CentroidTracker:
    def __init__(self, Q, imgdir, maxDisappeared=50, maxDistance=50):
        # initialize the next unique object ID along with two ordered
        # dictionaries used to keep track of mapping a given object
        # ID to its centroid and number of consecutive frames it has
        # been marked as "disappeared", respectively
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.Q = Q
        self.imgdir = imgdir
        # store the number of maximum consecutive frames a given
        # object is allowed to be marked as "disappeared" until we
        # need to deregister the object from tracking
        self.maxDisappeared = maxDisappeared

        # store the maximum distance between centroids to associate
        # an object -- if the distance is larger than this maximum
        # distance we'll start to mark the object as "disappeared"
        self.maxDistance = maxDistance
        self.trackableObjects = {}
        self.tStart = {}
        self.tEnd = {}    



    def register(self, boxs, score, frame):
        # when registering an object we use the next available object
        # ID to store the centroid
        
        save_img(self.imgdir, self.nextObjectID,frame[boxs[1]:boxs[3],boxs[0]:boxs[2]])
        
        picture_of_face = face_recognition.load_image_file(self.imgdir + str(self.nextObjectID) + '.png')
        face_encoding = face_recognition.face_encodings(picture_of_face,known_face_locations=None,num_jitters = 1, model ='small')
        # print(face_encoding)
        cX = int((boxs[0] + boxs[2]) / 2.0)
        cY = int((boxs[1] + boxs[3]) / 2.0)
        centroid = (cX, cY)
        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        face = TrackableObject(self.nextObjectID, centroid, score, face_encoding)
        self.trackableObjects[self.nextObjectID] = face
        self.tStart[self.nextObjectID] = time.time() 
        self.nextObjectID += 1


    """
    拿到臉部數據 圖片 放到Q_encoding 然後muti去放到Q_encoding取資料 
    進資料庫比對  無就新增  有就案電梯
    要把所有需要資訊都存到Q
    deregister 需要在存 結束時間?

    電梯關門後  樓層應該都確定了

    """
    def deregister(self, objectID , floor = {"6":5}, floor_w = {"6":0.25}):
        # to deregister an object ID we delete the object ID from
        # both of our respective dictionaries
        self.tEnd[objectID] = time.time()
        encoding = None
        img_path = None
        trackerOb = None
        if floor:
            print("==============in deregister ")
            print("==============in deregister obj ID : {}".format(objectID))
            trackerOb = self.trackableObjects.get(objectID)  
            
            encoding = trackerOb.face_encoding
            if encoding:
                print("==============in deregister has encoding  about to push Qencoding")
                img_path = trackerOb.path
                # print("==============in deregister  img_path :{}".format(img_path))
                print("==============in deregister  encoding :{}".format(encoding))
                print("==============in deregister  encoding type:{}".format(type(encoding)))
                print("==============in deregister  push {} to Q_encoding".format([encoding, img_path,floor, floor_w]))
                self.Q.put([encoding[0], img_path,floor, floor_w])
        del self.objects[objectID]
        del self.disappeared[objectID]

    def update(self, rects, scores, frame):
        # check to see if the list of input bounding box rectangles
        # is empty
        if len(rects) == 0:
            # loop over any existing tracked objects and mark them
            # as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1

                # if we have reached a maximum number of consecutive
                # frames where a given object has been marked as
                # missing, deregister it
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            # return early as there are no centroids or tracking info
            # to update
            return self.objects

        # initialize an array of input centroids for the current frame
        inputCentroids = np.zeros((len(rects), 2), dtype="int")

        # loop over the bounding box rectangles
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            # use the bounding box coordinates to derive the centroid
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)
        # if we are currently not tracking any objects take the input
        # centroids and register each of them
        if len(self.objects) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(rects[i],scores[i], frame)

        # otherwise, are are currently tracking objects so we need to
        # try to match the input centroids to existing object
        # centroids
        else:
            # grab the set of object IDs and corresponding centroids
            objectIDs = list(self.objects.keys())
            objectCentroids = list(self.objects.values())

            # compute the distance between each pair of object
            # centroids and input centroids, respectively -- our
            # goal will be to match an input centroid to an existing
            # object centroid
            D = dist.cdist(np.array(objectCentroids), inputCentroids)

            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value as at the *front* of the index
            # list
            rows = D.min(axis=1).argsort()

            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = D.argmin(axis=1)[rows]

            # in order to determine if we need to update, register,
            # or deregister an object we need to keep track of which
            # of the rows and column indexes we have already examined
            usedRows = set()
            usedCols = set()

            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                if row in usedRows or col in usedCols:
                    continue

                # if the distance between centroids is greater than
                # the maximum distance, do not associate the two
                # centroids to the same object
                if D[row, col] > self.maxDistance:
                    continue

                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                objectID = objectIDs[row]
                self.objects[objectID] = inputCentroids[col]
     
                self.disappeared[objectID] = 0

                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)

            # compute both the row and column index we have NOT yet
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # in the event that the number of object centroids is
            # equal or greater than the number of input centroids
            # we need to check and see if some of these objects have
            # potentially disappeared
            if D.shape[0] >= D.shape[1]:
                # loop over the unused row indexes
                for row in unusedRows:
                    # grab the object ID for the corresponding row
                    # index and increment the disappeared counter
                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1

                    # check to see if the number of consecutive
                    # frames the object has been marked "disappeared"
                    # for warrants deregistering the object
                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)

            # otherwise, if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as a trackable object
            else:
                for col in unusedCols:
                    self.register(rects[col],scores[col], frame)

        # return the set of trackable objects
        return self.objects

def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((68, 2), dtype=dtype)

    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)

    # return the list of (x, y)-coordinatesqqqqqqq
    return coords
class TrackableObject:
    def __init__(self, objectID, centroid, score, face_encoding):
        # store the object ID, then initialize a list of centroids
        # using the current centroid
        self.objectID = objectID
        self.centroids = [centroid]
        self.score = score
        self.face_encoding = face_encoding
        self.path = 'images/temp_face/photo'+ str(objectID) + '.png'

def save_img(imgdir,num,img):
    cv2.imwrite(imgdir + str(num) + '.png',img)
    # print('儲存:','photo' + str(num) + '.png')