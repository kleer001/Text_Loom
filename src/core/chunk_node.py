import hashlib
import time
import re
from typing import List, Dict
from core.base_classes import Node, NodeType, NodeState
from core.parm import Parm, ParameterType
from core.enums import FunctionalGroup

class ChunkNode(Node):
    """A node that splits text into chunks using various strategies.

    Supports chunking by character count, sentence boundaries, or paragraph boundaries.
    Can respect sentence/paragraph boundaries to avoid mid-sentence splits and supports
    overlapping chunks for context preservation. This is particularly useful for
    preparing text for LLM processing with token limits or creating manageable text
    segments.

    Attributes:
        chunk_mode (str): Determines the chunking strategy. Options: "character"
            (splits by character count), "sentence" (splits by sentence boundaries
            using punctuation detection), "paragraph" (splits by paragraph boundaries
            using double newlines).
        chunk_size (int): Target size for each chunk in characters. The actual size
            may vary based on boundary respect settings. Default: 1000.
        overlap_size (int): Number of characters to overlap between consecutive chunks.
            Useful for maintaining context across chunk boundaries. Default: 100.
        respect_boundaries (bool): When True and chunk_mode is "character", avoids
            splitting mid-sentence. When False, splits strictly at character count.
            Default: True.
        min_chunk_size (int): Minimum size for a chunk in characters. Chunks smaller
            than this are merged with the previous chunk. Default: 50.
        add_metadata (bool): When True, prepends each chunk with metadata in format
            "Chunk N/Total: {content}". Default: False.
        enabled (bool): Enables/disables the node's functionality. Default: True.

    Example:
        >>> node = Node.create_node(NodeType.CHUNK, node_name="chunker")
        >>> node._parms["chunk_mode"].set("character")
        >>> node._parms["chunk_size"].set(500)
        >>> node._parms["overlap_size"].set(50)
        >>> node._parms["respect_boundaries"].set(True)
        >>> node.cook()
        # Splits text into ~500 character chunks with 50 character overlap

    Note:
        **Chunking Strategies:**
        *   "character": Splits by character count
        *   "sentence": Splits by sentence boundaries (uses punctuation detection)
        *   "paragraph": Splits by paragraph boundaries (double newlines)

        **Boundary Respect:**
        *   When respect_boundaries is True, chunks may be larger than chunk_size
        *   Sentence detection uses regex for periods, exclamation marks, question marks
        *   Paragraph detection requires double newlines (`\n\n`)

        **Input:**
        *   `List[str]`: Collection of text items to chunk

        **Output:**
        *   `List[str]`: Text chunks (all input items are chunked and concatenated)

        **Edge Cases:**
        *   Sentence detection: `(?<=[.!?])\s+` regex pattern
        *   Paragraph detection: requires `\n\n` separator
        *   Overlap is measured in characters, not semantic units
        *   Minimum chunk size prevents orphaned fragments
        *   Multiple input items are processed sequentially
        *   When respect_boundaries is True, chunks preserve complete sentences
        *   Metadata format when add_metadata is True: "Chunk N/Total: {content}"
    """

    GLYPH = '⊞'
    GROUP = FunctionalGroup.TEXT
    SINGLE_INPUT = True
    SINGLE_OUTPUT = True
    GROUP = FunctionalGroup.FILE

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

    def _split_units(self, text: str, mode: str) -> List[str]:
        if mode == 'sentence':
            return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        return [p.strip() for p in text.split('\n\n') if p.strip()]

    def _chunk_characters(self, text: str, size: int, overlap: int, min_size: int) -> List[str]:
        if not text or size <= 0:
            return [text] if text else []

        chunks, start = [], 0
        while start < len(text):
            chunk = text[start:start + size]
            if len(chunk) >= min_size or not chunks:
                chunks.append(chunk)
            else:
                chunks[-1] += chunk if chunks else chunk
            start += size - overlap
            if start >= len(text):
                break
        return chunks

    def _chunk_units(self, units: List[str], size: int, overlap: int, min_size: int) -> List[str]:
        if not units:
            return []

        chunks, current, current_len = [], [], 0
        for unit in units:
            if current_len + len(unit) > size and current:
                chunks.append(' '.join(current))
                overlap_items, overlap_len = [], 0
                for u in reversed(current):
                    if overlap_len + len(u) > overlap:
                        break
                    overlap_items.insert(0, u)
                    overlap_len += len(u)
                current, current_len = overlap_items, overlap_len

            current.append(unit)
            current_len += len(unit)

        if current:
            chunk_text = ' '.join(current)
            if len(chunk_text) >= min_size or not chunks:
                chunks.append(chunk_text)
            else:
                chunks[-1] += ' ' + chunk_text
        return chunks

    def _chunk_text(self, text: str, mode: str, size: int, overlap: int, respect: bool, min_size: int) -> List[str]:
        if mode == 'character':
            return self._chunk_units(self._split_units(text, 'sentence'), size, overlap, min_size) if respect else self._chunk_characters(text, size, overlap, min_size)
        return self._chunk_units(self._split_units(text, mode), size, overlap, min_size)

    def _get_input_data(self):
        if not self.inputs():
            return []
        raw = self.inputs()[0].output_node().eval(requesting_node=self)
        return [str(item) for item in raw] if isinstance(raw, list) else []

    def _compute_param_hash(self, accessor='eval'):
        getter = lambda k: getattr(self._parms[k], accessor)()
        keys = ['enabled', 'chunk_mode', 'chunk_size', 'overlap_size', 'respect_boundaries', 'min_chunk_size', 'add_metadata']
        return hashlib.md5(''.join(str(getter(k)) for k in keys).encode()).hexdigest()

    def _internal_cook(self, force: bool = False) -> None:
        self.set_state(NodeState.COOKING)
        self._cook_count += 1
        start_time = time.time()

        p = lambda k: self._parms[k].eval()
        input_data = self._get_input_data()

        if not p('enabled') or not input_data:
            self._output = input_data
        else:
            chunks = []
            for item in input_data:
                item_chunks = self._chunk_text(item, p('chunk_mode'), p('chunk_size'),
                                               p('overlap_size'), p('respect_boundaries'),
                                               p('min_chunk_size'))
                if p('add_metadata'):
                    total = len(item_chunks)
                    item_chunks = [f"Chunk {i+1}/{total}: {c}" for i, c in enumerate(item_chunks)]
                chunks.extend(item_chunks)
            self._output = chunks

        self._param_hash = self._compute_param_hash()
        self._input_hash = hashlib.md5(str(input_data).encode()).hexdigest()
        self.set_state(NodeState.UNCHANGED)
        self._last_cook_time = (time.time() - start_time) * 1000

    def needs_to_cook(self) -> bool:
        if super().needs_to_cook():
            return True
        try:
            return (self._compute_param_hash('raw_value') != self._param_hash or
                    hashlib.md5(str(self._get_input_data()).encode()).hexdigest() != self._input_hash)
        except Exception:
            return True

    def input_names(self) -> Dict[int, str]:
        return {0: "Input Text"}

    def output_names(self) -> Dict[int, str]:
        return {0: "Chunks"}

    def input_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}

    def output_data_types(self) -> Dict[int, str]:
        return {0: "List[str]"}
