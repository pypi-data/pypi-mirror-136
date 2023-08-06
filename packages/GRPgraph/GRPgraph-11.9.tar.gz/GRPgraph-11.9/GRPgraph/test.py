import py2D
win = py2D.Screen_([600,600]) ; run = True



dirt = win.Shape2D.Rect('black',[0,500],[600,100],0,win.screen)


v_pos = py2D.Vec2(pos=[100,200])
v_sped = py2D.Vec2(pos=[4,1])
v_tygi = py2D.Vec2(pos=[0,0.5])

tr = 0.99


while(run):
    run = win.close() ; win.Update().BG_col('white') ; win.set_fps(60)

    dirt.Draw()

    
    
    ball = win.Shape2D.Circle('red',v_pos.pos1,10,0,win.screen)
    
    v_sped = v_sped.sum(v_tygi)
    v_pos = v_pos.sum(v_sped)
    if ball.up[1]<=win.up or ball.down[1]>=win.down-100 :
        v_sped = v_sped.umn(tr)
        v_sped.y = -v_sped.y
        v_pos = v_pos.sum(v_sped)
       

    if ball.left[0]<=win.left or ball.right[0]>=win.right :
        v_sped = v_sped.umn(tr)
        v_sped.x = -v_sped.x
        v_pos = v_pos.sum(v_sped)
        

    ball.Draw()


    