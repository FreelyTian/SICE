import threading
from deepface import DeepFace
import re
import cv2
import os

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
    except Exception as e:
        with lock:
            match = False
        print(f"Erro durante o reconhecimento: {e}")

while True:
    ret, frame = cap.read()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    if ret:
            # Verificar se uma thread já está em execução
        if cnt % 60 == 0:
            if not any(thread.is_alive() for thread in threading.enumerate() if thread is not threading.main_thread()):
                threading.Thread(target=find_and_match, args=(frame,)).start()
        cnt += 1

        with lock:
            if match:
                # Carregar a imagem do banco de dados ou face temporária
                db_img = cv2.imread(img_path)
                if db_img is not None:
                    # Redimensionar a imagem para uma altura apropriada (por exemplo, 100 pixels de altura)
                    height = 200
                    aspect_ratio = db_img.shape[1] / db_img.shape[0]
                    width = int(height * aspect_ratio)
                    db_img = cv2.resize(db_img, (width, height))

                    # Posicionar a imagem no frame
                    x_offset = frame.shape[1] - width - 10
                    y_offset = 10
                    frame[y_offset:y_offset+height, x_offset:x_offset+width] = db_img

                cv2.putText(frame, f"Bem vindo, {name}", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 1)
            else:
                cv2.putText(frame, "Nada ainda", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 1)

    cv2.imshow('video', frame)

cap.release()
cv2.destroyAllWindows()
