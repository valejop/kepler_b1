# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 21:15:49 2022

@author: Thiago
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.title("Desenho de padrão B1 de Kepler")

def pentagon(center, radius, angle):
    ls=[]
    for i in range(5):
        ls.append([center[0]+radius*np.cos(np.radians(angle+90+i*72)),
                   center[1]+radius*np.sin(np.radians(angle+90+i*72))])
    return np.array(ls)
def star10(center,big_radius,small_radius,angle):
    ls=[]
    for i in range(10):
        ls.append([center[0]+small_radius*np.cos(np.radians(angle+90+i*36)),
                    center[1]+small_radius*np.sin(np.radians(angle+90+i*36))])
        ls.append([center[0]+big_radius*np.cos(np.radians(angle+108+i*36)),
                    center[1]+big_radius*np.sin(np.radians(angle+108+i*36))])
    return np.array(ls)

def draw5stars(pentagon):
    #Find center
    center=pentagon.mean(axis=0)
    rad=np.linalg.norm(pentagon[0]-center)
    br=hd/phi*rad/3/np.sin(np.pi/10)*np.sin(7*np.pi/10)
    sr=hd/phi*rad/3/np.sin(np.pi/10)*np.sin(2*np.pi/10)
    #Find unitary vectors
    vecs=(pentagon-center)
    vecs=1/rad*vecs
    #Find stars centers
    star_centers=center+vecs*(rad+sr)
    #Find angles
    angles=np.apply_along_axis(lambda x:np.degrees(np.angle(x[0]+x[1]*1j)),1,vecs)
    star_list=[]
    for s in range(5):
        star_list.append(star10(center+(rad+sr)*vecs[s],br,sr,18+angles[s]))
    return star_list

def get_outer_pentagon(star_list,original_pentagon):
    #Encontra centro da estrela 1
    new_pentagon=[]
    c=original_pentagon.mean(axis=0)
    ang=np.degrees(np.angle(np.dot((original_pentagon[0]-c),np.array([1,1j]))))
    rad=np.linalg.norm(original_pentagon[0]-original_pentagon.mean(axis=0))
    centros=[np.mean(s,axis=0) for s in star_list]
    for i in range(5):
        for j in range(i,5):
            #Encontra ponto mais próximo da estrela 2 do centro da estrela 1
            idx_closer_2nd=np.argmin([np.linalg.norm(s-centros[i]) for s in star_list[j]])
            #Encontra ponto mais próximo da estrela 1 do ponto da estrela 2
            idx_closer_1st=np.argmin([np.linalg.norm(s-star_list[j][idx_closer_2nd]) for s in star_list[i]])
            #Calcula a distância entre eles
            dist=np.linalg.norm(star_list[i][idx_closer_1st]-star_list[j][idx_closer_2nd])
            #Se a distância for menor do que 0.01, entendemos que eles estão tocando
            if dist<0.01 and i!=j:
                coord=(star_list[i][idx_closer_1st]+star_list[j][idx_closer_2nd])/2
                center=original_pentagon.mean(axis=0)
                new_center=2*coord-center
                new_pentagon.append(pentagon(new_center,rad,ang+18))
    return new_pentagon

def get_3rd_level_pentagon(star_list,original_pentagon):
    new_pentagon=[]
    c=original_pentagon.mean(axis=0)
    rad=np.linalg.norm(original_pentagon[0]-original_pentagon.mean(axis=0))
    star_center=np.array([s.mean(axis=0) for s in star_list])
    ang=np.degrees(np.angle(np.dot((original_pentagon[0]-c),np.array([1,1j]))))
    coord=2*star_center-c
    for n_p in coord:
        new_pentagon.append(pentagon(n_p,rad,ang+18))
    return new_pentagon


###### CONSTANTES
phi=(1+np.sqrt(5))/2
hd=np.sqrt((5+np.sqrt(5))/2)

#### Streamlit objects

largura=st.sidebar.number_input(label="Largura da parede",min_value=1,value=238)
altura=st.sidebar.number_input(label="Altura da parede",min_value=1,value=148)

radius=st.sidebar.number_input(label='Raio do pentágono',min_value=0,value=30,step=1)
angulo=st.sidebar.slider(label="Ângulo do pentágono",min_value=-18.0,max_value=18.0,step=0.1)
x_center=st.sidebar.slider(label="Centro do pentágono (eixo x)",min_value=0,max_value=largura,value=largura//2)
y_center=st.sidebar.slider(label="Centro do pentágono (eixo y)",min_value=0,max_value=altura,value=altura//2)

levels=st.selectbox(label="Complexidade",options=[1,2,3,4])

default=['#FFFFFF','#FF0000','#00FF00','#0000FF','#DDDD44']
colors=st.columns(levels+1)
res_col=['#FFFFFF','#FF0000','#00FF00','#0000FF','#DDDD44']
print(type(colors))
for col in range(len(colors)):
    if col==0:
        res_col[col]=colors[col].color_picker(label="Cor de fundo",value='#FFFFFF')
    else:
        res_col[col]=colors[col].color_picker(label=f"Cor nível {col}",value=default[col-1])

L=hd/phi*radius
B_R=L/3/np.sin(np.pi/10)*np.sin(7*np.pi/10)
s_R=L/3/np.sin(np.pi/10)*np.sin(2*np.pi/10)

print(colors[0])

p=pentagon((x_center,y_center),radius,angulo)

fig, axes = plt.subplots(figsize=(13,8))
axes.set_xlim(0,largura)
axes.set_ylim(0,altura)
axes.set_facecolor(res_col[0])
axes.add_patch(plt.Polygon(p, ec='k',facecolor=res_col[1]))
if levels>1:
    star_list=draw5stars(p)
    for s in star_list:
        axes.add_patch(plt.Polygon(s, ec='k',facecolor=res_col[2]))
if levels>2:
    outer_pentagon=get_outer_pentagon(star_list,p)
    for n_p in outer_pentagon:
        axes.add_patch(plt.Polygon(n_p,ec='k',facecolor=res_col[3]))
if levels>3:
    third_level=get_3rd_level_pentagon(star_list,p)
    for n_p in third_level:
        axes.add_patch(plt.Polygon(n_p,ec='k',facecolor=res_col[4]))
st.pyplot(fig)