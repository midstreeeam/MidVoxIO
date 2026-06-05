import numpy as np

from midvoxio.models import XYZI
from midvoxio.voxio import get_vox, write_list_to_vox
from midvoxio.writer import ArrayWriter


def test_transparent_palette_color_is_written_as_empty_space():
    palette = np.zeros((255, 4), dtype=np.uint8)
    palette[0] = [0, 0, 0, 0]
    palette[88] = [10, 20, 30, 255]
    palette[93] = [40, 50, 60, 255]

    arr = np.zeros((3, 1, 1, 4), dtype=float)
    arr[0, 0, 0] = palette[93] / 255
    arr[2, 0, 0] = palette[88] / 255

    writer = ArrayWriter(arr, palette_arr=palette)

    assert writer.xyzi.xyzi.tolist() == [[[94]], [[0]], [[89]]]
    assert _written_voxels(writer.xyzi) == [
        (0, 0, 0, 94),
        (2, 0, 0, 89),
    ]


def test_issue_15_round_trip_keeps_middle_voxel_empty(tmp_path):
    palette = np.zeros((255, 4), dtype=np.uint8)
    palette[88] = [10, 20, 30, 255]
    palette[93] = [40, 50, 60, 255]

    arr = np.zeros((3, 1, 1, 4), dtype=float)
    arr[0, 0, 0] = palette[93] / 255
    arr[2, 0, 0] = palette[88] / 255

    out = tmp_path / "3x1_out.vox"
    write_list_to_vox(arr, str(out), palette_arr=palette)

    assert get_vox(str(out)).voxels == [[(0, 0, 0, 94), (2, 0, 0, 89)]]


def test_last_parsed_palette_color_can_be_written():
    palette = np.zeros((255, 4), dtype=np.uint8)
    palette[254] = [1, 2, 3, 255]

    arr = np.zeros((1, 1, 1, 4), dtype=float)
    arr[0, 0, 0] = palette[254] / 255

    writer = ArrayWriter(arr, palette_arr=palette)

    assert writer.xyzi.xyzi.tolist() == [[[255]]]
    assert _written_voxels(writer.xyzi) == [(0, 0, 0, 255)]


def _written_voxels(xyzi: XYZI):
    raw = xyzi.to_b()
    count = np.frombuffer(raw[:4], dtype=np.int32)[0]
    return [tuple(voxel) for voxel in np.frombuffer(raw[4:], dtype=np.uint8).reshape(count, 4)]
