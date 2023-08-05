from numpy import interp, linspace
from matplotlib import colors


def _inter_from_256(x):
    return interp(x=x,xp=[0,255],fp=[0,1])


def custom_cmap(clrs, name):
    N = len(clrs)
    nodes = linspace(0,1,N)
    
    cdict = {
        "red": [],
        "green": [],
        "blue": []
            }
   
    
    for num, c in enumerate(clrs):
        r = (nodes[num], _inter_from_256(c[0]), _inter_from_256(c[0]))
        g = (nodes[num], _inter_from_256(c[1]), _inter_from_256(c[1]))
        b = (nodes[num], _inter_from_256(c[2]), _inter_from_256(c[2]))
        
        cdict["red"].append(r)
        cdict["green"].append(g)
        cdict["blue"].append(b)
        
    return colors.LinearSegmentedColormap(name,segmentdata=cdict)


# Some custom colormaps

lightning = custom_cmap([[0,0,0],[90,42,141],[0,115,255],[178,223,138],[255,255,153]], "garden")
icefire = custom_cmap([[255,255,255],[1,240,255],[0,1,227],[0,0,0],[245,11,0],[255,232,24],[255,255,255]], "fireice")
frigid = custom_cmap([[0,0,0],[0,1,227],[0,217,255],[255,255,255]], "frigid")
poison = custom_cmap([[0,0,0],[0,99,19],[32,223,2],[255,255,255]], "poison")
wraith = custom_cmap([[0,0,0],[194,193,243],[198,220,239],[255,255,255]], "wraith")
ghost = custom_cmap([[0,0,0],[49,130,189],[199,233,193],[255,255,255]], "ghost")
mute_rainbow = custom_cmap([[98,102,150],[123,144,206],[135,199,208],[187,229,183],[209,208,141],[210,158,133],[172,108,111]], "mute_rainbow")


lightning_r = custom_cmap([[255,255,153],[178,223,138],[0,115,255],[90,42,141],[0,0,0]], "garden_r")
icefire_r = custom_cmap([[255,255,255],[255,232,24],[245,11,0],[0,0,0],[0,1,227],[1,240,255],[255,255,255]], "fireice_r")
frigid_r = custom_cmap([[255,255,255],[0,217,255],[0,1,227],[0,0,0]], "frigid_r")
poison_r = custom_cmap([[255,255,255],[32,223,2],[0,99,19],[0,0,0]], "poison_r")
wraith_r = custom_cmap([[255,255,255],[198,220,239],[194,193,243],[0,0,0]], "wraith_r")
ghost_r = custom_cmap([[255,255,255],[199,233,193],[49,130,189],[0,0,0]], "ghost_r")
mute_rainbow_r = custom_cmap([[172,108,111],[210,158,133],[209,208,141],[187,229,183],[135,199,208],[[123,144,206],98,102,150]], "mute_rainbow_r")
