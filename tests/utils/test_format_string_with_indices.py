from src.utils.text import format_string_with_indices


class TestFormatStringWithIndices:
    def test_format_string_with_indices(self) -> None:
        """Test basic string formatting with single variables."""
        result, indices = format_string_with_indices(
            "The {adjective} brown {animal}", adjective="quick", animal="fox"
        )
        assert result == "The quick brown fox"
        assert indices == {"adjective": [(4, 9)], "animal": [(16, 19)]}

    def test_format_string_with_indices_multiple_occurrences(self) -> None:
        """Test that repeated variables are tracked correctly."""
        result, indices = format_string_with_indices(
            "{name} likes {name}", name="Alice"
        )
        assert result == "Alice likes Alice"
        assert indices == {"name": [(0, 5), (12, 17)]}

    def test_format_string_with_indices_no_placeholders(self) -> None:
        """Test string with no placeholders."""
        result, indices = format_string_with_indices("Hello world")
        assert result == "Hello world"
        assert indices == {}

    def test_format_string_with_indices_missing_variable(self) -> None:
        """Test that missing variables are not replaced."""
        result, indices = format_string_with_indices(
            "Hello {name}, you are {age}. {name}? {age}", name="Bob"
        )
        assert result == "Hello Bob, you are {age}. Bob? {age}"
        assert indices == {"name": [(6, 9), (26, 29)]}

    def test_format_string_with_indices_empty_string(self) -> None:
        """Test empty format string."""
        result, indices = format_string_with_indices("")
        assert result == ""
        assert indices == {}

    def test_format_string_with_indices_only_placeholder(self) -> None:
        """Test string that is only a placeholder."""
        result, indices = format_string_with_indices("{value}", value="test")
        assert result == "test"
        assert indices == {"value": [(0, 4)]}

    def test_format_string_with_indices_adjacent_placeholders(self) -> None:
        """Test adjacent placeholders with no space between them."""
        result, indices = format_string_with_indices(
            "{first}{second}", first="Hello", second="World"
        )
        assert result == "HelloWorld"
        assert indices == {"first": [(0, 5)], "second": [(5, 10)]}

    def test_format_string_with_indices_numeric_values(self) -> None:
        """Test that numeric values are converted to strings."""
        result, indices = format_string_with_indices("I have {count} apples", count=42)
        assert result == "I have 42 apples"
        assert indices == {"count": [(7, 9)]}

    def test_format_string_with_indices_variable_names(self) -> None:
        """Test that variable names can contain underscores and numbers."""
        result, indices = format_string_with_indices(
            "Value: {var_1}, another: {value_2_name}",
            var_1="first",
            value_2_name="second",
        )
        assert result == "Value: first, another: second"
        assert indices == {"var_1": [(7, 12)], "value_2_name": [(23, 29)]}
