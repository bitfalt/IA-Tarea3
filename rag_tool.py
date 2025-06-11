from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

class RAGSearchInput(BaseModel):
    """Input para la herramienta RAG"""
    query: str = Field(description="Consulta para buscar en los apuntes del curso")
    k: int = Field(default=5, description="Número de resultados a devolver")

class RAGSearchTool(BaseTool):
    """Herramienta para buscar en los apuntes del curso usando RAG"""
    
    name: str = "rag_search"
    description: str = """
    Busca información en los apuntes del curso de Inteligencia Artificial.
    Útil para responder preguntas sobre:
    - Conceptos vistos en clase (regresión, redes neuronales, etc.)
    - Información de tareas y proyectos
    - Contenido específico de alguna semana
    - Información sobre autores de los apuntes
    - Cualquier tema cubierto en el curso
    """
    vector_store: FAISS = None
    args_schema: Type[BaseModel] = RAGSearchInput
    
    def __init__(self):
        super().__init__()
        self.vector_store = self._load_vector_store()
    
    def _load_vector_store(self):
        """Carga el vector store existente"""
        try:
            directory = os.path.dirname(os.path.abspath(__file__))
            persist_dir = os.path.join(directory, "vector_store")
            
            if not os.path.exists(persist_dir):
                raise FileNotFoundError("Vector store not found. Please run the RAG setup first.")
            
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            return FAISS.load_local(persist_dir, embeddings, allow_dangerous_deserialization=True)
        
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return None
    
    def _run(self, query: str, k: int = 5) -> str:
        """Ejecuta la búsqueda RAG"""
        if not self.vector_store:
            return "Error: No se pudo cargar la base de datos de apuntes."
        
        try:
            # Realizar búsqueda
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            if not results:
                return "No se encontró información relevante en los apuntes del curso."
            
            # Formatear resultados
            formatted_results = "📚 **Información encontrada en los apuntes:**\n\n"
            
            for i, (doc, score) in enumerate(results, 1):
                metadata = doc.metadata
                formatted_results += f"**Resultado {i}:**\n"
                formatted_results += f"- **Semana:** {metadata.get('semana', 'N/A')}\n"
                formatted_results += f"- **Autor:** {metadata.get('autor', 'N/A')}\n"
                formatted_results += f"- **Fecha:** {metadata.get('fecha', 'N/A')}\n"
                formatted_results += f"- **Archivo:** {metadata.get('filename', 'N/A')}\n"
                formatted_results += f"- **Contenido:** {doc.page_content[:300]}...\n\n"
            
            return formatted_results
            
        except Exception as e:
            return f"Error al buscar en los apuntes: {str(e)}"
    
    async def _arun(self, query: str, k: int = 5) -> str:
        """Versión asíncrona"""
        return self._run(query, k)