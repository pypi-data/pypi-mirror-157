from xmlrpc.client import TRANSPORT_ERROR
import GL
import GL_VFX

win = GL.Display_init_(flags=GL.D_Full)






p1 = GL_VFX.Particles.Rect(
    surf=win,
    rect=[500,500,10,10],
    shape_data=['c',20,[(10,225,20)]],
    circle_speed=1,
    color_randoming=False,
    teni=True,
    teni_fill=True,
    size_deller=0.8,
    particle_count=3,
    teni_color=(20,50,30),
    teni_vector=[5,5],
    spawn_time=1,
    spawn_delta=1,
    size_randoming=True,
    size_min_max=[5,20],
    size_resize_timer=10,
    size_resize=True,
    max_particle=300,
    gravity=[0,0],
    vector_speed=[0,1],
    vector_speed_randoming_angle=30,



)








while win.CEUF(FPS=60):





    
    


    win.GL.Rect('red',[0,1080-100],[1920,100],0,'s','D')
    win.GL.Rect('red',[200,500],[100,100],0,'s','D')
    win.GL.Rect('red',[200,400],[600,100],0,'s','D')
    win.GL.Rect('red',[200,600],[600,100],0,'s','D')
    win.GL.Circle('red',[500+500,500],120,0,'s','D')
    win.GL.Circle('red',[500+700,500],120,0,'s','D')
    
    
    p1.Set_position(GL.Open_mouse.GET_POSITION())
    p1.Phisics([255,0,0],False,[10,3],tyga=[0,0],density_y=0.6,density_x=0.99)

    if GL.Open_mouse.GET_PRESS_ON_PYGL_WINDOW():
        p1.Emiter()
    p1.Focus()
    p1.Render()
    p1.Xclean()
    
    