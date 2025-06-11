import streamlit as st
import os
from dotenv import load_dotenv
from agent import AIAssistant

# Cargar variables de entorno
load_dotenv()

def init_session_state():
    """Inicializa todas las variables de estado de sesión"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False
    
    if "assistant_initialized" not in st.session_state:
        st.session_state.assistant_initialized = False
    
    if "assistant" not in st.session_state:
        st.session_state.assistant = None
    
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
    
    if "processing" not in st.session_state:
        st.session_state.processing = False

def initialize_assistant():
    """Inicializa el asistente de IA"""
    if not st.session_state.assistant_initialized:
        try:
            with st.spinner("🤖 Inicializando asistente de IA..."):
                st.session_state.assistant = AIAssistant()
                st.session_state.assistant_initialized = True
        except Exception as e:
            st.error(f"Error al inicializar el asistente: {str(e)}")
            st.stop()

def display_chat_history():
    """Muestra el historial de chat"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Renderizar LaTeX si está presente
            content = message["content"]
            if "\\(" in content or "$$" in content:
                st.markdown(content, unsafe_allow_html=True)
            else:
                st.markdown(content)

def process_user_input(user_input):
    """Procesa la entrada del usuario"""
    if not st.session_state.assistant:
        st.error("El asistente no está inicializado")
        return None
    
    try:
        response = st.session_state.assistant.chat(user_input)
        
        # Asegurar que la respuesta tenga fuentes si no las tiene
        if "**Fuentes:**" not in response and "Fuentes:" not in response:
            response += "\n\n**Fuentes:**\n- Basado en conocimiento general del curso"
        
        return response
    except Exception as e:
        return f"**Error:** {str(e)}\n\n**Fuentes:**\n- Error en el procesamiento"

def main():
    # Configuración de la página
    st.set_page_config(
        page_title="Asistente IA - Curso TEC",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado para LaTeX y mejor UI
    st.markdown("""
    <style>
    /* Soporte para LaTeX */
    .katex { font-size: 1.1em !important; }
    
    /* Mejorar apariencia del chat */
    .stChatMessage {
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Spinner personalizado */
    .stSpinner > div {
        text-align: center;
        color: #ff6b6b;
    }
    
    /* Mejorar sidebar */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Evitar que el spinner aparezca en el sidebar */
    .css-1kyxreq .stSpinner {
        display: none;
    }
    
    /* Estilos para fuentes */
    .sources-section {
        border-top: 1px solid #333;
        padding-top: 1rem;
        margin-top: 1rem;
        background-color: rgba(0,0,0,0.1);
        border-radius: 5px;
        padding: 1rem;
    }
    </style>
    
    <!-- MathJax para renderizar LaTeX -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
    window.MathJax = {
        tex: {
            inlineMath: [['\\(', '\\)']],
            displayMath: [['$$', '$$']],
            processEscapes: true
        }
    };
    </script>
    """, unsafe_allow_html=True)
    
    # Inicializar estado de sesión PRIMERO
    init_session_state()
    
    # Título principal
    st.title("🤖 Asistente de IA - Curso TEC")
    st.markdown("*Especializado en Inteligencia Artificial*")
    st.markdown("---")
    
    # Sidebar con información
    with st.sidebar:
        st.header("📚 Información del Asistente")
        
        # Verificar API Key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("No se encontró OPENAI_API_KEY")
        else:
            st.success("API Key configurada")
        
        st.markdown("""
        **Capacidades:**
        - 🔍 Búsqueda en apuntes del curso
        - 📖 Consultas en Wikipedia
        - 💬 Memoria de conversación
        - 🎯 Respuestas especializadas en IA
        - 📐 Soporte para fórmulas matemáticas (LaTeX)
        - 📚 Fuentes siempre citadas
        
        **Herramientas disponibles:**
        - `rag_search`: Busca en apuntes del curso
        - `wikipedia_search`: Busca información externa
        """)
        
        st.markdown("---")
        
        # Botón para reiniciar conversación
        if st.button("🔄 Nueva Conversación", type="secondary"):
            st.session_state.messages = []
            if st.session_state.assistant:
                st.session_state.assistant.reset_memory()
            st.session_state.conversation_started = False
            st.session_state.pending_question = None
            st.session_state.processing = False
            st.rerun()
        
        # Estadísticas de la conversación
        if st.session_state.messages:
            user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
            st.metric("Mensajes enviados", user_messages)
        
        st.markdown("---")
        
        # Ejemplos de preguntas
        st.markdown("### 💡 Preguntas de ejemplo:")
        example_questions = [
            "¿Qué es backpropagation?",
            "¿Quién escribió los apuntes de la semana 7?",
            "Explícame el proyecto II",
            "¿Qué es la función sigmoide?",
            "Busca información sobre Geoffrey Hinton en Wikipedia"
        ]
        
        for i, question in enumerate(example_questions):
            if st.button(f"📝 {question}", key=f"example_{i}", disabled=st.session_state.processing):
                # Solo marcar la pregunta como pendiente si no estamos procesando
                if not st.session_state.processing:
                    st.session_state.pending_question = question
                    st.rerun()
    
    # Inicializar asistente
    initialize_assistant()
    
    # Mensaje de bienvenida
    if not st.session_state.conversation_started:
        welcome_message = """
        ¡Hola! 👋 Soy tu asistente especializado en el curso de **Inteligencia Artificial del TEC**.
        
        **¿En qué puedo ayudarte?**
        - 📚 Responder preguntas sobre conceptos del curso
        - 📝 Explicar tareas y proyectos
        - 🔍 Buscar información específica por semana o autor
        - 🌐 Proporcionar información adicional de Wikipedia
        - 📐 Explicar fórmulas matemáticas con notación LaTeX
        
        **Instrucciones:**
        - Haz preguntas específicas sobre el curso
        - Si necesitas información externa, pídeme que busque en Wikipedia
        - Puedo recordar nuestra conversación anterior
        - Las fórmulas matemáticas se mostrarán correctamente
        - Siempre citaré mis fuentes al final de cada respuesta
        
        ¡Pregúntame lo que necesites! 🚀
        
        **Fuentes:**
        - Mensaje de bienvenida del sistema
        """
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": welcome_message
        })
        st.session_state.conversation_started = True
    
    # Mostrar historial de chat
    display_chat_history()
    
    # Procesar pregunta pendiente del sidebar
    if st.session_state.pending_question and not st.session_state.processing:
        user_input = st.session_state.pending_question
        st.session_state.pending_question = None
        st.session_state.processing = True
        
        # Agregar mensaje del usuario al historial
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input
        })
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Procesar y mostrar respuesta del asistente
        with st.chat_message("assistant"):
            # Crear placeholder vacío para evitar "fantasmas"
            message_placeholder = st.empty()
            
            with st.spinner("🤔 Pensando y buscando información..."):
                response = process_user_input(user_input)
            
            if response:
                # Mostrar la respuesta final
                if "\\(" in response or "$$" in response:
                    message_placeholder.markdown(response, unsafe_allow_html=True)
                else:
                    message_placeholder.markdown(response)
                
                # Agregar respuesta al historial
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })
        
        st.session_state.processing = False
        st.rerun()
    
    # Input del usuario - Deshabilitado durante procesamiento
    user_input = st.chat_input("Escribe tu pregunta aquí...", disabled=st.session_state.processing)
    
    # Procesar input del usuario desde el chat
    if user_input and not st.session_state.processing:
        st.session_state.processing = True
        
        # Agregar mensaje del usuario al historial
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input
        })
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Procesar y mostrar respuesta del asistente
        with st.chat_message("assistant"):
            # Crear placeholder vacío para evitar "fantasmas"
            message_placeholder = st.empty()
            
            with st.spinner("🤔 Pensando y buscando información..."):
                response = process_user_input(user_input)
            
            if response:
                # Mostrar la respuesta final
                if "\\(" in response or "$$" in response:
                    message_placeholder.markdown(response, unsafe_allow_html=True)
                else:
                    message_placeholder.markdown(response)
                
                # Agregar respuesta al historial
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })
        
        st.session_state.processing = False
        st.rerun()

if __name__ == "__main__":
    main()