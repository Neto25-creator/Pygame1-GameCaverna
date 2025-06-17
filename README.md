# 🕹️ Escape da Caverna

### Desenvolvedor  
**Ênio Muliterno Neto**  
**RA:** 1138165

---

## 📖 Sobre o Jogo

Escape da Caverna é um jogo de plataforma vertical em que o jogador deve subir o máximo que conseguir por plataformas flutuantes, desviando de inimigos voadores e coletando moedas no caminho. O ambiente é uma caverna misteriosa e dinâmica, com elementos decorativos animados que enriquecem a ambientação. O jogo oferece níveis de dificuldade e um sistema de pontuação com histórico salvo localmente.

---

## 🧠 Tecnologias e Bibliotecas Utilizadas

- **Python 3**
- **Pygame** – biblioteca principal para construção do jogo, animações, controle de eventos, sons e renderização.
- **speech_recognition** – permite que o jogador fale seu nome, que é capturado automaticamente pelo microfone.
- **pyttsx3** – utilizado para que o sistema fale com o jogador em português (voz sintetizada).
- **threading** – permite que a voz e a escuta ocorram paralelamente à execução do jogo.
- **json** – usado para armazenamento persistente dos recordes (pontuação e moedas).
- **os & datetime** – suporte para manipulação de arquivos e formatação de data/hora.

---

## 🧩 Funcionalidades Implementadas

- Interface gráfica interativa com botões e menus.
- Dificuldade ajustável (Fácil, Médio, Difícil).
- Sistema de fala com voz em português para introdução do jogador.
- Reconhecimento de fala para capturar o nome do jogador.
- Animações para moedas, jogador e inimigos.
- Objetos decorativos (vagalumes) com movimento aleatório.
- Sistema de recordes com salvamento local em `game_scores.json`.
- Menu de pausa e tela de game over com reinício imediato.
- Pulo adaptativo. Se a tecla W for pressionada rapidamente, o pulo será pequeno, caso a tecla for pressionada por mais tempo, o pulo será maior.

---

## ▶️ Como Jogar

1. Clone este repositório.
2. Instale as dependências:
   ```bash
   pip install pygame pyttsx3 SpeechRecognition pyaudio
3. Caso preferir, execute o arquivo .exe

## divirta-se !