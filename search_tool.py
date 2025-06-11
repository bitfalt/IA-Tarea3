from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import wikipedia

class WikipediaSearchInput(BaseModel):
    """Input para la herramienta Wikipedia"""
    query: str = Field(description="Término a buscar en Wikipedia")
    max_results: int = Field(default=3, description="Número máximo de resultados")

class WikipediaSearchTool(BaseTool):
    """Herramienta para buscar en Wikipedia"""
    
    name: str = "wikipedia_search"
    description: str = """
    Busca información general en Wikipedia.
    Útil para obtener información adicional sobre:
    - Conceptos generales de IA no cubiertos en clase
    - Definiciones de términos técnicos
    - Información histórica o contextual
    - Biografías de investigadores famosos
    Solo usar cuando se solicite explícitamente buscar información externa.
    """
    args_schema: Type[BaseModel] = WikipediaSearchInput
    
    def __init__(self, language: str = "es"):
        super().__init__()
        wikipedia.set_lang(language)
    
    def _run(self, query: str, max_results: int = 3) -> str:
        """Ejecuta la búsqueda en Wikipedia"""
        try:
            # Buscar páginas
            search_results = wikipedia.search(query, results=max_results)
            
            if not search_results:
                return "No se encontraron resultados en Wikipedia."
            
            formatted_results = "**Información de Wikipedia:**\n\n"
            
            for i, title in enumerate(search_results, 1):
                try:
                    summary = wikipedia.summary(title, sentences=2)
                    page = wikipedia.page(title)
                    
                    formatted_results += f"**{i}. {title}**\n"
                    formatted_results += f"Resumen: {summary}\n"
                    formatted_results += f"Leer más: {page.url}\n\n"
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    # Tomar la primera opción si hay ambigüedad
                    try:
                        summary = wikipedia.summary(e.options[0], sentences=2)
                        page = wikipedia.page(e.options[0])
                        formatted_results += f"**{i}. {e.options[0]}**\n"
                        formatted_results += f"Resumen: {summary}\n"
                        formatted_results += f"Leer más: {page.url}\n\n"
                    except:
                        continue
                except:
                    continue
            
            return formatted_results
            
        except Exception as e:
            return f"Error al buscar en Wikipedia: {str(e)}"
    
    async def _arun(self, query: str, max_results: int = 3) -> str:
        """Versión asíncrona"""
        return self._run(query, max_results)