import PySimpleGUI as sg
import pyaudio 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

"""Imagen grafica de una onda sonora capatada 
por microfono con PyAudio, PyPlot y PysimpleGUI"""

_VARS = {'window': False,
         'stream': False,
         'fig_agg': False,
         'pltFig': False,
         'xData': False,
         'yData': False,
         'audioData': np.array([])}

# pysimpleGUI 
AppFont='Any 16'
sg.theme('DarkPurple4')
layout=[[sg.Canvas(key='figCanvas')],
        [sg.ProgressBar(4000, orientation='h', 
                        size=(60, 20), key='-PROG-')],
        [sg.Button('Escuchar', font=AppFont),
         sg.Button('Parar', font=AppFont, disabled=True),
         sg.Button('Salir', font=AppFont)]]

_VARS['window']=sg.Window('Onda sonora captada por microfono - PyPlot',
                            layout, finalize=True, location=(400, 100))
                            

# PyAudio
CHUNK= 1024 # Trozos de datos por bloque. 1024 muestras de datos por bloque
RATE = 44100 #Frecuencia en hz que indica que en un segundo se tomaron dichas 
#cantidades de muestras analogicas de audio para crear el audio digital correspondiente. 
INTERVAL= 1
TIMEOUT= 10
pAud = pyaudio.PyAudio()

# Pyplot

def draw_figure(canvas, figure):
        figure_canvas_agg= FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1) 
        return figure_canvas_agg

def drawPlot():
        _VARS['pltFig']=plt.figure()
        plt.plot(_VARS['xData'], _VARS['yData'], '--k')
        plt.ylim(-4000, 4000)
        _VARS['fig_agg'] = draw_figure(
                _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])

def updatePlot(data):
        _VARS['fig_agg'].get_tk_widget().forget()
        plt.cla()
        plt.clf()
        plt.plot(_VARS['xData'], data, '--k' )
        plt.ylim(-4000, 4000)
        _VARS['fig_agg']=draw_figure(
                _VARS['window']['figCanvas'].TKCanvas, _VARS['pltFig'])


#Funciones:

def parar():
        if _VARS['stream']:
            _VARS['stream'].stop_stream()
            _VARS['stream'].close()
            _VARS['window']['-PROG-'].update(0)
            _VARS['window'].FindElement('Parar').Update(disabled=True)
            _VARS['window'].FindElement('Escuchar').Update(disabled=False)


def callback(in_data, frame_count, time_info, status):
        _VARS['audioData']=np.frombuffer(in_data, dtype=np.int16)
        return (in_data, pyaudio.paContinue)


def escuchar():
    _VARS['window'].FindElement('Parar').Update(disabled=False)
    _VARS['window'].FindElement('Escuchar').Update(disabled=True)
    _VARS['stream'] = pAud.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK,
                                stream_callback=callback)

    _VARS['stream'].start_stream()

# Inicializar PyPlot

plt.style.use('ggplot')
_VARS['xData'] = np.linspace(0, CHUNK, num=CHUNK, dtype=int)
_VARS['yData'] = np.zeros(CHUNK)
drawPlot()

# Bloque principal

while True:
        event, values= _VARS['window'].read(timeout=TIMEOUT)
        if event == sg.WIN_CLOSED or event == 'Salir':
                parar()
                pAud.terminate()
                break
        
        if event == 'Escuchar':
                escuchar()
        elif event == 'Parar': 
                parar()
        elif _VARS['audioData'].size !=0:
             _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))
             updatePlot(_VARS['audioData'])

_VARS ['window'].close()   

