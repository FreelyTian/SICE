import threading
from deepface import DeepFace
import re
import cv2
import os

# Variáveis globais
match = False
name = ''
img_path = ''
lock = threading.Lock()

def find_and_match(cap):
    global match, name, img_path
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
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
                    img_path = fullname  # Guardar o caminho completo da imagem

                    # Extrair a face do banco de dados
                    extracted_faces = DeepFace.extract_faces(img_path=img_path)
                    if extracted_faces:
                        face_only = extracted_faces[0]['face']

                        # Converter a face extraída para uint8 e BGR
                        face_only_bgr = cv2.cvtColor((face_only * 255).astype('uint8'), cv2.COLOR_RGB2BGR)

                        # Salvar a face extraída na pasta temp/
                        temp_face_path = os.path.join('temp', f'temp_face_{name}.jpg')
                        os.makedirs(os.path.dirname(temp_face_path), exist_ok=True)
                        cv2.imwrite(temp_face_path, face_only_bgr)
                        img_path = temp_face_path  # Atualizar img_path para a face temporária
        except Exception as e:
            with lock:
                match = False
            print(f"Erro durante o reconhecimento: {e}")
