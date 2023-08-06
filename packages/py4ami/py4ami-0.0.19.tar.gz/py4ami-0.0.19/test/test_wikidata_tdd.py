# Tests wikipedia and wikidata methods under pytest
import os
from pathlib import Path
import logging

try:
    from ..py4ami.wikimedia import WikidataLookup
    from ..py4ami.dict_lib import AMIDict, AMIDictError, Entry
    logging.info(f"loaded py4ami.dict_lib")
except Exception:
    try:
        from py4ami.wikimedia import WikidataLookup
        from py4ami.dict_lib import AMIDict, AMIDictError, Entry
    except Exception as e:
        logging.severe(f"Cannot import from py4ami.dict_lib")

# NOTE some of these are lengthy (seconds) as they lookup on the Net


def test_lookup_wikidata_acetone():
    term = "acetone"
    wikidata_lookup = WikidataLookup()
    qitem0, desc, wikidata_hits = wikidata_lookup.lookup_wikidata(term)
    assert qitem0 == "Q49546"
    assert desc == "chemical compound"
    assert wikidata_hits == ['Q49546', 'Q24634417', 'Q329022', 'Q63986955', 'Q4673277']


def test_lookup_wikidata_bad():
    """This fails"""
    term = "benzene"
    wikidata_lookup = WikidataLookup()
    qitem0, desc, wikidata_hits = wikidata_lookup.lookup_wikidata(term)
    assert qitem0 == "Q170304"  # dopamine???
    assert desc == "hormone and neurotransmitter"
    # this needs mending as it found dopmamine (4-(2-azanylethyl)benzene-1,2-diol)
    assert wikidata_hits == ['Q170304', 'Q2270', 'Q15779', 'Q186242', 'Q28917']


def test_lookup_solvents():
    terms = ["acetone", "chloroform", "ethanol"]
    wikidata_lookup = WikidataLookup()
    qitems, descs = wikidata_lookup.lookup_items(terms)
    assert qitems == ['Q49546', 'Q172275', 'Q153']
    assert descs == ['chemical compound', 'chemical compound', 'chemical compound']


def test_lookup_parkinsons():
    terms = [
        "SCRNASeq",
        "SNPS",
        "A53T",
        "linkage disequilibrium",
        "Parkinsons",
        "transcriptomics"
    ]
    wikidata_lookup = WikidataLookup()
    # qitems, descs = wikidata_lookup.lookup_items(terms)
    temp_dir = Path(Path(__file__).parent.parent, "temp")
    dictfile, amidict = AMIDict.create_from_list_of_strings_and_write_to_file(terms, title="parkinsons",
                                                                              wikidata=True, directory=temp_dir)
    assert os.path.exists(dictfile)
