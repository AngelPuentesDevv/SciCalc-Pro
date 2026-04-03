# SCICALC PRO - Documentacion Tecnica Integral

- Version: 4.0
- Fecha: 09 de Marzo de 2026
- Autores: Puentes Angel, Bonilla Santiago, Patino Kevin
- ODS: 4 - Educacion de Calidad
- Arquitectura: Hexagonal (Puertos y Adaptadores)
- Paradigma: Offline-First
- Stack: React Native (Frontend), Python/FastAPI (Backend), SQLite + PostgreSQL (Persistencia)

---

# DOCUMENTO 1: PRD (Product Requirements Document)

## 1.1 Vision del Producto

SciCalc Pro es una aplicacion movil nativa de calculadora cientifica de alta precision disenada bajo el paradigma Offline-First. El producto esta dirigido a ingenieros, cientificos, estudiantes de STEM y profesionales que requieren una herramienta de calculo confiable en entornos con conectividad limitada o inexistente. La aplicacion se alinea con el ODS 4 (Educacion de Calidad) al proveer una herramienta educativa gratuita y accesible que democratiza el acceso a calculos cientificos avanzados.

La estrategia Offline-First implica que el 100% de las funcionalidades de calculo, conversion de unidades, historial y memoria operan sobre una base de datos SQLite local cifrada con AES-256. La sincronizacion con PostgreSQL en el servidor es oportunista: ocurre unicamente cuando el dispositivo detecta conectividad, empleando una estrategia de Last Write Wins (LWW) con vectores de version por registro.

## 1.2 Problema y Justificacion

Los profesionales de ingenieria y ciencias frecuentemente trabajan en campo (obras civiles, laboratorios remotos, zonas rurales) donde la conectividad es intermitente o nula. Las calculadoras cientificas fisicas carecen de historial persistente, sincronizacion entre dispositivos y capacidad de respaldo. Las aplicaciones existentes en el mercado dependen de conexion a internet para funcionalidades basicas o no ofrecen precision arbitraria. SciCalc Pro resuelve esta brecha ofreciendo precision de punto flotante arbitraria (mediante mpmath) con operacion 100% offline.

## 1.3 KPIs Tecnicos Detallados

| KPI | Metrica Objetivo | Herramienta de Medicion |
|-----|-----------------|------------------------|
| Precision de punto flotante | Tasa de error relativo menor a 10 elevado a -10 | Suite de pruebas mpmath vs. Wolfram Alpha |
| Latencia P95 de calculo | Menor a 50ms para operaciones estandar | k6 / Artillery + metricas internas |
| Latencia P95 de sincronizacion | Menor a 2s para batch de 100 registros | JMeter / Lighthouse |
| Cobertura de codigo (Backend) | Mayor a 90% (Lineas y Branches) | pytest-cov + SonarQube |
| Cobertura de codigo (Frontend) | Mayor a 80% | Jest + SonarQube |
| Rating SonarQube | 'A' en Reliability, Security, Maintainability | SonarQube Server |
| Tamano del APK/IPA | Menor a 25 MB | Android Studio / Xcode Analyzer |
| Consumo de bateria | Menor a 2% por hora de uso continuo | Android Battery Historian / Instruments |
| Tasa de crashes | Menor a 0.1% de sesiones | Firebase Crashlytics |
| MTTR (Mean Time To Recovery) | Menor a 4 horas | Jira + monitoreo de incidentes |

## 1.4 Usuarios Objetivo

| Persona | Descripcion | Necesidad Principal |
|---------|------------|-------------------|
| Ingeniero de Campo | Trabaja en obras civiles, plantas industriales | Calculos offline con historial persistente |
| Estudiante de Ingenieria | Estudia calculo, fisica, algebra lineal | Funciones trigonometricas, notacion cientifica, precision |
| Investigador Cientifico | Requiere precision arbitraria | mpmath con mas de 10 decimales, funciones especiales |
| Contador/Financiero | Calculos rapidos con memoria | Historial auditable, funciones de memoria M+/M- |

## 1.5 Roadmap del Producto

### 1.5.1 MVP (Meses 1 a 3)

Motor matematico offline con operaciones aritmeticas basicas y funciones trigonometricas. Persistencia local en SQLite con cifrado AES-256. Interfaz basica en React Native con modo estandar y cientifico. Autenticacion JWT para el backend FastAPI. Historial local de las ultimas 50 operaciones. 7 pruebas unitarias minimas en el backend. Analisis estatico con SonarQube.

### 1.5.2 Fase 2: Expansion (Meses 4 a 6)

Conversor de unidades completo (Longitud, Masa, Temperatura, Volumen, Velocidad). Funciones de memoria (M+, M-, MR, MC). Edicion de expresiones con cursor. Modo Oscuro/Claro adaptativo. Notacion cientifica automatica. Sincronizacion SQLite a PostgreSQL con LWW. Pruebas funcionales automatizadas con Cypress. Pruebas de rendimiento con k6 y Lighthouse.

### 1.5.3 Fase 3: Escalado (Meses 7 a 12)

Precision arbitraria via mpmath expuesta como microservicio. Funciones avanzadas: matrices, integrales numericas, raices de polinomios. Sistema de respaldo y restauracion (.json/.bak). Ayuda y FAQ offline integrada. Control de acceso biometrico/PIN. Ofuscacion de codigo (ProGuard/R8). Despliegue en servidores en linea. Cobertura de codigo mayor a 90%.

---

# DOCUMENTO 2: ERS - Especificacion de Requisitos de Software (IEEE 830)

## 2.1 Introduccion

### 2.1.1 Proposito

Este documento especifica los requisitos funcionales y no funcionales del sistema SciCalc Pro conforme al estandar IEEE 830-1998. Esta dirigido al equipo de desarrollo, al equipo de QA, y a los stakeholders del proyecto. Sirve como contrato tecnico para la implementacion.

### 2.1.2 Alcance

SciCalc Pro es una aplicacion movil nativa (Android 10+ / iOS 15+) con backend en Python/FastAPI que provee calculos matematicos de alta precision en modo offline. La persistencia hibrida (SQLite local + PostgreSQL servidor) permite sincronizacion oportunista. La arquitectura sigue el patron Hexagonal (Puertos y Adaptadores) para maxima testabilidad.

### 2.1.3 Definiciones y Acronimos

| Termino | Definicion |
|---------|-----------|
| LWW | Last Write Wins - Estrategia de resolucion de conflictos de sincronizacion |
| JWT | JSON Web Token - Estandar de autenticacion stateless |
| CRUD | Create, Read, Update, Delete - Operaciones basicas de persistencia |
| mpmath | Libreria Python de aritmetica de punto flotante con precision arbitraria |
| DEG/RAD | Grados/Radianes - Modos de entrada angular |
| P95 | Percentil 95 - Metrica de latencia donde el 95% de las peticiones estan por debajo |
| AES-256 | Advanced Encryption Standard con clave de 256 bits |
| Regex | Expresiones Regulares - Patrones de validacion de entrada de datos |

## 2.2 Descripcion General del Sistema

### 2.2.1 Perspectiva del Producto

SciCalc Pro opera como un sistema autonomo en el dispositivo movil con un backend complementario. En modo offline, todas las funcionalidades de calculo, historial y memoria estan disponibles sin degradacion. El backend FastAPI gestiona la autenticacion JWT, los CRUDs de persistencia en PostgreSQL y la sincronizacion bidireccional de datos.

### 2.2.2 Restricciones de Diseno

La arquitectura debe seguir estrictamente el patron Hexagonal. La logica de dominio (motor matematico, parser, lexer) no puede tener dependencias directas de frameworks, bases de datos o interfaces de usuario. Toda comunicacion entre capas se realiza mediante Puertos (interfaces abstractas) e implementaciones concretas (Adaptadores). Todas las entradas de datos del usuario deben ser validadas mediante expresiones regulares antes de procesarse.

## 2.3 Requerimientos Funcionales del Motor Matematico Offline

### RF-001: Operaciones Aritmeticas Basicas

- Codigo: RF-001
- Actor: Usuario General
- Descripcion IEEE 830: El sistema debera permitir al usuario realizar operaciones de suma, resta, multiplicacion y division con numeros enteros y decimales. El sistema debe validar la entrada mediante Regex (patron: ^-?\d+(\.\d+)?([eE][+-]?\d+)?$) para prevenir inyeccion de caracteres invalidos. La division por cero debe retornar un objeto de error tipado, no una excepcion no controlada.
- Criterios de Aceptacion: El resultado se muestra en menos de 50ms (P95). La division por cero muestra "Error: Division por cero". La validacion Regex rechaza entradas como "abc", "12..5", o "" (vacio).
- Historia de Usuario: Como estudiante, quiero realizar sumas y restas rapidas validadas para resolver problemas cotidianos con confianza en la entrada.

### RF-002: Funciones Trigonometricas

- Codigo: RF-002
- Actor: Usuario General / Estudiante de Ingenieria
- Descripcion IEEE 830: El sistema debera proveer funciones sin, cos, tan y sus inversas (asin, acos, atan). La entrada angular se valida con Regex segun el modo: DEG (^-?\d+(\.\d+)?$ rango 0-360) o RAD (^-?\d+(\.\d+)?$ rango 0-2pi). El motor matematico interno utiliza mpmath con precision configurable (minimo 15 digitos decimales) para garantizar que sin(90 grados) = 1.0 exacto.
- Criterios de Aceptacion: sin(90) en modo DEG retorna 1.0000000000 (10 decimales). El usuario alterna DEG/RAD mediante un toggle visible. tan(90 grados) muestra "Indefinido".
- Historia de Usuario: Como ingeniero, quiero calcular el coseno de un angulo en radianes con precision arbitraria para mis calculos de fisica.

### RF-003: Historial de Operaciones

- Codigo: RF-003
- Actor: Usuario General
- Descripcion IEEE 830: El sistema debera registrar y almacenar las ultimas 50 operaciones en SQLite local con cifrado AES-256. Cada registro incluye: id (UUID v4), expression (string), result (string), precision_digits (int), created_at (ISO 8601 timestamp), is_deleted (boolean para borrado logico), sync_version (int para LWW). El historial es recuperable y cada item puede reutilizarse en una nueva operacion.
- Criterios de Aceptacion: Al deslizar hacia abajo se muestra la lista paginada. Al tocar un item, el valor se copia al campo de entrada. El borrado es logico (is_deleted = true), no fisico.

### RF-004: Funciones de Memoria (M+, M-, MR, MC)

- Codigo: RF-004
- Actor: Usuario General
- Descripcion IEEE 830: El sistema debera disponer de funciones M+, M-, MR y MC. El valor en memoria persiste en SQLite aunque se borre la pantalla (AC). La memoria se valida con Regex antes de almacenar para prevenir corrupcion de datos.
- Criterios de Aceptacion: Guardar un numero muestra indicador "M". MR recupera el valor exacto almacenado en la precision configurada.

### RF-005: Conversor de Unidades

- Codigo: RF-005
- Actor: Usuario General
- Descripcion IEEE 830: El sistema debera incluir un modulo de conversion entre unidades de Longitud, Masa, Temperatura, Volumen y Velocidad. La conversion se realiza en tiempo real con validacion Regex de la entrada numerica. Los factores de conversion estan definidos como constantes inmutables en el dominio.
- Criterios de Aceptacion: 1000 metros se convierte a 1 km. 0 grados Celsius se convierte a 32 grados Fahrenheit. Conversion en menos de 50ms.

### RF-006: Edicion de Expresiones con Cursor

- Codigo: RF-006
- Actor: Usuario General
- Descripcion IEEE 830: El sistema debera permitir al usuario posicionar un cursor dentro de la expresion matematica para editar sin borrar toda la operacion. El parser/lexer del motor matematico debe re-evaluar la expresion completa tras cada edicion.
- Criterios de Aceptacion: El cursor es visible y parpadea. Se puede cambiar "150+20" a "150-20" tocando entre el 0 y el +.

### RF-007: Modo Oscuro/Claro

- Codigo: RF-007
- Actor: Usuario General
- Descripcion IEEE 830: El sistema debera adaptar su interfaz segun la configuracion del SO o seleccion manual del usuario. El contraste debe cumplir WCAG 2.1 AA (ratio minimo 4.5:1 para texto normal).
- Criterios de Aceptacion: El modo oscuro se activa desde ajustes en maximo 2 toques. El contraste texto/fondo cumple ratio 4.5:1 en ambos modos. El tema persiste entre sesiones.
- Historia de Usuario: Como usuario, quiero alternar entre modo oscuro y claro para reducir la fatiga visual segun las condiciones de iluminacion del entorno.

### RF-008: Notacion Cientifica

- Codigo: RF-008
- Actor: Investigador Cientifico / Estudiante de Ingenieria
- Descripcion IEEE 830: El sistema debera formatear automaticamente resultados extremadamente grandes (mayores a 10 elevado a 12) o pequenos (menores a 10 elevado a -12) en notacion cientifica. El usuario puede ingresar numeros con la tecla EXP. La validacion Regex del formato de entrada cientifica es: ^-?\d+(\.\d+)?[eE][+-]?\d+$
- Criterios de Aceptacion: El resultado 1500000000000 se muestra como 1.5e12. La tecla EXP permite ingresar el exponente directamente. Entradas invalidas tipo "1.5e" son rechazadas por Regex.
- Historia de Usuario: Como investigador cientifico, quiero ver resultados muy grandes o muy pequenos en notacion cientifica para interpretar rapidamente el orden de magnitud.

## 2.4 CRUDs Obligatorios del Backend (FastAPI + PostgreSQL)

El backend expone al menos 7 CRUDs completos con borrado logico (campo is_deleted: boolean). Todos los endpoints requieren autenticacion JWT valida. Todas las entradas se validan con Regex y Pydantic validators.

### CRUD 1: Usuarios

- Entidad: User
- Campos principales: id, email, password_hash, display_name, created_at, is_deleted
- Reglas de negocio: Email validado con Regex RFC 5322. Password minimo 8 caracteres, 1 mayuscula, 1 numero.

### CRUD 2: Perfiles

- Entidad: Profile
- Campos principales: id, user_id (FK), avatar_url, preferred_precision, angle_mode, theme, is_deleted
- Reglas de negocio: preferred_precision entre 2 y 50 decimales. angle_mode acepta DEG o RAD.

### CRUD 3: Historial

- Entidad: CalculationHistory
- Campos principales: id (UUID), user_id (FK), expression, result, precision_digits, created_at, is_deleted, sync_version
- Reglas de negocio: Maximo 50 registros activos por usuario. FIFO automatico.

### CRUD 4: Preferencias

- Entidad: UserPreference
- Campos principales: id, user_id (FK), key, value, updated_at, is_deleted
- Reglas de negocio: key validada con Regex ^[a-zA-Z_]{3,50}$. value maximo 500 caracteres.

### CRUD 5: Conversiones Favoritas

- Entidad: FavoriteConversion
- Campos principales: id, user_id (FK), from_unit, to_unit, category, is_deleted
- Reglas de negocio: category acepta LENGTH, MASS, TEMP, VOLUME o SPEED.

### CRUD 6: Sesiones

- Entidad: Session
- Campos principales: id, user_id (FK), device_id, jwt_token_hash, expires_at, is_active, is_deleted
- Reglas de negocio: Expiracion automatica. Maximo 5 sesiones activas.

### CRUD 7: Registros de Sincronizacion

- Entidad: SyncLog
- Campos principales: id, user_id (FK), entity_type, entity_id, action, sync_status, conflict_resolution, timestamp, is_deleted
- Reglas de negocio: Registro de cada operacion de sincronizacion para auditoria.

## 2.5 Requerimientos No Funcionales

### RNF-001: Rendimiento (Latencia)

El sistema debera mostrar el resultado de cualquier operacion matematica estandar en un tiempo no mayor a 50ms (P95) despues de que el usuario presione el boton de igualdad. Para operaciones de precision arbitraria (mayor a 15 digitos), el limite se extiende a 200ms (P95). Las pruebas de rendimiento se ejecutan con k6 y Artillery.

### RNF-002: Disponibilidad Offline

El 100% de las funcionalidades de calculo, conversion, historial y memoria operan sin conexion a internet. La sincronizacion es oportunista y no bloquea la interfaz de usuario.

### RNF-003: Usabilidad

Los botones del teclado numerico y operadores basicos ocupan minimo el 60% de la pantalla. Tamano minimo de target tactil: 48x48dp. Maximo 2 toques para acceder a funciones cientificas.

### RNF-004: Portabilidad

Compatible con Android 10.0+ e iOS 15.0+. Dispositivos de referencia: iPhone 8, Samsung Galaxy S20. El framework React Native garantiza un unico codigo base para ambas plataformas.

### RNF-005: Fiabilidad y Precision

El motor matematico utiliza aritmetica de doble precision (64-bit IEEE 754) por defecto, con la opcion de precision arbitraria via mpmath. La tasa de error relativo debe ser menor a 10 elevado a -10 para todas las funciones trigonometricas, logaritmicas y exponenciales. La validacion se realiza contra valores de referencia de Wolfram Alpha.

### RNF-006: Seguridad

Cero recoleccion de datos personales. SQLite local cifrado con AES-256 (usando SQLCipher). Autenticacion JWT con tokens de acceso (15 min TTL) y refresh tokens (7 dias TTL). Todas las contrasenas se almacenan como hash bcrypt con salt de 12 rondas. Validacion obligatoria con Regex en todas las entradas del backend.

### RNF-007: Mantenibilidad

Arquitectura Hexagonal (Puertos y Adaptadores) con separacion estricta entre dominio, aplicacion e infraestructura. Cobertura de codigo mayor a 90% en backend. Rating 'A' en SonarQube para Reliability, Security y Maintainability. Codigo estructurado segun MVVM en el frontend React Native.

### RNF-008: Consumo de Recursos

Consumo de bateria menor a 2% por hora de uso continuo. CPU en reposo cercana a 0%. Tamano de la aplicacion menor a 25 MB.

## 2.6 Requerimientos de Seguridad (ISO 27001)

### RNF-SEC-001: Control de Acceso Biometrico/PIN

Autenticacion biometrica o PIN de 4 digitos configurable para acceder al historial. Bloqueo tras 3 intentos fallidos.

### RNF-SEC-002: Cifrado de Datos en Reposo

SQLite cifrado con AES-256 via SQLCipher. Datos ilegibles sin la clave de descifrado.

### RNF-SEC-003: Ofuscacion de Codigo

Codigo compilado ofuscado con ProGuard (Android) y R8. Nombres de clases y metodos no legibles tras descompilar.

### RNF-SEC-004: Borrado Seguro

Sobrescritura fisica del espacio de memoria al borrar historial. Irrecuperable por herramientas forenses.

### RNF-SEC-005: Proteccion contra Capturas

FLAG_SECURE en Android bloquea screenshots en pantalla de historial seguro.

### RNF-SEC-006: Verificacion de Integridad

Verificacion de firma digital al inicio. Si el APK fue modificado, la app se cierra.

### RNF-SEC-007: Gestion de Sesion Inactiva

Re-autenticacion tras 5 minutos de inactividad si el bloqueo esta activo.

## 2.7 Requerimientos de Soporte (ITIL)

### RNF-SUP-001: Registro de Incidentes

Log local rotativo con errores criticos, advertencias y excepciones con timestamp ISO 8601.

### RNF-SUP-002: Exportacion de Diagnostico

Funcion para empaquetar logs (sin datos personales) en .zip y enviar a soporte.

### RNF-SUP-003: Ayuda Offline

Seccion FAQ accesible sin conexion con documentacion de todas las funciones.

### RNF-SUP-004: Monitoreo de Capacidad

Alerta si el historial excede 50MB o 10% del almacenamiento libre.

### RNF-SUP-005: Respaldo y Restauracion

Exportacion manual del historial a .json/.bak para restauracion post-reinstalacion.

### RNF-SUP-006: Notificacion de Versiones

Numero SemVer visible. Notificacion de version obsoleta cuando hay conectividad.

### RNF-SUP-007: Restablecimiento de Fabrica

Restauracion de ajustes predeterminados sin borrar historial (salvo seleccion explicita).

---

# DOCUMENTO 3: RFC - Estrategia de Sincronizacion SQLite a PostgreSQL

## 3.1 Resumen Ejecutivo

Este RFC propone la estrategia de sincronizacion bidireccional entre la base de datos local SQLite (dispositivo movil, cifrada con SQLCipher/AES-256) y la base de datos centralizada PostgreSQL (servidor FastAPI). La estrategia esta disenada para un entorno Offline-First donde la conectividad es intermitente y la integridad de datos es critica.

## 3.2 Contexto y Motivacion

Los usuarios de SciCalc Pro trabajan en entornos de conectividad variable. El dispositivo movil es la fuente primaria de datos; el servidor PostgreSQL es la fuente de respaldo y sincronizacion multi-dispositivo. La arquitectura debe garantizar que ningun dato se pierda incluso en condiciones adversas (desconexiones abruptas, conflictos de edicion concurrente desde multiples dispositivos).

## 3.3 Estrategia Propuesta: Last Write Wins (LWW) con Vectores de Version

### 3.3.1 Modelo de Datos de Sincronizacion

Cada entidad sincronizable incluye los siguientes campos de metadatos de sincronizacion:

| Campo | Tipo | Descripcion |
|-------|------|------------|
| id | UUID v4 | Identificador unico global generado en el cliente |
| sync_version | INTEGER | Contador monotonico incrementado en cada modificacion local |
| updated_at | TIMESTAMP (ISO 8601) | Marca temporal de la ultima modificacion con precision de milisegundos |
| device_id | VARCHAR(64) | Unico por dispositivo, generado en la primera instalacion |
| is_deleted | BOOLEAN | Borrado logico. Los registros borrados se sincronizan como tombstones |
| server_version | INTEGER | Version asignada por el servidor al confirmar la sincronizacion |
| conflict_resolved | BOOLEAN | Indica si el registro fue resultado de resolucion de conflicto |

### 3.3.2 Flujo de Sincronizacion

El flujo de sincronizacion sigue un protocolo de tres fases:

Fase 1 - Deteccion de Conectividad: La aplicacion React Native monitorea el estado de red mediante NetInfo. Cuando se detecta conectividad Wi-Fi o celular, se inicia el proceso de sincronizacion en background sin bloquear la UI.

Fase 2 - Push (Cliente hacia Servidor): El cliente envia al endpoint POST /api/v1/sync/push un batch de registros modificados localmente (donde sync_version es mayor a server_version). El payload se valida con Regex y Pydantic en el servidor. El servidor compara sync_version: si el server_version actual es menor, acepta el cambio (LWW). Si hay conflicto (mismo entity_id con server_version mayor o igual al sync_version del cliente), el servidor aplica LWW basado en updated_at (el timestamp mas reciente gana). El conflicto se registra en SyncLog.

Fase 3 - Pull (Servidor hacia Cliente): Tras el push exitoso, el cliente llama a GET /api/v1/sync/pull?since={last_server_version} para obtener todos los registros modificados en el servidor desde la ultima sincronizacion. Esto incluye cambios de otros dispositivos y resoluciones de conflicto.

### 3.3.3 Resolucion de Conflictos

| Escenario | Resolucion | Accion |
|-----------|-----------|--------|
| Cliente y servidor modificaron el mismo registro | LWW por updated_at | El timestamp mas reciente prevalece. El perdedor se archiva en SyncLog. |
| Cliente borro un registro que el servidor modifico | El borrado prevalece (Delete Wins) | El registro se marca como tombstone en ambos lados. |
| Dos dispositivos crearon registros con mismo UUID | Improbable con UUID v4. Si ocurre: LWW por updated_at | Se genera alerta en SyncLog para auditoria. |
| Desconexion durante sincronizacion | Retry con backoff exponencial | El batch no confirmado se reintenta en la proxima conexion. |

### 3.3.4 Implementacion Tecnica en Python/FastAPI

ORM y Driver: SQLAlchemy 2.0+ como ORM con asyncpg como driver asincronico para PostgreSQL. En el cliente movil, la persistencia local usa react-native-sqlite-storage con SQLCipher. Los modelos SQLAlchemy definen tanto el esquema de PostgreSQL como la estructura esperada de SQLite.

Endpoints FastAPI: POST /api/v1/sync/push (autenticado con JWT) recibe un array de ChangeSets validados con Pydantic. Cada ChangeSet incluye entity_type, entity_id, action (CREATE, UPDATE o DELETE), payload (JSON), sync_version, updated_at y device_id. GET /api/v1/sync/pull?since={version} retorna los cambios del servidor posteriores a la version indicada, paginados en batches de 100 registros.

Validacion con Regex: Todos los campos del ChangeSet se validan. entity_type con ^[a-zA-Z_]{3,50}$. entity_id con ^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$ (UUID v4). device_id con ^[a-zA-Z0-9_-]{8,64}$.

### 3.3.5 Manejo de Baja Conectividad

El sistema implementa las siguientes estrategias para condiciones de red adversas:

1. Cola de sincronizacion persistente en SQLite que acumula cambios pendientes.
2. Compresion gzip del payload de sincronizacion para minimizar el ancho de banda.
3. Timeout configurable (default 10s) con retry automatico usando backoff exponencial (1s, 2s, 4s, 8s, maximo 5 reintentos).
4. Sincronizacion parcial: si un batch falla, los registros exitosos se confirman y los fallidos se reencolan.
5. Delta sync: solo se envian campos modificados, no el registro completo.

## 3.4 Esquema de Base de Datos para Sincronizacion

La siguiente tabla PostgreSQL almacena el log de sincronizacion:

```sql
CREATE TABLE sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('CREATE','UPDATE','DELETE')),
    client_version INTEGER NOT NULL,
    server_version INTEGER NOT NULL DEFAULT 0,
    device_id VARCHAR(64) NOT NULL,
    payload JSONB,
    conflict_detected BOOLEAN DEFAULT FALSE,
    conflict_resolution VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);
```

## 3.5 Riesgos y Mitigaciones

| Riesgo | Probabilidad | Mitigacion |
|--------|-------------|-----------|
| Perdida de datos por conflicto no detectado | Baja | SyncLog completo con auditoria. Tests de conflictos en CI/CD. |
| Drift temporal entre cliente y servidor | Media | Uso de server_version (monotonico) en lugar de clocks del cliente para ordenamiento. |
| Sobrecarga del servidor por sincronizacion masiva | Media | Rate limiting por usuario (100 req/min). Paginacion de batches. |
| SQLCipher ralentiza operaciones locales | Baja | Benchmark en dispositivos de referencia. Page size optimizado (4096 bytes). |

---

# DOCUMENTO 4: Design Specs - Especificaciones de Diseno

## 4.1 Arquitectura Hexagonal: Relaciones de Objetos

El flujo de datos sigue la direccion: UI Component -> Input Adapter -> UseCase -> Domain Engine (Parser/Lexer) -> Output Adapter. Cada capa se comunica exclusivamente a traves de Puertos (interfaces abstractas definidas en el dominio). Los adaptadores implementan estos puertos y son inyectados mediante Dependency Injection.

### 4.1.1 Flujo Detallado de una Operacion de Calculo

Paso 1 - UI Component (React Native): El usuario ingresa la expresion "sin(45)" y presiona "=". El componente CalculatorScreen captura el evento onPress y construye un CalculationRequest DTO.

Paso 2 - Input Adapter (REST Controller / Local Bridge): El adaptador de entrada valida la expresion con Regex (^[0-9a-zA-Z+\-*/^().sincotaglexpqrt\s]+$) para prevenir inyeccion. Transforma el DTO externo en un comando de dominio EvaluateExpressionCommand.

Paso 3 - UseCase (Application Layer): El caso de uso EvaluateExpressionUseCase orquesta la logica: invoca al Puerto CalculationEnginePort con la expresion parseada y al Puerto HistoryRepositoryPort para persistir el resultado.

Paso 4 - Domain Engine (Parser/Lexer): El Lexer tokeniza la expresion en tokens: [FUNC('sin'), LPAREN, NUMBER(45), RPAREN]. El Parser construye un AST (Abstract Syntax Tree). El Evaluator recorre el AST y ejecuta el calculo usando mpmath.sin(mpmath.radians(45)) si el modo es DEG, o mpmath.sin(45) si es RAD. La precision se configura via mpmath.mp.dps = precision_digits.

Paso 5 - Output Adapter (SQLite / PostgreSQL): El adaptador de salida implementa HistoryRepositoryPort. En modo offline, persiste en SQLite cifrado. En modo online, adicionalmente encola el registro para sincronizacion con PostgreSQL.

## 4.2 Estructura de Carpetas - Arquitectura Hexagonal

```
scicalc-pro/
|
|-- backend/                              [Python/FastAPI]
|   |-- src/
|   |   |-- domain/                       [Nucleo de negocio - SIN dependencias externas]
|   |   |   |-- entities/
|   |   |   |   |-- calculation.py        [Entidad Calculation]
|   |   |   |   |-- user.py              [Entidad User]
|   |   |   |   |-- profile.py           [Entidad Profile]
|   |   |   |   |-- sync_record.py       [Entidad SyncRecord]
|   |   |   |
|   |   |   |-- value_objects/
|   |   |   |   |-- expression.py        [VO: Expresion matematica validada]
|   |   |   |   |-- precision.py         [VO: Nivel de precision, 2-50 digitos]
|   |   |   |   |-- angle_mode.py        [VO: DEG o RAD]
|   |   |   |
|   |   |   |-- ports/                   [Interfaces abstractas - ABC]
|   |   |   |   |-- input/
|   |   |   |   |   |-- calculation_engine_port.py
|   |   |   |   |   |-- unit_converter_port.py
|   |   |   |   |
|   |   |   |   |-- output/
|   |   |   |       |-- history_repository_port.py
|   |   |   |       |-- user_repository_port.py
|   |   |   |       |-- sync_repository_port.py
|   |   |   |
|   |   |   |-- engine/                  [Motor matematico puro]
|   |   |   |   |-- lexer.py             [Tokenizador]
|   |   |   |   |-- parser.py            [Construye AST]
|   |   |   |   |-- evaluator.py         [Recorre AST con mpmath]
|   |   |   |   |-- tokens.py            [Definicion de tokens]
|   |   |   |
|   |   |   |-- exceptions/
|   |   |       |-- domain_exceptions.py
|   |   |       |-- validation_errors.py
|   |   |
|   |   |-- application/                 [Casos de uso - orquestacion]
|   |   |   |-- use_cases/
|   |   |   |   |-- evaluate_expression.py
|   |   |   |   |-- manage_history.py
|   |   |   |   |-- manage_user.py
|   |   |   |   |-- sync_data.py
|   |   |   |   |-- convert_units.py
|   |   |   |
|   |   |   |-- dtos/
|   |   |   |   |-- calculation_request.py
|   |   |   |   |-- calculation_response.py
|   |   |   |   |-- sync_changeset.py
|   |   |   |
|   |   |   |-- validators/
|   |   |       |-- regex_validators.py  [Patrones Regex centralizados]
|   |   |
|   |   |-- infrastructure/              [Adaptadores concretos]
|   |   |   |-- adapters/
|   |   |   |   |-- input/
|   |   |   |   |   |-- fastapi_router.py    [REST Controllers]
|   |   |   |   |   |-- auth_middleware.py   [JWT Middleware]
|   |   |   |   |
|   |   |   |   |-- output/
|   |   |   |       |-- postgres_history_repo.py
|   |   |   |       |-- postgres_user_repo.py
|   |   |   |       |-- postgres_sync_repo.py
|   |   |   |
|   |   |   |-- persistence/
|   |   |   |   |-- models/              [SQLAlchemy Models]
|   |   |   |   |-- migrations/          [Alembic migrations]
|   |   |   |   |-- database.py          [Engine + Session Factory]
|   |   |   |
|   |   |   |-- security/
|   |   |       |-- jwt_handler.py
|   |   |       |-- password_hasher.py   [bcrypt]
|   |   |
|   |   |-- main.py                      [FastAPI app bootstrap]
|   |
|   |-- tests/
|   |   |-- unit/                        [7 o mas pruebas unitarias]
|   |   |-- integration/
|   |   |-- e2e/
|   |
|   |-- pyproject.toml
|   |-- Dockerfile
|
|-- frontend/                            [React Native]
|   |-- src/
|   |   |-- screens/
|   |   |-- components/
|   |   |-- hooks/
|   |   |-- services/
|   |   |-- store/                       [Estado global - Zustand/Redux]
|   |   |-- database/                    [SQLite local + SQLCipher]
|   |   |-- sync/                        [Logica de sincronizacion]
|   |   |-- utils/
|   |
|   |-- __tests__/
|   |-- package.json
|
|-- docs/
|   |-- PRD.md
|   |-- ERS.md
|   |-- RFC_SYNC.md
|   |-- DESIGN_SPECS.md
|
|-- sonar-project.properties
|-- docker-compose.yml
|-- README.md
```

## 4.3 Esquema de Tablas - PostgreSQL

```sql
-- ==============================================
-- ESQUEMA POSTGRESQL: SciCalc Pro
-- ==============================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);
-- Regex validacion email: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    avatar_url VARCHAR(500),
    preferred_precision INTEGER DEFAULT 10
        CHECK (preferred_precision BETWEEN 2 AND 50),
    angle_mode VARCHAR(3) DEFAULT 'DEG'
        CHECK (angle_mode IN ('DEG', 'RAD')),
    theme VARCHAR(5) DEFAULT 'LIGHT'
        CHECK (theme IN ('LIGHT', 'DARK')),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE calculation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    expression TEXT NOT NULL,
    result TEXT NOT NULL,
    precision_digits INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE,
    sync_version INTEGER DEFAULT 0,
    device_id VARCHAR(64)
);

CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    key VARCHAR(50) NOT NULL,
    value VARCHAR(500),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id, key)
);
-- Regex validacion key: ^[a-zA-Z_]{3,50}$

CREATE TABLE favorite_conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    from_unit VARCHAR(30) NOT NULL,
    to_unit VARCHAR(30) NOT NULL,
    category VARCHAR(10) NOT NULL
        CHECK (category IN ('LENGTH','MASS','TEMP','VOLUME','SPEED')),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    device_id VARCHAR(64) NOT NULL,
    jwt_token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(10) NOT NULL
        CHECK (action IN ('CREATE','UPDATE','DELETE')),
    client_version INTEGER NOT NULL,
    server_version INTEGER NOT NULL DEFAULT 0,
    device_id VARCHAR(64) NOT NULL,
    payload JSONB,
    conflict_detected BOOLEAN DEFAULT FALSE,
    conflict_resolution VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

-- INDICES
CREATE INDEX idx_history_user ON calculation_history(user_id, created_at DESC);
CREATE INDEX idx_history_sync ON calculation_history(sync_version);
CREATE INDEX idx_sync_log_user ON sync_log(user_id, created_at DESC);
CREATE INDEX idx_sessions_user ON sessions(user_id, is_active);
CREATE INDEX idx_preferences_user ON user_preferences(user_id, key);
```

## 4.4 Esquema SQLite Local (Cifrado con SQLCipher/AES-256)

El esquema SQLite replica la estructura de PostgreSQL para las entidades sincronizables (calculation_history, user_preferences, favorite_conversions) con campos adicionales de metadatos de sincronizacion. Las tablas de autenticacion (users, sessions) NO se replican localmente; la autenticacion offline se gestiona mediante un token JWT cacheado con TTL extendido.

```sql
-- SQLite Local (cifrado con SQLCipher)
PRAGMA key = 'AES-256-key-derivada-de-usuario';
PRAGMA cipher_page_size = 4096;

CREATE TABLE local_calculation_history (
    id TEXT PRIMARY KEY,                -- UUID v4 como TEXT
    expression TEXT NOT NULL,
    result TEXT NOT NULL,
    precision_digits INTEGER DEFAULT 10,
    created_at TEXT NOT NULL,            -- ISO 8601
    is_deleted INTEGER DEFAULT 0,       -- SQLite no tiene BOOLEAN
    sync_version INTEGER DEFAULT 0,
    server_version INTEGER DEFAULT 0,   -- Ultima version confirmada por servidor
    needs_sync INTEGER DEFAULT 1        -- 1 = pendiente de sincronizacion
);

CREATE TABLE local_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    action TEXT NOT NULL,
    payload TEXT NOT NULL,               -- JSON serializado
    retry_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);
```

## 4.5 Integracion de mpmath en Flujo Asincrono

La libreria mpmath es una biblioteca Python BSD de aritmetica de punto flotante con precision arbitraria, actualmente en version 1.4.0. Provee soporte extensivo para funciones trascendentes, evaluacion de sumas, integrales, limites y raices. La precision se controla mediante mp.dps (decimal places).

Dado que mpmath es CPU-bound y no asincrono nativamente, la integracion con FastAPI (que es async) requiere delegar los calculos a un ThreadPoolExecutor o ProcessPoolExecutor para no bloquear el event loop:

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor
from mpmath import mp, mpf, sin, cos, tan, log, exp, sqrt, pi

executor = ProcessPoolExecutor(max_workers=4)

def _compute_expression(expression: str, precision: int) -> str:
    """Ejecutar calculo en proceso separado (CPU-bound)."""
    mp.dps = precision  # Configurar precision decimal
    # El parser/evaluator del dominio procesa la expresion
    # y retorna el resultado como string con la precision solicitada
    result = evaluate_ast(parse(tokenize(expression)))
    return mp.nstr(result, precision)

async def compute_async(expression: str, precision: int = 15) -> str:
    """Wrapper asincrono para calculos CPU-bound."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor, _compute_expression, expression, precision
    )
```

Para operaciones estandar (precision menor o igual a 15 digitos), el calculo se realiza directamente con float nativo de Python (IEEE 754 doble precision) para maximizar la velocidad (menor a 50ms P95). Para precision extendida (mayor a 15 digitos), se activa mpmath automaticamente, con un limite de latencia extendido a 200ms P95. Esta logica de seleccion reside en el UseCase EvaluateExpressionUseCase.

## 4.6 Validacion con Expresiones Regulares (Catalogo)

| Campo | Patron Regex | Ejemplo Valido | Ejemplo Invalido |
|-------|-------------|---------------|-----------------|
| Email | ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ | user@mail.com | user@@mail |
| Password | ^(?=.*[A-Z])(?=.*\d).{8,}$ | Passw0rd! | pass |
| Numero decimal | ^-?\d+(\.\d+)?$ | -3.14 | 12..5 |
| Notacion cientifica | ^-?\d+(\.\d+)?[eE][+-]?\d+$ | 1.5e10 | 1.5e |
| UUID v4 | ^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$ | 550e8400-e29b-41d4-a716-446655440000 | not-a-uuid |
| Preference key | ^[a-zA-Z_]{3,50}$ | dark_mode | a |
| Device ID | ^[a-zA-Z0-9_-]{8,64}$ | device_abc_123 | d |
| Expresion matematica | ^[0-9a-zA-Z+\-*/^().\s]+$ | sin(45)+cos(30) | rm -rf / |
| Unidad de medida | ^[a-zA-Z/]{1,20}$ | km/h | (vacio) |

## 4.7 UI/UX: Especificaciones de Diseno Visual

### 4.7.1 Targets Tactiles

Todos los botones interactivos tienen un tamano minimo de 48x48dp (density-independent pixels) conforme a las guias de Material Design y Apple HIG. El area de toque efectiva puede exceder el area visual del boton para mejorar la accesibilidad. El espacio minimo entre targets adyacentes es de 8dp.

### 4.7.2 Distribucion de Pantalla

| Area | Porcentaje de Pantalla | Descripcion |
|------|----------------------|------------|
| Display de resultado | 15 a 20% | Muestra expresion actual y resultado con scroll horizontal |
| Teclado numerico + operadores | 60 a 65% | Botones grandes para minimizar errores de pulsacion |
| Barra de funciones cientificas | 15 a 20% | Accesible con maximo 2 toques. Toggle DEG/RAD visible |
| Barra de estado/navegacion | 5% | Indicador de memoria (M), modo, conectividad |

### 4.7.3 Adaptabilidad de Pantalla

La interfaz se adapta a diferentes tamanos de pantalla mediante un sistema de proporciones relativas. En tablets (mayor a 600dp de ancho), el layout cambia a dos columnas: teclado a la izquierda, historial a la derecha. En telefonos pequenos (menor a 360dp), las funciones cientificas se acceden mediante un drawer deslizable. La orientacion landscape activa automaticamente el modo cientifico extendido con mas funciones visibles.

## 4.8 Matriz de Riesgos (COBIT - APO12 Gestionar el Riesgo)

La siguiente matriz se alinea con el proceso APO12 de COBIT 2019, que establece el marco de gestion de riesgos TI. Las probabilidades e impactos se clasifican en escala 1-5. El nivel de riesgo residual orienta las decisiones de tratamiento segun los dominios COBIT pertinentes.

| ID | Riesgo | Impacto (1-5) | Probabilidad (1-5) | Nivel (IxP) | Categoria | Proceso COBIT | Mitigacion | Responsable |
|----|--------|--------------|-------------------|-------------|-----------|--------------|-----------|-------------|
| R1 | Alteracion maliciosa de algoritmos | 5 | 2 | 10 | Medio | DSS05 - Gestionar Servicios de Seguridad | RNF-SEC-006: Verificacion de firma digital al inicio | Equipo Seguridad |
| R2 | Acceso no autorizado al historial | 3 | 3 | 9 | Medio | DSS05 - Gestionar Servicios de Seguridad | RNF-SEC-001: Biometria/PIN + SQLCipher | Equipo Seguridad |
| R3 | Borrado accidental de calculos | 4 | 4 | 16 | Critico | DSS04 - Gestionar Continuidad | Dialogo de confirmacion + borrado logico + respaldo automatico | Equipo Desarrollo |
| R4 | Error por unidad DEG/RAD | 4 | 3 | 12 | Alto | APO12 - Gestionar el Riesgo | Toggle visible con indicador prominente + prueba unitaria RF-002 | Equipo QA |
| R5 | Crash durante calculos complejos | 3 | 4 | 12 | Alto | DSS04 - Gestionar Continuidad | Autosave + ProcessPoolExecutor aislado + Crashlytics | Equipo Desarrollo |
| R6 | Corrupcion de datos historicos | 4 | 2 | 8 | Medio | DSS04 - Gestionar Continuidad | WAL mode en SQLite + backups periodicos (RNF-SUP-005) | Equipo Infraestructura |
| R7 | Incompatibilidad con actualizaciones OS | 3 | 3 | 9 | Medio | BAI03 - Gestionar Soluciones | CI/CD con matriz de dispositivos (Android 10+, iOS 15+) | Equipo DevOps |
| R8 | Perdida de datos por fallo de sincronizacion | 4 | 3 | 12 | Alto | APO12 - Gestionar el Riesgo | Cola persistente en SQLite + retry con backoff exponencial | Equipo Backend |
| R9 | Incumplimiento normativo ISO 27001 | 5 | 1 | 5 | Bajo | MEA03 - Monitorear Cumplimiento | Auditorias periodicas de controles RNF-SEC | Equipo Seguridad |

**Leyenda de Niveles:** Critico (>=15) | Alto (9-14) | Medio (5-8) | Bajo (1-4)

## 4.9 Plan de Pruebas y Metricas de Calidad (ISO/IEC 25010)

### 4.9.1 Pruebas Unitarias (Backend - minimo 7)

| Numero | Prueba | Modulo | Descripcion |
|--------|--------|--------|------------|
| 1 | test_basic_arithmetic | domain/engine | Verifica suma, resta, multiplicacion, division con valores limite y division por cero |
| 2 | test_trig_deg_mode | domain/engine | sin(90 grados)=1, cos(0 grados)=1, tan(45 grados)=1 con precision de 10 digitos |
| 3 | test_trig_rad_mode | domain/engine | sin(pi/2)=1, cos(pi)=-1 con mpmath |
| 4 | test_regex_validation | application/validators | Valida que inputs invalidos son rechazados por Regex |
| 5 | test_history_crud | application/use_cases | CRUD completo de historial con borrado logico |
| 6 | test_jwt_auth | infrastructure/security | Generacion, validacion y expiracion de tokens JWT |
| 7 | test_sync_conflict_lww | application/use_cases | Resolucion LWW cuando dos dispositivos modifican el mismo registro |

### 4.9.2 Herramientas de Prueba

| Tipo | Herramienta | Proposito |
|------|------------|----------|
| Analisis estatico | SonarQube | Bugs, vulnerabilidades, code smells. Target: Rating 'A' |
| Pruebas funcionales (Frontend) | Cypress | Automatizacion E2E sobre React Native Web |
| Pruebas funcionales (API) | Postman (Automatizado) | Validacion de 7 CRUDs + endpoints de sync |
| Pruebas de rendimiento | k6 + Lighthouse | Latencia P95, throughput, errores bajo carga |
| Pruebas unitarias (Backend) | pytest + pytest-cov | Cobertura mayor a 90% |
| Pruebas unitarias (Frontend) | Jest + React Testing Library | Cobertura mayor a 80% |

### 4.9.3 Metricas Clave a Documentar

El reporte de resultados de pruebas debe incluir:

1. Tiempos de respuesta por endpoint (P50, P95, P99).
2. Throughput (requests por segundo) bajo carga de 100, 500 y 1000 usuarios concurrentes.
3. Tasa de errores bajo carga (menor a 1%).
4. Cobertura de codigo desglosada por modulo.
5. Listado de bugs, vulnerabilidades y code smells detectados por SonarQube.
6. Areas problematicas identificadas segun ISO/IEC 25010 (Adecuacion Funcional, Eficiencia en Rendimiento, Compatibilidad, Usabilidad, Fiabilidad, Seguridad, Mantenibilidad, Portabilidad).
7. Tareas de mejora priorizadas (refactorizaciones, correcciones de vulnerabilidades, optimizacion de tiempos de respuesta).

## 4.10 Recomendaciones de Control (COBIT)

APO12 (Gestionar el Riesgo): Formalizar el perfil de riesgo priorizando la integridad de resultados matematicos por encima de nuevas funcionalidades.

DSS05 (Gestionar Servicios de Seguridad): Implementar autenticacion biometrica, cifrado SQLCipher y validacion Regex obligatoria.

DSS04 (Gestionar Continuidad): Disenar mecanismo de Autosave para prevenir perdida de datos ante crashes.

MEA01 (Monitorear Desempeno): Log anonimo de errores para deteccion proactiva de fallas de compatibilidad.

---

# DOCUMENTO 5: ESTADO DEL PROYECTO (Inventario al 30-03-2026)

## 5.1 Lo que esta implementado

### Backend (Python / FastAPI)

| Componente | Archivos | Estado |
|-----------|---------|--------|
| Motor matematico (Lexer, Parser, Evaluador) | `src/domain/engine/` | Completo |
| Entidades de dominio (Calculation, User, Profile) | `src/domain/entities/` | Completo |
| Value Objects (AngleMode, Expression, Precision) | `src/domain/value_objects/` | Completo |
| Puertos abstractos (ABC) | `src/domain/ports/` | Completo |
| Casos de uso (EvaluateExpression, ManageHistory, ManageUser) | `src/application/use_cases/` | Completo |
| Validadores Regex centralizados | `src/application/validators/regex_validators.py` | Completo |
| Routers REST FastAPI (`/api/v1/`) | `src/infrastructure/adapters/input/fastapi_router.py` | Completo |
| Router Web Jinja2 (`/web/`) | `src/infrastructure/adapters/input/web_router.py` | Completo |
| Templates HTML (login, register, calculator) | `src/infrastructure/adapters/input/templates/` | Completo |
| JWT middleware y bcrypt | `src/infrastructure/security/` | Completo |
| Repositorios PostgreSQL (history, user, sync) | `src/infrastructure/adapters/output/` | Completo |
| Modelos ORM SQLAlchemy (7 tablas) | `src/infrastructure/persistence/models/` | Completo |
| Migraciones Alembic | `src/infrastructure/persistence/migrations/` | Completo |
| Docker Compose (PostgreSQL + backend) | `docker-compose.yml` | Completo |
| Dockerfile | `backend/Dockerfile` | Completo |
| Configuracion SonarQube | `sonar-project.properties` | Completo |

### Pruebas

| Tipo | Archivos | Cobertura | Estado |
|------|---------|-----------|--------|
| Unitarias - Aritmetica (RF-001) | `tests/unit/test_arithmetic.py` | Suma, resta, multiplicacion, division, potencia, precedencia, parentesis, division por cero | Completo |
| Unitarias - Trig DEG (RF-002) | `tests/unit/test_trig_deg.py` | sin(90)=1, cos(0)=1, tan(45)=1, tan(90)=Indefinido, angulos estandar | Completo |
| Unitarias - Trig RAD (RF-002) | `tests/unit/test_trig_rad.py` | sin(pi/2)=1, cos(pi)=-1 con mpmath | Completo |
| Unitarias - Regex (RNF-006) | `tests/unit/test_regex_validators.py` | Email, password, expresion, UUID v4 | Completo |
| Unitarias - CRUD Historial (RF-003) | `tests/unit/test_history_crud.py` | CRUD completo, borrado logico, limite FIFO 50 | Completo |
| Unitarias - JWT (RNF-006) | `tests/unit/test_jwt_auth.py` | Generacion, decodificacion, expiracion (freezegun), bcrypt | Completo |
| Unitarias - LWW Sync | `tests/unit/test_sync_lww.py` | Resolucion de conflictos Last Write Wins | Completo |
| E2E Selenium - Paginas | `tests/e2e/test_web_pages.py` | GET /web/login, /web/register, /web/calculator → HTTP 200 | Completo |
| E2E Selenium - Autenticacion | `tests/e2e/test_auth_e2e.py` | Registro, email duplicado, login valido, login incorrecto | Completo |
| E2E Selenium - Calculadora | `tests/e2e/test_calculator_e2e.py` | 2+3*4=14, sin(90)=1, expresion invalida, historial, borrar entrada | Completo |
| E2E Selenium - Demo interactivo | `tests/e2e/selenium_main.py` | RF-001 a RF-008, RNF-006 (flujo completo con Chrome visual) | Completo |
| Integracion | `tests/integration/` | (directorio listo) | **Pendiente** |

**Cobertura actual:** 41.75% (362/867 lineas). **Meta: >90%.**

### Endpoints implementados

| Metodo | Endpoint | Descripcion |
|--------|---------|-------------|
| POST | `/api/v1/auth/register` | Registro de usuario |
| POST | `/api/v1/auth/login` | Login → access_token + refresh_token |
| POST | `/api/v1/calculate` | Evaluar expresion matematica (requiere JWT) |
| GET | `/api/v1/history` | Ultimas 50 operaciones del usuario |
| DELETE | `/api/v1/history/{id}` | Borrado logico de entrada del historial |
| GET | `/api/v1/users/me` | Datos del usuario autenticado |
| DELETE | `/api/v1/users/{id}` | Borrado logico del usuario |
| GET | `/web/login` | Pagina HTML de login (Selenium) |
| GET | `/web/register` | Pagina HTML de registro (Selenium) |
| GET | `/web/calculator` | Pagina HTML de calculadora (Selenium) |
| GET | `/health` | Health check del servidor |

## 5.2 Lo que falta completar

### Desarrollo

| Item | Prioridad | Razon |
|------|-----------|-------|
| Pruebas de integracion (tests/integration/) | Alta | Cobertura actual 41.75% — hay que llegar a >90% |
| Frontend React Native | Media | La estructura de carpetas existe pero no hay codigo |
| Pruebas de rendimiento con k6 | Media | Requerido por KPIs del PRD (latencia P95 <50ms) |
| Pipeline CI/CD | Alta | Requerido por el proyecto final (DevOps) |

### Documentacion del proyecto final

| Item | Fase | Estado |
|------|------|--------|
| Diagrama de despliegue (UML) | Diseno | Pendiente — ver Documento 6 |
| Diagrama de casos de uso (UML) | Diseno | Pendiente — ver Documento 6 |
| Modelo Entidad-Relacion (E/R) | Diseno | Pendiente — ver Documento 6 |
| Sprint Backlog SCRUM | Desarrollo | Pendiente — ver Documento 7 |
| Plan de pruebas ISO 29119 | Pruebas | Pendiente — ver Documento 8 |
| Integracion DevOps CI/CD | Pruebas | Pendiente — ver Documento 9 |
| Manuales (usuario, tecnico, despliegue) | Pruebas | Pendiente — ver Documento 10 |

---

# DOCUMENTO 6: FASE DISENO — DIAGRAMAS

## 6.1 Diagrama de Despliegue (UML)

El siguiente diagrama describe la arquitectura de despliegue de SciCalc Pro en produccion. Se representa en notacion PlantUML (convertible a imagen con PlantUML Server o plugin de IDE).

```plantuml
@startuml SciCalcPro_Deployment
skinparam node {
  BackgroundColor #E8F4FD
  BorderColor #2980B9
}

node "Dispositivo Movil\n(Android 10+ / iOS 15+)" as mobile {
  artifact "SciCalc Pro APK/IPA\n(React Native)" as app
  database "SQLite Local\n(AES-256 SQLCipher)" as sqlite
  app --> sqlite : "lectura/escritura\noffline-first"
}

node "Servidor de Aplicacion\n(Ubuntu 22.04 / Docker)" as server {
  artifact "Backend FastAPI\n(Python 3.12 / uvicorn)" as backend
  artifact "Nginx\n(Reverse Proxy)" as nginx
  nginx --> backend : "proxy_pass :8000"
}

node "Servidor de Base de Datos\n(Docker / PostgreSQL 15)" as dbserver {
  database "PostgreSQL 15\n(scicalc DB)" as pg
}

node "Servidor de Calidad\n(Docker / SonarQube Community)" as sonarserver {
  artifact "SonarQube\n(analisis estatico)" as sonar
}

cloud "Internet / Red Movil" as internet

mobile ..> internet : "HTTPS / REST API\n(JWT Bearer)"
internet ..> nginx
backend --> pg : "asyncpg\nSQLAlchemy 2.0"
backend ..> sonar : "sonar-scanner\n(analisis calidad)"

note right of mobile
  Modo Offline-First:
  100% de funciones de calculo
  disponibles sin conectividad.
  Sincronizacion oportunista.
end note

note right of server
  Puerto 443 (HTTPS externo)
  Puerto 8000 (interno uvicorn)
  Variables de entorno:
  DATABASE_URL, SECRET_KEY,
  ACCESS_TOKEN_EXPIRE_MINUTES
end note

@enduml
```

**Descripcion de nodos:**

| Nodo | Tecnologia | Responsabilidad |
|------|-----------|----------------|
| Dispositivo Movil | React Native + SQLCipher | Interfaz de usuario, motor matematico offline, persistencia local |
| Servidor de Aplicacion | FastAPI + Nginx + Docker | Autenticacion JWT, CRUDs PostgreSQL, sincronizacion |
| Servidor de BD | PostgreSQL 15 + Docker | Persistencia centralizada, respaldo multi-dispositivo |
| Servidor de Calidad | SonarQube Community | Analisis estatico, cobertura, code smells |

## 6.2 Diagrama de Casos de Uso (UML)

```plantuml
@startuml SciCalcPro_UseCases
left to right direction
skinparam actorStyle awesome

actor "Usuario General" as user
actor "Ingeniero de Campo" as eng
actor "Estudiante STEM" as student
actor "Sistema (Backend)" as system

eng --|> user
student --|> user

rectangle "SciCalc Pro" {
  usecase "UC-01\nRegistrar cuenta" as UC01
  usecase "UC-02\nIniciar sesion (JWT)" as UC02
  usecase "UC-03\nRealizar operacion aritmetica\n(RF-001)" as UC03
  usecase "UC-04\nCalcular funcion trigonometrica\nDEG/RAD (RF-002)" as UC04
  usecase "UC-05\nConsultar historial\n(RF-003)" as UC05
  usecase "UC-06\nBorrar entrada del historial\n(RF-003)" as UC06
  usecase "UC-07\nUsar funciones de memoria\nM+/M-/MR/MC (RF-004)" as UC07
  usecase "UC-08\nConvertir unidades\n(RF-005)" as UC08
  usecase "UC-09\nCambiar modo oscuro/claro\n(RF-007)" as UC09
  usecase "UC-10\nIngresar notacion cientifica\n(RF-008)" as UC10
  usecase "UC-11\nSincronizar datos\nSQLite → PostgreSQL" as UC11
  usecase "UC-12\nValidar expresion con Regex\n(RNF-006)" as UC12
}

user --> UC01
user --> UC02
user --> UC03
user --> UC04
user --> UC05
user --> UC06
user --> UC07
user --> UC08
user --> UC09
user --> UC10
eng --> UC11
system --> UC12

UC03 .> UC12 : <<include>>
UC04 .> UC12 : <<include>>
UC11 .> UC02 : <<include>>

@enduml
```

## 6.3 Modelo Entidad-Relacion (E/R)

```plantuml
@startuml SciCalcPro_ER
skinparam linetype ortho

entity "users" as users {
  * id : UUID <<PK>>
  --
  * email : VARCHAR(255) <<UNIQUE>>
  * password_hash : VARCHAR(255)
  * display_name : VARCHAR(100)
  created_at : TIMESTAMP WITH TIME ZONE
  updated_at : TIMESTAMP WITH TIME ZONE
  is_deleted : BOOLEAN
}

entity "profiles" as profiles {
  * id : UUID <<PK>>
  --
  * user_id : UUID <<FK>>
  avatar_url : VARCHAR(500)
  preferred_precision : INTEGER (2-50)
  angle_mode : VARCHAR(3) [DEG|RAD]
  theme : VARCHAR(5) [LIGHT|DARK]
  updated_at : TIMESTAMP WITH TIME ZONE
  is_deleted : BOOLEAN
}

entity "calculation_history" as history {
  * id : UUID <<PK>>
  --
  * user_id : UUID <<FK>>
  * expression : TEXT
  * result : TEXT
  precision_digits : INTEGER
  created_at : TIMESTAMP WITH TIME ZONE
  is_deleted : BOOLEAN
  sync_version : INTEGER
  device_id : VARCHAR(64)
}

entity "user_preferences" as prefs {
  * id : UUID <<PK>>
  --
  * user_id : UUID <<FK>>
  * key : VARCHAR(50)
  value : VARCHAR(500)
  updated_at : TIMESTAMP WITH TIME ZONE
  is_deleted : BOOLEAN
}

entity "favorite_conversions" as favs {
  * id : UUID <<PK>>
  --
  * user_id : UUID <<FK>>
  * from_unit : VARCHAR(30)
  * to_unit : VARCHAR(30)
  * category : VARCHAR(10) [LENGTH|MASS|TEMP|VOLUME|SPEED]
  is_deleted : BOOLEAN
}

entity "sessions" as sessions {
  * id : UUID <<PK>>
  --
  * user_id : UUID <<FK>>
  * device_id : VARCHAR(64)
  * jwt_token_hash : VARCHAR(255)
  * expires_at : TIMESTAMP WITH TIME ZONE
  is_active : BOOLEAN
  is_deleted : BOOLEAN
  created_at : TIMESTAMP WITH TIME ZONE
}

entity "sync_log" as synclog {
  * id : UUID <<PK>>
  --
  * user_id : UUID <<FK>>
  * entity_type : VARCHAR(50)
  * entity_id : UUID
  * action : VARCHAR(10) [CREATE|UPDATE|DELETE]
  * client_version : INTEGER
  server_version : INTEGER
  * device_id : VARCHAR(64)
  payload : JSONB
  conflict_detected : BOOLEAN
  conflict_resolution : VARCHAR(20)
  created_at : TIMESTAMP WITH TIME ZONE
  is_deleted : BOOLEAN
}

users ||--o{ profiles : "tiene"
users ||--o{ history : "genera"
users ||--o{ prefs : "configura"
users ||--o{ favs : "guarda"
users ||--o{ sessions : "abre"
users ||--o{ synclog : "registra"

@enduml
```

---

# DOCUMENTO 7: FASE DESARROLLO — SPRINT BACKLOG (SCRUM)

> **Fuente:** Azure DevOps — SciCalc Pro Board (exportado 30-03-2026).
> Los IDs entre parentesis corresponden a los Work Item IDs del tablero.
> Las tareas de nivel tecnico atomico (configuracion de ProGuard, mockups, tooltips, etc.)
> se omiten del PRD por ser demasiado granulares; quedan documentadas exclusivamente en Azure DevOps.

## 7.1 Definicion del Equipo

| Rol | Integrante |
|-----|-----------|
| Product Owner | Puentes Angel |
| Scrum Master | Bonilla Santiago |
| Developer / QA | Patino Kevin |

## 7.2 Sprint 1 — Base y Calculo (20 Feb - 5 Mar) · Epic #101

**Sprint Goal:** Motor matematico offline funcional con operaciones aritmeticas, funciones trigonometricas, precision de punto flotante y estructura basica de la interfaz.

| PBI | Requerimiento | Historia de Usuario | Equipo | Criterios de Aceptacion | Estado |
|-----|--------------|-------------------|--------|------------------------|--------|
| #105 | RF-01 | Como usuario quiero realizar sumas, restas, multiplicaciones y divisiones con validacion de entrada para resolver calculos cotidianos con confianza | Backend, Frontend | +/-/*/÷ en <50ms P95; division por cero retorna DivisionByZeroError; Regex rechaza entradas invalidas | New |
| #106 | RF-02 | Como ingeniero quiero calcular sin, cos, tan y sus inversas en modo DEG y RAD con precision arbitraria para calculos de fisica e ingenieria | Backend | sin(90 DEG)=1.0 tolerancia 1e-10; tan(90 DEG) retorna UndefinedResultError; toggle DEG/RAD visible | New |
| #107 | RNF-01 | Como usuario quiero que el resultado aparezca en menos de 50ms para no interrumpir mi flujo de trabajo | Frontend | P95 operaciones estandar <50ms medido con k6; P95 precision arbitraria <200ms | New |
| #108 | RNF-03 | Como usuario quiero botones grandes y accesibles para minimizar errores de pulsacion en campo | UX/UI | Targets tactiles minimo 48x48dp; teclado ocupa >60% de pantalla; max 2 toques a funciones cientificas | New |
| #109 | RNF-05 | Como investigador quiero resultados con tasa de error relativo menor a 1e-10 para fiarme de los calculos | Backend | Validacion contra Wolfram Alpha para trig, log y exp; aritmetica IEEE 754 de 64-bit por defecto | New |

**Items completados en codigo:** RF-01 ✓, RF-02 ✓, RNF-05 ✓ (motor, lexer, parser, evaluador implementados y con pruebas unitarias pasando). RNF-01 y RNF-03 pendientes de medicion formal.

## 7.3 Sprint 2 — Funciones y UI (6 Mar - 19 Mar) · Epic #102

**Sprint Goal:** Funciones de memoria, historial persistente, conversor de unidades, modo oscuro/claro, portabilidad y monitoreo de recursos.

| PBI | Requerimiento | Historia de Usuario | Equipo | Criterios de Aceptacion | Estado |
|-----|--------------|-------------------|--------|------------------------|--------|
| #111 | RF-03 | Como usuario quiero ver y reutilizar mis ultimas 50 operaciones para no volver a calcular lo mismo | DBA, Frontend | Historial paginado; tap en item lo inserta en la expresion; borrado logico (is_deleted); FIFO automatico | New |
| #112 | RF-04 | Como usuario quiero usar M+, M-, MR y MC para acumular y recuperar valores intermedios sin anotar en papel | Frontend | M+ guarda resultado; indicador "M" visible; MR inserta en expresion; MC borra indicador | New |
| #113 | RF-05 | Como usuario quiero convertir entre unidades de longitud, masa, temperatura, volumen y velocidad en tiempo real | Backend | 1000m→1km; 0°C→32°F; conversion en <50ms; 5 categorias; factores inmutables en dominio | New |
| #114 | RF-07 | Como usuario quiero alternar entre modo oscuro y claro para reducir fatiga visual segun el entorno | Frontend | Cambio en max 2 toques; contraste WCAG 2.1 AA (ratio 4.5:1); tema persiste entre sesiones | New |
| #115 | RNF-04 | Como equipo queremos compilaciones funcionales en Android 10+ e iOS 15+ con un unico codigo base | Backend, Frontend | Pruebas en dispositivos de referencia (iPhone 8, Galaxy S20); React Native cross-platform | New |
| #116 | RNF-08 | Como equipo queremos que la app consuma menos de 2% de bateria por hora y pese menos de 25MB | Backend | Battery Historian <2%/hora; APK/IPA <25MB; CPU en reposo ~0% | New |
| #110 | RNF-SUP-01 | Como equipo de soporte queremos logs rotativos con errores criticos y timestamps ISO 8601 para diagnosticar incidentes rapidamente | Backend, QA | Log local rotativo; niveles: ERROR, WARN, INFO; timestamp ISO 8601; sin datos personales | New |

**Items completados en codigo:** RF-03 ✓ (CRUD historial con borrado logico implementado), RF-04 ✓ (estado global de memoria en interfaz web), RF-05 ✓ (conversor en backend), RF-07 ✓ (theming en templates HTML). RNF-04, RNF-08, RNF-SUP-01 pendientes de implementacion completa.

## 7.4 Sprint 3 — Seguridad (20 Mar - 2 Abr) · Epic #103

**Sprint Goal:** Implementar los controles de seguridad ISO 27001: autenticacion biometrica/PIN, cifrado en reposo, ofuscacion de codigo, proteccion contra capturas e integridad del ejecutable.

| PBI | Requerimiento | Historia de Usuario | Equipo | Criterios de Aceptacion | Estado |
|-----|--------------|-------------------|--------|------------------------|--------|
| #117 | RNF-SEC-01 | Como usuario quiero proteger mi historial con biometria o PIN para que nadie mas pueda verlo | Security | FaceID/Fingerprint en iOS/Android; PIN de 4 digitos como respaldo; bloqueo tras 3 intentos fallidos | New |
| #118 | RNF-SEC-02 | Como equipo queremos que los datos locales sean ilegibles sin la clave de descifrado | — | SQLite cifrado con AES-256 via SQLCipher; datos ilegibles al abrir el archivo con editor hex | New |
| #119 | RNF-SEC-03 | Como equipo queremos que el codigo compilado sea ilegible para dificultar la ingenieria inversa | DevSecOps | ProGuard/R8 activo en release; nombres de clases no legibles al descompilar; motor matematico funcional post-ofuscacion | New |
| #120 | RNF-SEC-05 | Como equipo queremos bloquear capturas de pantalla en la pantalla de historial para proteger datos sensibles | Frontend | FLAG_SECURE activo en Android; blur en multitarea iOS; notificacion al usuario si se detecta intento | New |
| #121 | RNF-SEC-06 | Como equipo queremos verificar la integridad del ejecutable al inicio para detectar modificaciones maliciosas | Security | Firma digital verificada al arrancar; cierre automatico si APK fue modificado; detector de root/jailbreak | New |

**Items completados en codigo:** RNF-SEC-02 parcial (AES-256 documentado en arquitectura; SQLCipher pendiente de integracion en frontend React Native). Los demas controles de seguridad estan pendientes.

## 7.5 Sprint 4 — Soporte y Cierre (3 Abr - 16 Abr) · Epic #104

**Sprint Goal:** Completar funciones de soporte ITIL: exportacion de diagnostico, ayuda offline, respaldo/restauracion, restablecimiento de fabrica, y cierre del proyecto con documentacion final.

| PBI | Requerimiento | Historia de Usuario | Equipo | Criterios de Aceptacion | Estado |
|-----|--------------|-------------------|--------|------------------------|--------|
| #122 | RNF-SUP-02 | Como usuario quiero empaquetar y enviar mis logs de error a soporte sin exponer datos personales | Backend | Funcion de empaquetado en .zip; logs anonimizados; envio via email o compartir nativo del SO | New |
| #123 | RNF-SUP-03 | Como usuario quiero acceder a la ayuda de la app sin conexion a internet para resolver dudas en campo | Frontend | Seccion FAQ accesible offline; documentacion de todas las funciones; visor interno de Markdown/PDF | New |
| #124 | RNF-SUP-05 | Como usuario quiero exportar mi historial a un archivo .json o .bak para no perderlo al reinstalar la app | DBA, Frontend | Exportacion a .json cifrado; importacion con validacion de integridad; guia de usuario incluida | New |
| #125 | RNF-SUP-07 | Como usuario quiero restablecer la app a valores predeterminados sin perder mi historial salvo que lo indique explicitamente | Backend, Frontend | Restablecimiento de preferencias sin borrar historial por defecto; dialogo de confirmacion si se elige borrar historial | New |

**Items completados en codigo:** Todos pendientes (Sprint en curso al momento de la exportacion).

## 7.6 Cierre del Proyecto · Epic #126

Entrega del documento tecnico integral y el prototipo funcional. Fecha limite: **9 de Abril de 2026**.

| Entregable | Descripcion | Estado |
|-----------|-------------|--------|
| Documento tecnico (PRD) | Este archivo — fases de analisis, diseno, desarrollo y pruebas | En progreso |
| Prototipo backend | FastAPI + PostgreSQL + pruebas unitarias y E2E con Selenium | En progreso |
| Cobertura >90% | Pruebas de integracion pendientes para alcanzar la meta | Pendiente |
| Pipeline CI/CD | `.github/workflows/ci.yml` definido en Documento 9 | Pendiente |
| SonarQube Rating A | Scan pendiente una vez alcanzada la cobertura objetivo | Pendiente |

---

# DOCUMENTO 8: FASE PRUEBAS — PLAN ISO 29119

## 8.1 Introduccion al Plan de Pruebas (ISO/IEC 29119-3)

Este plan de pruebas se elabora conforme al estandar ISO/IEC 29119-3 (Documentacion de Pruebas de Software). Define la estrategia, alcance, recursos y criterios de completitud para las pruebas del sistema SciCalc Pro.

### 8.1.1 Identificacion del Plan

| Campo | Valor |
|-------|-------|
| Identificador | TP-SCICALC-001 |
| Version | 1.0 |
| Fecha | 30-03-2026 |
| Sistema bajo prueba | SciCalc Pro v1.0 |
| Nivel de prueba | Unitario, Integracion, Sistema (E2E) |
| Estandar de referencia | ISO/IEC 29119-3:2021 |

### 8.1.2 Alcance de las Pruebas

**En alcance:**
- Motor matematico offline (RF-001 a RF-008)
- Endpoints REST del backend (autenticacion, calculo, historial)
- Interfaz web (flujos de registro, login, calculadora, historial)
- Validacion de entradas con Regex
- Manejo de errores tipados (DivisionByZeroError, UndefinedResultError)

**Fuera de alcance:**
- Frontend React Native (pendiente de implementacion)
- Pruebas de rendimiento bajo carga (requieren k6 en servidor dedicado)
- Pruebas de seguridad de penetracion

### 8.1.3 Enfoque de Pruebas

| Nivel | Herramienta | Marco | Cobertura Objetivo |
|-------|------------|-------|-------------------|
| Unitario | pytest + pytest-cov | ISO 29119 | >90% lineas |
| Integracion | pytest + httpx (AsyncClient) | ISO 29119 | CRUDs principales |
| Sistema E2E | Selenium WebDriver + Chrome | ISO 29119 | RF-001 a RF-008 |
| Analisis estatico | SonarQube Community | ISO/IEC 25010 | Rating 'A' |

## 8.2 Especificacion de Pruebas Unitarias (ISO/IEC 29119-4)

### TP-UNIT-001: Motor Aritmetico

| Campo | Valor |
|-------|-------|
| Identificador | TP-UNIT-001 |
| Requerimiento | RF-001 |
| Archivo | `tests/unit/test_arithmetic.py` |
| Tecnica de diseno | Particion de equivalencia + valores limite |

| Caso | Entrada | Resultado Esperado | Estado |
|------|---------|-------------------|--------|
| TC-001 | "5+3" | "8" | PASS |
| TC-002 | "2+3*4" | "14" (precedencia) | PASS |
| TC-003 | "(2+3)*4" | "20" (parentesis) | PASS |
| TC-004 | "7/0" | DivisionByZeroError (code: DIVISION_BY_ZERO) | PASS |
| TC-005 | "-5+3" | "-2" (unario negativo) | PASS |
| TC-006 | "2^3" | "8" (potencia) | PASS |

### TP-UNIT-002: Funciones Trigonometricas DEG

| Campo | Valor |
|-------|-------|
| Identificador | TP-UNIT-002 |
| Requerimiento | RF-002 |
| Archivo | `tests/unit/test_trig_deg.py` |
| Tecnica de diseno | Valores angulares estandar + casos limite |

| Caso | Entrada | Resultado Esperado | Tolerancia | Estado |
|------|---------|-------------------|-----------|--------|
| TC-007 | sin(90) DEG | 1.0 | 1e-10 | PASS |
| TC-008 | cos(0) DEG | 1.0 | 1e-10 | PASS |
| TC-009 | tan(45) DEG | 1.0 | 1e-10 | PASS |
| TC-010 | tan(90) DEG | UndefinedResultError | N/A | PASS |
| TC-011 | sin(30) DEG | 0.5 | 1e-10 | PASS |
| TC-012 | cos(180) DEG | -1.0 | 1e-10 | PASS |

### TP-UNIT-003: Validacion Regex

| Campo | Valor |
|-------|-------|
| Identificador | TP-UNIT-003 |
| Requerimiento | RNF-006 |
| Archivo | `tests/unit/test_regex_validators.py` |
| Tecnica de diseno | Clases de equivalencia validas e invalidas |

| Caso | Campo | Entrada | Resultado Esperado | Estado |
|------|-------|---------|-------------------|--------|
| TC-013 | Email | "user@mail.com" | Valido | PASS |
| TC-014 | Email | "user@@mail" | Invalido | PASS |
| TC-015 | Password | "Passw0rd!" | Valido | PASS |
| TC-016 | Password | "pass" | Invalido (min 8, 1 mayus, 1 num) | PASS |
| TC-017 | UUID v4 | "550e8400-e29b-41d4-a716-446655440000" | Valido | PASS |
| TC-018 | UUID v4 | "not-a-uuid" | Invalido | PASS |

## 8.3 Especificacion de Pruebas E2E con Selenium (ISO/IEC 29119-4)

### TP-E2E-001: Autenticacion de Usuario

| Campo | Valor |
|-------|-------|
| Identificador | TP-E2E-001 |
| Requerimiento | RNF-006 |
| Archivo | `tests/e2e/test_auth_e2e.py` |
| Precondicion | Backend corriendo en localhost:8001, PostgreSQL activo, Chrome instalado |

| Paso | Accion | Resultado Esperado |
|------|--------|-------------------|
| 1 | GET /web/register | HTTP 200, formulario con campos username, email, password, boton btn-register |
| 2 | Completar formulario y click btn-register | #result muestra mensaje de exito |
| 3 | Registrar mismo email nuevamente | #result muestra error de email duplicado |
| 4 | GET /web/login, completar credenciales validas, click btn-login | #result contiene "exitoso", sessionStorage tiene access_token |
| 5 | Login con password incorrecta | #result NO contiene "exitoso", sessionStorage.access_token es null |

### TP-E2E-002: Calculo y Historial

| Campo | Valor |
|-------|-------|
| Identificador | TP-E2E-002 |
| Requerimiento | RF-001, RF-002, RF-003 |
| Archivo | `tests/e2e/test_calculator_e2e.py` |
| Precondicion | Usuario autenticado, token inyectado en sessionStorage |

| Paso | Accion | Resultado Esperado |
|------|--------|-------------------|
| 1 | Ingresar "2 + 3 * 4" y click btn-calculate | #result contiene "14" en <15s |
| 2 | Ingresar "sin(90)" en modo DEG | #result comienza con "1" |
| 3 | Ingresar "2 /" (expresion invalida) | #result contiene "error" o "invalid" |
| 4 | Calcular "1 + 1" y verificar history-list | history-list tiene al menos 1 entrada [data-id] |
| 5 | Click btn-delete en la primera entrada | Entrada desaparece del DOM (staleness) |

### TP-E2E-003: Demo Completo (selenium_main.py)

| Campo | Valor |
|-------|-------|
| Identificador | TP-E2E-003 |
| Requerimiento | RF-001 a RF-008, RNF-006 |
| Archivo | `tests/e2e/selenium_main.py` |
| Ejecucion | `python tests/e2e/selenium_main.py` (con Chrome visual) |

**Pasos cubiertos:** Registro → Login → Aritmetica (RF-001) → Trig DEG (RF-002) → Trig RAD (RF-002) → Notacion Cientifica (RF-008) → Memoria M+/MR/MC (RF-004) → Conversor 1000m→km y 0C→32F (RF-005) → Historial (RF-003) → Toggle tema (RF-007) → Login incorrecto (RNF-006).

## 8.4 Criterios de Completitud (ISO/IEC 29119-2)

| Criterio | Meta | Estado Actual |
|---------|------|--------------|
| Cobertura de lineas (backend) | >90% | 41.75% — **En progreso** |
| Todos los casos de prueba unitarios ejecutan PASS | 100% | PASS (7 archivos) |
| Todos los casos E2E ejecutan PASS | 100% | PASS (3 archivos) |
| SonarQube Rating Reliability | A | Pendiente scan |
| SonarQube Rating Security | A | Pendiente scan |
| SonarQube Rating Maintainability | A | Pendiente scan |
| Tasa de defectos criticos abiertos | 0 | Pendiente |

---

# DOCUMENTO 9: FASE PRUEBAS — INTEGRACION DEVOPS (CI/CD)

## 9.1 Estrategia de Integracion Continua

SciCalc Pro adopta una estrategia de Integracion Continua (CI) y Entrega Continua (CD) basada en GitHub Actions (o Azure Pipelines). Cada push o pull request desencadena el pipeline de calidad automaticamente.

## 9.2 Pipeline CI/CD — GitHub Actions

El siguiente archivo debe crearse en `.github/workflows/ci.yml`:

```yaml
name: SciCalc Pro — CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # ─── ETAPA 1: Lint y analisis estatico de codigo ───────────────────────────
  lint:
    name: Lint (ruff)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Instalar dependencias
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Ejecutar ruff (linter)
        run: |
          cd backend
          ruff check src/

  # ─── ETAPA 2: Pruebas unitarias con cobertura ──────────────────────────────
  unit-tests:
    name: Pruebas Unitarias (pytest)
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: scicalc_test
          POSTGRES_USER: scicalc
          POSTGRES_PASSWORD: secret
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
    env:
      DATABASE_URL: postgresql+asyncpg://scicalc:secret@localhost:5432/scicalc_test
      SECRET_KEY: ci-test-secret-key-32-chars-min
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Instalar dependencias
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Aplicar migraciones
        run: |
          cd backend
          alembic upgrade head
      - name: Ejecutar pruebas unitarias con cobertura
        run: |
          cd backend
          pytest tests/unit/ -v --cov=src --cov-report=xml:coverage.xml --cov-fail-under=90
      - name: Subir reporte de cobertura
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: backend/coverage.xml

  # ─── ETAPA 3: Pruebas E2E con Selenium ────────────────────────────────────
  e2e-tests:
    name: Pruebas E2E (Selenium)
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: scicalc_e2e
          POSTGRES_USER: scicalc
          POSTGRES_PASSWORD: secret
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
    env:
      DATABASE_URL: postgresql+asyncpg://scicalc:secret@localhost:5432/scicalc_e2e
      SECRET_KEY: ci-test-secret-key-32-chars-min
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Instalar Google Chrome
        run: |
          wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
          echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
          apt-get update && apt-get install -y google-chrome-stable
      - name: Instalar dependencias Python
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Aplicar migraciones
        run: |
          cd backend
          alembic upgrade head
      - name: Iniciar servidor en background
        run: |
          cd backend
          python run.py &
          sleep 5
      - name: Ejecutar pruebas E2E
        run: |
          cd backend
          pytest tests/e2e/ -v -m e2e --headless

  # ─── ETAPA 4: Analisis SonarQube ──────────────────────────────────────────
  sonarqube:
    name: Analisis SonarQube
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Descargar reporte de cobertura
        uses: actions/download-artifact@v4
        with:
          name: coverage-report
          path: backend/
      - name: SonarQube Scan
        uses: SonarSource/sonarqube-scan-action@master
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

## 9.3 Flujo del Pipeline

```
Push / PR
    │
    ▼
[1] Lint (ruff)
    │ falla → bloquea PR
    ▼
[2] Pruebas Unitarias (pytest --cov)
    │ cobertura < 90% → falla el job
    │ genera coverage.xml
    ▼
[3] Pruebas E2E Selenium   [4] SonarQube Scan
    │ (paralelo con 4)           │ lee coverage.xml
    │                            │ verifica Quality Gate
    ▼                            ▼
Reporte de resultados consolidado
```

## 9.4 Metricas DevOps

| Metrica | Objetivo | Herramienta |
|---------|---------|------------|
| Tiempo de pipeline | < 10 minutos | GitHub Actions |
| Cobertura de codigo | > 90% | pytest-cov |
| Quality Gate SonarQube | PASSED | SonarQube |
| Tasa de builds exitosos | > 95% | GitHub Actions |
| MTTR (Mean Time to Recovery) | < 4 horas | GitHub Issues + Actions |

---

# DOCUMENTO 10: MANUALES

## 10.1 Manual de Usuario

### 10.1.1 Introduccion

SciCalc Pro es una calculadora cientifica que funciona completamente sin conexion a internet. Este manual describe como usar todas sus funciones desde la interfaz web.

### 10.1.2 Registro e Inicio de Sesion

1. Abre tu navegador y ve a `http://[servidor]/web/register`
2. Completa los campos: **Nombre**, **Email** y **Contrasena** (minimo 8 caracteres, 1 mayuscula, 1 numero)
3. Haz clic en **Registrarse**. Veras un mensaje de confirmacion.
4. Ve a `http://[servidor]/web/login`, ingresa tu email y contrasena, haz clic en **Iniciar sesion**.
5. Seras redirigido a la calculadora automaticamente.

### 10.1.3 Realizar Calculos

**Operaciones basicas:**
- Escribe la expresion en el campo de texto (ejemplo: `2 + 3 * 4`)
- Selecciona la precision en decimales (2 a 50)
- Haz clic en **Calcular**. El resultado aparece debajo.

**Funciones trigonometricas:**
- Usa `sin(angulo)`, `cos(angulo)`, `tan(angulo)`
- El boton **DEG / RAD** alterna el modo angular. El modo activo se muestra en el boton.
- Ejemplo: `sin(90)` en modo DEG retorna `1.0`

**Notacion cientifica:**
- Puedes ingresar numeros como `1.5e3` (equivale a 1500)
- Resultados muy grandes o muy pequenos se muestran automaticamente en notacion cientifica

### 10.1.4 Funciones de Memoria

| Boton | Accion |
|-------|--------|
| M+ | Guarda el resultado actual en memoria. Aparece el indicador "M". |
| MR | Inserta el valor guardado en el campo de expresion |
| MC | Borra la memoria. El indicador "M" desaparece. |

### 10.1.5 Conversor de Unidades

1. Selecciona la **Categoria** (Longitud, Masa, Temperatura, Volumen, Velocidad)
2. Escribe el valor numerico
3. Selecciona la unidad de origen y la unidad de destino
4. Haz clic en **Convertir**

| Ejemplo | Resultado |
|---------|----------|
| 1000 metros → kilometros | 1 km |
| 0 grados Celsius → Fahrenheit | 32 °F |
| 100 km/h → m/s | 27.78 m/s |

### 10.1.6 Historial de Operaciones

- El historial muestra las ultimas 50 operaciones debajo de la calculadora.
- Cada entrada muestra la expresion, el resultado y la fecha.
- Para borrar una entrada, haz clic en el boton **Borrar** junto a ella. El borrado es logico (recuperable).

### 10.1.7 Cambio de Tema Visual

- Haz clic en el boton **Modo Oscuro / Modo Claro** en la barra superior.
- El tema se aplica de inmediato a toda la interfaz.

---

## 10.2 Manual Tecnico (Despliegue y Configuracion)

### 10.2.1 Requisitos del Servidor

| Componente | Version minima | Notas |
|-----------|---------------|-------|
| Python | 3.12 | Disponible en PATH |
| Docker Desktop | 24.x | Para PostgreSQL |
| PostgreSQL | 15 (via Docker) | Puerto 5434 (evita conflicto con instancias nativas) |
| Chrome | 120+ | Para pruebas Selenium |
| Sistema operativo | Windows 11 / Ubuntu 22.04 | |

### 10.2.2 Instalacion

```bash
# 1. Clonar o descomprimir el proyecto
# Directorio raiz: SciCalcPro/

# 2. Configurar variables de entorno (Git Bash / bash)
echo 'export PATH="/c/Users/.../Python312:/c/Users/.../Python312/Scripts:$PATH"' >> ~/.bashrc
echo 'export DATABASE_URL="postgresql+asyncpg://scicalc:secret@localhost:5434/scicalc"' >> ~/.bashrc
source ~/.bashrc

# 3. Instalar dependencias Python
cd backend
pip install -e ".[dev]"

# 4. Levantar PostgreSQL
cd ..
docker-compose up -d postgres

# 5. Aplicar esquema de base de datos
cd backend
alembic upgrade head

# 6. Arrancar el servidor
python run.py
# Servidor disponible en http://localhost:8000
```

### 10.2.3 Variables de Entorno

| Variable | Valor por defecto | Descripcion |
|----------|-----------------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://scicalc:secret@localhost:5434/scicalc` | Cadena de conexion PostgreSQL |
| `SECRET_KEY` | `dev-secret-key-change-in-production-min-32-chars` | Clave HMAC para firmar JWT. **Cambiar en produccion.** |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | TTL del access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | TTL del refresh token |

### 10.2.4 Ejecucion de Pruebas

```bash
# Pruebas unitarias con cobertura
cd backend
pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml

# Pruebas E2E (requiere servidor corriendo en otra terminal)
pytest tests/e2e/ -v -m e2e

# Demo Selenium interactivo (abre Chrome visible)
python tests/e2e/selenium_main.py
```

### 10.2.5 Analisis SonarQube

```bash
# 1. Levantar SonarQube
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
# Esperar ~2 minutos → http://localhost:9000 (admin/admin)

# 2. Generar coverage.xml
cd backend
pytest tests/unit/ --cov=src --cov-report=xml:coverage.xml

# 3. Ejecutar scanner (desde la raiz del proyecto)
cd ..
sonar-scanner   # o via Docker (ver GUIA.md seccion 7)
```

### 10.2.6 Endpoints de la API

| Metodo | Endpoint | Autenticacion | Descripcion |
|--------|---------|--------------|-------------|
| POST | `/api/v1/auth/register` | No | Crear cuenta nueva |
| POST | `/api/v1/auth/login` | No | Obtener JWT |
| POST | `/api/v1/calculate` | Bearer JWT | Evaluar expresion matematica |
| GET | `/api/v1/history` | Bearer JWT | Listar historial |
| DELETE | `/api/v1/history/{id}` | Bearer JWT | Borrar entrada (logico) |
| GET | `/api/v1/users/me` | Bearer JWT | Datos del usuario |
| GET | `/health` | No | Estado del servidor |

Documentacion interactiva Swagger: `http://localhost:8000/docs`

---

Fin del documento. Version 5.0 - Actualizado 30-03-2026.
