import os
import time
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont
import pyautogui   # Biblioteca para automação de teclado/mouse

# ---------------------------------------------------------
# CONFIGURAÇÕES DO PROJETO
# ---------------------------------------------------------
PASTA_FOTOS = "fotos_recebidas"
PASTA_PROCESSADAS = "fotos_processadas"
PASTA_SAIDAS = "saidas"

# Caminho do Adobe Acrobat (ajuste se necessário)
ACROBAT = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"

# ---------------------------------------------------------
# FUNÇÃO: Espera até ter 9 fotos na pasta
# ---------------------------------------------------------
def esperar_9_fotos():
    print("Aguardando 9 fotos...")
    while True:
        arquivos = os.listdir(PASTA_FOTOS)
        fotos = [f for f in arquivos if f.lower().endswith((".jpg", ".jpeg", ".png"))]

        print(f"Fotos encontradas: {len(fotos)}")
        if len(fotos) >= 9:
            print("9 fotos recebidas!")
            return [os.path.join(PASTA_FOTOS, f) for f in fotos[:9]]

        time.sleep(2)

# ---------------------------------------------------------
# FUNÇÃO: Move as fotos para uma subpasta por lote
# ---------------------------------------------------------
def mover_para_processadas(lista_fotos):
    lotes_existentes = [d for d in os.listdir(PASTA_PROCESSADAS) if d.startswith("lote_")]
    numero_lote = len(lotes_existentes) + 1

    nome_lote = f"lote_{numero_lote:03d}"
    pasta_lote = os.path.join(PASTA_PROCESSADAS, nome_lote)
    os.makedirs(pasta_lote, exist_ok=True)

    for caminho in lista_fotos:
        destino = os.path.join(pasta_lote, os.path.basename(caminho))
        shutil.move(caminho, destino)

    print(f"Fotos movidas para a pasta '{nome_lote}'.")

# ---------------------------------------------------------
# FUNÇÃO: Aplica moldura polaroid em uma foto
# ---------------------------------------------------------
def aplicar_polaroid(caminho_foto):
    img = Image.open(caminho_foto)
    img.thumbnail((1200, 1000))

    margem = 50
    margem_inferior_extra = 220
    largura, altura = img.size
    nova_largura = largura + 2 * margem
    nova_altura = altura + margem + margem_inferior_extra

    polaroid = Image.new("RGB", (nova_largura, nova_altura), "white")
    polaroid.paste(img, (margem, margem))

    draw = ImageDraw.Draw(polaroid)
    try:
        fonte = ImageFont.truetype("GreatVibes-Regular.ttf", 80)
    except:
        fonte = ImageFont.load_default()

    texto = "Maria Clara - 15 anos"
    bbox = draw.textbbox((0, 0), texto, font=fonte)
    largura_texto = bbox[2] - bbox[0]
    pos_texto = ((nova_largura - largura_texto) // 2, altura + margem + 40)
    draw.text(pos_texto, texto, fill="black", font=fonte)

    contorno = Image.new("RGB", (nova_largura + 6, nova_altura + 6), "black")
    contorno.paste(polaroid, (3, 3))

    return contorno

# ---------------------------------------------------------
# FUNÇÃO: Monta a folha A4 com 9 polaroids
# ---------------------------------------------------------
def montar_folha_a4(lista_fotos):
    largura_a4, altura_a4 = 2480, 3508  # A4 retrato
    folha = Image.new("RGB", (largura_a4, altura_a4), "white")

    posicoes = [
        (30, 20), (800, 20), (1600, 20),
        (30, 1180), (800, 1180), (1600, 1180),
        (30, 2340), (800, 2340), (1600, 2340)
    ]

    for caminho, pos in zip(lista_fotos, posicoes):
        polaroid = aplicar_polaroid(caminho)
        polaroid.thumbnail((750, 1050))
        folha.paste(polaroid, pos)

    os.makedirs(PASTA_SAIDAS, exist_ok=True)
    nome_arquivo = os.path.join(PASTA_SAIDAS, f"folha_{int(time.time())}.pdf")
    folha.save(nome_arquivo, "PDF")

    print(f"Folha A4 criada: {nome_arquivo}")
    imprimir_folha(nome_arquivo)

# ---------------------------------------------------------
# FUNÇÃO: Imprimir folha A4 via Acrobat + PyAutoGUI
# ---------------------------------------------------------
def imprimir_folha(caminho):
    caminho_absoluto = os.path.abspath(caminho)

    tentativas = 0
    while not os.path.exists(caminho_absoluto):
        time.sleep(0.2)
        tentativas += 1
        if tentativas > 30:
            print("Erro: arquivo não encontrado para impressão:", caminho_absoluto)
            return

    print("Abrindo janela de impressão (Adobe Acrobat):", caminho_absoluto)

    comando = f'"{ACROBAT}" /p "{caminho_absoluto}"'
    subprocess.Popen(comando, shell=True)

    # espera alguns segundos para a janela abrir
    time.sleep(5)
    # envia Enter para confirmar impressão automaticamente
    pyautogui.press('enter')

# ---------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------
def main():
    while True:
        fotos = esperar_9_fotos()

        print("\nAs 9 fotos selecionadas foram:")
        for f in fotos:
            print(" -", f)

        montar_folha_a4(fotos)
        mover_para_processadas(fotos)

        print("\nProcesso concluído. Aguardando novas fotos...\n")

# ---------------------------------------------------------
# EXECUÇÃO
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
