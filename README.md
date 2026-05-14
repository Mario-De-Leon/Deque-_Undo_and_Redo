# Editor con Undo/Redo — Implementación con Deque

Sistema de edición de texto con historial de acciones completo, implementado en Python con una estructura **Deque propia** y una interfaz gráfica en **Tkinter**.

---

## Estructura del proyecto

```
editor_undo_redo/
├── deque.py           # Clase Deque implementada desde cero
├── editor_history.py  # Lógica de negocio: EditorHistory y Action
├── app.py             # Interfaz gráfica con Tkinter
├── tests.py           # Pruebas unitarias con unittest
└── README.md
```

---

## Requisitos

- Python 3.12 o superior
- Tkinter (incluido con Python en la mayoría de sistemas)

> En Ubuntu/Debian, si Tkinter no está disponible:
> ```bash
> sudo apt-get install python3-tk
> ```

---

## Cómo ejecutar

### Aplicación gráfica

```bash
cd editor_undo_redo
python app.py
```

### Pruebas unitarias

```bash
# Con unittest (sin dependencias externas)
python tests.py

# Con pytest (si está instalado)
pytest tests.py -v
```

---

## Funcionalidades

| Operación | Descripción |
|-----------|-------------|
| **Registrar acción** | Agrega una nueva acción con descripción y tipo al historial |
| **Undo** | Deshace la última acción (Ctrl+Z) |
| **Redo** | Rehace la última acción deshecha (Ctrl+Y) |
| **Historial Undo** | Panel lateral izquierdo con todas las acciones deshacer |
| **Historial Redo** | Panel lateral derecho con acciones disponibles para rehacer |
| **Reset** | Reinicia el editor y limpia todo el historial |

---

## Cómo funciona el Undo/Redo

Se usan **dos instancias de Deque** como pilas:

- **`_undo_stack`**: acciones registradas. El frente es el "tope" (última acción).
- **`_redo_stack`**: acciones deshecha. El frente es el "tope".

**Al registrar una acción:**
1. Se guarda `(before_state, after_state)` en la acción.
2. Se hace `add_front()` en `_undo_stack`.
3. Se vacía `_redo_stack` (nueva acción invalida el futuro).

**Al hacer Undo:**
1. `remove_front()` de `_undo_stack` → obtiene la acción más reciente.
2. `add_front()` en `_redo_stack`.
3. El estado actual vuelve a `before_state`.

**Al hacer Redo:**
1. `remove_front()` de `_redo_stack`.
2. `add_front()` en `_undo_stack`.
3. El estado actual avanza a `after_state`.

---

## Validaciones implementadas

- Descripción vacía o solo espacios → `ValueError`
- Acción que no cambia el estado → `ValueError`
- Undo sin historial → retorna `None` (sin crash)
- Redo sin historial disponible → retorna `None` (sin crash)
- Límite máximo de 100 acciones en el historial
- Confirmación antes de hacer reset
- Botones deshabilitados cuando no aplica la operación
