from tkinter import *
import time
import threading
class Elevator():
    waiting_list = [0,0,0,0,0,0] 
    status = 0
    vardoor = "DOOR CLOSE"
    floor = 1
    
    def __init__(self,is_elavetor_open,floor_list,current_floor,floor_list_to_push):
        #reset values
        self.waiting_list = [0,0,0,0,0,0] 
        self.status = 0
        self.vardoor = "DOOR CLOSE"
        self.floor = 1
        # self.is_open = is_open
        self.floor_list_to_push = floor_list_to_push
        self.is_elavetor_open = is_elavetor_open
        self.floor_list = floor_list
        self.current_floor = current_floor
    def getdoorstatus(self):
        return self.vardoor
    def getfloor(self):
        return self.floor
    def getallfloor(self):
        floorlist = []
        for i in self.waiting_list:
            if(i != 0):
                floorlist.append(i)
        return floorlist
    ## elevator
    #control elevator from A to b
    def elevatormove(self,a,b): 
        pp = 1
        n = b-a
        if(n<0):
            pp = -1
        for i in range(n*pp):
            time.sleep(1.5)
            self.w.move(self.elevator_sqr,0,-50*pp)
            self.w.update()
    #control elevator move a step
    def moveone(self,pp):
        time.sleep(1.5)
        self.w.move(self.elevator_sqr,0,-50*pp)
        self.w.update()
    ####Trigger can't control
    def doortrigger(self):
        global is_open
        if(self.vardoor == "DOOR CLOSE"):
            self.vardoor = "DOOR OPEN"
            filling = "green"
            self.is_elavetor_open.value = True
        else:
            self.vardoor = "DOOR CLOSE"
            filling = "red"
            self.is_elavetor_open.value = False
        self.d.itemconfigure(self.doorstatus,text = self.vardoor,fill = filling) 
    def doorcontrol(self,OC):
        if(OC == 1):
            self.vardoor = "DOOR OPEN"
            filling = "green"
  
            self.is_elavetor_open.value = True
        else:
            self.vardoor = "DOOR CLOSE"
            filling = "red"
    
            self.is_elavetor_open.value = False
        self.d.itemconfigure(self.doorstatus,text = self.vardoor,fill = filling)
    def pushButton(self):
        for i in self.floor_list_to_push:
            if i == 6:
                self.pushtrigger6()
            elif i == 5:
                self.pushtrigger5()
            elif i == 4:
                self.pushtrigger4()
            elif i == 3:
                self.pushtrigger3()
            elif i == 2:
                self.pushtrigger2()
            elif i == 1:
                self.pushtrigger1()
    def pushtrigger6(self):
        self.s6.configure(fg="red")
        self.waiting_list[5] = 6
        self.floor_list[5] = 6
    def pushtrigger5(self):
        self.s5.configure(fg="red")  
        self.waiting_list[4] = 5
        self.floor_list[4] = 5
    def pushtrigger4(self):
        self.s4.configure(fg="red")
        self.waiting_list[3] = 4
        self.floor_list[3] = 4
    def pushtrigger3(self):
        self.s3.configure(fg="red")
        self.waiting_list[2] = 3
        self.floor_list[2] = 3
    def pushtrigger2(self):
        self.s2.configure(fg="red")
        self.waiting_list[1] = 2
        self.floor_list[1] = 2
    def pushtrigger1(self):
        self.s1.configure(fg="red") 
        self.waiting_list[0] = 1
        self.floor_list[0] = 1
    def relighttrigger(self,num):
        self.doorcontrol(1)
        if(num == 1):
            self.s1.configure(fg="black") 
            self.waiting_list[0] = 0
            self.floor_list[0] = 0
        elif(num == 2):
            self.s2.configure(fg="black") 
            self.waiting_list[1] = 0
            self.floor_list[1] = 0
        elif(num == 3):
            self.s3.configure(fg="black") 
            self.waiting_list[2] = 0
            self.floor_list[2] = 0
        elif(num == 4):
            self.s4.configure(fg="black") 
            self.waiting_list[3] = 0
            self.floor_list[3] = 0
        elif(num == 5):
            self.s5.configure(fg="black") 
            self.waiting_list[4] = 0
            self.floor_list[4] = 0
        else:
            self.s6.configure(fg="black") 
            self.waiting_list[5] = 0
            self.floor_list[5] = 0
        time.sleep(4)
        self.doorcontrol(0)
        time.sleep(1)
    def doorclose(self):
        self.doorcontrol(0)
    def staircontrol(self,F):
        self.floor = F
        self.current_floor.value = F
        self.d.itemconfigure(self.stairstatus,text = self.floor) 
    ##### Elevator main moving function
    def moving(self):
        uptrigger = 0
        check = False
        remb = 0
        rems = 0
        while(1):
            maxnum = max(self.waiting_list);
            if(maxnum == 0):
                pass
            else:
                if(check == False):
                    remb = maxnum
                    check = True
                minnum = 0;
                for i in range(6):
                    minnum+=1
                    if(self.waiting_list[i] != 0):
                        break
                if(uptrigger == 0 and self.status+1 == remb):
                    uptrigger = 1        
                    rems = minnum
                elif(uptrigger == 1 and self.status+1 == rems):
                    uptrigger = 0        
                    remb = maxnum
                if((self.waiting_list[self.status]>0)):
                    self.relighttrigger(self.status+1)

                elif(uptrigger == 0):
                    if(self.status+1 < maxnum):
                            self.moveone(1)
                            self.status+=1
                            self.staircontrol(self.status+1)
                            if(self.waiting_list[self.status]>0):
                                self.relighttrigger(self.status+1)
                    elif(self.status+1 > maxnum):
                            self.moveone(-1)
                            self.status-=1
                            self.staircontrol(self.status+1)
                            if(self.waiting_list[self.status]>0):
                                self.relighttrigger(self.status+1)
                else:
                    if(self.status+1 > rems):
                            self.moveone(-1)
                            self.status-=1
                            self.staircontrol(self.status+1)
                            if(self.waiting_list[self.status]>0):
                                self.relighttrigger(self.status+1)
                    elif(self.status+1 < rems):
                            self.moveone(1)
                            self.status+=1
                            self.staircontrol(self.status+1)
                            if(self.waiting_list[self.status]>0):
                                self.relighttrigger(self.status+1)
    ##########
    def createElevator(self):
        self.master=Tk()
        #btn
        self.f6 = Frame(self.master,width=200, height=320)
        self.f6.pack(side=LEFT,anchor = NW)
        self.s6 = Button(self.f6,text="6",width=5,height=3,command=self.pushtrigger6)
        self.s6.pack()
        self.s5 = Button(self.f6,text="5",width=5,height=3,command=self.pushtrigger5)
        self.s5.pack()
        self.s4 = Button(self.f6,text="4",width=5,height=3,command=self.pushtrigger4)
        self.s4.pack()
        self.s3 = Button(self.f6,text="3",width=5,height=3,command=self.pushtrigger3)
        self.s3.pack()
        self.s2 = Button(self.f6,text="2",width=5,height=3,command=self.pushtrigger2)
        self.s2.pack()
        self.s1 = Button(self.f6,text="1",width=5,height=3,command=self.pushtrigger1)
        self.s1.pack()
        self.ds = Button(self.f6,text="Close",width=5,height=3,command=self.doorclose)
        self.ds.pack()
        ##############
        self.w = Canvas(self.master, width=200, height=320)
        self.w.pack(side=LEFT,anchor = NW)
        #w.pack()
        self.w.create_rectangle(70, 10, 170, 310, fill = "white")
        for i in range(1,7):
            self.w.create_line(70, 50*i+10, 170, 50*i+10)
        for i in range(6):
            self.w.create_text(20, 50*i+18,anchor=NW,text=str(6-i)+'F',font = ('TimesNewRoman',15))

        self.elevator_sqr=self.w.create_rectangle(72, (6-self.floor)*50+12, 168, (6-self.floor)*50+58, fill = "grey")    
        self.master.update()
        ##################
        self.d = Canvas(self.master, width=200, height=320)
        self.d.pack(side=LEFT,anchor = NW)
        self.stairstatus = self.d.create_text(100,100,font=('TimesNewRoman',50),text=self.floor)
        self.doorstatus = self.d.create_text(100,150,font=('TimesNewRoman',30),text=self.vardoor,fill = "red")   
        th = threading.Thread(target = self.moving)
        th.setDaemon(True)
        th.start()
        mainloop()


def run_elavtor(is_elavetor_open,floor_list,current_floor,floor_list_to_push):
    try:
        a = Elevator(is_elavetor_open,floor_list,current_floor,floor_list_to_push)
        print(is_elavetor_open.value)
        #create a Elevator
        a.createElevator()
        #get floor now
        print(a.getfloor())
        #get all the floor
        print(a.getallfloor())
        #get if door is open
        print(a.getdoorstatus())
    except Exception as e:
        print(e)



