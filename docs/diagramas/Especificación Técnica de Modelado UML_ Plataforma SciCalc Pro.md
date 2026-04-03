### Especificación Técnica de Modelado UML: Plataforma SciCalc Pro

Como Arquitecto de Software Senior, establezco la presente especificación técnica para la plataforma  **SciCalc Pro** . Este documento prescribe el uso riguroso del lenguaje UML, no solo como una herramienta de dibujo, sino como un modelo de pensamiento arquitectónico basado en la metodología de Fontela, garantizando que la transición desde los requisitos hasta la implementación sea precisa y libre de ambigüedades.

##### 1\. Fundamentos Metodológicos y Abstracción del Sistema

La construcción de una arquitectura robusta para SciCalc Pro exige la aplicación estratégica de la  **abstracción** . Siguiendo la premisa de Fontela, abstraer no es omitir, sino "enfatizar cuestiones críticas para comprenderlas mejor, postergando detalles menores". En esta fase, nuestro enfoque debe centrarse en la lógica estructural y de comportamiento, asegurando que el equipo de desarrollo no se pierda en implementaciones prematuras.Para SciCalc Pro, se emplearán cinco mecanismos de abstracción, cuya correcta aplicación es mandatoria para habilitar comportamientos polimórficos y una lógica centralizada:| Mecanismo | Definición Técnica (Fontela) | Representación en UML | Impacto en la Robustez de SciCalc Pro || \------ | \------ | \------ | \------ || **Clasificación** | Relaciona individuos (instancias) con especies (clases). | Rectángulo con el nombre de la clase. | Permite deducir comportamientos generales para conjuntos de entidades. || **Asociación** | Relación entre clases que implica un vínculo entre sus instancias. | Línea sólida con cardinalidad en los extremos. | Define la conectividad estructural y el flujo de navegación entre objetos. || **Agregación** | Asociación "todo-parte", asimétrica y  **transitiva** . | Rombo vacío en el extremo del "todo". | Permite construir jerarquías lógicas donde las partes (Items) pueden ser compartidas. || **Composición** | Agregación fuerte con dependencia de existencia. | Rombo relleno en el extremo del "todo". | Garantiza la integridad referencial; el objeto "parte" muere con el "todo". || **Generalización** | Operación para agrupar elementos comunes en clases genéricas. | Flecha triangular vacía hacia la superclase. | Facilita la reutilización de código y el cumplimiento del principio de sustitución. |  
*Nota Arquitectónica:*  Se debe observar que tanto la Agregación como la Generalización son  **transitivas** . Si una clase  *C*  es parte de  *B* , y  *B*  es parte de  *A* , entonces  *C*  es parte de  *A* . Esta propiedad es vital para la navegación profunda en el grafo de objetos del sistema.

##### 2\. Arquitectura Funcional: Diagramas de Casos de Uso y Contexto

El modelo de casos de uso se prescribe aquí como un "modelo de comportamiento" estructural. Su valor no reside en el detalle del procedimiento, sino en la  **delimitación de la frontera del sistema** , permitiendo validar qué funcionalidades pertenecen al alcance contratado y cuáles son externas.

###### *Definición de Actores y Fronteras*

Se exige la distinción técnica estricta entre actores basada en la Figura 4.3:

* **Actores Humanos:**  Representados mediante el esquema de "monigote" (ej. Administrador).  
* **Sistemas Externos:**  Representados mediante un rectángulo con el estereotipo «actor» (ej. Sistema de Personal).

###### *Subsistema de Administración y Control de Alcance*

Es imperativo el uso del  **rectángulo del sistema**  (Sistema de Administración). Este elemento no es decorativo; es vital para prevenir el  *scope creep*  (corrimiento de alcance) al distinguir claramente los requisitos funcionales internos de los estímulos externos. Los casos de uso primarios definidos son:

1. **Ingresar al sistema:**  Gestión de sesión y seguridad.  
2. **Agregar empresa:**  Proceso de alta de clientes corporativos.  
3. **Deshabilitar empresa:**  Gestión del ciclo de vida y suspensión de servicios.La  **navegabilidad**  se representará con una flecha desde el actor hacia el caso de uso, indicando que el actor es quien inicia la interacción y se vale de la funcionalidad del software.

##### 3\. Modelado Estructural de Dominio: Relaciones y Jerarquías

El diagrama de clases para SciCalc Pro actúa como un "glosario gráfico" que unifica el lenguaje entre analistas y desarrolladores. Para asegurar la integridad referencial, se prescriben las siguientes reglas de modelado:

###### *Prescripción de Relaciones (Figura 4.17)*

* **Composición (Rombo Relleno):**  Obligatoria para relaciones  **Organización-Proyecto** . Un proyecto carece de sentido y existencia independiente sin su organización madre.  
* **Agregación (Rombo Vacío):**  Mandatoria para la relación  **Backlog-Item** . Los items son partes lógicas del backlog, pero mantienen una identidad conceptual que permite su gestión modular.

###### *Guía Normativa de Cardinalidad*

A diferencia de la práctica común, para SciCalc Pro la cardinalidad  **nunca debe omitirse** . Aunque habitualmente se asume "1" por omisión, esto no es normativo en UML (p. 51).

* **Número fijo (ej. 1):**  Relación unívoca estricta.  
* *o 2..5):* \* Define límites operativos de negocio.  
* *o 0..*):\* \* Indica multiplicidad opcional o ilimitada.

##### 4\. Especificación bajo Patrón BCE (Boundary, Control, Entity)

Para reducir la brecha entre el dominio del problema y la solución, utilizaremos estereotipos de análisis. Esta es una  **decisión de análisis** , no una preferencia de diseño, orientada a la separación de incumbencias ( *Separation of Concerns* ).

###### *Clasificación y Responsabilidades (Figura 5.5)*

Cada clase de análisis debe incluir un compartimiento de  **Responsabilidades**  donde las acciones se listen precedidas por un guion doble.

1. **«boundary»**  **(Interface de Alta):**  Clases de interfaz para capturar datos del actor.  
2. **«control»**  **(Gestor de Proyectos):**  Clases que coordinan la lógica de los casos de uso.  
3. **«entity»**  **(Empresa, Proyecto, Documento):**  Clases que representan el estado persistente.**Ejemplo de Responsabilidades (p. 68):**  
* **Clase: Documento**  
* \-- instanciarse a partir de una plantilla  
* \-- actualizarse por demanda  
* \-- pedir actualizaciones  
* **Clase: Sistema de Incidencias**  
* \-- gestionar incidencias para testing  
* \-- gestionar incidencias para desarrollo

##### 5\. Dinámica del Sistema: Diagramas de Actividades y Secuencia

El modelado dinámico debe diferenciar rigurosamente entre  **Acciones (instantáneas)**  y  **Actividades (que requieren tiempo)** , según define Fontela (p. 39).

###### *Flujo Operativo y Concurrencia*

En los diagramas de actividades, se utilizarán  **particiones (calles)**  para segregar las responsabilidades entre el Usuario y el Sistema.

* **Bifurcaciones:**  Rombos con condiciones de guarda entre corchetes condición. El uso de else es recomendado para mayor claridad.  
* **Sincronización:**  Uso de conectores  **fork**  (inicio de concurrencia) y  **join**  (fin de concurrencia) para procesos como la "Generación de usuario" y "Envío de mail".

###### *Modelado de Eventos y Señales (Figuras 4.9 y 4.10)*

Se exige el uso de la simbología correcta para señales:

* **Señal Temporal:**  Representada con un  **reloj de arena**  (ej. "2 meses en preventa").  
* **«signal receipt»**  **(Evento Externo):**  Rectángulo con el lado entrante de  **ángulo cóncavo**  (ej. "Cancelación del cliente").  
* **«signal sending»**  **(Evento Generado):**  Rectángulo con el lado saliente de  **ángulo convexo** .  
* **Estado de Objeto:**  Notación entre corchetes, ej. generado, para indicar cambios en el ciclo de vida de objetos persistentes.

###### *Checklist de Consistencia Técnica (p. 72\)*

Para garantizar que el modelo dinámico y el estático sean coherentes, cada mensaje identificado en los diagramas de secuencia debe tener un receptor correspondiente en el diagrama de clases:| Ítem de Verificación | Descripción Técnica || \------ | \------ || **Correspondencia de Métodos** | ¿Cada mensaje entrante en el diagrama de secuencia tiene un método definido en la clase receptora? || **Navegabilidad** | ¿Existe una asociación o dependencia que permita el paso del mensaje entre los objetos? || **Mensajería Asíncrona** | ¿Se han utilizado flechas de punta abierta para representar mensajes que no esperan respuesta? || **Estado Post-Condición** | ¿Los estados finales (círculo blanco con negro concéntrico) coinciden con el cierre lógico del proceso? |  
Este rigor técnico asegura que la implementación de SciCalc Pro sea una traducción directa del modelo, eliminando cualquier margen de error interpretativo.  
