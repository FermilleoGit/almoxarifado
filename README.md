# 📦 Almoxarifado — Versão Web (Flask)

## Estrutura de arquivos

```
almoxarifado/
├── app.py              ← Servidor Flask (backend)
├── almoxarifado.json   ← Dados (criado automaticamente)
└── static/
    └── index.html      ← Interface mobile (frontend)
```

---

## ▶️ Como rodar

### 1. Instale o Flask (uma vez só)
```bash
pip install flask
```

### 2. Rode o servidor
```bash
python app.py
```

Você verá algo como:
```
 * Running on http://0.0.0.0:5000
```

### 3. Acesse no computador
Abra o navegador em: **http://localhost:5000**

### 4. Acesse no celular (mesma rede Wi-Fi!)
No terminal, descubra o IP da sua máquina:
- **Windows**: `ipconfig` → procure "IPv4 Address"
- **Mac/Linux**: `ifconfig` → procure o IP em `en0` ou `eth0`

Então acesse no celular: **http://SEU_IP:5000**
Exemplo: `http://192.168.1.10:5000`

> 💡 O celular e o computador precisam estar na mesma rede Wi-Fi!

---

## 📱 Para instalar como app no celular (PWA)

**No Chrome (Android):**
1. Acesse o endereço no Chrome
2. Menu (⋮) → "Adicionar à tela inicial"

**No Safari (iPhone):**
1. Acesse o endereço no Safari
2. Botão de compartilhar → "Adicionar à Tela de Início"

O app vai aparecer como ícone no celular, igual a um app normal!

---

## ☁️ Quer que os clientes acessem de qualquer lugar (sem Wi-Fi)?

Você vai precisar fazer deploy em um servidor. Opções gratuitas:
- **Railway** (railway.app) — mais fácil, recomendado
- **Render** (render.com) — também simples
- **PythonAnywhere** (pythonanywhere.com) — específico para Python

Me peça ajuda para configurar qualquer uma dessas opções!
