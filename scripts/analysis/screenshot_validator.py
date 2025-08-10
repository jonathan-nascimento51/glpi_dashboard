# -*- coding: utf-8 -*-
import pyautogui
import time
import webbrowser
from PIL import Image
import os

def capture_dashboard_screenshot():
    """Captura screenshot do dashboard para validacao"""
    
    print("Abrindo o dashboard no navegador...")
    # Abrir o dashboard no navegador
    webbrowser.open('http://localhost:3001')
    
    # Aguardar o carregamento da pagina
    print("Aguardando carregamento da pagina...")
    time.sleep(5)
    
    # Capturar screenshot
    print("Capturando screenshot...")
    screenshot = pyautogui.screenshot()
    
    # Salvar screenshot
    screenshot_path = 'dashboard_screenshot.png'
    screenshot.save(screenshot_path)
    print(f"Screenshot salva em: {os.path.abspath(screenshot_path)}")
    
    # Informacoes sobre a screenshot
    print(f"Dimensoes da tela: {screenshot.size}")
    
    return screenshot_path

def analyze_screenshot(screenshot_path):
    """Analise basica da screenshot"""
    try:
        img = Image.open(screenshot_path)
        
        # Converter para RGB se necessario
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Analise basica de cores
        colors = img.getcolors(maxcolors=256*256*256)
        
        print("\n=== ANALISE DA SCREENSHOT ===")
        print(f"Modo da imagem: {img.mode}")
        print(f"Tamanho: {img.size}")
        
        if colors:
            print(f"Numero de cores unicas: {len(colors)}")
            
            # Verificar se ha diversidade de cores (indicando conteudo)
            if len(colors) > 100:
                print(" Boa diversidade de cores - provavelmente ha conteudo carregado")
            else:
                print(" Poucas cores - pode indicar pagina em branco ou erro")
        
        # Verificar pixels predominantes
        pixel_sample = img.getpixel((img.width//2, img.height//2))
        print(f"Pixel central (RGB): {pixel_sample}")
        
        # Verificar se e muito branco (pagina em branco)
        if pixel_sample[0] > 240 and pixel_sample[1] > 240 and pixel_sample[2] > 240:
            print(" Pixel central muito claro - pode ser pagina em branco")
        else:
            print(" Pixel central com cor - provavelmente ha conteudo")
            
    except Exception as e:
        print(f"Erro na analise: {e}")

if __name__ == "__main__":
    try:
        print("=== VALIDADOR DE DASHBOARD ===")
        print("Verificando se pyautogui esta disponivel...")
        
        # Verificar se consegue capturar
        screen_size = pyautogui.size()
        print(f"Tamanho da tela detectado: {screen_size}")
        
        screenshot_path = capture_dashboard_screenshot()
        analyze_screenshot(screenshot_path)
        
        print("\n=== INSTRUCOES ===")
        print(f"1. Verifique o arquivo: {os.path.abspath(screenshot_path)}")
        print("2. Analise visualmente se o dashboard esta carregado")
        print("3. Verifique se ha dados sendo exibidos corretamente")
        
    except ImportError as e:
        print(f"Erro de importacao: {e}")
        print("Instale as dependencias: pip install pyautogui pillow")
    except Exception as e:
        print(f"Erro geral: {e}")
        print("Verifique se o dashboard esta rodando em http://localhost:3001")
