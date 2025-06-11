import wikipedia
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class WikiResult:
    """Resultado de búsqueda en Wikipedia"""
    title: str
    summary: str
    url: str

class WikipediaSearchTool:
    """Herramienta simple para buscar en Wikipedia"""
    
    def __init__(self, language: str = "es"):
        """
        Inicializar herramienta de Wikipedia
        
        Args:
            language: Idioma para las búsquedas ("es" para español, "en" para inglés)
        """
        wikipedia.set_lang(language)
        self.language = language
        print(f"Wikipedia Search Tool initialized (Language: {language})")
    
    def search(self, query: str, max_results: int = 3) -> List[WikiResult]:
        """
        Busca en Wikipedia
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            Lista de WikiResult
        """
        try:
            print(f"Searching Wikipedia for: '{query}'")
            
            # Buscar páginas relacionadas
            search_results = wikipedia.search(query, results=max_results)
            
            if not search_results:
                return []
            
            results = []
            for title in search_results:
                try:
                    # Obtener resumen de la página
                    summary = wikipedia.summary(title, sentences=3)
                    page = wikipedia.page(title)
                    
                    result = WikiResult(
                        title=title,
                        summary=summary,
                        url=page.url
                    )
                    results.append(result)
                    
                except wikipedia.exceptions.DisambiguationError as e:
                    # Si hay ambigüedad, tomar la primera opción
                    try:
                        summary = wikipedia.summary(e.options[0], sentences=3)
                        page = wikipedia.page(e.options[0])
                        result = WikiResult(
                            title=e.options[0],
                            summary=summary,
                            url=page.url
                        )
                        results.append(result)
                    except:
                        continue
                        
                except wikipedia.exceptions.PageError:
                    # Página no encontrada, continuar
                    continue
                except:
                    # Cualquier otro error, continuar
                    continue
            
            return results
            
        except Exception as e:
            print(f"Error searching Wikipedia: {e}")
            return []
    
    def get_page_content(self, title: str, sentences: int = 5) -> Optional[str]:
        """
        Obtiene el contenido completo de una página específica
        
        Args:
            title: Título de la página
            sentences: Número de oraciones del resumen
            
        Returns:
            Contenido de la página o None si no se encuentra
        """
        try:
            return wikipedia.summary(title, sentences=sentences)
        except:
            return None
    
    def format_results(self, results: List[WikiResult]) -> str:
        """Formatea los resultados para mostrar"""
        if not results:
            return "No se encontraron resultados en Wikipedia."
        
        formatted = "**Resultados de Wikipedia:**\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"**{i}. {result.title}**\n"
            formatted += f"{result.summary}\n"
            formatted += f"[Ver más...]({result.url})\n\n"        
        return formatted
    
    def search_ai_topics(self, query: str) -> List[WikiResult]:
        """Búsqueda específica para temas de IA"""
        ai_terms = [
            f"{query} inteligencia artificial",
            f"{query} machine learning",
            f"{query} aprendizaje automático"
        ]
        
        all_results = []
        for term in ai_terms:
            results = self.search(term, max_results=2)
            all_results.extend(results)
        
        # Eliminar duplicados por título
        unique_results = []
        seen_titles = set()
        for result in all_results:
            if result.title not in seen_titles:
                unique_results.append(result)
                seen_titles.add(result.title)
        
        return unique_results[:5]  # Máximo 5 resultados únicos

def test_wikipedia_search():
    """Función para probar la herramienta"""
    # Probar en español
    wiki_es = WikipediaSearchTool("es")
    
    test_queries = [
        "inteligencia artificial",
        "redes neuronales",
        "machine learning",
        "OpenAI"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Probando: {query}")
        print('='*50)
        
        results = wiki_es.search(query, max_results=2)
        formatted = wiki_es.format_results(results)
        print(formatted)

if __name__ == "__main__":
    test_wikipedia_search()