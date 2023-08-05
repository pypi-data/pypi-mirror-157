# AUTOGENERATED FILE! PLEASE DON'T EDIT
"""This module is not really fleshed out, not that useful/elegant, and I just use
:class:`~k1lib.cli.inp.cmd` instead"""
import k1lib.cli as cli
from typing import Union, List
__all__ = ["esearch", "efetch"]
def esearch(db:str="nucleotide", query:str="PRJNA257197"):
    return cli.cmd(f"esearch -db {db} -query {query}")
def efetch(db:str=None, ids:Union[str, List[str]]=None, format:str=None):
    args = ""
    if db is not None: args += f"-db {db} "
    if ids is not None:
        if isinstance(ids, (list, tuple)): ids = ",".join(ids)
        args += f"-id {ids} "
    if format is not None:
        args += f"-format {format} "
    return cli.cmd(f"efetch {args}")