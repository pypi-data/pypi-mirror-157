import builtins
import gc
import os
from io import SEEK_END, BytesIO
from pathlib import Path

import pytest
from heif_test import compare_heif_files_fields
from PIL import Image

from pillow_heif import _options  # noqa
from pillow_heif import HeifError, HeifFile, open_heif, options, register_heif_opener

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if not options().hevc_enc:
    pytest.skip("No HEVC encoder.", allow_module_level=True)
imagehash = pytest.importorskip("compare_hashes", reason="NumPy not installed")

register_heif_opener()


def test_outputs():
    with builtins.open(Path("images/rgb8_128_128_2_1.heic"), "rb") as f:
        output = BytesIO()
        open_heif(f).save(output, quality=10)
        assert output.seek(0, SEEK_END) > 0
        with builtins.open(Path("tmp.heic"), "wb") as output:
            open_heif(f).save(output, quality=10)
            assert output.seek(0, SEEK_END) > 0
        open_heif(f).save(Path("tmp.heic"), quality=10)
        assert Path("tmp.heic").stat().st_size > 0
        Path("tmp.heic").unlink()
        with pytest.raises(TypeError):
            open_heif(f).save(bytes(b"1234567890"), quality=10)


def test_save_empty():
    heic_file = open_heif(Path("images/rgb8_512_512_1_2.heic"))
    del heic_file[0]
    out_buffer = BytesIO()
    with pytest.raises(ValueError):
        heic_file.save(out_buffer)


def test_save_empty_with_append():
    empty_heic_file = HeifFile()
    heic_file = open_heif(Path("images/rgb8_128_128_2_1.heic"))
    out_buffer = BytesIO()
    empty_heic_file.save(out_buffer, append_images=heic_file)
    compare_heif_files_fields(heic_file, open_heif(out_buffer))
    empty_heic_file.save(out_buffer, append_images=heic_file, save_all=False)
    heic_file = open_heif(out_buffer)
    assert len(heic_file) == 1


@pytest.mark.parametrize(
    "image_path,remove_img,remove_thumb,expected",
    (
        ("images/rgb8_512_512_1_2.heic", [], [(0, 1)], (1, 1)),
        ("images/rgb8_128_128_2_1.heic", [0], [], (1, 1)),
        ("images/rgb8_128_128_2_1.heic", [1], [], (1, 1)),
        ("images/rgb8_128_128_2_1.heic", [1], [(0, 0)], (1, 0)),
        ("images/rgb8_210_128_2_2.heic", [0], [(0, 0)], (1, 1)),
        ("images/rgb8_210_128_2_2.heic", [0], [(0, 1)], (1, 1)),
        ("images/rgb10_639_480_1_3.heic", [], [(0, 1), (0, 0)], (1, 1)),
    ),
)
def test_remove(image_path, remove_img: list, remove_thumb: list, expected: tuple):
    heic_file_2_images = open_heif(Path(image_path))
    for remove_index in remove_img:
        del heic_file_2_images[remove_index]
    for remove_tuple in remove_thumb:
        del heic_file_2_images[remove_tuple[0]].thumbnails[remove_tuple[1]]
    out_buffer = BytesIO()
    heic_file_2_images.save(out_buffer)
    heic_file_1_image = open_heif(out_buffer)
    assert len(heic_file_1_image) == expected[0]
    assert len(heic_file_1_image.thumbnails) == expected[1]


@pytest.mark.parametrize(
    "thumbs,expected",
    (
        (-1, [1, 1]),
        ([-1], [1, 1]),
        (0, [1, 1]),
        ([0], [1, 1]),
        (1, [1, 1]),
        ([1], [1, 1]),
        (64, [1, 2]),
        ([64], [1, 2]),
        ([2048], [1, 1]),
        (96, [2, 2]),
        ([96], [2, 2]),
        ([84, 0], [2, 2]),
        ([0, 84], [2, 2]),
        ([96, 84], [3, 3]),
    ),
)
def test_add_thumbs(thumbs, expected):
    for i, image_path in enumerate((Path("images/rgb8_128_128_2_1.heic"), Path("images/rgb8_150_128_2_1.heic"))):
        heif_file = open_heif(image_path)
        heif_file[0].add_thumbnails(thumbs)
        heif_file.add_thumbnails(thumbs)
        output = BytesIO()
        heif_file.save(output, quality=100)
        out_heif = open_heif(output)
        assert len(out_heif[0].thumbnails) == expected[i]
        assert len(out_heif[1].thumbnails) == expected[i]
        imagehash.compare_hashes(
            [heif_file[0].to_pillow(), out_heif[0].to_pillow(), *[i.to_pillow() for i in out_heif[0].thumbnails]],
            hash_size=8,
            max_difference=2,
        )
        imagehash.compare_hashes(
            [heif_file[1].to_pillow(), out_heif[1].to_pillow(), *[i.to_pillow() for i in out_heif[1].thumbnails]],
            hash_size=8,
            max_difference=2,
        )


def test_append_images():
    heif_file = open_heif(Path("images/rgb8_210_128_2_2.heic"))
    heif_file2 = open_heif(Path("images/rgb8_150_128_2_1.heic"))
    heif_file3 = open_heif(Path("images/rgb8_128_128_2_1.heic"))
    out_buf = BytesIO()
    heif_file.save(out_buf, append_images=[heif_file2, heif_file3, heif_file3[1]])
    heif_file_out = open_heif(out_buf)
    assert len([i for i in heif_file_out.thumbnails_all()]) == 4 + 2 + 2 + 1
    assert len(heif_file_out) == 7
    compare_heif_files_fields(heif_file[0], heif_file_out[0])
    compare_heif_files_fields(heif_file[1], heif_file_out[1])
    compare_heif_files_fields(heif_file2[0], heif_file_out[2])
    compare_heif_files_fields(heif_file2[1], heif_file_out[3])
    compare_heif_files_fields(heif_file3[0], heif_file_out[4])
    compare_heif_files_fields(heif_file3[1], heif_file_out[5])


def test_10_bit():
    heif_file = open_heif(Path("images/mono10.heif"), convert_hdr_to_8bit=False)
    heif_file.add_from_heif(heif_file)
    assert len(heif_file) == 2
    compare_heif_files_fields(heif_file[0], heif_file[1])
    heif_file_to_add = open_heif(Path("images/rgba10.heif"), convert_hdr_to_8bit=False)
    heif_file.add_from_heif(heif_file_to_add)
    heif_file.add_from_heif(heif_file_to_add[0])
    compare_heif_files_fields(heif_file[2], heif_file[3])
    heif_file_to_add = None  # noqa
    gc.collect()
    out_buf = BytesIO()
    heif_file.save(out_buf, enc_params=[("x265:ctu", "32")])
    heif_file = open_heif(out_buf, convert_hdr_to_8bit=False)
    assert len(heif_file) == 4
    compare_heif_files_fields(heif_file[0], heif_file[1])
    compare_heif_files_fields(heif_file[2], heif_file[3])
    assert heif_file[0].bit_depth == 10
    assert heif_file[0].mode == "RGBA;10"
    assert heif_file[2].bit_depth == 10
    assert heif_file[2].mode == "RGBA;10"


def test_save_all():
    heif_file = open_heif(Path("images/rgb8_210_128_2_2.heic"))
    out_buf_save_all = BytesIO()
    heif_file.save(out_buf_save_all, save_all=True, quality=15)
    out_buf_save_one = BytesIO()
    heif_file.save(out_buf_save_one, save_all=False, quality=15)
    assert len(open_heif(out_buf_save_all)) == 2
    assert len(open_heif(out_buf_save_one)) == 1


def test_hif_file():
    heif_file1 = open_heif(Path("images/etc_heif/cat.hif"))
    assert heif_file1.original_bit_depth == 10
    out_buf = BytesIO()
    heif_file1.save(out_buf, quality=10)
    heif_file2 = open_heif(out_buf)
    assert heif_file2.original_bit_depth == 8
    compare_heif_files_fields(heif_file1, heif_file2, ignore=["t_stride", "original_bit_depth"])


def test_no_encoder():
    try:
        _options.CFG_OPTIONS._hevc_enc = False
        heic_file = open_heif(Path("images/rgb8_128_128_2_1.heic"))
        out_buffer = BytesIO()
        with pytest.raises(HeifError):
            heic_file.save(out_buffer)
    finally:
        _options.CFG_OPTIONS = _options.PyLibHeifOptions()


def test_scale():
    heic_file = open_heif(Path("images/rgb8_512_512_1_0.heic"))
    heic_file.scale(754, 754)
    out_buffer = BytesIO()
    heic_file.save(out_buffer, quality=-1)
    imagehash.compare_hashes([Path("images/rgb8_512_512_1_0.heic"), out_buffer])


def test_add_from():
    heif_file1 = open_heif(Path("images/rgb8_512_512_1_0.heic"))
    heif_file2 = open_heif(Path("images/rgb8_210_128_2_2.heic"))
    heif_file1.add_from_heif(heif_file2, load_one=True)
    heif_file1.add_from_heif(heif_file2[1], load_one=True)
    heif_file1.add_from_heif(heif_file2[1])
    gc.collect()
    out_buf = BytesIO()
    heif_file1.save(out_buf, quality=100)
    out_heif = open_heif(out_buf)
    assert len(out_heif) == 4
    assert len(list(out_heif.thumbnails_all(one_for_image=True))) == 3
    assert len(list(out_heif.thumbnails_all(one_for_image=False))) == 6
    compare_heif_files_fields(heif_file1[0], out_heif[0])
    compare_heif_files_fields(heif_file2[0], out_heif[1])
    compare_heif_files_fields(heif_file2[1], out_heif[2])
    compare_heif_files_fields(heif_file2[1], out_heif[3])
    pillow_image = Image.open(out_buf)
    imagehash.compare_hashes([pillow_image, Path("images/rgb8_512_512_1_0.heic")])
    pillow_image.seek(1)
    pillow_original = Image.open(Path("images/rgb8_210_128_2_2.heic"))
    imagehash.compare_hashes([pillow_image, pillow_original])
    pillow_image.seek(2)
    pillow_original.seek(1)
    imagehash.compare_hashes([pillow_image, pillow_original])


def test_primary_image():
    img1_2 = open_heif(Path("images/rgb8_128_128_2_1.heic"))
    img3 = open_heif(Path("images/rgb8_512_512_1_0.heic"))
    out_buf1 = BytesIO()
    img3.save(out_buf1, append_images=[img1_2[0], img1_2[1]], save_all=True, primary_index=1, quality=-1)
    heif_file = open_heif(out_buf1)
    assert heif_file.primary_index() == 1
    assert heif_file[1].info["primary"]
    out_buf2 = BytesIO()
    heif_file.save(out_buf2, quality=1)
    heif_file = open_heif(out_buf2)
    assert heif_file.primary_index() == 1
    assert heif_file[1].info["primary"]
    heif_file.save(out_buf1, quality=1, append_images=[heif_file])
    heif_file = open_heif(out_buf1)
    assert heif_file.primary_index() == 1
    heif_file.save(out_buf1, quality=1, primary_index=0)
    assert heif_file.primary_index() == 1
    heif_file2 = open_heif(out_buf1)
    assert heif_file2.primary_index() == 0
    heif_file2.save(out_buf2, primary_index=-1, quality=1)
    assert heif_file2.primary_index() == 0
    heif_file = open_heif(out_buf2)
    assert heif_file.primary_index() == 5
    heif_file2.save(out_buf1, primary_index=99, quality=1)
    assert heif_file2.primary_index() == 0
    heif_file = open_heif(out_buf1)
    assert heif_file.primary_index() == 5


def test_exif_removing():
    heif_file = open_heif(Path("images/rgb8_128_128_2_1.heic"))
    for frame in heif_file:
        assert frame.info["exif"]
    out_buf = BytesIO()
    heif_file.save(out_buf, exif=None, save_all=True)  # remove Exif from primary image
    assert heif_file.info["exif"]
    saved_heif = open_heif(out_buf)
    for i, frame in enumerate(saved_heif):
        assert frame.info["exif"] if i else not frame.info["exif"]


def test_xmp_add_remove():
    xmp_data = b"<xmp_data>"
    heif_file = open_heif(Path("images/rgb8_128_128_2_1.heic"))
    # No XMP in images
    for frame in heif_file:
        assert not frame.info["xmp"]
    out_buf = BytesIO()
    heif_file.save(out_buf, xmp=xmp_data, save_all=True)
    # Checking `heif_file` to not change
    for frame in heif_file:
        assert not frame.info["xmp"]
    saved_heif = open_heif(out_buf)
    # Checking that output  of`heif_file` was changed
    for i, frame in enumerate(saved_heif):
        assert not frame.info["xmp"] if i else frame.info["xmp"]
    out_buf2 = BytesIO()
    # Remove XMP from primary image
    saved_heif.save(out_buf2, xmp=None, save_all=True)
    # Checking `saved_heif` to not change
    for i, frame in enumerate(saved_heif):
        assert not frame.info["xmp"] if i else frame.info["xmp"]
    saved_heif2 = open_heif(out_buf2)
    # Checking that output has no XMP
    for i, frame in enumerate(saved_heif2):
        assert not frame.info["xmp"]
