# -*- coding: utf-8 -*-
import pyautogui
import time
import webbrowser
import os

def analyze_dashboard_regions():
    """Analisa diferentes regioes da tela para verificar conteudo"""
    
    print("=== ANALISE DETALHADA DO DASHBOARD ===")
    
    # Abrir o dashboard
    print("Abrindo dashboard em http://localhost:3001...")
    webbrowser.open('http://localhost:3001')
    
    # Aguardar carregamento
    print("Aguardando 8 segundos para carregamento completo...")
    time.sleep(8)
    
    # Capturar screenshot
    print("Capturando screenshot...")
    screenshot = pyautogui.screenshot()
    screenshot_path = 'dashboard_analysis.png'
    screenshot.save(screenshot_path)
    
    # Analisar diferentes regioes
    width, height = screenshot.size
    print(f"Dimensoes da tela: {width}x{height}")
    
    # Definir regioes para analise
    regions = {
        'topo_esquerdo': (width//4, height//4),
        'topo_direito': (3*width//4, height//4),
        'centro': (width//2, height//2),
        'baixo_esquerdo': (width//4, 3*height//4),
        'baixo_direito': (3*width//4, 3*height//4)
    }
    
    print("\n=== ANALISE POR REGIOES ===")
    content_detected = False
    
    for region_name, (x, y) in regions.items():
        pixel = screenshot.getpixel((x, y))
        r, g, b = pixel
        
        # Verificar se nao e branco puro
        is_white = r > 240 and g > 240 and b > 240
        is_very_dark = r < 50 and g < 50 and b < 50
        
        print(f"{region_name}: RGB({r}, {g}, {b}) - {'Branco' if is_white else 'Escuro' if is_very_dark else 'Com conteudo'}")
        
        if not is_white and not is_very_dark:
            content_detected = True
    
    # Analise geral de cores
    colors = screenshot.getcolors(maxcolors=256*256*256)
    unique_colors = len(colors) if colors else 0
    
    print(f"\nCores unicas detectadas: {unique_colors}")
    
    # Verificar se ha elementos visuais
    if unique_colors > 1000:
        print(" DASHBOARD CARREGADO: Muitas cores detectadas - interface rica")
    elif unique_colors > 100:
        print(" DASHBOARD PARCIAL: Algumas cores - pode estar carregando")
    else:
        print(" DASHBOARD VAZIO: Poucas cores - provavelmente erro")
    
    if content_detected:
        print(" CONTEUDO DETECTADO: Pixels nao-brancos encontrados em multiplas regioes")
    else:
        print(" SEM CONTEUDO: Apenas pixels brancos/escuros detectados")
    
    print(f"\nScreenshot salva em: {os.path.abspath(screenshot_path)}")
    
    # Verificar conectividade
    print("\n=== TESTE DE CONECTIVIDADE ===")
    try:
        import urllib.request
        
        # Testar backend
        try:
            response = urllib.request.urlopen('http://localhost:8000/health', timeout=5)
            print(f" Backend (8000): {response.getcode()} - {response.read().decode()}")
        except Exception as e:
            print(f" Backend (8000): Erro - {e}")
        
        # Testar frontend
        try:
            response = urllib.request.urlopen('http://localhost:3001', timeout=5)
            print(f" Frontend (3001): {response.getcode()} - Respondendo")
        except Exception as e:
            print(f" Frontend (3001): Erro - {e}")
            
    except ImportError:
        print("Modulo urllib nao disponivel para teste")
    
    return screenshot_path

if __name__ == "__main__":
    try:
        screenshot_path = analyze_dashboard_regions()
        print("\n=== CONCLUSAO ===")
        print("1. Verifique o arquivo de screenshot gerado")
        print("2. Analise os resultados acima")
        print("3. Se necessario, verifique os logs dos serviços")
        
    except Exception as e:
        print(f"Erro durante analise: {e}")
        print("Verifique se os servicos estao rodando:")
        print("- Backend: http://localhost:8000")
        print("- Frontend: http://localhost:3001")
