import PySimpleGUI as sg
import pyaudio
import numpy as np


"""Forma de onda captada en tiempo real mediante audio"""

# VARS consts:
_VARS = {'window': False,
         'stream': False,
         'audioData': np.array([]) }

# PySimpleGUI
AppFont = 'Any 16'
sg.theme('DarkPurple4')
layout = [[sg.Graph(canvas_size=(500, 500), 
                    graph_bottom_left=(-2, -2),
                    graph_top_right=(102, 102),
                    background_color='#9C00FF',
                    key='graph')],
         [sg.ProgressBar(4000, orientation='h',
                          size=(20, 20), key='-PROG-')],
           [sg.Button('Escuchar', font=AppFont),
            sg.Button('Parar', font=AppFont, disabled=True),
            sg.Button('Salir', font=AppFont)]]
_VARS['window'] = sg.Window('Forma de onda captada por microfono + Max nivel',
                                    layout, finalize=True)

graph = _VARS['window']['graph']

# PyAudio vars
CHUNK = 1024
RATE = 44100
INTERVAL = 1
TIMEOUT = 10 
pAud = pyaudio.PyAudio()

# Funciones

# PySimpleGUI TRAMA

def drawAxis(dataRangeMin=0, dataRangeMax=100):
    # Y
    graph.DrawLine((0, 50), (100, 50))
    # X
    graph.DrawLine((0, dataRangeMin), (0, dataRangeMax))


# PyAudio TRANSMISION 

def parar():
    if _VARS['stream']:
        _VARS['stream'].stop_stream()
        _VARS['stream'].close()
        _VARS['window']['-PROG-'].update(0)
        _VARS['window'].FindElement('Parar').Update(disabled=True)
        _VARS['window'].FindElement('Escuchar').Update(disabled=False)

def callback(in_data, frame_count, time_info, status):
    _VARS['audioData'] = np.frombuffer(in_data, dtype=np.int16)
    return(in_data, pyaudio.paContinue)


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


# Inicialización 

drawAxis()

# Bloque principal

while True:
    event, values = _VARS['window'].read(timeout=TIMEOUT)
    if event == sg.WIN_CLOSED or event == 'Salir':
        parar()
        pAud.terminate()
        break
    if event == 'Escuchar':
        escuchar()
    if event == 'Parar':
        parar()


    elif _VARS['audioData'].size != 0:
        
        _VARS['window']['-PROG-'].update(np.amax(_VARS['audioData']))
        
        graph.erase()
        drawAxis()
          
        for x in range(CHUNK):
            graph.DrawCircle((x, (_VARS['audioData'][x]/100)+50), 0.4,
                             line_color='black', fill_color='black')


_VARS['window'].close()