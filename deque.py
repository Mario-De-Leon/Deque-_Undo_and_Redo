class Deque:

    def __init__(self):
        self._data: list = []

    # ─────────────────────────── inserción ───────────────────────────

    def add_front(self, item) -> None:
        """Inserta un elemento al frente del deque."""
        self._data.insert(0, item)

    def add_rear(self, item) -> None:
        """Inserta un elemento al final del deque."""
        self._data.append(item)

    # ─────────────────────────── eliminación ─────────────────────────

    def remove_front(self):
        """
        Elimina y devuelve el elemento del frente.
        Lanza IndexError si el deque está vacío.
        """
        if self.is_empty():
            raise IndexError("remove_front() en un Deque vacío")
        return self._data.pop(0)

    def remove_rear(self):
        """
        Elimina y devuelve el elemento del final.
        Lanza IndexError si el deque está vacío.
        """
        if self.is_empty():
            raise IndexError("remove_rear() en un Deque vacío")
        return self._data.pop()

    # ─────────────────────────── consulta ────────────────────────────

    def peek_front(self):
        """Devuelve el elemento del frente sin eliminarlo."""
        if self.is_empty():
            raise IndexError("peek_front() en un Deque vacío")
        return self._data[0]

    def peek_rear(self):
        """Devuelve el elemento del final sin eliminarlo."""
        if self.is_empty():
            raise IndexError("peek_rear() en un Deque vacío")
        return self._data[-1]

    def is_empty(self) -> bool:
        """Retorna True si el deque no tiene elementos."""
        return len(self._data) == 0

    def size(self) -> int:
        """Retorna la cantidad de elementos en el deque."""
        return len(self._data)

    def to_list(self) -> list:
        """Devuelve una copia de los elementos como lista (frente → final)."""
        return list(self._data)

    # ─────────────────────────── representación ──────────────────────

    def __repr__(self) -> str:
        return f"Deque({self._data})"

    def __len__(self) -> int:
        return self.size()
