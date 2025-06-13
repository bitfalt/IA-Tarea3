# IA-Tarea3

## Integrantes
- Daniel Garbanzo c.2022117129
- Tomás Granados c.2021579524
- José Pablo Granados c.2022028503

## Descripción del Proyecto

Este proyecto implementa un agente de chat RAG (Retrieval Augmented Generation) utilizando Langchain, OpenAI, FAISS para el almacenamiento de vectores y Streamlit para la interfaz de usuario. El agente puede responder preguntas basándose en el contenido de una colección de documentos PDF y también puede buscar información en Wikipedia.

## Descripción de Archivos y Directorios

- **`.env.example`**: Archivo de ejemplo para las variables de entorno. Debes renombrarlo a `.env` y añadir tu `OPENAI_API_KEY`.
- **`Apuntadores/`**: Contiene los documentos PDF que se utilizan como fuente de conocimiento para el sistema RAG.
- **`agent.py`**: Define la lógica del agente Langchain, incluyendo las herramientas que puede utilizar (RAG sobre documentos y búsqueda en Wikipedia).
- **`app.py`**: Es la aplicación principal de Streamlit. Define la interfaz de usuario con la que se interactúa para chatear con el agente.
- **`manual_metadata.json`**: Archivo JSON que coniene metadatos manuales para los documentos PDF.
- **`rag_tool.py`**: Define la herramienta personalizada que permite al agente realizar búsquedas RAG sobre los documentos PDF indexados.
- **`run_app.py`**: Script de utilidad para ejecutar la aplicación Streamlit. Verifica la existencia del archivo `.env` antes de iniciar.
- **`search_tool.py`**: Define la herramienta personalizada que permite al agente buscar información en Wikipedia.
- **`testing_simple_rag.py`**: Script para realizar pruebas básicas de la funcionalidad RAG, se usó para pruebas iniciales.
- **`vector_creation_and_test.py`**: Script utilizado para crear el almacén de vectores FAISS a partir de los documentos PDF en `Apuntadores/` y para probar su funcionamiento.
- **`vector_store/`**: Directorio donde se almacena el índice FAISS (`index.faiss`) y los metadatos asociados (`index.pkl`) después de procesar los documentos PDF.

## Administrador de Paquetes

Este proyecto utiliza [Poetry](https://python-poetry.org/) para la gestión de dependencias.

## Cómo Ejecutar el Proyecto

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd IA-Tarea3
    ```

2.  **Instalar Poetry:**
    Si aún no tienes Poetry instalado, sigue las instrucciones en la [documentación oficial de Poetry](https://python-poetry.org/docs/#installation).

3.  **Configurar el entorno y las dependencias:**
    Poetry creará un entorno virtual y instalará las dependencias especificadas en `pyproject.toml`.
    ```bash
    poetry install
    ```

4.  **Configurar las variables de entorno:**
    Copia el archivo `.env.example` a `.env` y añade tu clave de API de OpenAI.
    ```bash
    cp .env.example .env
    ```
    Luego, edita `.env` y añade tu `OPENAI_API_KEY`:
    ```
    OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ```

5.  **Crear el almacén de vectores (si es la primera vez):**
    Ejecuta el script para procesar los PDFs y crear el índice FAISS. Esto solo es necesario la primera vez o si los documentos en `Apuntadores/` cambian.
    ```bash
    poetry run python vector_creation_and_test.py
    ```

6.  **Ejecutar la aplicación Streamlit:**
    Puedes ejecutar la aplicación usando el script `run_app.py`:
    ```bash
    poetry run python run_app.py
    ```
    O directamente con Streamlit:
    ```bash
    poetry run streamlit run app.py
    ```
    La aplicación estará disponible en `http://localhost:8501`.
