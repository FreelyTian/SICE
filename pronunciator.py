import edge_tts as tss
import pygame

async def amain(text : str, voice : str):
    communicate = tss.Communicate(text, voice)
    await communicate.save("temp/output.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("temp/output.mp3")
    pygame.mixer.music.play()