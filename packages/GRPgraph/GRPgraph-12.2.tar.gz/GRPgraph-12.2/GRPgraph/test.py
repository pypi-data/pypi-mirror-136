from tracemalloc import start
import py2D

win = py2D.Screen_([450,600])
run = True
key = py2D.Sub_.Bord()
time = 0

class Shatl:
    def __init__(self):
        self.pos = [225,580]
        self.size = [20,20]
        self.shatl = win.Shape2D.Rect(
            'red',self.pos,self.size,0,win.screen
        )


    def Update(self):
        global time
        if key.On_key_press('a'):
            if self.pos[0] > win.left:
                self.pos[0]-=7
        if key.On_key_press('d'):
            if self.pos[0]+self.size[0] < win.right:
                self.pos[0]+=7
        
        
        self.shatl = win.Shape2D.Rect(
            'red',self.pos,self.size,0,win.screen
        )
        self.shatl.Draw()
        time += 1
        if time%5==0:
            pos = [self.shatl.up[0]+self.shatl.size[0]/2-3,580]
            bulet.added_bulet(pos)
        
        


bulets = py2D.Objectes_('bulets')
class Bolet:
    def __init__(self):
        global bulets
    def added_bulet(self,pos):
        bulets.Add(pos,True)
    def Update(self):

        bul = bulets.Get_pack()
        for i in range(len(bul)):
            if bul[i-1][1]<0:
                    bulets.Del_min(i-1)
                    print(bulets.Get_pack())
        for i in range(len(bul)):
            
            win.Shape2D.Rect(
                'green',bul[i],[3,10],0,win.screen
            ).Draw()
            bul[i][1]-=10
            

        










bulet = Bolet()
boing = Shatl()
while (run):
    run = win.close() ; win.set_fps(60) ; win.Update().BG_col('black')

    boing.Update()
    bulet.Update()



    