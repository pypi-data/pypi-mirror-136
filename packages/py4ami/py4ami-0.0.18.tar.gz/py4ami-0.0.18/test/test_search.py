"""tests AmiSearch
"""

import logging
logging.warning("loading test_search")


def test_search():
    from py4ami.search_lib import AmiSearch, AmiRake
    from py4ami.dict_lib import AmiDictionary

    # option = "search"  # edit this
    #    option = "sparql"
    option = "rake"
    if option == "rake":
        print("no test for AmiRake")
        # AmiRake().test()
        pass

    elif option == "search":
        ami_search = AmiSearch()
        ami_search.run_args()
    elif option == "test":
        AmiRake().test()
    elif option == "sparql":
        AmiDictionary.test_dict_read()
    else:
        print("no option given")

