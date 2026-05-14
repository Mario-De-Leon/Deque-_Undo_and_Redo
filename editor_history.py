from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from deque import Deque


# ──────────────────────────────────────────────────────────────────────────────
# Modelo de una acción
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Action:
    description: str
    before_state: str          # estado del texto ANTES de la acción
    after_state: str           # estado del texto DESPUÉS de la acción
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    action_type: str = "edit"  # tipo: 'edit', 'insert', 'delete', 'format', etc.

    def __repr__(self) -> str:
        return f"[{self.timestamp}] {self.action_type.upper()}: {self.description!r}"

class EditorHistory:
    MAX_HISTORY = 100  # límite de acciones en el historial

    def __init__(self, initial_state: str = ""):
        self._current_state: str = initial_state
        self._undo_stack: Deque = Deque()   # frente = tope de la pila
        self._redo_stack: Deque = Deque()   # frente = tope de la pila

    # ──────────────────────────── propiedades ────────────────────────────────

    @property
    def current_state(self) -> str:
        return self._current_state

    @property
    def can_undo(self) -> bool:
        return not self._undo_stack.is_empty()

    @property
    def can_redo(self) -> bool:
        return not self._redo_stack.is_empty()

    # ──────────────────────────── operaciones ────────────────────────────────

    def add_action(
        self,
        description: str,
        new_state: str,
        action_type: str = "edit",
    ) -> Action:
        """
        Registra una nueva acción en el historial.

        Parámetros:
          description : texto descriptivo de la acción
          new_state   : nuevo contenido del editor tras la acción
          action_type : categoría de la acción

        Lanza:
          ValueError  : si description o new_state son inválidos
        """
        description = description.strip()
        if not description:
            raise ValueError("La descripción de la acción no puede estar vacía.")
        if new_state == self._current_state:
            raise ValueError("La nueva acción no produce ningún cambio en el estado.")

        action = Action(
            description=description,
            before_state=self._current_state,
            after_state=new_state,
            action_type=action_type,
        )

        # Agregar al tope de la pila de undo (= frente del deque)
        self._undo_stack.add_front(action)

        # Toda nueva acción invalida el historial de redo
        self._clear_redo()

        # Respetar el límite máximo (eliminar la acción más antigua = final del deque)
        if self._undo_stack.size() > self.MAX_HISTORY:
            self._undo_stack.remove_rear()

        self._current_state = new_state
        return action

    def undo(self) -> Optional[Action]:
        """
        Deshace la última acción.

        Retorna la acción deshecha, o None si no hay acciones previas.
        """
        if not self.can_undo:
            return None  # nada que deshacer → validación silenciosa

        action = self._undo_stack.remove_front()
        self._redo_stack.add_front(action)
        self._current_state = action.before_state
        return action

    def redo(self) -> Optional[Action]:
        """
        Rehace la última acción deshecha.

        Retorna la acción rehecha, o None si no hay acciones disponibles.
        """
        if not self.can_redo:
            return None  # nada que rehacer → validación silenciosa

        action = self._redo_stack.remove_front()
        self._undo_stack.add_front(action)
        self._current_state = action.after_state
        return action

    def get_undo_history(self) -> list[Action]:
        """Devuelve la lista de acciones deshacer (del más reciente al más antiguo)."""
        return self._undo_stack.to_list()

    def get_redo_history(self) -> list[Action]:
        """Devuelve la lista de acciones rehacer (del más reciente al más antiguo)."""
        return self._redo_stack.to_list()

    def reset(self, initial_state: str = "") -> None:
        """Reinicia el sistema por completo."""
        self._current_state = initial_state
        self._undo_stack = Deque()
        self._redo_stack = Deque()

    # ──────────────────────────── privados ───────────────────────────────────

    def _clear_redo(self) -> None:
        """Vacía el stack de redo elemento por elemento (usando la API del Deque)."""
        while not self._redo_stack.is_empty():
            self._redo_stack.remove_front()

    # ──────────────────────────── representación ─────────────────────────────

    def __repr__(self) -> str:
        return (
            f"EditorHistory("
            f"undo={self._undo_stack.size()}, "
            f"redo={self._redo_stack.size()}, "
            f"state={self._current_state[:30]!r})"
        )
