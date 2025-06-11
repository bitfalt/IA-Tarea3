import os
import re
import json
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

def load_manual_metadata():
    """Carga metadata manual desde archivo JSON"""
    json_file = os.path.join(os.path.dirname(__file__), "manual_metadata.json")
    
    if not os.path.exists(json_file):
        # Crear archivo JSON básico si no existe
        default_data = {
            "manual_metadata": {
                "9_SEMANA_AI_250424_1.pdf": {
                    "autor": "Marco Rivera Serrano",
                    "semana": 9,
                    "fecha": "2025-04-24"
                }
            }
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        
        print(f"Created manual metadata file: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("manual_metadata", {})
    except Exception as e:
        print(f"Error loading manual metadata: {e}")
        return {}

def extract_filename_metadata(filename):
    """Extrae semana, fecha y parte del nombre del archivo"""
    basename = os.path.basename(filename)
    
    # Patrón principal para capturar: número_semana_AI_fecha_parte
    pattern = r'(\d+)_[Ss]emana_(?:AI|IA|Al)_(\d{6,8})_?(\d+)?'
    match = re.search(pattern, basename, re.IGNORECASE)
    
    metadata = {'filename': basename, 'file_path': filename}
    
    if match:
        semana = int(match.group(1))
        fecha_str = match.group(2)
        parte = int(match.group(3)) if match.group(3) else 1
        
        try:
            # Manejar diferentes formatos de fecha
            if len(fecha_str) == 8:
                fecha = datetime.strptime(fecha_str, "%Y%m%d")
            else:
                fecha = datetime.strptime(f"20{fecha_str}", "%Y%m%d")
            
            metadata.update({
                'semana': semana,
                'fecha': fecha.strftime("%Y-%m-%d"),
                'parte': parte
            })
        except ValueError:
            pass
    
    return metadata

def extract_author_from_content(text):
    """Extrae el autor del contenido del documento"""
    # Normalizar texto básico
    text = text.replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã­', 'í')
    text = text.replace('Ã³', 'ó').replace('Ãº', 'ú').replace('Ã±', 'ñ')
    
    # Patrones para encontrar nombres de autor
    patterns = [
        r'Apuntes\s+Semana\s+\d+[^\n]*\n\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})',
        r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3}),?\s*(\d{10})',
        r'(?:Autor|Author)[:\s]+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){1,3})',
    ]
    
    # Buscar en los primeros 1000 caracteres
    search_text = text[:1000]
    
    for pattern in patterns:
        matches = re.findall(pattern, search_text, re.MULTILINE)
        for match in matches:
            if isinstance(match, tuple):
                author_name = match[0].strip()
            else:
                author_name = match.strip()
            
            if is_valid_name(author_name):
                return correct_name(author_name)
    
    return None

def is_valid_name(name):
    """Verifica si el texto es realmente un nombre de persona"""
    if not name or len(name) < 5:
        return False
    
    # Palabras que NO son nombres
    invalid_words = [
        'abstract', 'resumen', 'introducción', 'noticias', 'aprendizaje',
        'inteligencia artificial', 'redes neuronales', 'proyecto', 'semana'
    ]
    
    name_lower = name.lower()
    for invalid in invalid_words:
        if invalid in name_lower:
            return False
    
    # Debe tener al menos 2 palabras y empezar con mayúscula
    words = name.split()
    if len(words) < 2:
        return False
    
    return all(word[0].isupper() for word in words) and not name.isupper()

def correct_name(name):
    """Corrige nombres cortados o con caracteres especiales"""
    corrections = {
        "Kenneth Chac": "Kenneth Chacón",
        "Jose Carlos Uma": "José Carlos Umaña",
        "Victoria Sand": "Victoria Sandí",
        "Daniel Garbanzo": "Daniel Alonso Garbanzo",
        "Perez Picado Esteban": "Pérez Picado Esteban",
        "Jose Pablo Granados": "José Pablo Granados",
        "Deylan Sandoval Sanchez": "Deylan Sandoval Sánchez",
        "Rayforth Brenes Rodriguez": "Rayforth Brenes Rodríguez",
        "Jose Ignacio Calder": "José Ignacio Calderón",
        "Pamela Gonza": "Pamela González",
        "Jeremy Chac": "Jeremy Chacón",
        "Luis Carlos": "Luis Carlos Solano",
        "Mariana  Ferna": "Mariana Fernández",
    }
    
    return corrections.get(name, name)

def process_document(file_path, manual_metadata):
    """Procesa un documento PDF y extrae toda su metadata"""
    basename = os.path.basename(file_path)
    
    # Cargar el PDF
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    if not documents:
        return None, f"No content extracted from {basename}"
    
    # Extraer metadata del nombre del archivo
    metadata = extract_filename_metadata(file_path)
    
    # Verificar si hay metadata manual
    if basename in manual_metadata:
        metadata.update(manual_metadata[basename])
        print(f"  Using manual metadata for {basename}")
    else:
        # Intentar extraer autor del contenido
        author = extract_author_from_content(documents[0].page_content)
        if author:
            metadata['autor'] = author
            print(f"  Found author: {author}")
        else:
            metadata['autor'] = f"Autor no identificado - {basename}"
    
    # Agregar metadata a todos los documentos
    for i, doc in enumerate(documents):
        doc.metadata.update(metadata)
        doc.metadata['page_number'] = i + 1
        doc.metadata['total_pages'] = len(documents)
    
    return documents, None

def create_vector_store():
    """Crea el vector store con todos los documentos procesados"""
    directory = os.path.dirname(os.path.abspath(__file__))
    pdf_dir = os.path.join(directory, "Apuntadores")
    persist_dir = os.path.join(directory, "vector_store")
    
    # Cargar metadata manual
    manual_metadata = load_manual_metadata()
    
    # Verificar si ya existe el vector store
    if os.path.exists(persist_dir):
        print("Loading existing vector store...")
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        return FAISS.load_local(persist_dir, embeddings, allow_dangerous_deserialization=True)
    
    print("Creating new vector store...")
    
    # Procesar todos los PDFs
    file_paths = [os.path.join(pdf_dir, fn) for fn in os.listdir(pdf_dir) if fn.endswith('.pdf')]
    all_documents = []
    
    print(f"Found {len(file_paths)} PDF files to process")
    
    for file_path in file_paths:
        basename = os.path.basename(file_path)
        print(f"Processing: {basename}")
        
        try:
            documents, error = process_document(file_path, manual_metadata)
            
            if error:
                print(f"  Warning: {error}")
                continue
            
            all_documents.extend(documents)
            
            # Mostrar resumen de metadata
            metadata = documents[0].metadata
            print(f"  - Semana: {metadata.get('semana', 'N/A')}")
            print(f"  - Autor: {metadata.get('autor', 'N/A')}")
            print(f"  - Fecha: {metadata.get('fecha', 'N/A')}")
            
        except Exception as e:
            print(f"  Error processing {basename}: {str(e)}")
            continue
    
    # Dividir documentos en chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " "]
    )
    
    split_documents = text_splitter.split_documents(all_documents)
    print(f"Total documents after splitting: {len(split_documents)}")
    
    # Crear y guardar vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_documents(split_documents, embeddings)
    vector_store.save_local(persist_dir)
    
    print(f"Vector store created with {len(split_documents)} documents")
    return vector_store

def search_documents(vector_store, query, k=5):
    """Busca documentos similares a la consulta"""
    results = vector_store.similarity_search_with_score(query, k=k)
    
    print(f"\nQuery: {query}")
    print("=" * 60)
    
    for i, (doc, score) in enumerate(results):
        print(f"\nResult {i+1} (Score: {score:.4f})")
        print(f"Semana: {doc.metadata.get('semana', 'N/A')}")
        print(f"Autor: {doc.metadata.get('autor', 'N/A')}")
        print(f"Fecha: {doc.metadata.get('fecha', 'N/A')}")
        print(f"Archivo: {doc.metadata.get('filename', 'N/A')}")
        print(f"Página: {doc.metadata.get('page_number', 'N/A')}")
        print(f"Content: {doc.page_content[:200]}...")
        print("-" * 40)

if __name__ == "__main__":
    # Crear vector store
    vector_store = create_vector_store()
    
    # Probar búsquedas
    test_queries = [
        "Kenneth Chacón",
        "backpropagation",
        "proyecto II",
        "regresión logística"
    ]
    
    for query in test_queries:
        search_documents(vector_store, query, k=3)