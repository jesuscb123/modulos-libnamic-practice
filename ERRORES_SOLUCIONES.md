# 🛠️ Registro de Errores y Soluciones

Este documento recopila los errores históricos encontrados durante el desarrollo de los distintos módulos, así como las soluciones implementadas para resolverlos. Es una base de conocimiento para evitar repetir los mismos fallos en el futuro.

## 📌 NIVEL 2: Gestión de Préstamos (`asset_lending`)

### 1. Menús invisibles y Error 403 (Permisos de Superadmin)
**El Síntoma:** Instalaste el módulo perfectamente, pero en el menú lateral solo salía la palabra "Assets" y no podías desplegar los submenús (Recursos, Préstamos, etc.).
**La Causa:** En el framework declarativo (YAML) y en los decoradores `@exposed_action` de Python, habíamos dado permiso explícito a `asset_lending_group_reader` y `manager`. Como tú estabas logueado con un usuario "Superadmin" (`core_group_superadmin`), el sistema aplicó una seguridad estricta: "Si no estás en la lista exacta, te lo oculto".
**La Solución:** Añadimos `- core_group_superadmin` a la lista de `allowed_group_ext_ids` en los archivos `menu.yml` y a los decoradores de los servicios (`services/lending.py`), permitiendo que el administrador global tuviera acceso total a la UI y a las acciones de la API.

### 2. El "Pantallazo HTML" y la explosión del Formato de Fecha
**El Síntoma:** Al intentar guardar un Préstamo, la pantalla devolvió un error de `same-origin fallback returned HTML` y el log del backend mostraba `DatetimeFieldOverflow: date/time field value out of range: "15/06/2026"`.
**La Causa:** El frontend (tu navegador en español) estaba enviando la fecha límite en formato europeo (DD/MM/YYYY). PostgreSQL y SQLAlchemy esperaban el estándar internacional ISO (YYYY-MM-DD). Al leer "15" como mes, la base de datos explotaba.
**La Solución:** Aplicamos el patrón de "Interceptación" en la función `create()` del servicio. Antes de guardar, atrapamos el campo `due_at`, usamos `datetime.strptime()` para convertir ese texto español en un objeto de fecha real de Python con zona horaria UTC, y luego dejamos que el ORM lo guardase correctamente.

---

## 🧪 NIVEL 3: Moderación de Feedback (`feedback_moderation`)

### 3. Pytest se pierde buscando el código (ModuleNotFoundError)
**El Síntoma:** Al lanzar nuestro primer comando de pruebas unitarias, Pytest abortó inmediatamente quejándose de que `No module named 'app'`.
**La Causa:** Al ejecutar `pytest ruta/al/archivo` directamente, la herramienta limitó su visión a esa carpeta. No era capaz de ver la raíz del proyecto (`/opt/licium`) donde viven las herramientas del framework (`app.core`).
**La Solución:** Cambiamos la forma de invocarlo utilizando `python -m pytest ...`. Esto forzó al intérprete de Python a añadir el directorio raíz a su radar (el PYTHONPATH) antes de ejecutar nada, encontrando así todas las dependencias.

### 4. El fantasma de la Base de Datos (fixture 'db_session' not found)
**El Síntoma:** Los tests empezaron a correr, pero todos fallaron instantáneamente pidiendo un fixture llamado `db_session` que no existía en el framework.
**La Causa:** Intentamos hacer "Tests de Integración" (conectándonos a una base de datos de pruebas real), pero no conocíamos la configuración interna de testing del framework Licium.
**La Solución:** Pivotamos hacia una arquitectura de Tests Unitarios Puros. Usamos la librería nativa `unittest.mock` (con `MagicMock` y `@patch`) para crear una base de datos "falsa" en la memoria RAM. Aislamos nuestro código engañando al sistema para probar exclusivamente nuestra lógica de negocio, sin depender del estado del servidor.

### 5. El colapso del ORM con las Relaciones M2M (Multiple classes found for path "Tag")
**El Síntoma:** Pytest empezó a fallar con errores muy crípticos de SQLAlchemy como `ArgumentError: Error creating backref` y diciendo que había múltiples clases `Tag` en el registro.
**La Causa:** Durante los tests, Pytest escanea e importa los archivos varias veces. Nuestra relación Many-to-Many usaba un `backref="suggestions"` que inyectaba código dinámicamente. Al leerse dos veces, SQLAlchemy intentaba inyectar la misma propiedad dos veces y entraba en pánico (colisión de metadatos).
**La Solución:** Simplificamos drásticamente la relación en el modelo `Suggestion`. Eliminamos la "magia negra" del `backref`/`back_populates` (ya que a nivel de negocio no necesitábamos consultar las sugerencias desde la etiqueta) y usamos una ruta de importación estricta y absoluta como `String` (`"modules.feedback_moderation.models.feedback.Tag"`). Esto estabilizó la memoria de SQLAlchemy haciéndolo 100% compatible con los escaneos de Pytest.
