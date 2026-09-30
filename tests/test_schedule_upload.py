"""Unit tests for the schedule-review additions to chat_logic: no network, no Streamlit."""

import io
from pathlib import Path

import pytest
from openpyxl import Workbook

import chat_logic
from chat_logic import (
    EMPTY_UPLOAD_MESSAGE,
    MAX_UPLOAD_IMAGE_BYTES,
    MAX_UPLOAD_SHEET_BYTES,
    MAX_UPLOAD_TEXT_BYTES,
    MAX_UPLOAD_TEXT_CHARS,
    UNREADABLE_SHEET_MESSAGE,
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
        content, _display = upload_to_turn("week41.csv", CSV)
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

    def test_oversized_text_is_refused_before_it_is_decoded(self, monkeypatch):
        class Undecodable(bytes):
            def decode(self, *args, **kwargs):
                raise AssertionError("decoded despite exceeding the byte ceiling")

        data = Undecodable(b"\x00" * (MAX_UPLOAD_TEXT_BYTES + 1))
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

    def test_corrupt_xlsx_gets_its_own_copy_not_the_empty_message(self):
        with pytest.raises(UploadError, match="could not be read"):
            upload_to_turn("broken.xlsx", b"this is not a zip")
        with pytest.raises(UploadError, match=UNREADABLE_SHEET_MESSAGE):
            upload_to_turn("broken.xlsx", b"this is not a zip")

    def test_missing_openpyxl_is_the_operators_defect_and_propagates(self, monkeypatch):
        def no_openpyxl(_data):
            raise ImportError("No module named 'openpyxl'")

        monkeypatch.setattr(chat_logic, "_sheet_to_text", no_openpyxl)
        with pytest.raises(ImportError):
            upload_to_turn("week41.xlsx", b"PK\x03\x04 whatever")

    def test_oversized_workbook_is_refused_before_it_is_parsed(self, monkeypatch):
        def must_not_run(_data):
            raise AssertionError("workbook was parsed despite exceeding the byte ceiling")

        monkeypatch.setattr(chat_logic, "_sheet_to_text", must_not_run)
        with pytest.raises(UploadError, match=UPLOAD_TOO_LARGE_MESSAGE):
            upload_to_turn("huge.xlsx", b"\x00" * (MAX_UPLOAD_SHEET_BYTES + 1))

    def test_rendering_stops_once_the_text_bound_is_passed(self):
        # 2,000 rows of 40 chars is ~80k chars of output; the bound is 40k.
        rows = [["x" * 40] for _ in range(2_000)]
        text = chat_logic._sheet_to_text(xlsx_bytes(rows))
        assert MAX_UPLOAD_TEXT_CHARS < len(text) < 2 * MAX_UPLOAD_TEXT_CHARS
        with pytest.raises(UploadError, match=UPLOAD_TOO_LARGE_MESSAGE):
            upload_to_turn("long.xlsx", xlsx_bytes(rows))

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


class TestUploadPinning:
    """The latest upload stays in the API payload after the window scrolls past it."""

    def upload_turn(self, name="week41.csv"):
        history = []
        content, display = upload_to_turn(name, CSV)
        append_message(history, "user", content, display=display)
        return history[0]

    def chatter(self, count, start=0):
        return [
            {"role": "assistant" if i % 2 == 0 else "user", "content": f"turn {i}"}
            for i in range(start, start + count)
        ]

    def test_upload_inside_the_window_is_not_duplicated(self):
        history = [self.upload_turn()] + self.chatter(5)
        payload = build_api_messages(history, "SYSTEM", max_turns=20)
        assert [m["content"] for m in payload[1:]] == [m["content"] for m in history]

    def test_upload_evicted_by_the_window_is_carried_forward_first(self):
        upload = self.upload_turn()
        history = [upload] + self.chatter(30)
        payload = build_api_messages(history, "SYSTEM", max_turns=20)
        assert len(payload) == 22
        assert payload[0]["content"] == "SYSTEM"
        assert payload[1] == {"role": "user", "content": upload["content"]}
        assert [m["content"] for m in payload[2:]] == [m["content"] for m in history[-20:]]

    def test_only_the_latest_evicted_upload_is_pinned(self):
        first = self.upload_turn("week40.csv")
        second = self.upload_turn("week41.csv")
        history = [first] + self.chatter(3) + [second] + self.chatter(30, start=3)
        payload = build_api_messages(history, "SYSTEM", max_turns=20)
        assert payload[1]["content"] is second["content"]
        assert all(m["content"] is not first["content"] for m in payload)

    def test_plain_history_is_unchanged_by_pinning(self):
        history = self.chatter(50)
        payload = build_api_messages(history, "SYSTEM", max_turns=20)
        assert len(payload) == 21
        assert payload[1:] == history[-20:]
