from struct import pack

import numpy as np

from midvoxio.models import XYZI
from midvoxio.voxio import get_vox, vox_to_arr, write_list_to_vox
from midvoxio.writer import ArrayWriter


def test_transparent_palette_color_is_written_as_empty_space():
    palette = _issue_palette()
    arr = np.zeros((3, 1, 1, 4), dtype=float)
    arr[0, 0, 0] = palette[93] / 255
    arr[2, 0, 0] = palette[88] / 255

    writer = ArrayWriter(arr, palette_arr=palette)

    assert writer.xyzi.xyzi.tolist() == [[[94]], [[0]], [[89]]]
    assert _written_voxels(writer.xyzi) == [
        (0, 0, 0, 94),
        (2, 0, 0, 89),
    ]


def test_issue_15_roundtrip_does_not_export_empty_cell_as_voxel(tmp_path):
    src = tmp_path / "3x1.vox"
    out = tmp_path / "3x1_out.vox"
    src.write_bytes(_minimal_vox_file())

    vox_arr = vox_to_arr(src, -1)
    imported_palette = get_vox(src).palettes[0]
    write_list_to_vox(vox_arr, out, palette_arr=imported_palette)

    assert get_vox(src).voxels == [[(0, 0, 0, 94), (2, 0, 0, 89)]]
    assert get_vox(out).voxels == [[(0, 0, 0, 94), (2, 0, 0, 89)]]


def test_last_parsed_palette_color_can_be_written():
    palette = np.zeros((255, 4), dtype=np.uint8)
    palette[254] = [1, 2, 3, 255]

    arr = np.zeros((1, 1, 1, 4), dtype=float)
    arr[0, 0, 0] = palette[254] / 255

    writer = ArrayWriter(arr, palette_arr=palette)

    assert writer.xyzi.xyzi.tolist() == [[[255]]]
    assert _written_voxels(writer.xyzi) == [(0, 0, 0, 255)]


def _issue_palette():
    palette = np.arange(255 * 4, dtype=np.uint8).reshape(255, 4)
    palette[:, 3] = 255
    palette[0] = [0, 0, 0, 0]
    palette[88] = [10, 20, 30, 255]
    palette[93] = [40, 50, 60, 255]
    return palette


def _minimal_vox_file():
    palette = _issue_palette()
    size = _chunk(b"SIZE", pack("3i", 3, 1, 1))
    xyzi = _chunk(b"XYZI", pack("i", 2) + bytes([0, 0, 0, 94, 2, 0, 0, 89]))
    rgba = _chunk(b"RGBA", palette.tobytes())
    children = size + xyzi + rgba
    return pack("4si", b"VOX ", 150) + pack("4sii", b"MAIN", 0, len(children)) + children


def _chunk(chunk_id, content):
    return pack("4sii", chunk_id, len(content), 0) + content


def _written_voxels(xyzi: XYZI):
    raw = xyzi.to_b()
    count = np.frombuffer(raw[:4], dtype=np.int32)[0]
    return [tuple(voxel) for voxel in np.frombuffer(raw[4:], dtype=np.uint8).reshape(count, 4)]
