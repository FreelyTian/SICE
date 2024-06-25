import asyncio  # Importa o módulo asyncio para suporte a programação assíncrona
import threading  # Importa o módulo threading para suporte a threads
from deepface import DeepFace  # Importa a classe DeepFace do módulo deepface
import re  # Importa o módulo re para suporte a expressões regulares
import cv2  # Importa o módulo cv2 para suporte a processamento de imagens
from filelock import FileLock  # Importa a classe FileLock do módulo filelock
from helpers.pronunciator import save_say_mp3, say  # Importa as funções save_say_mp3 e say do módulo pronunciator do pacote helpers
from helpers.nameHandler import get_metadata, get_welcome_string  # Importa as funções get_metadata e get_welcome_string do módulo nameHandler do pacote helpers
import time  # Importa o módulo time para suporte a manipulação de tempo

cap = cv2.VideoCapture(0)  # Inicializa a captura de vídeo a partir da câmera
match = False  # Variável booleana que indica se houve correspondência facial
name = ''  # Variável que armazena o nome da pessoa reconhecida
cnt = 0  # Variável que conta o número de frames processados
said = False  # Variável booleana que indica se já foi dito algo
forbidden = False  # Variável booleana que indica se o acesso é proibido
last_said = 0  # Variável que armazena o tempo da última vez que algo foi dito
lock = threading.Lock()  # Inicializa um objeto de trava para sincronização de threads

def find_and_match(frame):
    """
    Função que faz o reconhecimento facial em um frame de vídeo.

    Parâmetros:
    - frame: O frame de vídeo a ser processado.

    Retorna:
    Nenhum valor de retorno.
    """
    global match, name, said, last_said, forbidden
    
    file_lock = FileLock("temp/output.lock")  # Inicializa um objeto de trava de arquivo
    
    try:
        result = DeepFace.find(frame, 'face-db/')  # Realiza o reconhecimento facial no frame usando as imagens do banco de imagens 'face-db/'
        
        with lock:
            
            if len(result) == 0:
                match = False
                print("Não reconhecido")
            else:
                match = True
                forbidden = False
                fullname = result[0]['identity'][0]
                ptn = r'(?<=^.{8})([^\\]*)'
                name = re.search(ptn, fullname).group(0)
                metadata = get_metadata(name)
                welcome_string = get_welcome_string(metadata)
                
                if not forbidden and time.time() - last_said > 15:  # Verifica se já passaram 15 segundos desde a última vez que a mensagem foi dita
                    said = False # Libera a flag de dito pra poder repetir a frase.
                    print("Reiniciando contador de tempo...")
                    last_said = time.time() # Atualiza o tempo da última vez que algo foi dito
                    
                if not said: # Caso possa, vai dizer a mensagem.
                    file_lock.acquire()
                    asyncio.run(save_say_mp3(welcome_string, "pt-BR-ThalitaNeural"))
                    print("Dizendo...")
                    say()
                    said = True # Atualiza a flag de dito pra não repetir isso várias vezes.
                else:
                    print("Já disse") # Se não pode dizer, vai dizer que já disse.
                    
    except Exception as e:
        with lock:
            match = False
            unrecognized_said = said and forbidden # Impede de dizer a mensagem de não reconhecido várias vezes.
            
            if not unrecognized_said: # Se não disse a mensagem de não reconhecido, vai dizer.
                    asyncio.run(save_say_mp3("Não reconhecido, favor dirija-se ao atendimento para fazer seu cadastro.", "pt-BR-ThalitaNeural"))
                    say()
                    said = True
                    forbidden = True
                    
        print(f"Erro durante o reconhecimento: {e}")
    finally:
        file_lock.release() # Libera a trava de arquivo

while True:
    ret, frame = cap.read()  # Lê um frame do vídeo
    
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Verifica se a tecla 'q' foi pressionada para sair do loop
        break
    
    if ret:
        
        if cnt % 60 == 0: # Verifica se o contador é múltiplo de 60 (aproximadamente 1 vez por segundo) pra rodar o reconhecimento (é menos pesado)
            
            if not any(thread.is_alive() for thread in threading.enumerate() if thread is not threading.main_thread()): 
                # Executa a função find_and_match em uma nova thread (sem travar execução do programa principal)
                threading.Thread(target=find_and_match, args=(frame,)).start()
                
        cnt += 1

        if match:
            cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 255, 0), 10)

    cv2.imshow('video', frame)  # Exibe o frame do vídeo

cap.release()  # Libera a captura de vídeo
cv2.destroyAllWindows()  # Fecha todas as janelas abertas
