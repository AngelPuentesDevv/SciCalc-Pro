# Manual de Usuario — SciCalc Pro

**Versión:** 1.0  
**Fecha:** Marzo 2026  
**Audiencia:** Usuarios finales (estudiantes STEM, ingenieros de campo, público general)

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Registro de cuenta](#2-registro-de-cuenta)
3. [Inicio de sesión](#3-inicio-de-sesión)
4. [Realizar cálculos](#4-realizar-cálculos)
5. [Funciones de memoria](#5-funciones-de-memoria)
6. [Conversor de unidades](#6-conversor-de-unidades)
7. [Historial de cálculos](#7-historial-de-cálculos)
8. [Cambio de tema (oscuro / claro)](#8-cambio-de-tema-oscuro--claro)
9. [Solución de problemas comunes](#9-solución-de-problemas-comunes)

---

## 1. Introducción

**SciCalc Pro** es una calculadora científica de precisión arbitraria accesible desde el navegador web. Está diseñada para profesionales, ingenieros y estudiantes que necesitan:

- Operaciones aritméticas y funciones trigonométricas con hasta **50 dígitos de precisión**.
- Almacenamiento persistente del historial de cálculos asociado a su cuenta.
- Conversión entre unidades de medida de uso frecuente.
- Funciones de memoria (M+, M−, MR, MC) para cálculos encadenados.
- Interfaz en modo oscuro o claro según preferencia personal.

La interfaz web se encuentra en `http://<servidor>/web/` y no requiere instalación en el equipo del usuario.

---

## 2. Registro de cuenta

### 2.1 Acceder a la página de registro

Abra su navegador web y diríjase a:

```
http://<servidor>/web/register
```

### 2.2 Completar el formulario

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Nombre de usuario** | Nombre visible en la interfaz | `Ana Gómez` |
| **Correo electrónico** | Dirección única para identificar la cuenta | `ana@ejemplo.com` |
| **Contraseña** | Mínimo 8 caracteres, al menos una mayúscula, un número y un carácter especial | `Segura1234!` |

### 2.3 Enviar el formulario

Haga clic en el botón **Registrar**. Si el registro es exitoso, verá el mensaje:

> _"Usuario registrado exitosamente."_

Si el correo electrónico ya está registrado, aparecerá un mensaje de error indicando que la dirección ya existe.

### 2.4 Después del registro

Una vez registrado, diríjase a la página de inicio de sesión (ver sección 3) para acceder a su cuenta.

---

## 3. Inicio de sesión

### 3.1 Acceder a la página de inicio de sesión

Navegue a:

```
http://<servidor>/web/login
```

### 3.2 Ingresar credenciales

| Campo | Descripción |
|-------|-------------|
| **Correo electrónico** | El correo registrado en su cuenta |
| **Contraseña** | La contraseña establecida durante el registro |

Haga clic en **Iniciar sesión**.

### 3.3 Resultado exitoso

Si las credenciales son correctas, verá:

> _"Inicio de sesión exitoso."_

El sistema almacenará automáticamente un **token de acceso JWT** en `sessionStorage`. Este token se usa en todas las operaciones subsiguientes (cálculos, historial, etc.) y expira al cerrar el navegador.

### 3.4 Resultado con error

Si la contraseña es incorrecta o el correo no existe, aparecerá un mensaje de error. No se almacenará ningún token. Verifique sus datos e inténtelo de nuevo.

---

## 4. Realizar cálculos

### 4.1 Acceder a la calculadora

Luego de iniciar sesión, diríjase a:

```
http://<servidor>/web/calculator
```

### 4.2 Ingresar una expresión

En el campo **Expresión**, escriba la operación que desea evaluar.

**Ejemplos de expresiones válidas:**

| Expresión | Resultado |
|-----------|-----------|
| `2 + 3 * 4` | `14` (se respeta precedencia de operadores) |
| `(10 - 3) / 2` | `3.5` |
| `sqrt(16)` | `4` |
| `2 ** 10` | `1024` |

### 4.3 Operaciones aritméticas (RF-001)

Los operadores soportados son:

- `+` suma
- `-` resta
- `*` multiplicación
- `/` división
- `**` potencia
- `%` módulo
- `sqrt(x)` raíz cuadrada
- `abs(x)` valor absoluto
- `log(x)` logaritmo natural
- `log10(x)` logaritmo base 10

### 4.4 Funciones trigonométricas con DEG/RAD (RF-002)

SciCalc Pro soporta dos modos angulares:

- **DEG** (grados sexagesimales): valor por defecto.
- **RAD** (radianes): para cálculo matemático puro.

**Cómo seleccionar el modo:**  
Use el selector **Modo angular** junto al campo de expresión para elegir DEG o RAD antes de calcular.

**Funciones disponibles:**

| Función | Descripción |
|---------|-------------|
| `sin(x)` | Seno del ángulo x |
| `cos(x)` | Coseno del ángulo x |
| `tan(x)` | Tangente del ángulo x |
| `asin(x)` | Arcoseno (resultado en el modo seleccionado) |
| `acos(x)` | Arcocoseno |
| `atan(x)` | Arcotangente |

**Ejemplos:**

```
sin(90)    → 1      (en modo DEG)
sin(pi/2)  → 1      (en modo RAD)
cos(0)     → 1      (ambos modos)
```

### 4.5 Notación científica (RF-008)

Para números muy grandes o muy pequeños puede usar notación científica:

```
1.5e10     → 15000000000
2.3e-4     → 0.00023
```

El resultado también se mostrará en notación científica cuando la magnitud lo justifique.

### 4.6 Seleccionar precisión de dígitos

Antes de calcular puede elegir la cantidad de dígitos decimales en el selector **Precisión**:

| Opción | Dígitos decimales |
|--------|-------------------|
| 10 | 10 dígitos |
| 15 | 15 dígitos (valor por defecto) |
| 50 | 50 dígitos (máxima precisión) |

### 4.7 Ver el resultado

Después de hacer clic en **Calcular**, el resultado aparecerá en el área de resultado debajo del formulario. El cálculo se guarda automáticamente en su historial.

---

## 5. Funciones de memoria

Las funciones de memoria permiten guardar un valor temporal para usarlo en cálculos posteriores, sin necesidad de escribirlo nuevamente. (RF-004)

| Botón | Acción |
|-------|--------|
| **M+** | Suma el resultado actual al valor almacenado en memoria |
| **M−** | Resta el resultado actual del valor almacenado en memoria |
| **MR** | Recupera el valor de memoria y lo inserta en el campo de expresión |
| **MC** | Borra (limpia) el valor de memoria |

**Ejemplo de uso:**

1. Calcule `5 * 8` → resultado: `40`. Presione **M+** (memoria = 40).
2. Calcule `3 ** 2` → resultado: `9`. Presione **M+** (memoria = 49).
3. Presione **MR** → el valor `49` aparece en la expresión.
4. Calcule `MR + 1` → resultado: `50`.
5. Presione **MC** para limpiar la memoria.

> **Nota:** La memoria es local a la sesión del navegador. Se pierde al cerrar la pestaña.

---

## 6. Conversor de unidades

### 6.1 Acceder al conversor

El conversor de unidades está disponible como sección dentro de la interfaz de la calculadora o en la ruta dedicada. (RF-005)

### 6.2 Categorías disponibles

| Categoría | Unidades de ejemplo |
|-----------|---------------------|
| **Longitud** | metros, kilómetros, millas, pies, pulgadas |
| **Masa** | kilogramos, gramos, libras, onzas |
| **Temperatura** | Celsius, Fahrenheit, Kelvin |
| **Volumen** | litros, mililitros, galones, onzas fluidas |
| **Velocidad** | m/s, km/h, mph, nudos |

### 6.3 Realizar una conversión

1. Seleccione la **categoría** de unidad (ej. Temperatura).
2. Ingrese el **valor** a convertir (ej. `100`).
3. Seleccione la **unidad de origen** (ej. Celsius).
4. Seleccione la **unidad de destino** (ej. Fahrenheit).
5. Haga clic en **Convertir**.

El resultado aparecerá inmediatamente.

**Ejemplo:**  
`100 °C → 212 °F`

---

## 7. Historial de cálculos

### 7.1 Ver el historial (RF-003)

Debajo de los resultados, la sección **Historial** muestra todos los cálculos realizados en su cuenta, con:

- La expresión ingresada.
- El resultado obtenido.
- La fecha y hora del cálculo.

El historial persiste entre sesiones y se carga automáticamente al iniciar sesión.

### 7.2 Eliminar una entrada del historial

Para borrar un cálculo específico:

1. Localice la entrada en la lista de historial.
2. Haga clic en el botón **Borrar** (ícono de papelera) junto a la entrada.
3. La entrada desaparece de la lista inmediatamente.

> La eliminación es permanente. No hay opción de deshacer desde la interfaz web.

---

## 8. Cambio de tema (oscuro / claro)

SciCalc Pro incluye soporte para tema oscuro y claro. (RF-007)

### 8.1 Cambiar el tema

Busque el botón de alternancia de tema (ícono de luna/sol) en la esquina superior de la interfaz. Haga clic para alternar entre:

- **Modo claro (Light):** Fondo blanco, texto oscuro. Recomendado en ambientes iluminados.
- **Modo oscuro (Dark):** Fondo oscuro, texto claro. Recomendado en ambientes de poca luz, reduce la fatiga visual.

La preferencia de tema se guarda automáticamente en su perfil y se restaurará en la próxima sesión.

---

## 9. Solución de problemas comunes

### Error: "Expresión vacía"

**Causa:** Se intentó calcular sin escribir ninguna expresión.  
**Solución:** Ingrese una expresión matemática válida en el campo correspondiente antes de hacer clic en **Calcular**.

---

### Error: "División por cero"

**Causa:** La expresión contiene una división entre cero, por ejemplo `5 / 0`.  
**Solución:** Verifique su expresión y asegúrese de que el divisor no sea cero. Ejemplo correcto: `5 / 2`.

---

### Error: "Expresión inválida" / "Caracteres no permitidos"

**Causa:** La expresión contiene caracteres que no son operadores o funciones matemáticas reconocidos (ej. letras no correspondientes a funciones, paréntesis desbalanceados, operadores incompletos como `2 /`).  
**Solución:**  
- Revise que todos los paréntesis estén cerrados: `(2 + 3)` en lugar de `(2 + 3`.  
- Verifique que los operadores tengan operandos en ambos lados: `2 + 3` en lugar de `2 +`.  
- Use únicamente las funciones listadas en la sección 4.3 y 4.4.

---

### No veo el historial después de iniciar sesión

**Causa posible 1:** No completó el inicio de sesión correctamente.  
**Solución:** Verifique que el mensaje de inicio de sesión muestre "exitoso" y que la URL del navegador sea `/web/calculator`.

**Causa posible 2:** El historial está vacío porque aún no ha realizado cálculos con esta cuenta.  
**Solución:** Realice al menos un cálculo para que aparezca en el historial.

---

### El token de sesión expiró

**Síntoma:** Al intentar calcular aparece un error de autorización (401).  
**Causa:** El token JWT expira después de un período de inactividad.  
**Solución:** Cierre la pestaña, regrese a `/web/login` e inicie sesión nuevamente.

---

### Problemas de conexión al servidor

**Síntoma:** La página no carga o muestra "No se puede conectar".  
**Solución:**  
1. Verifique que el servidor esté en funcionamiento (contacte al administrador).  
2. Verifique su conexión a internet.  
3. Compruebe que la URL del servidor sea correcta.

---

*Para soporte técnico, contacte al administrador del sistema o consulte el Manual Técnico.*
