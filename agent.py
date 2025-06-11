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

CAPACIDADES:
- Responder preguntas sobre conceptos del curso
- Explicar tareas y proyectos
- Buscar información por semana, autor o tema
- Proporcionar información adicional de Wikipedia cuando se solicite

TEMAS DEL CURSO:
- Regresión lineal y logística
- Redes neuronales y backpropagation
- Redes convolucionales (CNN)
- Proyectos y tareas del curso
- Conceptos de machine learning

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