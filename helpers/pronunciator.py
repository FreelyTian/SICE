
import edge_tts as tss  # Importa o módulo edge_tts pra poder usar a comunicação com o serviço de texto para fala
import pygame  # Importa o módulo pygame para suporte a reprodução de áudio. é mais flexível com formatos de áudio que o playsound

async def save_say_mp3(text: str, voice: str):
    """
    Salva o texto como um arquivo MP3 usando a voz especificada.

    Args:
        text (str): O texto a ser convertido em fala e salvo como um arquivo MP3.
        voice (str): A voz a ser usada para a conversão em fala.

    Returns:
        None
    """
    communicate = tss.Communicate(text, voice)
    print('salvando arquivo...')
    await communicate.save("temp/output.mp3")
    print('arquivo salvo!')

def say():
    """
    Reproduz o Arquivo de áudio salvo por `save_say_mp3()`.
    """
    print('tocando arquivo...')
    pygame.mixer.init()  # Inicializa o mixer do pygame
    pygame.mixer.music.load("temp/output.mp3")  # Carrega o arquivo de áudio
    pygame.mixer.music.play(loops=0)  # Toca o arquivo de áudio

    while pygame.mixer.music.get_busy():  # Enquanto o arquivo de áudio estiver tocando, impede que o programa termine
        pygame.time.Clock().tick(10)

    print('arquivo tocado!')
    pygame.mixer.music.unload()  # Descarrega o arquivo de áudio, acho que isso resolve um bug de file in use
    pygame.mixer.quit()  # Encerra o mixer do pygame
    pygame.quit()  # Encerra o pygame, mas não sei se é necessário
