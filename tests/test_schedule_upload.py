"""Unit tests for the schedule-review additions to chat_logic: no network, no Streamlit."""

import io
from pathlib import Path

import pytest
from openpyxl import Workbook

from chat_logic import (
    EMPTY_UPLOAD_MESSAGE,
    MAX_UPLOAD_IMAGE_BYTES,
    MAX_UPLOAD_TEXT_CHARS,
    UNSUPPORTED_UPLOAD_MESSAGE,
    UPLOAD_INSTRUCTION,
    UPLOAD_TOO_LARGE_MESSAGE,
    UploadError,
    append_message,
    build_api_messages,
    display_text,
    load_system_prompt,
    upload_to_turn,
)

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "schedule_review.md"
CSV = b"Day,Start,End,Role,Person\nMon,07:00,15:00,Open Lead,Dana Kowalski\n"


def xlsx_bytes(rows, title="Week 41"):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = title
    for row in rows:
        sheet.append(row)
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class TestSystemPrompt:
    def test_shipped_prompt_loads_and_is_the_review_prompt(self):
        text = load_system_prompt(PROMPT_PATH)
        assert text.startswith("You are PrimeOps Schedule Review.")
        # The three commitments the product is built on must be in the prompt
        # the app actually ships, not only in the design doc.
        assert "first name and last initial only" in text
        assert "You are not a payroll tool." in text
        assert "You do not build a schedule from scratch" in text

    def test_empty_prompt_file_is_refused(self, tmp_path):
        path = tmp_path / "empty.md"
        path.write_text("  \n", encoding="utf-8")
        with pytest.raises(ValueError):
            load_system_prompt(path)

    def test_missing_prompt_file_is_refused(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_system_prompt(tmp_path / "missing.md")


class TestTextUploads:
    def test_csv_becomes_one_text_part_after_the_instruction(self):
        content, display = upload_to_turn("week41.csv", CSV)
        assert len(content) == 1
        assert content[0]["type"] == "text"
        assert content[0]["text"].startswith(UPLOAD_INSTRUCTION)
        assert "Dana Kowalski" in content[0]["text"]
        assert "File: week41.csv" in content[0]["text"]

    def test_display_names_the_file_and_never_the_cells(self):
        _, display = upload_to_turn("week41.csv", CSV)
        assert "week41.csv" in display
        assert "Dana" not in display

    def test_display_strips_directories_from_the_name(self):
        _, display = upload_to_turn("/home/manager/exports/week41.csv", CSV)
        assert "/home/manager" not in display
        assert "week41.csv" in display

    def test_extension_case_is_ignored(self):
        content, _ = upload_to_turn("WEEK41.CSV", CSV)
        assert content[0]["type"] == "text"

    def test_undecodable_bytes_are_replaced_not_raised(self):
        content, _ = upload_to_turn("notes.txt", b"Mon 07:00 \xff\xfe Dana K.")
        assert "Dana K." in content[0]["text"]

    def test_over_long_text_is_refused_with_the_trim_message(self):
        data = b"x" * (MAX_UPLOAD_TEXT_CHARS + 1)
        with pytest.raises(UploadError, match=UPLOAD_TOO_LARGE_MESSAGE):
            upload_to_turn("big.csv", data)

    def test_empty_or_whitespace_file_is_refused(self):
        with pytest.raises(UploadError, match=EMPTY_UPLOAD_MESSAGE):
            upload_to_turn("empty.csv", b"")
        with pytest.raises(UploadError, match=EMPTY_UPLOAD_MESSAGE):
            upload_to_turn("blank.csv", b"  \n\n")


class TestSheetUploads:
    def test_xlsx_rows_become_tab_separated_text_under_a_sheet_heading(self):
        data = xlsx_bytes([["Day", "Start", "Person"], ["Mon", "07:00", "Dana K."]])
        content, _ = upload_to_turn("week41.xlsx", data)
        text = content[0]["text"]
        assert "## Sheet: Week 41" in text
        assert "Day\tStart\tPerson" in text
        assert "Mon\t07:00\tDana K." in text

    def test_blank_rows_are_dropped_and_empty_cells_kept_in_place(self):
        data = xlsx_bytes([["Day", "Person"], [None, None], ["Tue", None]])
        content, _ = upload_to_turn("week41.xlsx", data)
        body = content[0]["text"].split("\n\n", 2)[2]
        assert body.splitlines() == ["## Sheet: Week 41", "Day\tPerson", "Tue\t"]

    def test_corrupt_xlsx_is_refused_not_raised(self):
        with pytest.raises(UploadError, match=EMPTY_UPLOAD_MESSAGE):
            upload_to_turn("broken.xlsx", b"this is not a zip")

    def test_sheet_with_no_cells_is_refused(self):
        with pytest.raises(UploadError, match=EMPTY_UPLOAD_MESSAGE):
            upload_to_turn("empty.xlsx", xlsx_bytes([]))


class TestImageUploads:
    @pytest.mark.parametrize(
        ("name", "mime"),
        [("shot.png", "image/png"), ("shot.jpg", "image/jpeg"),
         ("shot.JPEG", "image/jpeg"), ("shot.webp", "image/webp")],
    )
    def test_image_becomes_instruction_plus_data_url_part(self, name, mime):
        content, display = upload_to_turn(name, b"\x89PNG fake bytes")
        assert content[0] == {"type": "text", "text": UPLOAD_INSTRUCTION}
        assert content[1]["type"] == "image_url"
        assert content[1]["image_url"]["url"].startswith(f"data:{mime};base64,")
        assert Path(name).name in display

    def test_oversized_image_is_refused(self):
        data = b"\x00" * (MAX_UPLOAD_IMAGE_BYTES + 1)
        with pytest.raises(UploadError, match=UPLOAD_TOO_LARGE_MESSAGE):
            upload_to_turn("huge.png", data)


class TestRefusals:
    @pytest.mark.parametrize("name", ["schedule.pdf", "schedule.docx", "schedule", "x.exe"])
    def test_unsupported_types_are_refused_with_the_list_of_supported_ones(self, name):
        with pytest.raises(UploadError, match="CSV, TSV, TXT, XLSX"):
            upload_to_turn(name, b"data")
        with pytest.raises(UploadError, match=UNSUPPORTED_UPLOAD_MESSAGE):
            upload_to_turn(name, b"data")

    def test_upload_error_is_a_value_error(self):
        assert issubclass(UploadError, ValueError)


class TestContentPartTurns:
    def test_content_part_turn_needs_display_text(self):
        history = []
        with pytest.raises(ValueError):
            append_message(history, "user", [{"type": "text", "text": "x"}])
        with pytest.raises(ValueError):
            append_message(history, "user", [{"type": "text", "text": "x"}], display="  ")
        with pytest.raises(ValueError):
            append_message(history, "user", [], display="Uploaded")
        assert history == []

    def test_content_part_turn_is_stored_with_its_display(self):
        history = []
        content, display = upload_to_turn("week41.csv", CSV)
        append_message(history, "user", content, display=display)
        assert history[0]["content"] is content
        assert display_text(history[0]) == display

    def test_plain_turn_displays_its_content(self):
        history = []
        append_message(history, "assistant", "reply")
        assert display_text(history[0]) == "reply"
        assert "display" not in history[0]

    def test_api_payload_carries_parts_and_drops_display(self):
        history = []
        content, display = upload_to_turn("week41.csv", CSV)
        append_message(history, "user", content, display=display)
        append_message(history, "assistant", "read-back")
        payload = build_api_messages(history, "SYSTEM", max_turns=20)
        assert payload[1] == {"role": "user", "content": content}
        assert "display" not in payload[1]
        assert payload[2] == {"role": "assistant", "content": "read-back"}
