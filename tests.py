import sys
import os
import unittest

# Asegurar que el directorio del proyecto esté en el path
sys.path.insert(0, os.path.dirname(__file__))

from deque import Deque
from editor_history import EditorHistory, Action


# ══════════════════════════════════════════════════════════════════════════════
# Tests para la clase Deque
# ══════════════════════════════════════════════════════════════════════════════

class TestDeque(unittest.TestCase):
    """Pruebas de la estructura Deque propia."""

    def setUp(self):
        self.dq = Deque()

    # ── estado inicial ────────────────────────────────────────────────────────

    def test_inicio_vacio(self):
        self.assertTrue(self.dq.is_empty())
        self.assertEqual(self.dq.size(), 0)

    # ── add_rear / remove_rear ────────────────────────────────────────────────

    def test_add_rear_y_remove_rear(self):
        self.dq.add_rear(1)
        self.dq.add_rear(2)
        self.dq.add_rear(3)
        self.assertEqual(self.dq.remove_rear(), 3)
        self.assertEqual(self.dq.remove_rear(), 2)
        self.assertEqual(self.dq.remove_rear(), 1)
        self.assertTrue(self.dq.is_empty())

    # ── add_front / remove_front ──────────────────────────────────────────────

    def test_add_front_y_remove_front(self):
        self.dq.add_front("a")
        self.dq.add_front("b")
        self.dq.add_front("c")
        # orden esperado (frente→final): c, b, a
        self.assertEqual(self.dq.remove_front(), "c")
        self.assertEqual(self.dq.remove_front(), "b")
        self.assertEqual(self.dq.remove_front(), "a")

    # ── mix de operaciones ────────────────────────────────────────────────────

    def test_mix_add_front_rear(self):
        self.dq.add_rear(10)
        self.dq.add_front(20)
        self.dq.add_rear(30)
        # frente→final: 20, 10, 30
        self.assertEqual(self.dq.size(), 3)
        self.assertEqual(self.dq.remove_front(), 20)
        self.assertEqual(self.dq.remove_rear(), 30)

    # ── size ──────────────────────────────────────────────────────────────────

    def test_size(self):
        for i in range(5):
            self.dq.add_rear(i)
        self.assertEqual(self.dq.size(), 5)
        self.dq.remove_front()
        self.assertEqual(self.dq.size(), 4)

    # ── peek ──────────────────────────────────────────────────────────────────

    def test_peek_front_no_elimina(self):
        self.dq.add_rear("x")
        self.dq.add_rear("y")
        self.assertEqual(self.dq.peek_front(), "x")
        self.assertEqual(self.dq.size(), 2)  # no se eliminó

    def test_peek_rear_no_elimina(self):
        self.dq.add_rear("x")
        self.dq.add_rear("y")
        self.assertEqual(self.dq.peek_rear(), "y")
        self.assertEqual(self.dq.size(), 2)

    # ── errores en deque vacío ────────────────────────────────────────────────

    def test_remove_front_vacio_lanza_error(self):
        with self.assertRaises(IndexError):
            self.dq.remove_front()

    def test_remove_rear_vacio_lanza_error(self):
        with self.assertRaises(IndexError):
            self.dq.remove_rear()

    def test_peek_front_vacio_lanza_error(self):
        with self.assertRaises(IndexError):
            self.dq.peek_front()

    def test_peek_rear_vacio_lanza_error(self):
        with self.assertRaises(IndexError):
            self.dq.peek_rear()

    # ── to_list ───────────────────────────────────────────────────────────────

    def test_to_list(self):
        self.dq.add_rear(1)
        self.dq.add_rear(2)
        self.dq.add_front(0)
        self.assertEqual(self.dq.to_list(), [0, 1, 2])

    def test_to_list_no_modifica_deque(self):
        self.dq.add_rear(42)
        lista = self.dq.to_list()
        lista.append(99)              # modificar la copia
        self.assertEqual(self.dq.size(), 1)  # deque intacto

    # ── len() ─────────────────────────────────────────────────────────────────

    def test_len_builtin(self):
        self.dq.add_rear("a")
        self.dq.add_rear("b")
        self.assertEqual(len(self.dq), 2)


# ══════════════════════════════════════════════════════════════════════════════
# Tests para EditorHistory
# ══════════════════════════════════════════════════════════════════════════════

class TestEditorHistory(unittest.TestCase):
    """Pruebas de la lógica de undo/redo."""

    def setUp(self):
        self.editor = EditorHistory("estado inicial")

    # ── estado inicial ────────────────────────────────────────────────────────

    def test_estado_inicial(self):
        self.assertEqual(self.editor.current_state, "estado inicial")
        self.assertFalse(self.editor.can_undo)
        self.assertFalse(self.editor.can_redo)

    # ── add_action ────────────────────────────────────────────────────────────

    def test_add_action_registra_correctamente(self):
        action = self.editor.add_action("Escribir hola", "hola", "edit")
        self.assertIsInstance(action, Action)
        self.assertEqual(self.editor.current_state, "hola")
        self.assertTrue(self.editor.can_undo)
        self.assertFalse(self.editor.can_redo)

    def test_add_action_descripcion_vacia_lanza_error(self):
        with self.assertRaises(ValueError):
            self.editor.add_action("", "nuevo estado")

    def test_add_action_descripcion_solo_espacios_lanza_error(self):
        with self.assertRaises(ValueError):
            self.editor.add_action("   ", "nuevo estado")

    def test_add_action_sin_cambio_en_estado_se_permite(self):
        # FIX: registrar una acción descriptiva sin cambiar el texto es válido
        action = self.editor.add_action("Acción sin cambio", "estado inicial")
        self.assertIsNotNone(action)
        self.assertTrue(self.editor.can_undo)

    # ── undo ─────────────────────────────────────────────────────────────────

    def test_undo_basico(self):
        self.editor.add_action("Cambio 1", "estado 1")
        result = self.editor.undo()
        self.assertIsNotNone(result)
        self.assertEqual(self.editor.current_state, "estado inicial")

    def test_undo_sin_historial_retorna_none(self):
        result = self.editor.undo()
        self.assertIsNone(result)

    def test_undo_multiples_pasos(self):
        self.editor.add_action("Paso 1", "estado 1")
        self.editor.add_action("Paso 2", "estado 2")
        self.editor.add_action("Paso 3", "estado 3")

        self.editor.undo()
        self.assertEqual(self.editor.current_state, "estado 2")
        self.editor.undo()
        self.assertEqual(self.editor.current_state, "estado 1")
        self.editor.undo()
        self.assertEqual(self.editor.current_state, "estado inicial")
        # No debe haber más
        result = self.editor.undo()
        self.assertIsNone(result)

    def test_undo_habilita_redo(self):
        self.editor.add_action("Acción", "nuevo")
        self.assertFalse(self.editor.can_redo)
        self.editor.undo()
        self.assertTrue(self.editor.can_redo)

    # ── redo ─────────────────────────────────────────────────────────────────

    def test_redo_basico(self):
        self.editor.add_action("Cambio 1", "estado 1")
        self.editor.undo()
        result = self.editor.redo()
        self.assertIsNotNone(result)
        self.assertEqual(self.editor.current_state, "estado 1")

    def test_redo_sin_historial_retorna_none(self):
        result = self.editor.redo()
        self.assertIsNone(result)

    def test_redo_multiples_pasos(self):
        self.editor.add_action("Paso 1", "estado 1")
        self.editor.add_action("Paso 2", "estado 2")
        self.editor.undo()
        self.editor.undo()

        self.editor.redo()
        self.assertEqual(self.editor.current_state, "estado 1")
        self.editor.redo()
        self.assertEqual(self.editor.current_state, "estado 2")
        # No debe haber más
        result = self.editor.redo()
        self.assertIsNone(result)

    # ── nueva acción borra redo ───────────────────────────────────────────────

    def test_nueva_accion_limpia_redo(self):
        self.editor.add_action("Acción 1", "estado 1")
        self.editor.add_action("Acción 2", "estado 2")
        self.editor.undo()

        self.assertTrue(self.editor.can_redo)
        # Nueva acción debe limpiar el redo
        self.editor.add_action("Acción nueva", "estado nuevo")
        self.assertFalse(self.editor.can_redo)

    # ── undo + redo + nueva acción (flujo completo) ───────────────────────────

    def test_flujo_completo(self):
        self.editor.add_action("Escribir A", "A")
        self.editor.add_action("Escribir AB", "AB")
        self.editor.add_action("Escribir ABC", "ABC")

        self.editor.undo()
        self.editor.undo()
        self.assertEqual(self.editor.current_state, "A")

        self.editor.redo()
        self.assertEqual(self.editor.current_state, "AB")

        # Nueva acción desde "AB" → borra "ABC" del redo
        self.editor.add_action("Escribir ABX", "ABX")
        self.assertFalse(self.editor.can_redo)
        self.assertEqual(self.editor.current_state, "ABX")

    # ── historial ────────────────────────────────────────────────────────────

    def test_get_undo_history_orden(self):
        self.editor.add_action("Paso 1", "s1")
        self.editor.add_action("Paso 2", "s2")
        history = self.editor.get_undo_history()
        # El más reciente debe estar primero
        self.assertEqual(history[0].description, "Paso 2")
        self.assertEqual(history[1].description, "Paso 1")

    def test_get_redo_history_orden(self):
        self.editor.add_action("Paso 1", "s1")
        self.editor.add_action("Paso 2", "s2")
        self.editor.undo()
        self.editor.undo()
        redo = self.editor.get_redo_history()
        self.assertEqual(redo[0].description, "Paso 1")
        self.assertEqual(redo[1].description, "Paso 2")

    # ── reset ─────────────────────────────────────────────────────────────────

    def test_reset(self):
        self.editor.add_action("Cambio", "nuevo")
        self.editor.reset("limpio")
        self.assertEqual(self.editor.current_state, "limpio")
        self.assertFalse(self.editor.can_undo)
        self.assertFalse(self.editor.can_redo)

    # ── tipos de acción ───────────────────────────────────────────────────────

    def test_tipos_de_accion(self):
        for atype in ["edit", "insert", "delete", "format"]:
            estado = f"estado_{atype}"
            action = self.editor.add_action(f"Acción {atype}", estado, atype)
            self.assertEqual(action.action_type, atype)
            self.editor.undo()  # dejar el editor listo para la siguiente


# ══════════════════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)