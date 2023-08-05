"""Create entry."""
# pylint: disable=invalid-name, wrong-import-position, too-many-locals, too-many-statements
import sys
import os
import time
from pathlib import Path

import gradio as gr
import logzero
import pandas as pd
from about_time import about_time
from aset2pairs import aset2pairs
from cmat2aset import cmat2aset
from icecream import install as ic_install, ic
from logzero import logger
from seg_text import seg_text
from set_loglevel import set_loglevel

sys.path.insert(0, Path(__file__).parent.parent.as_posix())

from radio_mlbee import __version__  # noqa
from radio_mlbee.gen_cmat import gen_cmat  # noqa
from radio_mlbee.utils import text1 as text1_, text2 as text2_  # noqa

os.environ["LOGLEVEL"] = "10"  # turn debug on
os.environ["LOGLEVEL"] = "20"  # turn debug off
logzero.loglevel(set_loglevel())
if set_loglevel() <= 10:
    logger.info(" debug is on ")
else:
    logger.info(" debug is off ")

ic_install()
ic.configureOutput(
    includeContext=True,
    outputFunction=logger.info,
)
ic.enable()
# ic.disenable()  # to turn off

os.environ["TZ"] = "Asia/Shanghai"
try:
    time.tzset()  # type: ignore
except Exception as _:
    logger.warning("time.tzset() error: %s. Probably running Windows, we let it pass.", _)


def greet(name):
    """Greet."""
    if not name:
        name = "world"
    return "Hello " + name + "!! (coming sooooon...)"


def ml_fn(
    text1: str,
    text2: str,
    split_to_sents: bool = False,
    preview: bool = False,
    # download_csv: bool = False,  # modi
) -> pd.DataFrame:
    """Align multilingual (50+ pairs) text1 text2."""
    text1 = str(text1)
    text2 = str(text2)
    try:
        paras1 = text1.splitlines()
        paras1 = [_.strip() for _ in paras1 if _.strip()]
    except Exception as exc:
        logger.error(" praras.slpitlines() erros: %s, setting to ['']", exc)
        paras1 = [""]
    try:
        paras2 = text2.splitlines()
        paras2 = [_.strip() for _ in paras2 if _.strip()]
    except Exception as exc:
        logger.error(" praras slpitlines erros: %s, setting to ['']", exc)
        paras2 = [""]

    if split_to_sents:
        try:
            paras1 = seg_text(paras1)
        except Exception as exc:
            logger.error(exc)
        try:
            paras2 = seg_text(paras2)
        except Exception as exc:
            logger.error(exc)

    with about_time() as t:
        try:
            cmat = gen_cmat(paras1, paras2)
        except Exception as exc:
            logger.exception(exc)
            logger.info(paras1)
            logger.info(paras2)
            logger.info("len(paras1): %s, len(paras2): %s", len(paras1), len(paras2))
            cmat = [[]]
        try:
            aset = cmat2aset(cmat)
        except Exception as exc:
            logger.exception(exc)
            aset = [["", "", ""]]

    len1 = len(paras1)
    len2 = len(paras2)
    ic(len1, len2)

    if not (len1 and len2):
        _ = "At least one text is empty... nothing to do."
        return pd.DataFrame([[_]]), None, None

    av = ""
    len12 = len1 + len2
    if len12:
        av = f"{t.duration / len12 * 1000:.2f}"
    logger.info(" %s blocks, took %s, av. %s s/1000 blk", len12, t.duration_human, av)

    pairs = aset2pairs(paras1, paras2, aset)
    df = pd.DataFrame(pairs, columns=["text1", "text2", "llh"])

    html = None
    if preview:
        html = df.to_html()

    _ = """  # modi
    dl_csv = None
    csv_str = None
    if download_csv:
        try:
            dl_csv = Path("aligned-blocks.csv")
            csv_str = df.to_csv(index=False)
            dl_csv.write_text(csv_str, encoding="gbk")
            ic("Saving df.to_csv to dl_csv...")
        except Exception as exc:
            logger.exception(exc)
    # """

    # return df, html, dl_csv
    return df, html  # modi


iface = gr.Interface(
    fn=ml_fn,
    inputs=[
        "textarea",
        "textarea",
        gr.Checkbox(label="Split to sents?"),
        gr.Checkbox(label="Preview?"),
        # gr.Checkbox(label="Download csv?"),  # modi
    ],
    outputs=[
        "dataframe",
        "html",
        # gr.outputs.File(label="Click to download csv"),  # modi
    ],
    # outputs="html",
    title=f"radio-mlbee {__version__}",
    description="mlbee rest api on dev ",
    examples=[
        # [text1, text2, False],
        # [text1[: len(text1) // 5], text2[: len(text2) // 5], False, False, False],
        [text1_, text2_, False, False],  # modi
    ],
    allow_flagging="never",
)

debug = False
if set_loglevel() <= 10:
    debug = True

iface.launch(
    show_error=debug,
    enable_queue=True,
    debug=debug,
)
