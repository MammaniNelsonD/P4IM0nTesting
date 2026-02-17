# -*- coding: utf-8 -*-
from burp import IBurpExtender, ITab, IContextMenuFactory, IMessageEditorController, IHttpListener
from java.io import PrintWriter, File, FileWriter
from java.util import ArrayList
from java.lang import String
from javax.swing import JPanel, JButton, JTextArea, JScrollPane, JSplitPane, JLabel, JTextField, JPasswordField, JMenuItem, SwingUtilities, BoxLayout, BorderFactory, JTabbedPane, JComboBox, JTable, JFileChooser, JCheckBox, JOptionPane
from javax.swing.table import AbstractTableModel
from java.awt import BorderLayout, Dimension, FlowLayout, Color, Font
from threading import Thread, Lock
import urllib2
import json
import base64
import sys
import traceback
import re
import datetime
import time
import hmac
import hashlib

class BurpExtender(IBurpExtender, ITab, IContextMenuFactory, IMessageEditorController, AbstractTableModel, IHttpListener):
    
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        self._stdout = PrintWriter(callbacks.getStdout(), True)
        self._stderr = PrintWriter(callbacks.getStderr(), True)
        
        callbacks.setExtensionName("P4IM0nTesting")
        
        self.currentlyDisplayedItem = None
        self._log = ArrayList()
        self._lock = Lock()
        self.context_file_path = None
        
        # Cyberpunk Colors
        self.CYBER_BLACK = Color(13, 13, 13)
        self.CYBER_GREEN = Color(0, 255, 65)  # Matrix Green
        self.CYBER_PINK = Color(255, 0, 85)
        self.CYBER_FONT = Font("Monospaced", Font.BOLD, 12)
        
        # Estado
        self.passive_scan_enabled = False
        self.current_provider = "Gemini" # Default
        
        self.build_ui()
        callbacks.addSuiteTab(self)
        callbacks.registerContextMenuFactory(self)
        callbacks.registerHttpListener(self)
        
        self._stdout.println("[+] P4IM0nTesting (Cyberpunk Edition v2.5 - STREAM FIX) cargado.")

    def apply_cyberpunk_style(self, component):
        component.setBackground(self.CYBER_BLACK)
        component.setForeground(self.CYBER_GREEN)
        if hasattr(component, 'setFont'):
            component.setFont(self.CYBER_FONT)
        if hasattr(component, 'setCaretColor'):
            component.setCaretColor(self.CYBER_PINK)
            
    def build_ui(self):
        self.main_panel = JPanel(BorderLayout())
        self.apply_cyberpunk_style(self.main_panel)
        
        # --- PANEL SUPERIOR: CONFIGURACIÓN ---
        config_panel = JPanel()
        config_panel.setLayout(BoxLayout(config_panel, BoxLayout.Y_AXIS))
        config_panel.setBorder(BorderFactory.createTitledBorder("SYSTEM CONFIG - P4IM0nTesting"))
        self.apply_cyberpunk_style(config_panel)
        
        # Fila 1: Provider & API Key
        top_config_row = JPanel(BorderLayout())
        self.apply_cyberpunk_style(top_config_row)
        
        # Provider Select
        prov_panel = JPanel(BorderLayout())
        self.apply_cyberpunk_style(prov_panel)
        lbl_prov = JLabel(" [PROV] Agent: ")
        self.apply_cyberpunk_style(lbl_prov)
        prov_panel.add(lbl_prov, BorderLayout.WEST)
        
        self.provider_combo = JComboBox(["Gemini", "ChatGLM"])
        self.apply_cyberpunk_style(self.provider_combo)
        self.provider_combo.addActionListener(lambda x: self.on_provider_change())
        prov_panel.add(self.provider_combo, BorderLayout.CENTER)
        
        # API Key
        api_panel = JPanel(BorderLayout())
        self.apply_cyberpunk_style(api_panel)
        lbl_api = JLabel(" [KEY] API Key: ")
        self.apply_cyberpunk_style(lbl_api)
        api_panel.add(lbl_api, BorderLayout.WEST)
        
        self.api_key_field = JPasswordField(25)
        self.apply_cyberpunk_style(self.api_key_field)
        self.api_key_field.setForeground(self.CYBER_PINK) 
        api_panel.add(self.api_key_field, BorderLayout.CENTER)
        
        btn_cargar_modelos = JButton(" [INIT] Cargar Modelos")
        self.apply_cyberpunk_style(btn_cargar_modelos)
        btn_cargar_modelos.setForeground(self.CYBER_PINK)
        btn_cargar_modelos.addActionListener(lambda x: self.start_fetch_models())
        api_panel.add(btn_cargar_modelos, BorderLayout.EAST)
        
        # Model Select
        model_panel = JPanel(BorderLayout())
        self.apply_cyberpunk_style(model_panel)
        lbl_model = JLabel(" [MOD] Modelo: ")
        self.apply_cyberpunk_style(lbl_model)
        model_panel.add(lbl_model, BorderLayout.WEST)
        
        self.model_combo = JComboBox(["-- AUTH REQUIRED --"])
        self.apply_cyberpunk_style(self.model_combo)
        model_panel.add(self.model_combo, BorderLayout.CENTER)
        
        # Assemble Top Row
        top_left = JPanel(BorderLayout())
        self.apply_cyberpunk_style(top_left)
        top_left.add(prov_panel, BorderLayout.WEST)
        top_left.add(api_panel, BorderLayout.CENTER)
        
        top_config_row.add(top_left, BorderLayout.CENTER)
        top_config_row.add(model_panel, BorderLayout.SOUTH)
        
        # Fila 2: System Prompt
        prompt_panel = JPanel(BorderLayout())
        self.apply_cyberpunk_style(prompt_panel)
        self.system_prompt_area = JTextArea(3, 50)
        self.apply_cyberpunk_style(self.system_prompt_area)
        self.system_prompt_area.setText("""## ROL Y PERSONA

Actúa como un **Ingeniero de Seguridad Ofensiva (Senior Pentester) de élite**, especializado en la explotación avanzada de aplicaciones web. Te caracterizas por:1.  **Astucia y Pensamiento Lateral**: No te limitas a lo obvio. Buscas fallos lógicos, condiciones de carrera y encadenamiento de vulnerabilidades (chaining) donde otros solo ven errores de sintaxis.2.  **Persistencia Metódica**: Si un vector de ataque estándar falla, propones inmediatamente técnicas de evasión (bypasses), ofuscación o métodos alternativos.3.  **Rigor Técnico**: Tus respuestas son puramente técnicas, formales y listas para la ejecución profesional.## BASE DE CONOCIMIENTO Y FUENTE DE VERDAD

Tu "Biblia" y fuente primaria de verdad es la **documentación y laboratorios de PortSwigger Web Security Academy**.- **Instrucción Crítica**: Al analizar una solicitud, debes correlacionarla *inmediatamente* con la mecánica específica de los laboratorios de PortSwigger.- Utiliza tus conocimientos internos y búsquedas web para complementar, pero la estructura del ataque debe seguir la lógica de los laboratorios (ej. BLaD, SQLi Union-Based, HTTP Request Smuggling, etc.).## OBJETIVOS DE LA MISIÓN

Tu tarea es generar vectores de ataque listos para ser inyectados en **Burp Suite**. Debes analizar los inputs del usuario (logs, requests, contexto) y generar:### 1. Batería de 20 Peticiones HTTP (Exploitation Vectors)

Debes construir 20 peticiones HTTP completas. No son ejemplos genéricos; son **modificaciones precisas** de la petición original del usuario adaptadas para explotar vulnerabilidades específicas.- **Formato**: Raw HTTP (listo para "Paste from clipboard" en Burp Repeater).- **Contenido**: Deben incluir payloads de inyección, modificaciones de headers, o manipulación de parámetros.### 2. Pensamiento Lateral y Novedades (6 Ideas Adicionales)

Aporta 6 vectores de prueba basados en **CVEs recientes** o técnicas avanzadas que podrían aplicar al stack tecnológico detectado.- Debes incluir el **PoC (Proof of Concept)** paso a paso.## PROTOCOLO DE ACTUACIÓN (Chain of Thought)

Para cada interacción, sigue este proceso mental antes de responder:1.  **ANÁLISIS**: Disecciona la petición del usuario. ¿Qué tecnología usa? ¿Dónde están los puntos de entrada (inputs)?2.  **HIPÓTESIS**: Basándote en PortSwigger, ¿qué laboratorio se parece a esto? (ej. "Esto parece un caso de Server-Side Template Injection debido a...").3.  **CONSTRUCCIÓN**: Redacta la petición HTTP cruda. Asegúrate de que `Content-Length` y los headers sean coherentes.4.  **REVISIÓN**: ¿Es esta la forma más astuta de atacar? ¿Necesito codificar el payload (URL encode, Base64)?## FORMATO DE SALIDA ESTRICTO

Tu respuesta debe seguir estrictamente esta estructura Markdown:### Resumen Ejecutivo

(2-3 líneas definiendo el contexto, superficie de ataque y tecnologías detectadas).



---### Batería de Pruebas (20 Requests)#### 01. [Nombre Técnico de la Vulnerabilidad] (Ref: [Nombre del Lab PortSwigger])**Lógica del Ataque**: Explicación breve de por qué funcionará este payload y qué mecanismo rompe.**Request**:```http

POST /login HTTP/1.1

Host: target-lab.net

...

Content-Length: [Calculado]



param=payload_malicioso



Expected Response: Qué cadena, código de estado o comportamiento confirma la vulnerabilidad.

(...Repetir numerado hasta 20...)

6 Vectores de Ataque Avanzados (CVEs & Research)

CVE-XXXX-YYYY (Título)

Fuente: [Link breve]

Concepto: Cómo aplica esto al contexto actual.

PoC Paso a Paso:

Inyectar X en Y.

Observar Z.

Snippet de Payload: {{7*7}}

REGLAS DE SEGURIDAD Y FORMATO

Datos Sensibles: Reemplaza cualquier dato real (cookies de sesión, dominios reales ajenos al lab) con placeholders como [REDACTED] o target.com.

Estilo: Mantén un tono profesional, directo y sin advertencias morales innecesarias, asumiendo que el usuario está en un entorno controlado de laboratorio (PortSwigger).

Integridad: No omitas headers necesarios. Las peticiones deben ser funcionales. [ESTRICTAMENTE LAS Batería de Pruebas (20 Requests) DEBES RESPONDER CON SOLO:] NO USES JSON. Devuelve CADA petición codificada en BASE64 en una línea separada precedida por 'VECTOR: '. Ejemplo:
VECTOR: VGhpcyBpcyBhIHRlc3QgcmVxdWVzdC4uLgo=
VECTOR: QW5vdGhlciBiYXNlNjQgc3RyaW5nIGhlcmUuLi4K
...
(Así sucesivamente hasta los 20 vectores).""")
        self.system_prompt_area.setLineWrap(True)
        prompt_panel.add(JScrollPane(self.system_prompt_area), BorderLayout.CENTER)
        
        # Fila 3: Archivo y Manual
        mid_panel = JPanel(BorderLayout())
        self.apply_cyberpunk_style(mid_panel)
        
        # Sub-panel archivo
        file_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        self.apply_cyberpunk_style(file_panel)
        btn_file = JButton("CTX FILE")
        self.apply_cyberpunk_style(btn_file)
        btn_file.addActionListener(lambda x: self.select_context_file())
        self.file_label = JLabel(" No File")
        self.apply_cyberpunk_style(self.file_label)
        file_panel.add(btn_file)
        file_panel.add(self.file_label)
        
        # Sub-panel Manual
        manual_panel = JPanel(BorderLayout())
        self.apply_cyberpunk_style(manual_panel)
        self.manual_input = JTextField()
        self.apply_cyberpunk_style(self.manual_input)
        
        manual_btn = JButton("EXECUTE M.P.")
        self.apply_cyberpunk_style(manual_btn)
        manual_btn.setForeground(self.CYBER_PINK)
        manual_btn.addActionListener(lambda x: self.start_manual_attack())
        manual_panel.add(JLabel(" [MANUAL]: "), BorderLayout.WEST)
        manual_panel.add(self.manual_input, BorderLayout.CENTER)
        manual_panel.add(manual_btn, BorderLayout.EAST)
        
        mid_panel.add(file_panel, BorderLayout.NORTH)
        mid_panel.add(manual_panel, BorderLayout.CENTER)
        
        # Fila 4: ADVANCED OPERATIONS
        adv_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        adv_panel.setBorder(BorderFactory.createTitledBorder("ADVANCED OPS"))
        self.apply_cyberpunk_style(adv_panel)
        
        # Passive Toggle
        self.passive_toggle = JCheckBox("Passive Scout")
        self.apply_cyberpunk_style(self.passive_toggle)
        self.passive_toggle.addActionListener(lambda x: self.toggle_passive_scan())
        adv_panel.add(self.passive_toggle)
        
        # Report Button
        btn_report = JButton("HTML REPORT (FULL)")
        self.apply_cyberpunk_style(btn_report)
        btn_report.addActionListener(lambda x: self.generate_html_report())
        adv_panel.add(btn_report)
        
        # 403 Bypass Button
        btn_403 = JButton("BYPASS 403 (Sel)")
        self.apply_cyberpunk_style(btn_403)
        btn_403.setForeground(self.CYBER_PINK)
        btn_403.addActionListener(lambda x: self.run_403_bypass_ui())
        adv_panel.add(btn_403)
        
        # Param Sniper Button
        btn_params = JButton("PARAM SNIPER")
        self.apply_cyberpunk_style(btn_params)
        btn_params.addActionListener(lambda x: self.run_param_sniper())
        adv_panel.add(btn_params)
        
        config_panel.add(top_config_row)
        config_panel.add(prompt_panel)
        config_panel.add(mid_panel)
        config_panel.add(adv_panel)
        
        # --- PANEL CENTRAL ---
        
        self.log_area = JTextArea()
        self.apply_cyberpunk_style(self.log_area)
        self.log_area.setEditable(False)
        self.log_area.setLineWrap(True)
        log_scroll = JScrollPane(self.log_area)
        
        log_chat_panel = JPanel(BorderLayout())
        log_chat_panel.setBorder(BorderFactory.createTitledBorder("NETRUNNER CONSOLE"))
        self.apply_cyberpunk_style(log_chat_panel)
        log_chat_panel.add(log_scroll, BorderLayout.CENTER)
        
        chat_bar = JPanel(BorderLayout())
        self.apply_cyberpunk_style(chat_bar)
        
        self.chat_input = JTextField()
        self.apply_cyberpunk_style(self.chat_input)
        self.chat_input.addActionListener(lambda x: self.send_manual_chat())
        
        send_btn = JButton("SEND >>")
        self.apply_cyberpunk_style(send_btn)
        send_btn.setForeground(self.CYBER_PINK)
        send_btn.addActionListener(lambda x: self.send_manual_chat())
        
        lbl_chat = JLabel(" CHAT: ")
        self.apply_cyberpunk_style(lbl_chat)
        chat_bar.add(lbl_chat, BorderLayout.WEST)
        chat_bar.add(self.chat_input, BorderLayout.CENTER)
        chat_bar.add(send_btn, BorderLayout.EAST)
        log_chat_panel.add(chat_bar, BorderLayout.SOUTH)
        
        # Tabla
        self.logTable = CustomTable(self)
        self.apply_cyberpunk_style(self.logTable)
        self.logTable.setGridColor(self.CYBER_GREEN)
        
        table_scroll = JScrollPane(self.logTable)
        table_scroll.setBorder(BorderFactory.createTitledBorder("ATTACK VECTOR HISTORY"))
        self.apply_cyberpunk_style(table_scroll.getViewport())
        
        top_split = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, log_chat_panel, table_scroll)
        top_split.setResizeWeight(0.5)
        self.apply_cyberpunk_style(top_split)
        
        # Visores
        self.request_viewer = self._callbacks.createMessageEditor(self, False)
        self.response_viewer = self._callbacks.createMessageEditor(self, False)
        
        tabs = JTabbedPane()
        tabs.addTab("REQ", self.request_viewer.getComponent())
        tabs.addTab("RES", self.response_viewer.getComponent())
        
        main_split = JSplitPane(JSplitPane.VERTICAL_SPLIT, top_split, tabs)
        main_split.setResizeWeight(0.6)
        self.apply_cyberpunk_style(main_split)
        
        self.main_panel.add(config_panel, BorderLayout.NORTH)
        self.main_panel.add(main_split, BorderLayout.CENTER)

    # --- PROVIDER LOGIC ---
    def on_provider_change(self):
        self.current_provider = self.provider_combo.getSelectedItem()
        self.log_to_ui("[*] SWITCHING AGENT TO: " + self.current_provider)
        self.model_combo.removeAllItems()
        self.model_combo.addItem("-- RELOAD MODELS --")
        
    def start_fetch_models(self):
        api_key = "".join(self.api_key_field.getPassword())
        if not api_key:
            self.log_to_ui("[-] ERROR: MISSING API KEY.")
            return
            
        self.log_to_ui("[*] UPLINK ESTABLISHED (%s). FETCHING MODELS..." % self.current_provider)
        
        if self.current_provider == "ChatGLM":
             # Zhipu no tiene endpoint simple de lista de modelos publico, hardcodeamos los comunes
             def update_combo_glm():
                 self.model_combo.removeAllItems()
                 self.model_combo.addItem("glm-4")
                 self.model_combo.addItem("glm-4-plus")
                 self.model_combo.addItem("glm-4-flash")
                 self.model_combo.addItem("glm-4-air")
                 self.model_combo.addItem("glm-3-turbo")
                 self.log_to_ui("[+] GLM MODELS LOADED (Key: %s...)." % api_key[:5])
             SwingUtilities.invokeLater(update_combo_glm)
             return

        # Gemini Logic
        t = Thread(target=self.fetch_models_worker_gemini, args=(api_key,))
        t.start()
        
    def fetch_models_worker_gemini(self, api_key):
        url = "https://generativelanguage.googleapis.com/v1beta/models?key=" + api_key
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req, timeout=15)
            result = json.loads(response.read())
            model_names = [m['name'].replace('models/', '') for m in result.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
            
            if model_names:
                def update_combo():
                    self.model_combo.removeAllItems()
                    for name in model_names:
                        self.model_combo.addItem(name)
                SwingUtilities.invokeLater(update_combo)
                self.log_to_ui("[+] MODELS SYNCED.")
        except Exception as e:
            self.log_to_ui("[-] UPLINK FAILED: " + str(e))

    # --- ZHIPU AI AUTH (FIXED) ---
    def generate_zhipu_token(self, apikey, exp_seconds):
        try:
            try:
                id, secret = apikey.split(".")
            except ValueError:
                raise Exception("Invalid API Key format")
    
            payload = {
                "api_key": id,
                "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
                "timestamp": int(round(time.time() * 1000)),
            }
    
            return self.jwt_encode(payload, secret, {"alg": "HS256", "sign_type": "SIGN"})
        except Exception as e:
            self.log_to_ui("[-] JWT GENERATION ERROR: " + str(e))
            return None

    def jwt_encode(self, payload, secret, header):
        # Implementacion manual JWT para Jython (no pyjwt)
        # Fix: Ensure strings are consistently handled (unicode vs str)
        def b64url(data):
            # En Jython 2.7, b64encode devuelve str
            if isinstance(data, unicode):
                data = data.encode("utf-8")
            encoded = base64.urlsafe_b64encode(data)
            return encoded.rstrip('=') # Remove padding
            
        header_json = json.dumps(header, separators=(',', ':'))
        payload_json = json.dumps(payload, separators=(',', ':'))
        
        # Force conversion to str (bytes) before b64
        if isinstance(header_json, unicode): header_json = header_json.encode("utf-8")
        if isinstance(payload_json, unicode): payload_json = payload_json.encode("utf-8")
        
        segments = [b64url(header_json), b64url(payload_json)]
        signing_input = ".".join(segments)
        
        # HMAC secret must be bytes (str in py2)
        if isinstance(secret, unicode):
            secret = secret.encode("utf-8")
            
        if isinstance(signing_input, unicode):
            signing_input = signing_input.encode("utf-8")
        
        signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
        segments.append(b64url(signature))
        
        return ".".join(segments)

    def call_ai_api(self, user_content, force_json=True):
        if self.current_provider == "ChatGLM":
            return self.call_zhipu_api(user_content, force_json)
        else:
            return self.call_gemini_api(user_content, force_json)

    def call_zhipu_api(self, user_content, force_json=True):
        api_key = "".join(self.api_key_field.getPassword())
        token = self.generate_zhipu_token(api_key, 3600)
        if not token: return None
        
        model_name = self.model_combo.getSelectedItem()
        if not model_name or "AUTH REQUIRED" in str(model_name): model_name = "glm-4"
        
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        
        system_prompt = self.system_prompt_area.getText()
        if force_json and "No JSON" not in system_prompt: # Slightly loose check
             # Ensure the prompt is very strict if JSON is needed
             system_prompt += " RESPOND ONLY IN RAW TEXT FORMAT WITH 'VECTOR: ' PREFIX."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        # FIX: Ensure temperature is float. GLM might be picky about message format
        payload_data = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.5,
            "top_p": 0.7,
            "stop": None
        }
        
        req = urllib2.Request(url)
        req.add_header('Authorization', 'Bearer ' + token)
        req.add_header('Content-Type', 'application/json')
        
        try:
            # FIX: Zhipu might be slow, increase timeout to 180s/300s
            response = urllib2.urlopen(req, json.dumps(payload_data), timeout=300)
            result = json.loads(response.read())
            # Handle potential error responses from API structure
            if 'error' in result:
                msg = str(result['error'])
                # Try to decode mojibake (utf-8 as latin1)
                try: 
                    msg = result['error']['message'].encode('latin1').decode('utf-8')
                except: pass
                self.log_to_ui("[-] ZHIPU API RETURNED ERROR: " + msg)
                return None
            
            content = result['choices'][0]['message']['content']
            return content
        except urllib2.HTTPError as e:
             self.log_to_ui("[-] ZHIPU HTTP ERROR %d: %s" % (e.code, e.read()))
             return None
        except Exception as e:
             self.log_to_ui("[-] ZHIPU CONN ERROR: " + str(e))
             return None

    def call_gemini_api(self, user_content, force_json=True):
        api_key = "".join(self.api_key_field.getPassword())
        model_name = self.model_combo.getSelectedItem()
        
        if not api_key or "AUTH REQUIRED" in str(model_name):
            self.log_to_ui("[-] ACCESS DENIED: CHECK API KEY/MODEL.")
            return None
            
        url = "https://generativelanguage.googleapis.com/v1beta/models/" + model_name + ":generateContent?key=" + api_key
        system_prompt = self.system_prompt_area.getText() if force_json else "Eres P4IM0nTesting, una IA de ciberseguridad avanzada."
        
        if self.context_file_path:
            try:
                with open(self.context_file_path, 'rb') as f:
                    file_content = f.read().decode('utf-8', 'ignore')
                system_prompt += "\n\n--- [CONTEXT FILE DATA] ---\n" + file_content + "\n---------------------------"
            except Exception as e:
                self.log_to_ui("[-] WARNING: CONTEXT FILE READ ERROR: " + str(e))
        
        payload_data = {"contents": [{"parts": [{"text": system_prompt + "\n\n" + user_content}]}]}
        # FIX: Increase Output Tokens limit & Turn OFF JSON mode to allow stream/raw text
        if force_json: 
            payload_data["generationConfig"] = {
                "maxOutputTokens": 8192
            }
        
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        
        try:
            # FIX: Increase timeout for Gemini too
            response = urllib2.urlopen(req, json.dumps(payload_data), timeout=300)
            result = json.loads(response.read())
            return result['candidates'][0]['content']['parts'][0]['text']
        except urllib2.HTTPError as e:
            self.log_to_ui("[-] HTTP ERROR " + str(e.code) + ": " + e.read())
            return None
        except Exception as e:
            self.log_to_ui("[-] CONNECTION FAILURE: " + str(e))
            return None

    # --- LISTENER PASSIVE SCOUT ---
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if not self.passive_scan_enabled or messageIsRequest:
            return
        resp = messageInfo.getResponse()
        if resp:
            resp_str = self._helpers.bytesToString(resp)
            patterns = {
                "AWS Key": "AKIA[0-9A-Z]{16}",
                "Private Key": "BEGIN RSA PRIVATE KEY",
                "Generic API Key": "api_key['\"]?\\s*[:=]\\s*['\"]?([a-zA-Z0-9]{20,})",
                "Slack Token": "xox[baprs]-([0-9a-zA-Z]{10,48})"
            }
            found = []
            for name, pat in patterns.items():
                if re.search(pat, resp_str):
                    found.append(name)
            if found:
                url = self._helpers.analyzeRequest(messageInfo).getUrl()
                self.log_to_ui("\n[!] PASSIVE SCOUT ALERT: Found %s in %s" % (", ".join(found), str(url)))

    def toggle_passive_scan(self):
        self.passive_scan_enabled = self.passive_toggle.isSelected()
        status = "ON" if self.passive_scan_enabled else "OFF"
        self.log_to_ui("[*] PASSIVE SCOUT MODULE: " + status)

    # --- 403 BYPASS LOGIC ---
    def run_403_bypass_ui(self):
        row = self.logTable.getSelectedRow()
        if row == -1:
            self.log_to_ui("[-] SELECT A 403 REQUEST FROM TABLE FIRST.")
            return
        logEntry = self._log.get(row)
        if logEntry.status != 403:
            self.log_to_ui("[-] TARGET IS NOT 403 (Status: %d). BYPASS SKIPPED." % logEntry.status)
            return
        self.log_to_ui("[*] INITIATING 403 BYPASS PROTOCOL on selected target...")
        t = Thread(target=self.run_403_bypass_worker, args=(logEntry.requestResponse,))
        t.start()
        
    def run_403_bypass_worker(self, baseRequestResponse):
        info = self._helpers.analyzeRequest(baseRequestResponse)
        req_bytes = baseRequestResponse.getRequest()
        headers = list(info.getHeaders())
        body_offset = info.getBodyOffset()
        body = req_bytes[body_offset:]
        service = baseRequestResponse.getHttpService()
        bypass_headers = [
            ("X-Original-URL", "/admin"), ("X-Rewrite-URL", "/admin"),
            ("X-Forwarded-For", "127.0.0.1"), ("X-Forwarded-Host", "127.0.0.1"),
            ("X-Custom-IP-Authorization", "127.0.0.1")
        ]
        for h_name, h_val in bypass_headers:
            new_headers = list(headers)
            new_headers.append(h_name + ": " + h_val)
            new_req = self._helpers.buildHttpMessage(new_headers, body)
            resp = self._callbacks.makeHttpRequest(service, new_req)
            code = self._helpers.analyzeResponse(resp.getResponse()).getStatusCode()
            self.log_to_ui("  -> Trying %s: %s... Status: %d" % (h_name, h_val, code))
            if code == 200:
                self.log_to_ui("[!!!] BYPASS SUCCESSFUL WITH HEADER: %s" % h_name)
                self._lock.acquire()
                r = self._log.size()
                self._log.add(LogEntry(r+1, resp, code, len(resp.getResponse())))
                self.fireTableRowsInserted(r, r)
                self._lock.release()

    # --- PARAM SNIPER ---
    def run_param_sniper(self):
        if not self.currentlyDisplayedItem: return
        req = self.currentlyDisplayedItem.getRequest()
        info = self._helpers.analyzeRequest(req)
        params = info.getParameters()
        out = "--- PARAMETER HEATMAP ---\n"
        for p in params:
            t = p.getType()
            if t == 0: type_s = "URL"
            elif t == 1: type_s = "BODY"
            elif t == 2: type_s = "COOKIE"
            else: type_s = "OTHER"
            name = p.getName()
            risk = "LOW"
            if name in ["id", "file", "path", "cmd", "exec", "user", "role", "admin"]: risk = "CRITICAL"
            out += "[%s] %s (%s) -> RISK: %s\n" % (type_s, name, p.getValue(), risk)
        JOptionPane.showMessageDialog(self.main_panel, out, "PARAM SNIPER SIGHT", JOptionPane.INFORMATION_MESSAGE)

    # --- HTML REPORT (DETAILED) ---
    def generate_html_report(self):
        chooser = JFileChooser()
        chooser.setSelectedFile(File("Cyberpunk_Report.html"))
        if chooser.showSaveDialog(self.main_panel) == JFileChooser.APPROVE_OPTION:
            f = chooser.getSelectedFile()
            
            # Use %% for CSS width
            html = """<html><head><style>
            body { background-color: #0d0d0d; color: #00ff41; font-family: monospace; padding: 20px; }
            h1 { color: #ff0055; border-bottom: 2px solid #ff0055; }
            table { border-collapse: collapse; width: 100%%; margin-bottom: 20px; }
            th, td { border: 1px solid #333; padding: 8px; text-align: left; vertical-align: top; }
            th { background-color: #1a1a1a; color: #ff0055; }
            tr:nth-child(even) { background-color: #111; }
            .high { color: red; font-weight: bold; }
            pre { background-color: #1a1a1a; padding: 10px; border: 1px solid #333; white-space: pre-wrap; word-wrap: break-word; color: #ccc; }
            .section-title { color: #00ffff; font-weight: bold; margin-top: 10px; }
            </style></head><body>
            <h1>P4IM0nTesting MISSION REPORT (DETAILED)</h1>
            <p>Generated: %s</p>
            <table><tr><th>ID</th><th>Status</th><th>Length</th><th>Details (Req/Res)</th></tr>""" % datetime.datetime.now().isoformat()
            
            for i in range(self._log.size()):
                e = self._log.get(i)
                status_class = "high" if e.status == 200 else "normal"
                
                # Extract Request and Response as Strings
                req_str = "No Request Data"
                if e.requestResponse.getRequest():
                    req_str = self._helpers.bytesToString(e.requestResponse.getRequest())
                    # Only show first 1000 chars to keep report sane
                    if len(req_str) > 2000: req_str = req_str[:2000] + "... [TRUNCATED]"
                    
                res_str = "No Response Data"
                if e.requestResponse.getResponse():
                    res_str = self._helpers.bytesToString(e.requestResponse.getResponse())
                    if len(res_str) > 2000: res_str = res_str[:2000] + "... [TRUNCATED]"

                # Sanitize HTML
                req_str = req_str.replace("<", "&lt;").replace(">", "&gt;")
                res_str = res_str.replace("<", "&lt;").replace(">", "&gt;")
                
                detail_cell = """
                <div class="section-title">REQUEST_PAYLOAD:</div>
                <pre>%s</pre>
                <div class="section-title">SERVER_RESPONSE:</div>
                <pre>%s</pre>
                """ % (req_str, res_str)

                html += "<tr><td>%d</td><td class='%s'>%d</td><td>%d</td><td>%s</td></tr>" % (e.id, status_class, e.status, e.length, detail_cell)
            
            html += "</table></body></html>"
            
            try:
                fw = FileWriter(f)
                fw.write(html)
                fw.close()
                self.log_to_ui("[+] DETAILED REPORT EXPORTED TO: " + f.getAbsolutePath())
            except Exception as e:
                self.log_to_ui("[-] REPORT ERROR: " + str(e))

    def select_context_file(self):
        chooser = JFileChooser()
        ret = chooser.showOpenDialog(self.main_panel)
        if ret == JFileChooser.APPROVE_OPTION:
            selected_file = chooser.getSelectedFile()
            self.context_file_path = selected_file.getAbsolutePath()
            self.file_label.setText(" " + selected_file.getName())
            self.log_to_ui("[*] CONTEXT UPLOADED: " + selected_file.getName())
        else:
            self.context_file_path = None
            self.file_label.setText(" No File Loaded")
    def getRowCount(self):
        try: return self._log.size()
        except: return 0
    def getColumnCount(self): return 3
    def getColumnName(self, columnIndex):
        if columnIndex == 0: return "ID"
        if columnIndex == 1: return "STATUS"
        if columnIndex == 2: return "LENGTH"
        return ""
    def getValueAt(self, rowIndex, columnIndex):
        logEntry = self._log.get(rowIndex)
        if columnIndex == 0: return str(logEntry.id)
        if columnIndex == 1: return str(logEntry.status)
        if columnIndex == 2: return str(logEntry.length)
        return ""
    def getTabCaption(self): return "P4IM0nTesting"
    def getUiComponent(self): return self.main_panel
    def createMenuItems(self, invocation):
        menu_list = ArrayList()
        messages = invocation.getSelectedMessages()
        if messages and len(messages) > 0:
            menuItem = JMenuItem(">> P4IM0nTesting: AUTO-EXPLOIT (20 Variants)")
            menuItem.addActionListener(lambda x: self.start_ai_analysis(messages[0]))
            menu_list.add(menuItem)
        return menu_list
    def getHttpService(self): return self.currentlyDisplayedItem.getHttpService() if self.currentlyDisplayedItem else None
    def getRequest(self): return self.currentlyDisplayedItem.getRequest() if self.currentlyDisplayedItem else None
    def getResponse(self): return self.currentlyDisplayedItem.getResponse() if self.currentlyDisplayedItem else None
    def log_to_ui(self, message):
        def update_log():
            self.log_area.append(message + "\n")
            self.log_area.setCaretPosition(self.log_area.getDocument().getLength())
        SwingUtilities.invokeLater(update_log)

    def start_ai_analysis(self, messageInfo):
        self.currentlyDisplayedItem = messageInfo
        self.request_viewer.setMessage(messageInfo.getRequest(), True)
        if messageInfo.getResponse(): self.response_viewer.setMessage(messageInfo.getResponse(), False)
        self._log.clear()
        self.fireTableDataChanged()
        t = Thread(target=self.run_ai_workflow, args=(messageInfo,))
        t.start()
    def start_manual_attack(self):
        text_input = self.manual_input.getText()
        if not text_input: return
        self.log_to_ui("[*] INITIATING MANUAL OVERRIDE SEQUENCE...")
        t = Thread(target=self.run_manual_workflow, args=(text_input,))
        t.start()
    def run_manual_workflow(self, text_input):
        potential_payloads = re.findall(r'[a-zA-Z0-9+/=]{20,}', text_input)
        valid_payloads = []
        for p in potential_payloads: valid_payloads.append(p)
        if not valid_payloads:
            self.log_to_ui("[-] NO VALID B64 PAYLOADS DETECTED IN INPUT.")
            return
        self.log_to_ui("[+] DETECTED %d MANUAL PAYLOADS. EXECUTING..." % len(valid_payloads))
        if not self.currentlyDisplayedItem or not self.currentlyDisplayedItem.getHttpService():
             self.log_to_ui("[-] ERROR: NO TARGET SELECTED. SELECT A REQUEST IN BURP FIRST TO DEFINE TARGET.")
             return
        self.execute_tests(valid_payloads, self.currentlyDisplayedItem.getHttpService())
    def send_manual_chat(self):
        user_text = self.chat_input.getText().strip()
        if not user_text: return
        self.chat_input.setText("")
        self.log_to_ui("\n[USER_OVERRIDE]: " + user_text)
        t = Thread(target=self.process_manual_chat, args=(user_text,))
        t.start()
    def process_manual_chat(self, user_text):
        response = self.call_ai_api(user_text, force_json=False) # UPDATED: Use call_ai_api
        if response:
            self.log_to_ui("[A.I. CORE]: " + response)

    def execute_tests(self, payloads_b64, http_service):
        analysis_data = []
        blocked_count = 0
        for i, b64_req in enumerate(payloads_b64):
            # ADVERSARIAL FUZZING LOGIC
            if i == 5 and blocked_count >= 3:
                 self.log_to_ui("\n[!] WAF DETECTED (High Block Rate). INITIATING ADVERSARIAL EVASION...")
            try:
                mutated_req = base64.b64decode(b64_req)
                new_msg = self._callbacks.makeHttpRequest(http_service, self._helpers.stringToBytes(mutated_req))
                resp_bytes = new_msg.getResponse()
                status_code = 0
                length = 0
                if resp_bytes:
                    resp_info = self._helpers.analyzeResponse(resp_bytes)
                    status_code = resp_info.getStatusCode()
                    length = len(resp_bytes)
                if i < 5 and status_code in [403, 406]: blocked_count += 1
                self._lock.acquire()
                row = self._log.size()
                self._log.add(LogEntry(i+1, new_msg, status_code, length))
                self.fireTableRowsInserted(row, row)
                self._lock.release()
                analysis_data.append("TEST #%d - STATUS: %d - LEN: %d" % (i+1, status_code, length))
            except Exception as e:
                self.log_to_ui("  -> FAILURE IN TEST #%d: %s" % (i+1, str(e)))
        self.log_to_ui("[*] UPLOADING TELEMETRY TO A.I. CORE FOR ANALYSIS...")
        analysis_prompt = "ANALISIS DE RESULTADOS DE ATAQUE:\n" + "\n".join(analysis_data) + "\n\nAnaliza estos resultados. Destaca anomalías (500, tamaños inusuales). Identifica explotación exitosa."
        # Use longer timeout for report generation if needed, though usually fast
        final_analysis = self.call_ai_api(analysis_prompt, force_json=False) 
        if final_analysis:
            self.log_to_ui("\n[+] --- A.I. MISSION REPORT ---")
            self.log_to_ui(final_analysis)

    def run_ai_workflow(self, messageInfo):
        self.log_to_ui("\n[========== AUTO-EXPLOIT SEQUENCE STARTED ==========]")
        http_service = messageInfo.getHttpService()
        raw_request = self._helpers.bytesToString(messageInfo.getRequest())
        prompt = "TARGET ACQUIRED. GENERATE 20 ATTACK VECTORS (BASE64 JSON) FOR:\n\n" + raw_request
        self.log_to_ui("[*] GENERATING ATTACK VECTORS via GEMINI NET...")
        ai_response = self.call_ai_api(prompt, force_json=True) 
        if not ai_response: return
        
        # STREAM-ROBUST PARSING (Line-based Regex)
        # Instead of strict JSON which fails on truncation, we parse lines starting with VECTOR:
        # This allows us to recover 15-18 vectors even if the last one is cut off.
        payloads_b64 = re.findall(r'VECTOR:\s*([a-zA-Z0-9+/=]+)', ai_response)
        
        if not payloads_b64:
             # Fallback to JSON logic just in case the model ignored explicit instructions
             clean_json = ai_response.replace("```json", "").replace("```", "").strip()
             match = re.search(r'\{.*\}', ai_response, re.DOTALL)
             if match: clean_json = match.group(0)
             try:
                 payloads_b64 = json.loads(clean_json).get("payloads", [])
             except Exception as e:
                 self.log_to_ui("[-] PARSING ERROR (NO VECTORS FOUND): " + str(e))
                 self.log_to_ui("[-] RAW (Start): " + clean_json[:100])
                 return

        if not payloads_b64:
             self.log_to_ui("[-] ERROR: NO VALID VECTORS extracted from AI Response.")
             return
            
        self.log_to_ui("[+] %d VECTORS GENERATED. ENGAGING TARGET..." % len(payloads_b64))
        self.execute_tests(payloads_b64, http_service)

# --- AUX CLASSES ---
class Table(JTable):
    def __init__(self, extender):
        self._extender = extender
        self.setModel(extender)
    def changeSelection(self, row, col, toggle, extend):
        logEntry = self._extender._log.get(row)
        self._extender.request_viewer.setMessage(logEntry.requestResponse.getRequest(), True)
        if logEntry.requestResponse.getResponse(): self._extender.response_viewer.setMessage(logEntry.requestResponse.getResponse(), False)
        else: self._extender.response_viewer.setMessage(None, False)
        self._extender.currentlyDisplayedItem = logEntry.requestResponse
        JTable.changeSelection(self, row, col, toggle, extend)
class CustomTable(Table): pass
class LogEntry:
    def __init__(self, id, requestResponse, status, length):
        self.id = id
        self.requestResponse = requestResponse
        self.status = status
        self.length = length
