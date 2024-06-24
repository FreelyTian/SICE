import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from deepface import DeepFace
import re
import cv2
import os

from pronunciator import amain

cap = cv2.VideoCapture(0)

match = False
name = ''
img_path = ''
cnt = 0

# Adicionar lock para evitar condições de corrida
lock = threading.Lock()

def find_and_match(frame):
    global match, name, img_path
    try:
        result = DeepFace.find(frame, 'face-db/')
        with lock:
            if len(result) == 0:
                match = False
            else:
                match = True
                fullname = result[0]['identity'][0]
                ptn = r'(?<=^.{8})([^\\]*)'
                name = re.search(ptn, fullname).group(0)

                threading.Thread(target=run_audio_save_task, args=(name, "pt-BR-ThalitaNeural")).start()
    except Exception as e:
        with lock:
            match = False
        print(f"Erro durante o reconhecimento: {e}")

def run_audio_save_task(text: str, voice: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with ThreadPoolExecutor() as executor:
        loop.run_until_complete(loop.run_in_executor(executor, amain, text, voice))


while True:
    ret, frame = cap.read()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if ret:
        if cnt % 60 == 0:
            # Verificar se uma thread já está em execução
            if not any(thread.is_alive() for thread in threading.enumerate() if thread is not threading.main_thread()):
                threading.Thread(target=find_and_match, args=(frame,)).start()
        cnt += 1

        if match:
            cv2.putText(frame, f"Bem vindo, {name}", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)
        else:
            cv2.putText(frame, "Nada ainda", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 1)

    cv2.imshow('video', frame)

cap.release()
cv2.destroyAllWindows()