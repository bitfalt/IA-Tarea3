from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from rag_tool import RAGSearchTool
from search_tool import WikipediaSearchTool
from dotenv import load_dotenv
import os

load_dotenv()

class AIAssistant:
    """Asistente de IA para el curso de Inteligencia Artificial"""
    
    def __init__(self):
        # Inicializar LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=1000
        )
        
        # Inicializar herramientas
        self.tools = [
            RAGSearchTool(),
            WikipediaSearchTool()
        ]
        
        # Crear prompt del sistema
        self.system_prompt = self._create_system_prompt()
        
        # Inicializar memoria
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5  # Recordar últimas 5 interacciones
        )
        
        # Crear agente
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.system_prompt
        )
        
        # Crear executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate"
        )
        
        print("Asistente de IA inicializado correctamente!")
        print("Herramientas disponibles:")
        for tool in self.tools:
            print(f"  - {tool.name}: {tool.description.split('.')[0]}")
    
    def _create_system_prompt(self):
        """Crea el prompt del sistema"""
        template = """
        Eres un asistente especializado en el curso de Inteligencia Artificial del TEC. Tu objetivo es ayudar a los estudiantes con sus consultas sobre el curso.

        INSTRUCCIONES IMPORTANTES:
        1. **PRIORIDAD**: Siempre busca PRIMERO en los apuntes del curso usando 'rag_search'
        2. **Wikipedia**: Solo usa 'wikipedia_search' cuando el usuario EXPLÍCITAMENTE pida buscar información externa o cuando no encuentres la respuesta en los apuntes
        3. **Respuestas**: Sé preciso, educativo y cita las fuentes (semana, autor, archivo)
        4. **Contexto**: Recuerda el contexto de conversaciones anteriores

        5. **MATEMÁTICAS - REGLAS ESTRICTAS PARA LaTeX**:
        - Para fórmulas matemáticas SIEMPRE usa LaTeX
        - Fórmulas en línea: \\( fórmula \\) (con espacios antes y después)
        - Fórmulas centradas: $$ fórmula $$
        - NUNCA mezcles LaTeX con texto sin espacios
        - EJEMPLOS CORRECTOS:
            * "La función sigmoide es \\( \\sigma(x) = \\frac{{1}}{{1 + e^{{-x}}}} \\)"
            * "Su derivada es \\( \\sigma'(x) = \\sigma(x)(1 - \\sigma(x)) \\)"
            * "La función ReLU se define como \\( \\text{{ReLU}}(x) = \\max(0, x) \\)"
        - EJEMPLOS INCORRECTOS:
            * "Su derivada es ( \\sigma'(x) = \\sigma(x)(1 - \\sigma(x)) )"
            * "ReLU(x) = max(0,x)"(debe ser LaTeX)

        6. **FORMATO DE FUENTES OBLIGATORIO**: 
        - SIEMPRE termina tu respuesta con una sección de fuentes
        - Usa EXACTAMENTE este formato:
        
        **Fuentes:**
        - Semana X, Autor: [Nombre del Autor], Archivo: [nombre_archivo.pdf]
        - Semana Y, Autor: [Nombre del Autor], Archivo: [nombre_archivo.pdf]
        
        - Si usas Wikipedia, agrega: Wikipedia: [Título del artículo]
        - Si no encuentras fuentes específicas, indica: "Basado en conocimiento general del curso"

        CAPACIDADES:
        - Responder preguntas sobre conceptos del curso
        - Explicar tareas y proyectos
        - Buscar información por semana, autor o tema
        - Proporcionar información adicional de Wikipedia cuando se solicite
        - Mostrar fórmulas matemáticas correctamente con LaTeX

        TEMAS DEL CURSO:
        - Regresión lineal y logística
        - Redes neuronales y backpropagation
        - Redes convolucionales (CNN)
        - Proyectos y tareas del curso
        - Conceptos de machine learning

        ESTRUCTURA DE RESPUESTA:
        1. Respuesta principal (clara y educativa)
        2. Explicaciones técnicas (SIEMPRE con LaTeX para matemáticas)
        3. Ejemplos o aplicaciones (si es relevante)
        4. **Fuentes:** (OBLIGATORIO - siempre al final)

        REGLAS PARA MATEMÁTICAS:
        - Variables: \\( x \\), \\( y \\), \\( z \\)
        - Funciones: \\( f(x) \\), \\( \\sigma(x) \\), \\( \\text{{ReLU}}(x) \\)
        - Ecuaciones: \\( y = mx + b \\)
        - Derivadas: \\( \\frac{{dy}}{{dx}} \\)
        - Integrales: \\( \\int f(x) dx \\)
        - Operadores: \\( \\max \\), \\( \\min \\), \\( \\sum \\)

        Responde de manera clara y educativa. Si no encuentras información en los apuntes, menciona que puedes buscar en Wikipedia si el usuario lo desea.

        {chat_history}

        Usuario: {input}
        {agent_scratchpad}
        """
        
        return ChatPromptTemplate.from_template(template)
    
    def chat(self, message: str) -> str:
        """Procesa un mensaje del usuario"""
        try:
            response = self.agent_executor.invoke({"input": message})
            return response["output"]
        except Exception as e:
            return f"Lo siento, ocurrió un error: {str(e)}"
    
    def reset_memory(self):
        """Reinicia la memoria de conversación"""
        self.memory.clear()
        print("Memoria de conversación reiniciada")

def test_agent():
    """Función para probar el agente"""
    assistant = AIAssistant()
    
    # Pruebas
    test_cases = [
        "¿Qué es backpropagation?",
        "¿Quién escribió los apuntes de la semana 7?",
        "Explícame el proyecto II",
        "Busca información en Wikipedia sobre Geoffrey Hinton",
        "¿Qué es la función sigmoide?"
    ]
    
    print("\n" + "="*60)
    print("PROBANDO EL ASISTENTE DE IA")
    print("="*60)
    
    for i, test_query in enumerate(test_cases, 1):
        print(f"\n🔍 Prueba {i}: {test_query}")
        print("-" * 50)
        
        response = assistant.chat(test_query)
        print(f"🤖 Respuesta: {response}")
        print("\n" + "="*60)

if __name__ == "__main__":
    test_agent()