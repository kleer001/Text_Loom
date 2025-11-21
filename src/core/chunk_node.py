import hashlib
import time
import re
from typing import List, Dict
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType


class ChunkNode(Node):
    """Splits text into chunks using various strategies.

    GLYPH: ⊞

    Supports chunking by character count, sentence boundaries, or paragraph boundaries.
    Can respect sentence/paragraph boundaries to avoid mid-sentence splits.
    Supports overlapping chunks for context preservation.
    """

    GLYPH = '⊞'
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True

    def __init__(self, name: str, path: str, node_type: NodeType):
        super().__init__(name, path, [0.0, 0.0], node_type)
        self._is_time_dependent = False
        self._input_hash = None
        self._param_hash = None

        self._parms.update({
            "chunk_mode": Parm("chunk_mode", ParameterType.MENU, self),
            "chunk_size": Parm("chunk_size", ParameterType.INT, self),
            "overlap_size": Parm("overlap_size", ParameterType.INT, self),
            "respect_boundaries": Parm("respect_boundaries", ParameterType.TOGGLE, self),
            "min_chunk_size": Parm("min_chunk_size", ParameterType.INT, self),
            "add_metadata": Parm("add_metadata", ParameterType.TOGGLE, self),
            "enabled": Parm("enabled", ParameterType.TOGGLE, self),
        })

        self._parms["chunk_mode"].set("character")
        self._parms["chunk_size"].set(1000)
        self._parms["overlap_size"].set(100)
        self._parms["respect_boundaries"].set(True)
        self._parms["min_chunk_size"].set(50)
        self._parms["add_metadata"].set(False)
        self._parms["enabled"].set(True)

    def _split_sentences(self, text: str) -> List[str]:
        pattern = r'(?<=[.!?])\s+'
        return [s.strip() for s in re.split(pattern, text) if s.strip()]

    def _split_paragraphs(self, text: str) -> List[str]:
        return [p.strip() for p in text.split('\n\n') if p.strip()]

    def _chunk_by_character(self, text: str, size: int, overlap: int,
                           respect_boundaries: bool, min_size: int) -> List[str]:
        if not text or size <= 0:
            return [text] if text else []

        if respect_boundaries:
            sentences = self._split_sentences(text)
            return self._chunk_units(sentences, size, overlap, min_size)

        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end]
            if len(chunk) >= min_size or start == 0:
                chunks.append(chunk)
            else:
                if chunks:
                    chunks[-1] += chunk
                else:
                    chunks.append(chunk)
            start = end - overlap
            if start >= len(text):
                break
        return chunks

    def _chunk_by_sentence(self, text: str, size: int, overlap: int,
                          min_size: int) -> List[str]:
        sentences = self._split_sentences(text)
        return self._chunk_units(sentences, size, overlap, min_size)

    def _chunk_by_paragraph(self, text: str, size: int, overlap: int,
                           min_size: int) -> List[str]:
        paragraphs = self._split_paragraphs(text)
        return self._chunk_units(paragraphs, size, overlap, min_size)

    def _chunk_units(self, units: List[str], size: int, overlap: int,
                    min_size: int) -> List[str]:
        if not units:
            return []

        chunks = []
        current = []
        current_length = 0

        for unit in units:
            unit_length = len(unit)

            if current_length + unit_length > size and current:
                chunk_text = ' '.join(current)
                chunks.append(chunk_text)

                overlap_length = 0
                overlap_units = []
                for u in reversed(current):
                    if overlap_length + len(u) > overlap:
                        break
                    overlap_units.insert(0, u)
                    overlap_length += len(u)

                current = overlap_units
                current_length = overlap_length

            current.append(unit)
            current_length += unit_length

        if current:
            chunk_text = ' '.join(current)
            if len(chunk_text) >= min_size or not chunks:
                chunks.append(chunk_text)
            else:
                chunks[-1] += ' ' + chunk_text

        return chunks

    def _add_chunk_metadata(self, chunks: List[str]) -> List[str]:
        total = len(chunks)
        return [f"Chunk {i+1}/{total}: {chunk}" for i, chunk in enumerate(chunks)]

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        enabled = self._parms["enabled"].eval()
        chunk_mode = self._parms["chunk_mode"].eval()
        chunk_size = self._parms["chunk_size"].eval()
        overlap_size = self._parms["overlap_size"].eval()
        respect_boundaries = self._parms["respect_boundaries"].eval()
        min_chunk_size = self._parms["min_chunk_size"].eval()
        add_metadata = self._parms["add_metadata"].eval()

        input_data = []
        if self.inputs():
            raw_input = self.inputs()[0].output_node().eval(requesting_node=self)
            if isinstance(raw_input, list):
                input_data = [str(item) for item in raw_input]

        if not enabled or not input_data:
            self._output = input_data
        else:
            all_chunks = []
            for item in input_data:
                if chunk_mode == "character":
                    chunks = self._chunk_by_character(
                        item, chunk_size, overlap_size, respect_boundaries, min_chunk_size
                    )
                elif chunk_mode == "sentence":
                    chunks = self._chunk_by_sentence(
                        item, chunk_size, overlap_size, min_chunk_size
                    )
                elif chunk_mode == "paragraph":
                    chunks = self._chunk_by_paragraph(
                        item, chunk_size, overlap_size, min_chunk_size
                    )
                else:
                    chunks = [item]

                if add_metadata:
                    chunks = self._add_chunk_metadata(chunks)

                all_chunks.extend(chunks)

            self._output = all_chunks

        param_str = f"{enabled}{chunk_mode}{chunk_size}{overlap_size}{respect_boundaries}{min_chunk_size}{add_metadata}"
        self._param_hash = self._calculate_hash(param_str)
        self._input_hash = self._calculate_hash(str(input_data))

        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True

        try:
            enabled = self._parms["enabled"].raw_value()
            chunk_mode = self._parms["chunk_mode"].raw_value()
            chunk_size = self._parms["chunk_size"].raw_value()
            overlap_size = self._parms["overlap_size"].raw_value()
            respect_boundaries = self._parms["respect_boundaries"].raw_value()
            min_chunk_size = self._parms["min_chunk_size"].raw_value()
            add_metadata = self._parms["add_metadata"].raw_value()

            param_str = f"{enabled}{chunk_mode}{chunk_size}{overlap_size}{respect_boundaries}{min_chunk_size}{add_metadata}"
            new_param_hash = self._calculate_hash(param_str)

            input_data = []
            if self.inputs():
                input_data = self.inputs()[0].output_node().get_output()
            new_input_hash = self._calculate_hash(str(input_data))

            return new_input_hash != self._input_hash or new_param_hash != self._param_hash
        except Exception:
            return True

    def _calculate_hash(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()

    def input_names(self) -> Dict[int, str]:
        return {0: "Input Text"}

    def output_names(self) -> Dict[int, str]:
        return {0: "Chunks"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}
