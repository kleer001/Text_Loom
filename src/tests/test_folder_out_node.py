import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import tempfile
import shutil
from pathlib import Path
from core.folder_out_node import FolderOutNode
from core.base_classes import NodeType, NodeState
from core.text_node import TextNode


@pytest.fixture
def temp_output_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def folder_out_node(temp_output_dir):
    node = FolderOutNode("test_folder_out", "/test", [0.0, 0.0])
    node._parms["folder_path"].set(temp_output_dir)
    return node


@pytest.fixture
def text_source_node():
    node = TextNode("source", "/test", NodeType.TEXT)
    node._parms["text_string"].set('["First document", "Second document", "Third document"]')
    node._parms["pass_through"].set(False)
    return node


class TestFolderOutNodeBasics:

    def test_node_initialization(self):
        node = FolderOutNode("test", "/test", [0.0, 0.0])
        assert node.name() == "test"
        assert node._node_type == NodeType.FOLDER_OUT
        assert node._is_time_dependent is True
        assert isinstance(node._file_hashes, dict)
        assert len(node._file_hashes) == 0

    def test_default_parameters(self):
        node = FolderOutNode("test", "/test", [0.0, 0.0])
        assert node._parms["folder_path"].eval() == "./output"
        assert node._parms["filename_pattern"].eval() == "output_{count}.txt"
        assert node._parms["file_extension"].eval() == ".txt"
        assert node._parms["overwrite"].eval() is False
        assert node._parms["format_output"].eval() is True

    def test_node_metadata(self):
        node = FolderOutNode("test", "/test", [0.0, 0.0])
        assert node.GLYPH == '📂'
        assert node.SINGLE_INPUT is True
        assert node.SINGLE_OUTPUT is True
        assert node.input_names() == {0: "Input Text"}
        assert node.output_names() == {0: "File Paths"}
        assert node.input_data_types() == {0: "List[str]"}
        assert node.output_data_types() == {0: "List[str]"}


class TestFilenameGeneration:

    def test_generate_filename_with_count(self, folder_out_node):
        folder_out_node._parms["filename_pattern"].set("doc_{count}")
        filename = folder_out_node._generate_filename("test content", 0)
        assert filename == "doc_1.txt"

        filename = folder_out_node._generate_filename("test content", 5)
        assert filename == "doc_6.txt"

    def test_generate_filename_with_index(self, folder_out_node):
        folder_out_node._parms["filename_pattern"].set("file_{index}")
        filename = folder_out_node._generate_filename("test content", 0)
        assert filename == "file_0.txt"

        filename = folder_out_node._generate_filename("test content", 10)
        assert filename == "file_10.txt"

    def test_generate_filename_with_input(self, folder_out_node):
        folder_out_node._parms["filename_pattern"].set("output_{input}")
        filename = folder_out_node._generate_filename("Hello World", 0)
        assert filename == "output_Hello_World.txt"

        filename = folder_out_node._generate_filename("This is a very long content that exceeds twenty characters", 0)
        assert filename == "output_This_is_a_very_long_.txt"

    def test_generate_filename_with_multiple_patterns(self, folder_out_node):
        folder_out_node._parms["filename_pattern"].set("doc_{count}_{input}")
        filename = folder_out_node._generate_filename("Summary", 2)
        assert filename == "doc_3_Summary.txt"

    def test_generate_filename_with_custom_extension(self, folder_out_node):
        folder_out_node._parms["filename_pattern"].set("output_{count}")
        folder_out_node._parms["file_extension"].set(".md")
        filename = folder_out_node._generate_filename("test", 0)
        assert filename == "output_1.md"

    def test_generate_filename_preserves_extension_in_pattern(self, folder_out_node):
        folder_out_node._parms["filename_pattern"].set("output_{count}.txt")
        folder_out_node._parms["file_extension"].set(".txt")
        filename = folder_out_node._generate_filename("test", 0)
        assert filename == "output_1.txt"


class TestFilenameSanitization:

    def test_sanitize_basic_text(self, folder_out_node):
        result = folder_out_node._sanitize_filename("Hello World")
        assert result == "Hello_World"

    def test_sanitize_removes_invalid_chars(self, folder_out_node):
        result = folder_out_node._sanitize_filename('test/file\\name:with*bad?chars"<>|end')
        assert "/" not in result
        assert "\\" not in result
        assert ":" not in result
        assert "*" not in result
        assert "?" not in result
        assert '"' not in result
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result

    def test_sanitize_strips_whitespace_and_dots(self, folder_out_node):
        result = folder_out_node._sanitize_filename("  .test.  ")
        assert not result.startswith(".")
        assert not result.startswith(" ")
        assert not result.endswith(".")
        assert not result.endswith(" ")

    def test_sanitize_empty_string(self, folder_out_node):
        result = folder_out_node._sanitize_filename("")
        assert isinstance(result, str)

    def test_sanitize_preserves_valid_chars(self, folder_out_node):
        result = folder_out_node._sanitize_filename("test-file_123.txt")
        assert "test" in result
        assert "file" in result
        assert "123" in result


class TestCollisionHandling:

    def test_find_unique_filename_no_collision(self, folder_out_node, temp_output_dir):
        base_path = os.path.join(temp_output_dir, "test.txt")
        result = folder_out_node._find_unique_filename(base_path)
        assert result == base_path

    def test_find_unique_filename_with_overwrite(self, folder_out_node, temp_output_dir):
        folder_out_node._parms["overwrite"].set(True)
        base_path = os.path.join(temp_output_dir, "test.txt")
        Path(base_path).touch()

        result = folder_out_node._find_unique_filename(base_path)
        assert result == base_path

    def test_find_unique_filename_creates_suffix(self, folder_out_node, temp_output_dir):
        folder_out_node._parms["overwrite"].set(False)
        base_path = os.path.join(temp_output_dir, "test.txt")
        Path(base_path).touch()

        result = folder_out_node._find_unique_filename(base_path)
        assert result == os.path.join(temp_output_dir, "test_1.txt")

    def test_find_unique_filename_multiple_collisions(self, folder_out_node, temp_output_dir):
        folder_out_node._parms["overwrite"].set(False)
        base_path = os.path.join(temp_output_dir, "test.txt")
        Path(base_path).touch()
        Path(os.path.join(temp_output_dir, "test_1.txt")).touch()
        Path(os.path.join(temp_output_dir, "test_2.txt")).touch()

        result = folder_out_node._find_unique_filename(base_path)
        assert result == os.path.join(temp_output_dir, "test_3.txt")

    def test_find_unique_filename_preserves_extension(self, folder_out_node, temp_output_dir):
        folder_out_node._parms["overwrite"].set(False)
        base_path = os.path.join(temp_output_dir, "document.md")
        Path(base_path).touch()

        result = folder_out_node._find_unique_filename(base_path)
        assert result.endswith(".md")
        assert "_1" in result


class TestFileWriting:

    def test_writes_multiple_files(self, folder_out_node, text_source_node, temp_output_dir):
        folder_out_node.set_input(0, text_source_node, 0)
        folder_out_node._parms["filename_pattern"].set("doc_{count}")

        folder_out_node.cook()

        assert folder_out_node.state() == NodeState.UNCHANGED
        assert os.path.exists(os.path.join(temp_output_dir, "doc_1.txt"))
        assert os.path.exists(os.path.join(temp_output_dir, "doc_2.txt"))
        assert os.path.exists(os.path.join(temp_output_dir, "doc_3.txt"))

    def test_file_contents_correct(self, folder_out_node, text_source_node, temp_output_dir):
        folder_out_node.set_input(0, text_source_node, 0)
        folder_out_node._parms["filename_pattern"].set("doc_{count}")

        folder_out_node.cook()

        with open(os.path.join(temp_output_dir, "doc_1.txt"), 'r') as f:
            assert f.read() == "First document"

        with open(os.path.join(temp_output_dir, "doc_2.txt"), 'r') as f:
            assert f.read() == "Second document"

    def test_returns_file_paths(self, folder_out_node, text_source_node, temp_output_dir):
        folder_out_node.set_input(0, text_source_node, 0)

        result = folder_out_node.eval()

        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(path, str) for path in result)
        assert all(path.startswith(temp_output_dir) for path in result)

    def test_creates_directory_if_not_exists(self, folder_out_node, text_source_node, temp_output_dir):
        nested_dir = os.path.join(temp_output_dir, "nested", "deep", "path")
        folder_out_node._parms["folder_path"].set(nested_dir)
        folder_out_node.set_input(0, text_source_node, 0)

        folder_out_node.cook()

        assert os.path.exists(nested_dir)
        assert os.path.isdir(nested_dir)


class TestHashOptimization:

    def test_hash_prevents_rewrite_unchanged_content(self, folder_out_node, text_source_node, temp_output_dir):
        folder_out_node.set_input(0, text_source_node, 0)
        folder_out_node._parms["filename_pattern"].set("doc_{count}")

        folder_out_node.cook()
        file_path = os.path.join(temp_output_dir, "doc_1.txt")
        original_mtime = os.path.getmtime(file_path)

        import time
        time.sleep(0.1)

        folder_out_node.cook()
        new_mtime = os.path.getmtime(file_path)

        assert original_mtime == new_mtime

    def test_hash_triggers_write_on_changed_content(self, folder_out_node, temp_output_dir):
        source = TextNode("source", "/test", NodeType.TEXT)
        source._parms["text_string"].set('["Original content"]')
        source._parms["pass_through"].set(False)

        folder_out_node.set_input(0, source, 0)
        folder_out_node._parms["overwrite"].set(True)
        folder_out_node.cook()

        file_paths_1 = folder_out_node.get_output()
        with open(file_paths_1[0], 'r') as f:
            content1 = f.read()

        source._parms["text_string"].set('["Modified content"]')
        source.cook(force=True)
        folder_out_node.cook(force=True)

        file_paths_2 = folder_out_node.get_output()
        with open(file_paths_2[0], 'r') as f:
            content2 = f.read()

        assert content1 != content2
        assert content2 == "Modified content"

    def test_rewrite_after_state_change(self, folder_out_node, text_source_node, temp_output_dir):
        folder_out_node.set_input(0, text_source_node, 0)
        folder_out_node._parms["overwrite"].set(True)
        folder_out_node.cook()

        file_paths = folder_out_node.get_output()
        file_path = file_paths[0]

        os.remove(file_path)
        assert not os.path.exists(file_path)

        folder_out_node.set_state(NodeState.UNCOOKED)
        folder_out_node.cook()

        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            content = f.read()
        assert content == "First document"


class TestFormatOutput:

    def test_format_output_true_writes_raw_string(self, folder_out_node, text_source_node, temp_output_dir):
        folder_out_node.set_input(0, text_source_node, 0)
        folder_out_node._parms["format_output"].set(True)

        folder_out_node.cook()

        with open(os.path.join(temp_output_dir, "output_1.txt"), 'r') as f:
            content = f.read()

        assert content == "First document"
        assert "[" not in content
        assert "]" not in content

    def test_format_output_false_preserves_list_format(self, folder_out_node, temp_output_dir):
        source = TextNode("source", "/test", NodeType.TEXT)
        source._parms["text_string"].set('["test"]')
        source._parms["pass_through"].set(False)

        folder_out_node.set_input(0, source, 0)
        folder_out_node._parms["format_output"].set(False)

        folder_out_node.cook()

        with open(os.path.join(temp_output_dir, "output_1.txt"), 'r') as f:
            content = f.read()

        assert content == "['test']"


class TestErrorHandling:

    def test_error_on_no_input(self, folder_out_node):
        folder_out_node.cook()
        assert folder_out_node.state() == NodeState.UNCOOKED
        assert len(folder_out_node.errors()) > 0

    def test_error_on_invalid_input_type(self, folder_out_node):
        from core.null_node import NullNode

        source = NullNode("source", "/test", [0.0, 0.0])
        folder_out_node.set_input(0, source, 0)

        source._output = "not a list"
        source.set_state(NodeState.UNCHANGED)

        folder_out_node.cook()
        assert folder_out_node.state() == NodeState.UNCOOKED
        assert len(folder_out_node.errors()) > 0

    def test_handles_empty_list(self, folder_out_node, temp_output_dir):
        source = TextNode("source", "/test", NodeType.TEXT)
        source._parms["text_string"].set('[]')
        source._parms["pass_through"].set(False)

        folder_out_node.set_input(0, source, 0)
        folder_out_node.cook()

        result = folder_out_node.get_output()
        assert isinstance(result, list)


class TestEdgeCases:

    def test_handles_very_long_content(self, folder_out_node, temp_output_dir):
        source = TextNode("source", "/test", NodeType.TEXT)
        long_text = "x" * 10000
        source._parms["text_string"].set(f'["{long_text}"]')
        source._parms["pass_through"].set(False)

        folder_out_node.set_input(0, source, 0)
        folder_out_node.cook()

        assert folder_out_node.state() == NodeState.UNCHANGED

    def test_handles_special_characters_in_content(self, folder_out_node, temp_output_dir):
        source = TextNode("source", "/test", NodeType.TEXT)
        source._parms["text_string"].set('["Line1\\nLine2\\tTabbed"]')
        source._parms["pass_through"].set(False)

        folder_out_node.set_input(0, source, 0)
        folder_out_node.cook()

        assert folder_out_node.state() == NodeState.UNCHANGED

    def test_handles_unicode_content(self, folder_out_node, temp_output_dir):
        source = TextNode("source", "/test", NodeType.TEXT)
        source._parms["text_string"].set('["Hello 世界", "Emoji 🎉"]')
        source._parms["pass_through"].set(False)

        folder_out_node.set_input(0, source, 0)
        folder_out_node.cook()

        with open(os.path.join(temp_output_dir, "output_1.txt"), 'r', encoding='utf-8') as f:
            content = f.read()

        assert "世界" in content

    def test_handles_single_item_list(self, folder_out_node, temp_output_dir):
        source = TextNode("source", "/test", NodeType.TEXT)
        source._parms["text_string"].set('["Only one"]')
        source._parms["pass_through"].set(False)

        folder_out_node.set_input(0, source, 0)
        folder_out_node.cook()

        result = folder_out_node.get_output()
        assert len(result) == 1
