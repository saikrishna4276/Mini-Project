import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import sys
from colorsys import hsv_to_rgb
from ipywidgets import interact,IntSlider
from os import listdir
from PIL import Image, ImageDraw
from skimage import io

downsample = 4

def load_images(path):
    print("Loading images from \"",path,"\"")
    
    file_list = listdir(path)
    file_list = sorted(file_list)
    temp_im = io.imread(path+file_list[0],plugin="pil")
    temp_im = temp_im[0:temp_im.shape[0]:downsample,0:temp_im.shape[1]:downsample]
    im = np.zeros((temp_im.shape[0],temp_im.shape[1],len(file_list)))
    
    print("")
    for i,file in enumerate(file_list):       
        sys.stdout.write("\rReading image %i of %i" % ((i+1),len(file_list)))
        temp_im = io.imread(path+file,plugin="pil")
        temp_im = temp_im[0:temp_im.shape[0]:downsample,0:temp_im.shape[1]:downsample]
        im[:,:,i] = temp_im*4
        
    print("")
    print("Loaded image shape: ",im.shape)
        
    return im
def load_coordinates(path):
    print("Loading coordinates from \"",path,"\"")
    raw = np.genfromtxt(path,delimiter=",",skip_header=1)
    print("Loaded data shape: ",raw.shape)
    names = ["inde","ID","X","Y","FRAME","TRACK_ID"]
    coords = pd.DataFrame(raw,columns=names)
    coords.X = coords.X/downsample
    coords.Y = coords.Y/downsample
    print(" ")
       
    return coords
    


def show_overlay(image, coords, show_tracks):
    n_frames = image.shape[2]
    image = render_overlay(image,coords,show_tracks)
    plt.rcParams["figure.figsize"] = (8,6)
    plt.rcParams["toolbar"] = "None"
    fig, ax = plt.subplots()
    plt.tight_layout()
    def update_image(frame):
        frame = int(round(frame))
        ax.clear()
        ax.imshow(image[frame])
    interact(update_image,frame=IntSlider(min=0, max=n_frames-1,step=1,value=0));
    plt.show();
    

def render_overlay(image, coords, show_tracks):
    coords = coords.sort_values(by=['FRAME'])
    overlay_image = []
    n_frames = image.shape[2]
    for frame in range(0,n_frames):
        sys.stdout.write("\rRendering frame %d of %d" % ((frame+1),n_frames))
        overlay_image.append(Image.fromarray(image[:,:,frame]).convert('RGB'))
        draw_points(overlay_image[frame],coords,frame)
        if show_tracks:
            draw_tracks(overlay_image[frame],coords,frame)
        
    return overlay_image


def draw_points(image,coords,frame):
    rows = coords.index[coords.FRAME == frame]
    for row in rows:
        draw = ImageDraw.Draw(image) 
        draw_point(draw, coords.loc[row])
                    
def draw_point(draw,point):
    r = 2
    x = point.X
    y = point.Y
    draw.ellipse(((x-r,y-r),(x+r,y+r)),fill=(255,0,0))
                    
def draw_tracks(image,coords,frame):
    tracks_to_show = coords[:][(coords.FRAME <=frame)]
    track_IDs = tracks_to_show.TRACK_ID.unique()
    for track_ID in track_IDs:
        track = tracks_to_show[:][tracks_to_show.TRACK_ID == track_ID]
        draw = ImageDraw.Draw(image) 
        draw_track(draw, track)        

def draw_track(draw, track):
    track_ID = track.TRACK_ID.iloc[0]
    
    for row in range(1,track.shape[0]-1):
        x1 = track.X.values[[row-1]]
        x2 = track.X.values[[row]]
        y1 = track.Y.values[[row-1]]
        y2 = track.Y.values[[row]]
        random.seed(track_ID)
        h = random.random()
        rgb = tuple(round(i*255) for i in hsv_to_rgb(h,1,1))
        draw.line((x1,y1,x2,y2), fill=rgb)
        